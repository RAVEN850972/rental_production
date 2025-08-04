#!/usr/bin/env python3
"""
Расширенный тестовый скрипт для Avito Rental Bot с реальными данными
Без отправки ответов на Авито (только в консоль)
"""

import asyncio
import json
from datetime import datetime, timezone, timedelta
import sys
import os

# Импорты из проекта
from config import (
    AVITO_USER_ID, AVITO_CLIENT_ID, AVITO_CLIENT_SECRET,
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
    FOLLOWUP_MESSAGES, FOLLOWUP_INTERVALS,
    WORK_HOUR_START, WORK_HOUR_END
)
from avito import AvitoClient
from chat_gpt import get_agent_response, extract_final_client_data, check_dialog_completion
from telegram import send_completed_application


class TestAvitoBot:
    def __init__(self):
        self.test_mode = True
        print("🧪 ТЕСТОВЫЙ РЕЖИМ - ответы НЕ отправляются на Авито")
        print("=" * 60)
    
    def get_moscow_time(self):
        """Получить текущее время в МСК"""
        moscow_tz = timezone(timedelta(hours=3))
        return datetime.now(moscow_tz)
    
    def is_work_time(self, dt=None):
        """Проверка рабочего времени"""
        if dt is None:
            dt = self.get_moscow_time()
        hour_minute = dt.hour + dt.minute / 60.0
        return WORK_HOUR_START <= hour_minute <= WORK_HOUR_END
    
    def calculate_next_followup_time(self, base_time, interval_seconds):
        """Рассчитать время следующего follow-up с учетом рабочих часов"""
        moscow_tz = timezone(timedelta(hours=3))
        target_time = datetime.fromtimestamp(base_time + interval_seconds, moscow_tz)
        
        if self.is_work_time(target_time):
            return target_time.timestamp()
        
        if target_time.hour < WORK_HOUR_START:
            target_time = target_time.replace(hour=9, minute=30, second=0, microsecond=0)
        else:
            target_time = target_time.replace(hour=9, minute=30, second=0, microsecond=0) + timedelta(days=1)
        
        return target_time.timestamp()
    
    async def test_real_avito_connection(self):
        """Тест реального подключения к Avito API"""
        print("\n🔌 Тестирование подключения к Avito API...")
        
        try:
            async with AvitoClient(AVITO_USER_ID, AVITO_CLIENT_ID, AVITO_CLIENT_SECRET) as client:
                chats = await client.get_chats(limit=5)
                print(f"✅ Подключение успешно! Найдено {len(chats)} чатов")
                
                if chats:
                    chat = chats[0]
                    chat_id = chat.get("id")
                    print(f"📂 Тестовый чат: {chat_id}")
                    
                    # Получаем сообщения из реального чата
                    messages = await client.get_messages(chat_id, limit=10)
                    print(f"💬 Сообщений в чате: {len(messages)}")
                    
                    # Показываем последние 3 сообщения
                    if messages:
                        print("\n📜 Последние сообщения:")
                        for i, msg in enumerate(messages[-3:], 1):
                            direction = "👤 Клиент" if msg.get("direction") == "in" else "🤖 Агент"
                            text = msg.get("content", {}).get("text", "")[:100]
                            print(f"  {i}. {direction}: {text}")
                    
                    return chat, messages
                else:
                    print("⚠️ Нет активных чатов для тестирования")
                    return None, []
                    
        except Exception as e:
            print(f"❌ Ошибка подключения к Avito: {e}")
            return None, []
    
    async def test_chatgpt_responses(self, messages=None):
        """Тест генерации ответов через ChatGPT"""
        print("\n🤖 Тестирование генерации ответов ChatGPT...")
        
        # Тестовые сценарии диалогов
        test_dialogs = [
            {
                "name": "Первое сообщение",
                "dialog": "Клиент: Здравствуйте! Интересует ваша квартира",
                "is_first": True
            },
            {
                "name": "Уточнение жильцов",
                "dialog": """Клиент: Здравствуйте! Интересует ваша квартира
Светлана: Здравствуйте, на связи Светлана, АН Skyline

Расскажите, пожалуйста, кто проживать планирует
Клиент: Буду жить с девушкой""",
                "is_first": False
            },
            {
                "name": "Завершенный диалог",
                "dialog": """Клиент: Здравствуйте! Интересует ваша квартира
Светлана: Здравствуйте, на связи Светлана, АН Skyline

Расскажите, пожалуйста, кто проживать планирует
Клиент: Буду жить один, мне 28 лет
Светлана: Спасибо! Дети будут?
Клиент: Нет
Светлана: Животные есть?
Клиент: Да, кот
Светлана: Понятно! На какой срок планируете снимать?
Клиент: Хотя бы на год
Светлана: Когда планируете заселиться?
Клиент: До 20 августа
Светлана: Как к Вам обращаться?
Клиент: Максим
Светлана: Номер телефона для связи?
Клиент: +79161234567""",
                "is_first": False
            }
        ]
        
        # Если есть реальные сообщения, добавляем их
        if messages:
            real_dialog = self.format_messages_for_gpt(messages)
            test_dialogs.insert(0, {
                "name": "Реальный чат",
                "dialog": real_dialog,
                "is_first": len([m for m in messages if m.get("direction") == "out"]) == 0
            })
        
        for test in test_dialogs:
            print(f"\n📝 Тест: {test['name']}")
            print(f"📄 Диалог:\n{test['dialog']}")
            
            response = await get_agent_response(test['dialog'], test['is_first'])
            
            print(f"🤖 Ответ GPT: {response}")
            
            # Проверяем завершенность
            is_complete = check_dialog_completion(response)
            print(f"🎯 Диалог завершен: {'Да' if is_complete else 'Нет'}")
            
            if is_complete:
                # Извлекаем данные клиента
                client_data = await extract_final_client_data(test['dialog'])
                if client_data:
                    print("📊 Извлеченные данные:")
                    print(json.dumps(client_data, ensure_ascii=False, indent=2))
            
            print("-" * 40)
    
    def format_messages_for_gpt(self, messages):
        """Форматирование сообщений для GPT"""
        dialog = []
        sorted_messages = sorted(messages, key=lambda x: x.get("created", 0))
        
        for message in sorted_messages:
            if message.get("type") != "text":
                continue
            
            direction = message.get("direction")
            text = message.get("content", {}).get("text", "").strip()
            
            if not text or message.get("author_id", 0) == 0:
                continue
            
            if direction == "in":
                dialog.append(f"Клиент: {text}")
            elif direction == "out":
                clean_text = text
                if clean_text.startswith("Светлана: "):
                    clean_text = clean_text[10:].strip()
                dialog.append(f"Светлана: {clean_text}")
        
        return "\n".join(dialog)
    
    async def test_followup_system(self):
        """Тест системы follow-up сообщений"""
        print("\n🔄 Тестирование системы follow-up...")
        
        current_time = self.get_moscow_time()
        print(f"⏰ Текущее время МСК: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏢 Рабочее время: {'Да' if self.is_work_time() else 'Нет'}")
        
        # Симулируем время последней активности клиента (2 часа назад)
        last_activity = current_time.timestamp() - 2 * 3600
        
        print(f"\n📅 Тестовые расчеты follow-up от времени: {datetime.fromtimestamp(last_activity, timezone(timedelta(hours=3))).strftime('%H:%M')}")
        
        for stage, interval in FOLLOWUP_INTERVALS.items():
            next_time = self.calculate_next_followup_time(last_activity, interval)
            next_dt = datetime.fromtimestamp(next_time, timezone(timedelta(hours=3)))
            
            message = FOLLOWUP_MESSAGES[stage]
            print(f"📤 {stage}: {next_dt.strftime('%d.%m %H:%M')} - {message}")
        
        # Тест отправки в рабочее и нерабочее время
        print(f"\n🕘 Тест расчета времени отправки:")
        
        test_times = [
            ("08:00", "До рабочего времени"),
            ("12:00", "Рабочее время"),
            ("22:00", "После рабочего времени"),
            ("02:00", "Ночь")
        ]
        
        for time_str, description in test_times:
            test_hour, test_minute = map(int, time_str.split(':'))
            test_dt = current_time.replace(hour=test_hour, minute=test_minute)
            
            is_work = self.is_work_time(test_dt)
            print(f"  {time_str} ({description}): {'✅ Отправляем' if is_work else '⏰ Переносим'}")
    
    async def test_telegram_sending(self):
        """Тест отправки в Telegram"""
        print("\n📱 Тестирование отправки в Telegram...")
        
        # Тестовые данные клиента
        test_client_data = {
            "name": "Максим",
            "phone": "+79161234567",
            "residents_info": "мужчина 28 лет",
            "residents_count": 1,
            "residents_details": "мужчина 28 лет",
            "has_children": False,
            "children_details": None,
            "has_pets": True,
            "pets_details": "кот",
            "rental_period": "от 12 месяцев",
            "move_in_deadline": "до 20 августа"
        }
        
        # Тестовые данные объявления
        test_item_data = {
            "title": "2-комн. квартира, 45 м², 5/9 эт.",
            "location": {
                "title": "Москва",
                "lat": 55.7558,
                "lon": 37.6176
            }
        }
        
        print("📊 Тестовые данные клиента:")
        print(json.dumps(test_client_data, ensure_ascii=False, indent=2))
        
        try:
            success = await send_completed_application(test_client_data, test_item_data)
            
            if success:
                print("✅ Заявка успешно отправлена в Telegram!")
            else:
                print("❌ Ошибка отправки в Telegram")
                
        except Exception as e:
            print(f"❌ Ошибка при отправке в Telegram: {e}")
    
    async def test_full_integration(self):
        """Полный интеграционный тест"""
        print("\n🎯 ПОЛНЫЙ ИНТЕГРАЦИОННЫЙ ТЕСТ")
        print("=" * 60)
        
        # 1. Тест подключения к Avito
        chat_data, messages = await self.test_real_avito_connection()
        
        # 2. Тест ChatGPT
        await self.test_chatgpt_responses(messages)
        
        # 3. Тест follow-up системы
        await self.test_followup_system()
        
        # 4. Тест Telegram
        await self.test_telegram_sending()
        
        print("\n" + "=" * 60)
        print("🎉 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
        
        # Проверка конфигурации
        print(f"\n⚙️ Проверка конфигурации:")
        print(f"  Avito User ID: {AVITO_USER_ID}")
        print(f"  Avito Client ID: {AVITO_CLIENT_ID[:10]}...")
        print(f"  Telegram Bot Token: {'✅ Настроен' if TELEGRAM_BOT_TOKEN != 'ТОКЕН_БОТА' else '❌ Не настроен'}")
        print(f"  Telegram Chat ID: {TELEGRAM_CHAT_ID}")


async def main():
    print("🚀 ЗАПУСК РАСШИРЕННОГО ТЕСТИРОВАНИЯ AVITO RENTAL BOT")
    print("=" * 60)
    
    # Проверяем наличие config.py
    if not os.path.exists('config.py'):
        print("❌ Файл config.py не найден!")
        return
    
    # Проверяем базовые настройки
    if AVITO_USER_ID == 000000000:
        print("⚠️ ВНИМАНИЕ: Не настроен AVITO_USER_ID в config.py")
    
    if TELEGRAM_BOT_TOKEN == "ТОКЕН_БОТА":
        print("⚠️ ВНИМАНИЕ: Не настроен TELEGRAM_BOT_TOKEN в config.py")
    
    bot_tester = TestAvitoBot()
    
    try:
        await bot_tester.test_full_integration()
        
    except KeyboardInterrupt:
        print("\n👋 Тестирование остановлено пользователем")
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())