from flask import Flask, render_template, request, redirect
import json
import os
from datetime import datetime

app = Flask(__name__)
FILE_NAME = 'tasks.json'


# Функция для загрузки задач из файла
def load_tasks():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


# Функция для сохранения задач в файл
def save_tasks(tasks):
    with open(FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


tasks = load_tasks()


@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)


@app.route('/add', methods=['POST'])
def add_task():
    new_task_text = request.form.get('task')
    if new_task_text:
        # Получаем текущую дату и время
        current_date = datetime.now().strftime("%d.%m.%Y %H:%M")

        # Теперь задача — это словарь с текстом и датой
        new_task = {
            'text': new_task_text,
            'date': current_date
        }
        tasks.append(new_task)
        save_tasks(tasks)
    return redirect('/')


@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        save_tasks(tasks)
    return redirect('/')


# Новый маршрут для очистки всех задач (Задание 1)
@app.route('/clear')
def clear_tasks():
    tasks.clear()  # Очищаем список
    save_tasks(tasks)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)