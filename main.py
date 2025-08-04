import asyncio
import aiohttp
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import json

# Импорты модулей проекта
from avito import AvitoClient
from chat_gpt import get_agent_response, extract_final_client_data, check_dialog_completion
from telegram import send_completed_application
from config import (
   COMPLETION_MARKER,
   AVITO_USER_ID,
   AVITO_CLIENT_ID,
   AVITO_CLIENT_SECRET,
   CHECK_INTERVAL,
   TIME_WINDOW_HOURS,
   MAX_MESSAGES_HISTORY,
   FOLLOWUP_CHECK_INTERVAL,
   FOLLOWUP_INTERVALS,
   FOLLOWUP_MESSAGES,
   WORK_HOUR_START,
   WORK_HOUR_END
)

# Этапы диалога
STAGE_GREETING = "greeting"
STAGE_RESIDENTS = "residents"
STAGE_CHILDREN = "children"
STAGE_PETS = "pets"
STAGE_RENTAL_PERIOD = "rental_period"
STAGE_DEADLINE = "deadline"
STAGE_CONTACTS = "contacts"
STAGE_COMPLETE = "complete"

class AvitoRentalBot:
   def __init__(self):
       # Хранилище состояния чатов (chat_id -> dialog_history)
       self.chat_states = defaultdict(list)
       # Отслеживание обработанных сообщений (chat_id -> last_message_timestamp)
       self.processed_messages = defaultdict(int)
       # Завершенные диалоги (чтобы не обрабатывать повторно)
       self.completed_chats = set()
       # Этапы диалогов (chat_id -> stage)
       self.chat_stages = defaultdict(lambda: STAGE_GREETING)
       # Follow-up состояния (chat_id -> {last_client_activity, next_followup_time, followup_stage})
       self.followup_states = defaultdict(dict)
       # Данные объявлений для чатов (chat_id -> item_data)
       self.chat_items = defaultdict(dict)
       
   def get_moscow_time(self):
       """Получить текущее время в МСК"""
       moscow_tz = timezone(timedelta(hours=3))
       return datetime.now(moscow_tz)
   
   def is_work_time(self, dt=None):
       """Проверка рабочего времени (9:30-21:00 МСК)"""
       if dt is None:
           dt = self.get_moscow_time()
       hour_minute = dt.hour + dt.minute / 60.0
       return WORK_HOUR_START <= hour_minute <= WORK_HOUR_END
   
   def calculate_next_followup_time(self, base_time, interval_seconds):
       """Рассчитать время следующего follow-up с учетом рабочих часов"""
       moscow_tz = timezone(timedelta(hours=3))
       target_time = datetime.fromtimestamp(base_time + interval_seconds, moscow_tz)
       
       # Если попадает в рабочее время - отправляем
       if self.is_work_time(target_time):
           return target_time.timestamp()
       
       # Иначе переносим на ближайший рабочий час
       if target_time.hour < WORK_HOUR_START:
           # Перенести на 9:30 того же дня
           target_time = target_time.replace(hour=9, minute=30, second=0, microsecond=0)
       else:
           # Перенести на 9:30 следующего дня
           target_time = target_time.replace(hour=9, minute=30, second=0, microsecond=0) + timedelta(days=1)
       
       return target_time.timestamp()
   
   def is_dialog_complete_check(self, messages):
       """Проверка завершенности диалога на основе собранной информации"""
       client_messages = []
       agent_messages = []
       
       for message in messages:
           if message.get("type") != "text":
               continue
           text = message.get("content", {}).get("text", "").strip().lower()
           if not text:
               continue
               
           if message.get("direction") == "out":
               agent_messages.append(text)
           else:
               client_messages.append(text)
       
       # Проверяем наличие маркера завершения в сообщениях агента
       has_completion_marker = any(COMPLETION_MARKER.lower() in msg for msg in agent_messages)
       if has_completion_marker:
           return True
       
       client_text = " ".join(client_messages).lower()
       
       # Проверяем базовую информацию
       has_residents = any(word in client_text for word in ["человек", "буду", "планирую", "один", "два", "три", "пара", "семья"])
       has_period = any(word in client_text for word in ["месяц", "год"]) or any(char.isdigit() for char in client_text if "месяц" in client_text)
       has_date = any(word in client_text for word in ["август", "сентябр", "октябр", "ноябр", "декабр", "январ", "феврал", "март", "апрел", "май", "июн", "июл"]) or ("число" in client_text and any(char.isdigit() for char in client_text))
       has_phone = any(len([c for c in msg if c.isdigit()]) >= 10 for msg in client_messages)
       
       return has_residents and has_period and has_date and has_phone
   
   def get_last_real_client_message(self, messages):
       """Получить последнее реальное сообщение от клиента (не системное, не удаленное)"""
       last_client_message = None
       
       for message in messages:
           if (message.get("direction") == "in" and 
               message.get("type") == "text" and 
               message.get("author_id", 0) != 0 and  # Не системное
               message.get("content", {}).get("text", "").strip() and
               "сообщение удалено" not in message.get("content", {}).get("text", "").lower()):
               
               if last_client_message is None or message.get("created", 0) > last_client_message.get("created", 0):
                   last_client_message = message
       
       return last_client_message
   
   def start_followup_sequence(self, chat_id, last_activity_time):
       """Запуск последовательности follow-up сообщений"""
       if chat_id in self.completed_chats:
           return
           
       next_time = self.calculate_next_followup_time(last_activity_time, FOLLOWUP_INTERVALS["2h"])
       
       self.followup_states[chat_id] = {
           "last_client_activity": last_activity_time,
           "next_followup_time": next_time,
           "followup_stage": "2h"
       }
       
       moscow_time = datetime.fromtimestamp(next_time, timezone(timedelta(hours=3)))
       print(f"Запланирован follow-up для чата {chat_id} на {moscow_time.strftime('%Y-%m-%d %H:%M:%S МСК')}")
   
   def stop_followup_sequence(self, chat_id):
       """Остановка последовательности follow-up сообщений"""
       if chat_id in self.followup_states:
           del self.followup_states[chat_id]
           print(f"Follow-up остановлен для чата {chat_id}")
   
   async def process_followups(self, client):
       """Обработка запланированных follow-up сообщений"""
       current_time = datetime.utcnow().timestamp()
       moscow_tz = timezone(timedelta(hours=3))
       
       for chat_id, state in list(self.followup_states.items()):
           if current_time >= state["next_followup_time"]:
               
               # Проверяем рабочее время для времени отправки
               send_time = datetime.fromtimestamp(state["next_followup_time"], moscow_tz)
               if not self.is_work_time(send_time):
                   # Если время отправки не рабочее, переносим на следующий рабочий час
                   new_time = self.calculate_next_followup_time(state["next_followup_time"], 0)
                   self.followup_states[chat_id]["next_followup_time"] = new_time
                   continue
               
               # Дополнительная проверка: не завершился ли диалог
               try:
                   messages = await client.get_messages(chat_id, limit=MAX_MESSAGES_HISTORY)
                   if self.is_dialog_complete_check(messages):
                       print(f"Диалог {chat_id} завершен, отменяем follow-up")
                       del self.followup_states[chat_id]
                       continue
               except:
                   pass  # Если не удалось проверить, продолжаем отправку
               
               # Отправляем follow-up сообщение
               stage = state["followup_stage"]
               message = FOLLOWUP_MESSAGES[stage]
               
               success = await client.send_message(chat_id, message)
               
               if success:
                   print(f"Отправлен follow-up {stage} в чат {chat_id}: {message}")
                   
                   # Планируем следующий follow-up с накопительными интервалами
                   base_time = state["last_client_activity"]
                   
                   if stage == "2h":
                       next_stage = "16h"
                       next_interval = FOLLOWUP_INTERVALS["16h"]  # 16 часов от начала
                   elif stage == "16h":
                       next_stage = "2d"
                       next_interval = FOLLOWUP_INTERVALS["2d"]   # 2 дня от начала
                   elif stage == "2d":
                       next_stage = "4d"
                       next_interval = FOLLOWUP_INTERVALS["4d"]   # 4 дня от начала
                   else:  # stage == "4d"
                       # Последний follow-up отправлен
                       del self.followup_states[chat_id]
                       continue
                   
                   # Рассчитываем время следующего follow-up от базового времени
                   next_time = self.calculate_next_followup_time(base_time, next_interval)
                   
                   self.followup_states[chat_id].update({
                       "next_followup_time": next_time,
                       "followup_stage": next_stage
                   })
               else:
                   print(f"Ошибка отправки follow-up в чат {chat_id}")

   def determine_dialog_stage(self, messages):
       """Определение текущего этапа диалога на основе истории сообщений"""
       agent_messages = []
       client_messages = []
       
       for message in messages:
           if message.get("type") != "text":
               continue
           text = message.get("content", {}).get("text", "").strip().lower()
           if not text:
               continue
               
           if message.get("direction") == "out":
               agent_messages.append(text)
           else:
               client_messages.append(text)
       
       # Если нет сообщений от агента - это начало
       if not agent_messages:
           return STAGE_GREETING
       
       # Проверяем, есть ли уже приветствие
       has_greeting = any("здравствуйте" in msg and "светлана" in msg for msg in agent_messages)
       if not has_greeting:
           return STAGE_GREETING
           
       # Анализируем собранную информацию из сообщений клиента
       client_text = " ".join(client_messages).lower()
       last_agent_msg = agent_messages[-1] if agent_messages else ""
       
       # Проверяем наличие информации о жильцах
       has_residents_info = any(word in client_text for word in ["человек", "буду", "планирую", "один", "два", "три", "семь", "пара", "семья"])
       
       # Проверяем наличие информации о сроке
       has_period_info = any(word in client_text for word in ["месяц", "год", "надолго", "постоянно"]) or any(char.isdigit() for char in client_text if "месяц" in client_text)
       
       # Проверяем наличие даты
       has_date_info = any(word in client_text for word in ["август", "сентябр", "октябр", "ноябр", "декабр", "январ", "феврал", "март", "апрел", "май", "июн", "июл"]) or ("число" in client_text and any(char.isdigit() for char in client_text))
       
       # Проверяем наличие телефона
       has_phone = any(len([c for c in msg if c.isdigit()]) >= 10 for msg in client_messages)
       
       # Определяем этап на основе собранной информации
       if not has_residents_info or "кто проживать планирует" in last_agent_msg:
           return STAGE_RESIDENTS
       elif ("дет" in last_agent_msg or "ребен" in last_agent_msg) and not has_period_info:
           return STAGE_CHILDREN
       elif ("животн" in last_agent_msg or "питом" in last_agent_msg) and not has_period_info:
           return STAGE_PETS
       elif not has_period_info or ("срок" in last_agent_msg or "месяц" in last_agent_msg):
           return STAGE_RENTAL_PERIOD
       elif not has_date_info or ("дата" in last_agent_msg or "заез" in last_agent_msg):
           return STAGE_DEADLINE
       elif not has_phone or ("телефон" in last_agent_msg or "номер" in last_agent_msg):
           return STAGE_CONTACTS
       else:
           return STAGE_COMPLETE  

   def format_dialog_history(self, messages):
       """Форматирование истории диалога для отправки в GPT"""
       dialog = []
       
       # Берем последние 30 сообщений и сортируем по времени (от старых к новым)
       recent_messages = messages[-MAX_MESSAGES_HISTORY:]
       sorted_messages = sorted(recent_messages, key=lambda x: x.get("created", 0))
       
       for message in sorted_messages:
           if message.get("type") != "text":
               continue
               
           # Фильтруем системные и удаленные сообщения
           if (message.get("author_id", 0) == 0 or 
               "сообщение удалено" in message.get("content", {}).get("text", "").lower()):
               continue
               
           direction = message.get("direction")
           text = message.get("content", {}).get("text", "").strip()
           
           if not text:
               continue
           
           # Определяем роль отправителя
           if direction == "in":
               dialog.append(f"Клиент: {text}")
           elif direction == "out":
               # Убираем дублирование "Светлана:" если оно уже есть в тексте
               clean_text = text
               if clean_text.startswith("Светлана: "):
                   clean_text = clean_text[10:].strip()  # Убираем "Светлана: "
               dialog.append(f"Светлана: {clean_text}")
       
       return "\n".join(dialog)
       
   async def process_chat(self, client, chat_id, chat_data):
       """Обработка отдельного чата"""
       try:
           # Проверяем, не завершен ли уже диалог
           if chat_id in self.completed_chats:
               return
           
           # Сохраняем данные объявления
           item_data = chat_data.get("context", {}).get("value", {})
           if item_data:
               self.chat_items[chat_id] = item_data
           
           # Получаем сообщения чата
           messages = await client.get_messages(chat_id, limit=MAX_MESSAGES_HISTORY)
           if not messages:
               return
           
           # Ищем последнее реальное сообщение от клиента
           last_incoming = self.get_last_real_client_message(messages)
           
           if not last_incoming:
               return
           
           # Проверяем временные рамки - обрабатываем только новые сообщения
           cutoff_time = datetime.utcnow() - timedelta(hours=TIME_WINDOW_HOURS)
           message_time = datetime.utcfromtimestamp(last_incoming["created"])
           
           if message_time < cutoff_time:
               return
           
           # Проверяем, не обработано ли уже это сообщение
           last_processed_time = self.processed_messages.get(chat_id, 0)
           if last_incoming["created"] <= last_processed_time:
               return
           
           # Проверяем, нет ли уже ответа на это сообщение
           has_newer_outgoing = any(
               m.get("direction") == "out" and m.get("created", 0) > last_incoming["created"]
               for m in messages
           )
           
           if has_newer_outgoing:
               return
           
           print(f"Получено сообщение: {last_incoming['content']['text'][:100]}...")
           
           # Останавливаем follow-up при получении нового сообщения от клиента
           self.stop_followup_sequence(chat_id)
           
           # Определяем текущий этап диалога
           current_stage = self.determine_dialog_stage(messages)
           self.chat_stages[chat_id] = current_stage
           
           # Определяем, первое ли это сообщение
           has_any_outgoing = any(m.get("direction") == "out" and m.get("type") == "text" for m in messages)
           is_first_message = not has_any_outgoing
           
           # Форматируем историю диалога для отправки в GPT
           dialog_history = self.format_dialog_history(messages)
           
           # ОТЛАДКА: выводим что отправляется в нейросеть
           print(f"=== ОТЛАДКА ЧАТА {chat_id} ===")
           print(f"current_stage: {current_stage}")
           print(f"is_first_message: {is_first_message}")
           print(f"dialog_history отправляемый в GPT:")
           print(dialog_history[-500:])  # Показываем только последние 500 символов
           print("=== КОНЕЦ ОТЛАДКИ ===")
           
           # Генерируем ответ через ChatGPT
           response = await get_agent_response(dialog_history, is_first_message)
           
           if not response:
               print(f"Не удалось сгенерировать ответ для чата {chat_id}")
               return
           
           # Удаляем маркер завершения из ответа перед отправкой клиенту
           clean_response = response.replace(COMPLETION_MARKER, "").strip()
           
           # Отправляем ответ клиенту
           success = await client.send_message(chat_id, clean_response)
           
           if success:
               print(f"Отправлен ответ: {clean_response[:100]}...")
               
               # Обновляем время последнего обработанного сообщения
               self.processed_messages[chat_id] = last_incoming["created"]
               
               # Сохраняем состояние диалога
               self.chat_states[chat_id].append(dialog_history)
               
               # Проверяем завершенность диалога по маркеру
               if check_dialog_completion(response):
                   await self.handle_completed_dialog(chat_id, dialog_history + f"\nСветлана: {clean_response}")
               else:
                   # Запускаем follow-up последовательность только если диалог не завершен
                   if not self.is_dialog_complete_check(messages):
                       self.start_followup_sequence(chat_id, last_incoming["created"])
                   
           else:
               print(f"Ошибка отправки ответа в чат {chat_id}")
               
       except Exception as e:
           print(f"Ошибка обработки чата {chat_id}: {e}")
   
   async def handle_completed_dialog(self, chat_id, final_dialog):
       """Обработка завершенного диалога"""
       try:
           print(f"Диалог завершен в чате {chat_id}, извлекаем данные клиента...")
           
           # Извлекаем структурированные данные клиента
           client_data = await extract_final_client_data(final_dialog)
           
           if client_data:
               print(f"Данные клиента извлечены: {json.dumps(client_data, ensure_ascii=False, indent=2)}")
               
               # Получаем данные объявления для этого чата
               item_data = self.chat_items.get(chat_id)
               
               # Отправляем заявку в Telegram с данными объявления
               success = await send_completed_application(client_data, item_data)
               
               if success:
                   print(f"Заявка отправлена в Telegram для чата {chat_id}")
               else:
                   print(f"Ошибка отправки заявки в Telegram для чата {chat_id}")
           else:
               print(f"Не удалось извлечь данные клиента из чата {chat_id}")
           
           # Помечаем чат как завершенный и останавливаем follow-up
           self.completed_chats.add(chat_id)
           self.stop_followup_sequence(chat_id)
           
       except Exception as e:
           print(f"Ошибка обработки завершенного диалога {chat_id}: {e}")
   
   async def run(self):
       """Основной цикл работы бота"""
       print("Запуск Avito Rental Bot...")
       print(f"Интервал проверки: {CHECK_INTERVAL} секунд")
       print(f"Временное окно: {TIME_WINDOW_HOURS} часов")
       print(f"Интервал проверки follow-up: {FOLLOWUP_CHECK_INTERVAL} секунд")
       
       # Последняя проверка follow-up
       last_followup_check = 0
       
       while True:
           try:
               current_time = datetime.utcnow().timestamp()
               
               # Создаем клиент Avito API
               async with AvitoClient(AVITO_USER_ID, AVITO_CLIENT_ID, AVITO_CLIENT_SECRET) as client:
                   # Проверяем follow-up сообщения
                   if current_time - last_followup_check >= FOLLOWUP_CHECK_INTERVAL:
                       await self.process_followups(client)
                       last_followup_check = current_time
                   
                   # Получаем список чатов
                   chats = await client.get_chats(limit=100)
                   print(f"Получено {len(chats)} чатов для проверки")
                   
                   # Создаем задачи для параллельной обработки чатов
                   tasks = []
                   for chat in chats:
                       chat_id = chat.get("id")
                       if chat_id:
                           task = asyncio.create_task(
                               self.process_chat(client, chat_id, chat)
                           )
                           tasks.append(task)
                   
                   # Ждем завершения всех задач
                   if tasks:
                       await asyncio.gather(*tasks, return_exceptions=True)
                   
                   print(f"Обработка завершена. Ожидание {CHECK_INTERVAL} секунд...")
                   
           except Exception as e:
               print(f"Критическая ошибка в основном цикле: {e}")
               print("Ожидание перед повторной попыткой...")
           
           # Ждем до следующей проверки
           await asyncio.sleep(CHECK_INTERVAL)

async def main():
   """Точка входа в приложение"""
   bot = AvitoRentalBot()
   await bot.run()

if __name__ == "__main__":
   # Запуск основного приложения
   try:
       asyncio.run(main())
   except KeyboardInterrupt:
       print("\nОстановка бота по запросу пользователя")
   except Exception as e:
       print(f"Критическая ошибка: {e}")