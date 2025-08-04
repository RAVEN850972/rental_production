#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрая проверка конфигурации Avito Rental Bot
Проверяет базовую настройку перед запуском основных тестов
"""

import asyncio
import aiohttp
import sys
import os
from datetime import datetime

# Цвета для консоли
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class QuickConfigChecker:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def print_header(self):
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("╔═════════════════════════════════════════════════════════════════╗")
        print("║                  QUICK CONFIG CHECK                             ║")
        print("║               Avito Rental Bot                                  ║")
        print("╚═════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}\n")
        
    def check_pass(self, message):
        self.passed += 1
        print(f"{Colors.GREEN}✓{Colors.END} {message}")
        
    def check_fail(self, message, details=""):
        self.failed += 1
        detail_str = f" - {details}" if details else ""
        print(f"{Colors.RED}✗{Colors.END} {message}{detail_str}")
        
    def check_warning(self, message, details=""):
        self.warnings += 1
        detail_str = f" - {details}" if details else ""
        print(f"{Colors.YELLOW}⚠{Colors.END} {message}{detail_str}")
        
    def check_files(self):
        """Проверка наличия файлов"""
        print(f"{Colors.BLUE}Проверка файлов проекта:{Colors.END}")
        
        required_files = {
            "main.py": "Основной файл бота",
            "config.py": "Конфигурация",
            "avito.py": "Avito API клиент", 
            "chat_gpt.py": "OpenAI интеграция",
            "telegram.py": "Telegram интеграция",
            "deploy.sh": "Скрипт развертывания"
        }
        
        for file, description in required_files.items():
            if os.path.exists(file):
                self.check_pass(f"{description} ({file})")
            else:
                self.check_fail(f"{description} ({file})", "файл отсутствует")
                
    def check_config(self):
        """Проверка конфигурации"""
        print(f"\n{Colors.BLUE}Проверка конфигурации:{Colors.END}")
        
        try:
            from config import (
                OPENAI_API_KEY, OPENAI_MODEL, AVITO_USER_ID,
                AVITO_CLIENT_ID, AVITO_CLIENT_SECRET, TELEGRAM_BOT_TOKEN,
                TELEGRAM_CHAT_ID, CHECK_INTERVAL, TIME_WINDOW_HOURS
            )
            
            # OpenAI
            if OPENAI_API_KEY == "ВАШ_АПИ_КЛЮЧ":
                self.check_fail("OpenAI API ключ", "не настроен")
            elif len(OPENAI_API_KEY) < 20:
                self.check_warning("OpenAI API ключ", "слишком короткий")
            else:
                self.check_pass("OpenAI API ключ настроен")
                
            # Avito
            if AVITO_CLIENT_ID == "КЛИЕНТ_АЙДИ":
                self.check_fail("Avito Client ID", "не настроен")
            else:
                self.check_pass("Avito Client ID настроен")
                
            if AVITO_CLIENT_SECRET == "СИКРЕТ_КЕЙ":
                self.check_fail("Avito Client Secret", "не настроен")
            else:
                self.check_pass("Avito Client Secret настроен")
                
            if AVITO_USER_ID == 0:
                self.check_fail("Avito User ID", "не настроен")
            elif not isinstance(AVITO_USER_ID, int):
                self.check_fail("Avito User ID", "должен быть числом")
            else:
                self.check_pass("Avito User ID настроен")
                
            # Telegram
            if TELEGRAM_BOT_TOKEN == "ТОКЕН_БОТА":
                self.check_fail("Telegram Bot Token", "не настроен")
            else:
                self.check_pass("Telegram Bot Token настроен")
                
            if TELEGRAM_CHAT_ID == "ЧАТ_АЙДИ":
                self.check_fail("Telegram Chat ID", "не настроен")
            else:
                self.check_pass("Telegram Chat ID настроен")
                
            # Параметры работы
            if CHECK_INTERVAL < 5:
                self.check_warning("Интервал проверки", "слишком частый (<5 сек)")
            elif CHECK_INTERVAL > 300:
                self.check_warning("Интервал проверки", "слишком редкий (>5 мин)")
            else:
                self.check_pass(f"Интервал проверки ({CHECK_INTERVAL} сек)")
                
            if TIME_WINDOW_HOURS < 1:
                self.check_warning("Временное окно", "слишком маленькое (<1 час)")
            elif TIME_WINDOW_HOURS > 24:
                self.check_warning("Временное окно", "слишком большое (>24 часа)")
            else:
                self.check_pass(f"Временное окно ({TIME_WINDOW_HOURS} часов)")
                
        except ImportError as e:
            self.check_fail("Импорт конфигурации", str(e))
        except Exception as e:
            self.check_fail("Проверка конфигурации", str(e))
            
    def check_dependencies(self):
        """Проверка зависимостей"""
        print(f"\n{Colors.BLUE}Проверка зависимостей:{Colors.END}")
        
        dependencies = {
            "aiohttp": "HTTP клиент для асинхронных запросов",
            "asyncio": "Асинхронное программирование",
            "json": "Работа с JSON",
            "datetime": "Работа с датами"
        }
        
        for module, description in dependencies.items():
            try:
                __import__(module)
                self.check_pass(f"{description} ({module})")
            except ImportError:
                self.check_fail(f"{description} ({module})", "не установлен")
                
    async def check_api_connectivity(self):
        """Проверка доступности API"""
        print(f"\n{Colors.BLUE}Проверка доступности API:{Colors.END}")
        
        # Список API для проверки
        apis = {
            "https://api.openai.com": "OpenAI API",
            "https://api.avito.ru": "Avito API", 
            "https://api.telegram.org": "Telegram API"
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            for url, name in apis.items():
                try:
                    async with session.get(url) as response:
                        # Любой ответ (даже ошибка авторизации) означает что API доступен
                        self.check_pass(f"{name} доступен")
                except asyncio.TimeoutError:
                    self.check_fail(f"{name}", "таймаут подключения")
                except aiohttp.ClientConnectorError:
                    self.check_fail(f"{name}", "ошибка подключения")
                except Exception as e:
                    self.check_warning(f"{name}", f"неизвестная ошибка: {str(e)[:50]}")
                    
    def check_syntax(self):
        """Проверка синтаксиса Python файлов"""
        print(f"\n{Colors.BLUE}Проверка синтаксиса:{Colors.END}")
        
        python_files = ["main.py", "config.py", "avito.py", "chat_gpt.py", "telegram.py"]
        
        for file in python_files:
            if os.path.exists(file):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        code = f.read()
                    compile(code, file, 'exec')
                    self.check_pass(f"Синтаксис {file}")
                except SyntaxError as e:
                    self.check_fail(f"Синтаксис {file}", f"строка {e.lineno}: {e.msg}")
                except Exception as e:
                    self.check_warning(f"Синтаксис {file}", str(e))
                    
    def check_prompts(self):
        """Проверка промптов"""
        print(f"\n{Colors.BLUE}Проверка промптов:{Colors.END}")
        
        try:
            from config import SYSTEM_PROMPT, EXTRACTION_PROMPT_TEMPLATE
            
            # Проверка системного промпта
            required_keywords = ["Светлана", "агент", "аренде", "7 пунктов"]
            missing_keywords = [kw for kw in required_keywords if kw.lower() not in SYSTEM_PROMPT.lower()]
            
            if not missing_keywords:
                self.check_pass("Системный промпт содержит ключевые элементы")
            else:
                self.check_fail("Системный промпт", f"отсутствуют: {missing_keywords}")
                
            if len(SYSTEM_PROMPT) > 500:
                self.check_pass("Системный промпт достаточно детальный")
            else:
                self.check_warning("Системный промпт", "возможно слишком короткий")
                
            # Проверка промпта извлечения
            if "{dialog_history}" in EXTRACTION_PROMPT_TEMPLATE:
                self.check_pass("Промпт извлечения содержит плейсхолдер")
            else:
                self.check_fail("Промпт извлечения", "отсутствует {dialog_history}")
                
            if "JSON" in EXTRACTION_PROMPT_TEMPLATE:
                self.check_pass("Промпт извлечения требует JSON формат")
            else:
                self.check_warning("Промпт извлечения", "не указан JSON формат")
                
        except ImportError:
            self.check_fail("Проверка промптов", "не удается импортировать config")
        except Exception as e:
            self.check_fail("Проверка промптов", str(e))
            
    def print_summary(self):
        """Вывод итогов"""
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n{Colors.BOLD}═══ ИТОГИ БЫСТРОЙ ПРОВЕРКИ ═══{Colors.END}")
        print(f"{Colors.GREEN}✓ Пройдено: {self.passed}{Colors.END}")
        print(f"{Colors.RED}✗ Ошибки: {self.failed}{Colors.END}")
        print(f"{Colors.YELLOW}⚠ Предупреждения: {self.warnings}{Colors.END}")
        print(f"Всего проверок: {total}")
        
        print(f"\n{Colors.BOLD}Готовность системы: {success_rate:.1f}%{Colors.END}")
        
        if self.failed == 0:
            print(f"{Colors.GREEN}🎉 Базовая конфигурация готова! Можно запускать полное тестирование.{Colors.END}")
            return True
        elif self.failed <= 2 and success_rate >= 80:
            print(f"{Colors.YELLOW}⚠️ Есть незначительные проблемы, но можно продолжать тестирование.{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}❌ Критические проблемы! Исправьте ошибки перед продолжением.{Colors.END}")
            return False
            
    async def run_quick_check(self):
        """Запуск быстрой проверки"""
        self.print_header()
        
        print(f"Быстрая проверка конфигурации...")
        print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Запускаем проверки
        self.check_files()
        self.check_dependencies()
        self.check_config()
        self.check_syntax()
        self.check_prompts()
        await self.check_api_connectivity()
        
        # Выводим итоги
        return self.print_summary()

async def main():
    """Главная функция"""
    checker = QuickConfigChecker()
    
    try:
        success = await checker.run_quick_check()
        
        print(f"\n{Colors.CYAN}Рекомендации:{Colors.END}")
        if success:
            print(f"1. Запустите полное тестирование: python test_system.py")
            print(f"2. После успешных тестов можно развертывать: sudo ./deploy.sh")
        else:
            print(f"1. Исправьте все критические ошибки в config.py")
            print(f"2. Убедитесь что все файлы проекта на месте")
            print(f"3. Проверьте подключение к интернету")
            print(f"4. Повторите быструю проверку")
            
        print(f"\n{Colors.BLUE}Для получения помощи:{Colors.END}")
        print(f"- Проверьте документацию к API сервисов")
        print(f"- Убедитесь что API ключи активны и имеют нужные права")
        print(f"- Проверьте баланс на счетах OpenAI и других сервисов")
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Проверка прервана пользователем{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Критическая ошибка: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    # Запуск быстрой проверки
    asyncio.run(main())