#!/bin/bash

# Установка зависимостей
echo "📦 Устанавливаю зависимости..."
pip install -r requirements.txt

# Очистка старых файлов (опционально)
# rm -f bot_database.db

# Запуск бота
echo "🚀 Запускаю бота..."
python main.py