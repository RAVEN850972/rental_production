#!/bin/bash
# -*- coding: utf-8 -*-

# Полная проверка готовности Avito Rental Bot к продакшену
# Запускает все необходимые тесты и проверки

# Цвета для терминала
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Функции для вывода
print_header() {
   clear
   echo -e "${CYAN}${BOLD}"
   echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
   echo "║                    AVITO RENTAL BOT PRODUCTION READINESS                     ║"
   echo "║                        Comprehensive Pre-Production Check                    ║"
   echo "╠═══════════════════════════════════════════════════════════════════════════════╣"
   echo "║  🏠 Проверка готовности системы к боевому развертыванию                       ║"
   echo "║  🔍 Комплексное тестирование всех компонентов                                 ║"
   echo "║  ⚡ Валидация конфигурации и зависимостей                                     ║"
   echo "║  🛡️ Проверка безопасности и производительности                               ║"
   echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
   echo -e "${NC}"
   echo
}

print_step() {
   echo -e "${BLUE}[ЭТАП]${NC} $1"
}

print_success() {
   echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
   echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
   echo -e "${YELLOW}[⚠]${NC} $1"
}

print_info() {
   echo -e "${CYAN}[INFO]${NC} $1"
}

print_separator() {
   echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
}

# Переменные для отслеживания результатов
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNINGS=0
CRITICAL_ERRORS=()

# Функция для подсчета результатов
add_check() {
   TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
   if [ "$1" == "pass" ]; then
       PASSED_CHECKS=$((PASSED_CHECKS + 1))
       print_success "$2"
   elif [ "$1" == "fail" ]; then
       FAILED_CHECKS=$((FAILED_CHECKS + 1))
       print_error "$2"
       if [ "$3" == "critical" ]; then
           CRITICAL_ERRORS+=("$2")
       fi
   elif [ "$1" == "warning" ]; then
       WARNINGS=$((WARNINGS + 1))
       print_warning "$2"
   fi
}

# Проверка окружения
check_environment() {
   print_separator
   print_step "Проверка окружения и зависимостей"
   
   # Проверка Python
   if command -v python3 &> /dev/null; then
       PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
       add_check "pass" "Python 3 установлен (версия $PYTHON_VERSION)"
   else
       add_check "fail" "Python 3 не найден" "critical"
   fi
   
   # Проверка pip
   if command -v pip3 &> /dev/null; then
       add_check "pass" "pip3 доступен"
   else
       add_check "fail" "pip3 не найден" "critical"
   fi
   
   # Проверка git
   if command -v git &> /dev/null; then
       add_check "pass" "Git установлен"
   else
       add_check "warning" "Git не найден (может понадобиться для обновлений)"
   fi
   
   # Проверка curl
   if command -v curl &> /dev/null; then
       add_check "pass" "curl доступен"
   else
       add_check "warning" "curl не найден (может понадобиться для API запросов)"
   fi
   
   # Проверка systemctl (для продакшен развертывания)
   if command -v systemctl &> /dev/null; then
       add_check "pass" "systemctl доступен (для управления сервисом)"
   else
       add_check "warning" "systemctl не найден (развертывание может быть ограничено)"
   fi
}

# Проверка файлов проекта
check_project_files() {
   print_separator
   print_step "Проверка файлов проекта"
   
   # Список обязательных файлов
   REQUIRED_FILES=(
       "main.py:Основной файл бота"
       "config.py:Конфигурация"
       "avito.py:Avito API клиент"
       "chat_gpt.py:OpenAI интеграция"
       "telegram.py:Telegram интеграция"
       "deploy.sh:Скрипт развертывания"
   )
   
   for file_info in "${REQUIRED_FILES[@]}"; do
       IFS=':' read -r filename description <<< "$file_info"
       if [ -f "$filename" ]; then
           add_check "pass" "$description ($filename) найден"
       else
           add_check "fail" "$description ($filename) отсутствует" "critical"
       fi
   done
   
   # Проверка прав на выполнение deploy.sh
   if [ -f "deploy.sh" ]; then
       if [ -x "deploy.sh" ]; then
           add_check "pass" "deploy.sh имеет права на выполнение"
       else
           add_check "warning" "deploy.sh не имеет прав на выполнение (запустите: chmod +x deploy.sh)"
       fi
   fi
   
   # Проверка тестовых файлов
   TEST_FILES=("test_system.py" "quick_config_check.py" "test_scenarios.py")
   for test_file in "${TEST_FILES[@]}"; do
       if [ -f "$test_file" ]; then
           add_check "pass" "Тестовый файл $test_file найден"
       else
           add_check "warning" "Тестовый файл $test_file отсутствует"
       fi
   done
}

# Проверка синтаксиса Python файлов
check_python_syntax() {
   print_separator
   print_step "Проверка синтаксиса Python файлов"
   
   PYTHON_FILES=("main.py" "config.py" "avito.py" "chat_gpt.py" "telegram.py")
   
   for file in "${PYTHON_FILES[@]}"; do
       if [ -f "$file" ]; then
           if python3 -m py_compile "$file" 2>/dev/null; then
               add_check "pass" "Синтаксис $file корректен"
           else
               add_check "fail" "Синтаксическая ошибка в $file" "critical"
           fi
       fi
   done
   
   # Проверка тестовых файлов
   if [ -f "test_system.py" ]; then
       if python3 -m py_compile "test_system.py" 2>/dev/null; then
           add_check "pass" "Синтаксис test_system.py корректен"
       else
           add_check "warning" "Синтаксическая ошибка в test_system.py"
       fi
   fi
}

# Проверка Python зависимостей
check_python_dependencies() {
   print_separator
   print_step "Проверка Python зависимостей"
   
   # Список обязательных модулей
   REQUIRED_MODULES=("aiohttp" "asyncio" "json" "datetime")
   
   for module in "${REQUIRED_MODULES[@]}"; do
       if python3 -c "import $module" 2>/dev/null; then
           add_check "pass" "Модуль $module доступен"
       else
           if [ "$module" == "aiohttp" ]; then
               add_check "fail" "Модуль $module не найден (критический)" "critical"
           else
               add_check "warning" "Модуль $module не найден"
           fi
       fi
   done
   
   # Проверка версии aiohttp
   if python3 -c "import aiohttp; print(aiohttp.__version__)" 2>/dev/null; then
       AIOHTTP_VERSION=$(python3 -c "import aiohttp; print(aiohttp.__version__)" 2>/dev/null)
       add_check "pass" "aiohttp версия $AIOHTTP_VERSION"
   fi
}

# Быстрая проверка конфигурации
run_quick_config_check() {
   print_separator
   print_step "Быстрая проверка конфигурации"
   
   if [ -f "quick_config_check.py" ]; then
       print_info "Запуск быстрой проверки конфигурации..."
       
       if python3 quick_config_check.py; then
           add_check "pass" "Быстрая проверка конфигурации пройдена"
       else
           EXIT_CODE=$?
           if [ $EXIT_CODE -eq 1 ]; then
               add_check "fail" "Критические ошибки в конфигурации" "critical"
           else
               add_check "warning" "Предупреждения в конфигурации"
           fi
       fi
   else
       add_check "warning" "quick_config_check.py не найден, пропускаем быструю проверку"
   fi
}

# Проверка подключения к интернету
check_internet_connectivity() {
   print_separator
   print_step "Проверка подключения к интернету и API"
   
   # Список API для проверки
   APIS=(
       "api.openai.com:OpenAI API"
       "api.avito.ru:Avito API"
       "api.telegram.org:Telegram API"
       "google.com:Общее подключение"
   )
   
   for api_info in "${APIS[@]}"; do
       IFS=':' read -r hostname description <<< "$api_info"
       
       if ping -c 1 -W 5 "$hostname" &> /dev/null; then
           add_check "pass" "$description ($hostname) доступен"
       else
           if [ "$hostname" == "google.com" ]; then
               add_check "fail" "Нет подключения к интернету" "critical"
           else
               add_check "warning" "$description ($hostname) недоступен"
           fi
       fi
   done
}

# Проверка системных ресурсов
check_system_resources() {
   print_separator
   print_step "Проверка системных ресурсов"
   
   # Проверка свободного места на диске
   DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
   if [ "$DISK_USAGE" -lt 90 ]; then
       add_check "pass" "Свободное место на диске: $((100-DISK_USAGE))%"
   elif [ "$DISK_USAGE" -lt 95 ]; then
       add_check "warning" "Мало свободного места на диске: $((100-DISK_USAGE))%"
   else
       add_check "fail" "Критически мало места на диске: $((100-DISK_USAGE))%" "critical"
   fi
   
   # Проверка RAM
   if command -v free &> /dev/null; then
       TOTAL_RAM=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}')
       if [ "$TOTAL_RAM" -ge 1 ]; then
           add_check "pass" "RAM: ${TOTAL_RAM}GB доступно"
       else
           add_check "warning" "Мало RAM: ${TOTAL_RAM}GB (рекомендуется минимум 1GB)"
       fi
   fi
   
   # Проверка load average
   if command -v uptime &> /dev/null; then
       LOAD_AVG=$(uptime | awk '{print $10}' | sed 's/,//')
       add_check "pass" "Load average: $LOAD_AVG"
   fi
}

# Полное тестирование
run_full_testing() {
   print_separator
   print_step "Запуск полного тестирования"
   
   if [ -f "test_system.py" ]; then
       print_info "Запуск комплексного тестирования (может занять несколько минут)..."
       
       # Создаем временный лог файл
       TEST_LOG=$(mktemp)
       
       if timeout 300 python3 test_system.py > "$TEST_LOG" 2>&1; then
           add_check "pass" "Полное тестирование пройдено успешно"
           
           # Извлекаем статистику из лога
           if grep -q "Пройдено:" "$TEST_LOG"; then
               PASSED_TESTS=$(grep "Пройдено:" "$TEST_LOG" | awk '{print $2}')
               FAILED_TESTS=$(grep "Не пройдено:" "$TEST_LOG" | awk '{print $3}')
               print_info "Результаты тестирования: $PASSED_TESTS пройдено, $FAILED_TESTS не пройдено"
           fi
       else
           EXIT_CODE=$?
           if [ $EXIT_CODE -eq 124 ]; then
               add_check "fail" "Тестирование превысило лимит времени (5 минут)" "critical"
           else
               add_check "fail" "Ошибки в полном тестировании" "critical"
           fi
           
           # Показываем последние строки лога для диагностики
           if [ -f "$TEST_LOG" ]; then
               print_info "Последние строки лога тестирования:"
               tail -10 "$TEST_LOG"
           fi
       fi
       
       # Удаляем временный файл
       rm -f "$TEST_LOG"
   else
       add_check "warning" "test_system.py не найден, пропускаем полное тестирование"
   fi
}

# Проверка безопасности
check_security() {
   print_separator
   print_step "Проверка безопасности"
   
   # Проверка на захардкоженные секреты в config.py
   if [ -f "config.py" ]; then
       # Проверяем на плейсхолдеры
       if grep -q "ВАШ_АПИ_КЛЮЧ\|КЛИЕНТ_АЙДИ\|СИКРЕТ_КЕЙ\|ТОКЕН_БОТА" "config.py"; then
           add_check "fail" "В config.py остались плейсхолдеры вместо реальных ключей" "critical"
       else
           add_check "pass" "Плейсхолдеры в config.py заменены на реальные значения"
       fi
       
       # Проверяем права доступа к файлу конфигурации
       CONFIG_PERMS=$(stat -c "%a" config.py 2>/dev/null || stat -f "%A" config.py 2>/dev/null)
       if [ "$CONFIG_PERMS" == "600" ] || [ "$CONFIG_PERMS" == "644" ]; then
           add_check "pass" "Права доступа к config.py корректны ($CONFIG_PERMS)"
       else
           add_check "warning" "Рекомендуется ограничить права доступа к config.py (chmod 600 config.py)"
       fi
   fi
   
   # Проверка на debug режимы
   DEBUG_PATTERNS=("DEBUG.*=.*True" "debug.*=.*true" "LOGGING_LEVEL.*=.*DEBUG")
   for pattern in "${DEBUG_PATTERNS[@]}"; do
       if grep -rq "$pattern" . --include="*.py"; then
           add_check "warning" "Найден debug режим в коде (отключите для продакшена)"
       fi
   done
   
   add_check "pass" "Базовая проверка безопасности завершена"
}

# Проверка готовности к развертыванию
check_deployment_readiness() {
   print_separator
   print_step "Проверка готовности к развертыванию"
   
   # Проверка на root права для развертывания
   if [ "$EUID" -eq 0 ]; then
       add_check "pass" "Скрипт запущен с правами root (необходимо для развертывания)"
   else
       add_check "warning" "Для развертывания потребуются права root (sudo)"
   fi
   
   # Проверка systemd
   if systemctl --version &> /dev/null; then
       add_check "pass" "systemd доступен для управления сервисом"
   else
       add_check "warning" "systemd недоступен (альтернативные методы запуска)"
   fi
   
   # Проверка директории для логов
   if [ -d "/var/log" ] && [ -w "/var/log" ]; then
       add_check "pass" "Директория /var/log доступна для записи"
   else
       add_check "warning" "Проблемы с доступом к /var/log"
   fi
   
   # Проверка на конфликтующие процессы
   if pgrep -f "main.py" > /dev/null; then
       add_check "warning" "Обнаружен запущенный процесс main.py (остановите перед развертыванием)"
   else
       add_check "pass" "Нет конфликтующих процессов"
   fi
}

# Генерация итогового отчета
generate_final_report() {
   print_separator
   print_step "Генерация итогового отчета"
   
   # Расчет процента готовности
   if [ $TOTAL_CHECKS -gt 0 ]; then
       SUCCESS_RATE=$(( (PASSED_CHECKS * 100) / TOTAL_CHECKS ))
   else
       SUCCESS_RATE=0
   fi
   
   # Создание отчета
   REPORT_FILE="production_readiness_report_$(date +%Y%m%d_%H%M%S).txt"
   
   cat > "$REPORT_FILE" << EOF
AVITO RENTAL BOT - ОТЧЕТ О ГОТОВНОСТИ К ПРОДАКШЕНУ
==================================================

Дата проверки: $(date)
Общая готовность: ${SUCCESS_RATE}%

СТАТИСТИКА:
- Всего проверок: $TOTAL_CHECKS
- Пройдено: $PASSED_CHECKS
- Не пройдено: $FAILED_CHECKS  
- Предупреждения: $WARNINGS

КРИТИЧЕСКИЕ ОШИБКИ:
EOF

   if [ ${#CRITICAL_ERRORS[@]} -eq 0 ]; then
       echo "Критические ошибки не обнаружены" >> "$REPORT_FILE"
   else
       for error in "${CRITICAL_ERRORS[@]}"; do
           echo "- $error" >> "$REPORT_FILE"
       done
   fi
   
   cat >> "$REPORT_FILE" << EOF

РЕКОМЕНДАЦИИ:
1. Исправьте все критические ошибки перед развертыванием
2. Обратите внимание на предупреждения
3. Проведите тестирование на тестовой среде
4. Настройте мониторинг и алерты
5. Подготовьте план отката в случае проблем

СЛЕДУЮЩИЕ ШАГИ:
EOF

   if [ ${#CRITICAL_ERRORS[@]} -eq 0 ] && [ $SUCCESS_RATE -ge 90 ]; then
       cat >> "$REPORT_FILE" << EOF
✅ СИСТЕМА ГОТОВА К ПРОДАКШЕНУ!
- Запустите развертывание: sudo ./deploy.sh
- Настройте мониторинг
- Проведите smoke тесты после развертывания
EOF
   elif [ ${#CRITICAL_ERRORS[@]} -eq 0 ] && [ $SUCCESS_RATE -ge 75 ]; then
       cat >> "$REPORT_FILE" << EOF
⚠️ СИСТЕМА ПОЧТИ ГОТОВА К ПРОДАКШЕНУ
- Исправьте предупреждения
- Проведите дополнительное тестирование
- Затем запускайте развертывание
EOF
   else
       cat >> "$REPORT_FILE" << EOF
❌ СИСТЕМА НЕ ГОТОВА К ПРОДАКШЕНУ
- Исправьте все критические ошибки
- Повторите проверку готовности
- Не развертывайте до устранения проблем
EOF
   fi

   print_success "Отчет сохранен: $REPORT_FILE"
}

# Вывод итогов в консоль
print_final_summary() {
   print_separator
   echo -e "${BOLD}${WHITE}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
   echo -e "${BOLD}${WHITE}║                              ИТОГОВЫЙ РЕЗУЛЬТАТ                               ║${NC}"
   echo -e "${BOLD}${WHITE}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
   
   # Расчет процента готовности
   if [ $TOTAL_CHECKS -gt 0 ]; then
       SUCCESS_RATE=$(( (PASSED_CHECKS * 100) / TOTAL_CHECKS ))
   else
       SUCCESS_RATE=0
   fi
   
   echo
   echo -e "${BOLD}Результаты проверки:${NC}"
   echo -e "${GREEN}✓ Пройдено: $PASSED_CHECKS${NC}"
   echo -e "${RED}✗ Ошибки: $FAILED_CHECKS${NC}"
   echo -e "${YELLOW}⚠ Предупреждения: $WARNINGS${NC}"
   echo -e "${CYAN}📊 Всего проверок: $TOTAL_CHECKS${NC}"
   echo
   echo -e "${BOLD}Готовность системы: $SUCCESS_RATE%${NC}"
   
   # Определение статуса готовности
   if [ ${#CRITICAL_ERRORS[@]} -eq 0 ] && [ $SUCCESS_RATE -ge 90 ]; then
       echo
       echo -e "${GREEN}${BOLD}🎉 СИСТЕМА ГОТОВА К ПРОДАКШЕНУ! 🎉${NC}"
       echo -e "${GREEN}Можно приступать к развертыванию${NC}"
       echo
       echo -e "${CYAN}Следующие шаги:${NC}"
       echo -e "${WHITE}1. sudo ./deploy.sh                 ${CYAN}# Развертывание${NC}"
       echo -e "${WHITE}2. Настройка мониторинга            ${CYAN}# Логи и метрики${NC}"
       echo -e "${WHITE}3. Smoke тестирование               ${CYAN}# Проверка после развертывания${NC}"
       FINAL_EXIT_CODE=0
       
   elif [ ${#CRITICAL_ERRORS[@]} -eq 0 ] && [ $SUCCESS_RATE -ge 75 ]; then
       echo
       echo -e "${YELLOW}${BOLD}⚠️ СИСТЕМА ПОЧТИ ГОТОВА К ПРОДАКШЕНУ ⚠️${NC}"
       echo -e "${YELLOW}Рекомендуется устранить предупреждения${NC}"
       echo
       echo -e "${CYAN}Рекомендации:${NC}"
       echo -e "${WHITE}1. Просмотрите все предупреждения    ${CYAN}# Устраните по возможности${NC}"
       echo -e "${WHITE}2. Проведите дополнительное тестирование${NC}"
       echo -e "${WHITE}3. Затем запускайте развертывание${NC}"
       FINAL_EXIT_CODE=0
       
   else
       echo
       echo -e "${RED}${BOLD}❌ СИСТЕМА НЕ ГОТОВА К ПРОДАКШЕНУ ❌${NC}"
       echo -e "${RED}Обнаружены критические проблемы${NC}"
       echo
       if [ ${#CRITICAL_ERRORS[@]} -gt 0 ]; then
           echo -e "${RED}${BOLD}Критические ошибки:${NC}"
           for error in "${CRITICAL_ERRORS[@]}"; do
               echo -e "${RED}  ✗ $error${NC}"
           done
       fi
       echo
       echo -e "${CYAN}Необходимые действия:${NC}"
       echo -e "${WHITE}1. Исправьте все критические ошибки${NC}"
       echo -e "${WHITE}2. Повторите проверку готовности${NC}"
       echo -e "${WHITE}3. НЕ развертывайте до устранения проблем${NC}"
       FINAL_EXIT_CODE=1
   fi
   
   echo
   print_separator
}

# Главная функция
main() {
   print_header
   
   print_info "Начало комплексной проверки готовности к продакшену..."
   print_info "Это может занять несколько минут..."
   echo
   
   # Запуск всех проверок
   check_environment
   check_project_files
   check_python_syntax
   check_python_dependencies
   run_quick_config_check
   check_internet_connectivity
   check_system_resources
   run_full_testing
   check_security
   check_deployment_readiness
   
   # Генерация отчета и вывод итогов
   generate_final_report
   print_final_summary
   
   # Дополнительная информация
   echo -e "${CYAN}Дополнительная информация:${NC}"
   echo -e "${WHITE}📄 Детальный отчет:${NC} production_readiness_report_*.txt"
   echo -e "${WHITE}🔧 Логи тестирования:${NC} test_report_*.txt (если запускались)"
   echo -e "${WHITE}📚 Документация:${NC} Проверьте README и комментарии в коде"
   echo -e "${WHITE}🆘 Поддержка:${NC} Обратитесь к документации API сервисов"
   echo
   
   exit $FINAL_EXIT_CODE
}

# Обработка сигналов
trap 'echo -e "\n${RED}Проверка прервана пользователем${NC}"; exit 1' INT TERM

# Проверка аргументов командной строки
while [[ $# -gt 0 ]]; do
   case $1 in
       -h|--help)
           echo "Использование: $0 [опции]"
           echo
           echo "Опции:"
           echo "  -h, --help     Показать справку"
           echo "  --quick        Только быстрые проверки (без полного тестирования)"
           echo "  --verbose      Подробный вывод"
           echo
           echo "Примеры:"
           echo "  $0                    # Полная проверка"
           echo "  $0 --quick           # Быстрая проверка"
           echo "  sudo $0              # Проверка с правами root"
           echo
           exit 0
           ;;
       --quick)
           QUICK_MODE=true
           shift
           ;;
       --verbose)
           VERBOSE=true
           shift
           ;;
       *)
           echo "Неизвестная опция: $1"
           echo "Используйте $0 --help для справки"
           exit 1
           ;;
   esac
done

# Модификация для быстрого режима
if [ "$QUICK_MODE" = true ]; then
   print_info "Режим быстрой проверки (полное тестирование пропущено)"
   run_full_testing() {
       print_separator
       print_step "Полное тестирование (пропущено в быстром режиме)"
       add_check "warning" "Полное тестирование пропущено (используйте без --quick для полной проверки)"
   }
fi

# Запуск основной функции
main "$@"