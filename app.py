# app.py

import os
import sqlite3
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# --- Документация ---
# Это главный файл Flask-приложения для платформы RDA.
#
# Модули:
# - os: для работы с переменными окружения.
# - sqlite3: для подключения к базе данных.
# - google.generativeai: для взаимодействия с Gemini API.
# - Flask: основной веб-фреймворк.
# - dotenv: для загрузки переменных окружения из .env файла.
#
# Функции (маршруты):
# - get_db_connection(): Вспомогательная функция для подключения к БД.
# - lessons(): Отображает страницу с видеоуроками.
# - tasks(): Извлекает задания из БД и отображает страницу с практикой.
# - chatbot(): Отображает страницу чат-бота.
# - ask(): API-эндпоинт для чат-бота. Принимает POST-запрос с сообщением
#   пользователя, отправляет его в Gemini и возвращает ответ в формате JSON.
#
# Переменные окружения:
# - GEMINI_API_KEY: Необходимо указать в файле .env для работы чат-бота.
# --- Конец документации ---

# Загружаем переменные окружения из файла .env
load_dotenv()

# Настраиваем API Gemini
# Важно: Убедитесь, что у вас есть файл .env с вашим ключом
api_key = "AIzaSyD90KpxI-_0zxnb86IQ2N3Wy36DWGvoyxM"
if not api_key:
    raise ValueError("Не найден ключ GEMINI_API_KEY. Пожалуйста, добавьте его в файл .env")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

# Создаем экземпляр Flask-приложения
app = Flask(__name__)

# Вспомогательная функция для подключения к базе данных
def get_db_connection():
    # Подключаемся к файлу БД
    conn = sqlite3.connect('rda.db')
    # Устанавливаем row_factory, чтобы получать строки в виде словарей,
    # что позволяет обращаться к колонкам по их именам.
    conn.row_factory = sqlite3.Row
    return conn

# Маршрут для страницы с видеоуроками
@app.route('/')
@app.route('/lessons')
def lessons():
    return render_template('lessons.html', title='Видеоуроки')

# Маршрут для страницы с практическими заданиями
@app.route('/tasks')
def tasks():
    # Устанавливаем соединение с БД
    conn = get_db_connection()
    # Выполняем запрос для получения всех заданий
    tasks_list = conn.execute('SELECT * FROM tasks').fetchall()
    # Закрываем соединение
    conn.close()
    # Передаем список заданий в HTML-шаблон
    return render_template('tasks.html', title='Практические задания', tasks_list=tasks_list)

# Маршрут для страницы чат-бота
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html', title='Чат-бот')

# Маршрут-API для обработки запросов к чат-боту
@app.route('/ask', methods=['POST'])
def ask():
    # Получаем данные из JSON-тела запроса
    user_message = request.json['message']
    
    try:
        # Отправляем запрос модели Gemini
        # Добавляем контекст, чтобы модель отвечала как учитель физики
        prompt = f"Ты — полезный ассистент, эксперт по физике. Ответь на следующий вопрос кратко и понятно для школьника: {user_message}"
        response = model.generate_content(prompt)
        
        # Возвращаем ответ в формате JSON
        return jsonify({'reply': response.text})
    except Exception as e:
        print(f"Ошибка API: {e}")
        return jsonify({'reply': 'Извините, произошла ошибка при обработке вашего запроса.'}), 500

# Запускаем приложение
if __name__ == '__main__':
    # debug=True позволяет автоматически перезагружать сервер при изменениях в коде
    app.run(debug=True)