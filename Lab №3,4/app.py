# lab №3
from flask import Flask, render_template, request
import datetime
import os

# Создаем экземпляр приложения Flask
app = Flask(__name__)

answers_file = 'answers.txt'


# Главная страница - отображение анкеты
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.form.get('name')
        age = request.form.get('age')
        city = request.form.get('city')
        hobby = request.form.get('hobby')
        reason = request.form.get('reason')

        # Получаем текущую дату и время для записи
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        # Формируем строку для записи в файл
        data_line = f"[{timestamp}] Имя: {name}, Возраст: {age}, Город: {city}, Хобби: {hobby}, Информация о себе: {reason}\n"

        # Записываем данные в файл (режим 'a' - добавление в конец)
        with open(answers_file, 'a', encoding='utf-8') as file:
            file.write(data_line)

        # Отображаем страницу с подтверждением
        return render_template('thankyou.html', name=name)

    # Если GET-запрос - показываем форму анкеты
    return render_template('form.html')


# Дополнительный маршрут для просмотра всех ответов (опционально)
@app.route('/answers')
def show_answers():
    answers = []
    if os.path.exists(answers_file):
        with open(answers_file, 'r', encoding='utf-8') as file:
            answers = file.readlines()
    return render_template('answers.html', answers=answers)


# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=8080)
