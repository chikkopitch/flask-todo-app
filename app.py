from flask import Flask, render_template, request, redirect
import json
import os
from datetime import date

app = Flask(__name__)

TASKS_FILE = 'tasks.json'
PRIORITY_CHOICES = ['High', 'Medium', 'Low']
PRIORITY_ORDER = {'High': 3, 'Medium': 2, 'Low': 1}


def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_tasks(tasks):
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def normalize_task(task):
    if 'priority' not in task or task.get('priority') not in PRIORITY_ORDER:
        task['priority'] = 'Medium'
    if 'done' not in task:
        task['done'] = False
    return task


def prepare_tasks(filtered):
    return [{'id': idx, 'task': task} for idx, task in enumerate(filtered)]


def sort_by_priority(task_list):
    return sorted(task_list, key=lambda t: PRIORITY_ORDER.get(t.get('priority', 'Medium'), 2), reverse=True)


tasks = load_tasks()
for task in tasks:
    normalize_task(task)
save_tasks(tasks)


@app.route('/')
def index():
    return render_template(
        'index.html',
        tasks=prepare_tasks(tasks),
        filter='all',
        sort='none',
        remaining=sum(1 for task in tasks if not task.get('done', False)),
        priorities=PRIORITY_CHOICES,
    )


# ── Активные задачи ───────────────────────────────────────────────────────────
@app.route('/active')
def active_tasks():
    visible = [task for task in tasks if not task.get('done', False)]
    return render_template(
        'index.html',
        tasks=prepare_tasks(visible),
        filter='active',
        sort='none',
        remaining=len(visible),
        priorities=PRIORITY_CHOICES,
    )


# ── Выполненные задачи ────────────────────────────────────────────────────────
@app.route('/completed')
def completed_tasks():
    visible = [task for task in tasks if task.get('done', False)]
    return render_template(
        'index.html',
        tasks=prepare_tasks(visible),
        filter='completed',
        sort='none',
        remaining=len(visible),
        priorities=PRIORITY_CHOICES,
    )


# ── Сортировка по приоритету ────────────────────────────────────────────────────
@app.route('/priority')
def priority_tasks():
    visible = sort_by_priority(tasks)
    return render_template(
        'index.html',
        tasks=prepare_tasks(visible),
        filter='priority',
        sort='priority',
        remaining=sum(1 for task in visible if not task.get('done', False)),
        priorities=PRIORITY_CHOICES,
    )


# ── Добавление задачи ─────────────────────────────────────────────────────────
@app.route('/add', methods=['POST'])
def add_task():
    new_task = request.form.get('task', '').strip()
    priority = request.form.get('priority', 'Medium')
    if priority not in PRIORITY_ORDER:
        priority = 'Medium'

    if new_task:
        today = date.today().strftime('%Y-%m-%d')
        tasks.append({'text': new_task, 'date': today, 'done': False, 'priority': priority})
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
        return 'Задача не найдена', 404

    if request.method == 'POST':
        new_text = request.form.get('task', '').strip()
        new_priority = request.form.get('priority', 'Medium')
        if new_priority not in PRIORITY_ORDER:
            new_priority = 'Medium'

        if new_text == '':
            return render_template('edit.html', task=tasks[task_id], message='Текст не может быть пустым!', priorities=PRIORITY_CHOICES)

        old_text = tasks[task_id].get('text', '')
        old_priority = tasks[task_id].get('priority', 'Medium')
        if new_text == old_text and new_priority == old_priority:
            return render_template('edit.html', task=tasks[task_id], message='Ничего не изменено', priorities=PRIORITY_CHOICES)

        tasks[task_id]['text'] = new_text
        tasks[task_id]['priority'] = new_priority
        save_tasks(tasks)
        return redirect('/')

    return render_template('edit.html', task=tasks[task_id], priorities=PRIORITY_CHOICES)


# ── Переключение статуса выполнения ──────────────────────────────────────────
@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    if 0 <= task_id < len(tasks):
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
