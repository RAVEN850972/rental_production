import asyncio
import aiohttp
import json
from config import EXTRACTION_PROMPT_TEMPLATE

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

async def get_address_from_coords(session, lat, lon):
    """Получение адреса по координатам через Nominatim API"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        headers = {"User-Agent": "AvitoBot/1.0"}
        
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                address_parts = data.get("address", {})
                
                # Формируем адрес из компонентов
                address_components = []
                for key in ["road", "house_number", "suburb", "city", "town", "village"]:
                    if address_parts.get(key):
                        address_components.append(address_parts[key])
                
                return ", ".join(address_components) if address_components else data.get("display_name", "Адрес не найден")
    except Exception as e:
        return f"Ошибка получения адреса: {e}"
    return "Адрес не найден"

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
    
    async def send_message(self, chat_id, text, parse_mode="Markdown"):
        """Отправка сообщения в телеграм"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return True
                else:
                    error_text = await response.text()
                    print(f"Telegram API error: {response.status} — {error_text}")
                    return False
    
    async def send_client_info(self, client_data, chat_id, item_data=None):
        """Отправка информации о клиенте в телеграм"""
        try:
            # Парсим JSON данные о клиенте
            if isinstance(client_data, str):
                data = json.loads(client_data)
            else:
                data = client_data
            
            # Формируем красивое сообщение
            message = "🏠 НОВАЯ ЗАЯВКА НА АРЕНДУ\n\n"
            
            # Информация об объявлении
            if item_data:
                item_title = item_data.get("title", "Без названия")
                message += f"📋 Объявление: {item_title}\n"
                
                # Получаем адрес из координат
                location_data = item_data.get("location", {})
                if location_data:
                    city = location_data.get("title", "Не указан")
                    lat = location_data.get("lat")
                    lon = location_data.get("lon")
                    
                    if lat and lon:
                        async with aiohttp.ClientSession() as session:
                            address = await get_address_from_coords(session, lat, lon)
                            message += f"📍 Адрес: {address}\n"
                    else:
                        message += f"📍 Город: {city}\n"
                else:
                    message += f"📍 Местоположение не указано\n"
                
                message += "\n"
            
            # Основная информация о клиенте
            if data.get('name'):
                message += f"👤 Имя: {data['name']}\n"
            
            if data.get('phone'):
                message += f"📞 Телефон: {data['phone']}\n"
            
            # Информация о жильцах
            if data.get('residents_info'):
                message += f"👥 Жильцы: {data['residents_info']}\n"
            
            if data.get('residents_count'):
                message += f"🔢 Количество взрослых: {data['residents_count']}\n"
            
            # Дети
            if data.get('has_children'):
                children_info = data.get('children_details', 'Есть дети')
                message += f"👶 Дети: {children_info}\n"
            else:
                message += f"👶 Дети: Нет\n"
            
            # Животные
            if data.get('has_pets'):
                pets_info = data.get('pets_details', 'Есть животные')
                message += f"🐾 Животные: {pets_info}\n"
            else:
                message += f"🐾 Животные: Нет\n"
            
            # Срок аренды и дата заезда
            if data.get('rental_period'):
                message += f"📅 Срок аренды: {data['rental_period']}\n"
            
            if data.get('move_in_deadline'):
                message += f"🗓️ Дата заезда: {data['move_in_deadline']}\n"
            
            message += f"\n✅ Статус: Готов к презентации собственнице"
            
            # Отправляем сообщение
            success = await self.send_message(chat_id, message)
            if success:
                print("Заявка отправлена в Telegram")
            else:
                print("Ошибка отправки заявки в Telegram")
            
            return success
            
        except Exception as e:
            print(f"Ошибка при отправке заявки: {e}")
            return False

# Глобальный экземпляр телеграм бота
telegram_bot = TelegramBot(TELEGRAM_BOT_TOKEN)

async def send_completed_application(client_data, item_data=None):
    """Отправка завершенной заявки в телеграм"""
    return await telegram_bot.send_client_info(client_data, TELEGRAM_CHAT_ID, item_data)