from flask import Flask, render_template, request, redirect
import json
import os
from datetime import date

app = Flask(__name__)

TASKS_FILE = 'tasks.json'


def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_tasks(tasks):
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


tasks = load_tasks()


@app.route('/')
def index():
    return render_template('index.html', tasks=tasks, filter='all')


# ── Активные задачи ───────────────────────────────────────────────────────────
@app.route('/active')
def active_tasks():
    active = [t for t in tasks if not t.get('done', False)]
    return render_template('index.html', tasks=active, filter='active')


# ── Выполненные задачи ────────────────────────────────────────────────────────
@app.route('/completed')
def completed_tasks():
    completed = [t for t in tasks if t.get('done', False)]
    return render_template('index.html', tasks=completed, filter='completed')


# ── Добавление задачи ─────────────────────────────────────────────────────────
@app.route('/add', methods=['POST'])
def add_task():
    new_task = request.form.get('task', '').strip()
    if new_task:
        today = date.today().strftime('%Y-%m-%d')
        tasks.append({'text': new_task, 'date': today, 'done': False})
        save_tasks(tasks)
    return redirect('/')


# ── Удаление задачи ───────────────────────────────────────────────────────────
@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        save_tasks(tasks)
    return redirect('/')


# ── Редактирование задачи ─────────────────────────────────────────────────────
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if task_id < 0 or task_id >= len(tasks):
        return "Задача не найдена", 404

    if request.method == 'POST':
        new_text = request.form.get('task', '').strip()

        # Проверка на пустое поле
        if new_text == '':
            return render_template('edit.html', task=tasks[task_id],
                                   message="Текст не может быть пустым!")

        # Проверка: текст не изменился
        old_text = tasks[task_id]['text']
        if new_text == old_text:
            return render_template('edit.html', task=tasks[task_id],
                                   message="Ничего не изменено")

        tasks[task_id]['text'] = new_text
        save_tasks(tasks)
        return redirect('/')

    else:
        return render_template('edit.html', task=tasks[task_id])


# ── Переключение статуса выполнения ──────────────────────────────────────────
@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    # Проверка: существует ли задача с таким номером (индексом)
    if 0 <= task_id < len(tasks):
        # Переключаем значение: было False → станет True, и наоборот
        tasks[task_id]['done'] = not tasks[task_id].get('done', False)
        save_tasks(tasks)
    return redirect('/')


# ── Выполнить все задачи ──────────────────────────────────────────────────────
@app.route('/complete_all')
def complete_all():
    for task in tasks:
        task['done'] = True
    save_tasks(tasks)
    return redirect('/')


# ── Снять отметку со всех задач ───────────────────────────────────────────────
@app.route('/reset_all')
def reset_all():
    for task in tasks:
        task['done'] = False
    save_tasks(tasks)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
