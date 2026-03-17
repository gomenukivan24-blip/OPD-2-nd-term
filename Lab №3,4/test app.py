# lab №4
import unittest
import os
import tempfile
from unittest.mock import patch
from app import app


class TestAnketApp(unittest.TestCase):

    def setUp(self):
        """Подготовка к тестированию"""
        self.app = app.test_client()
        self.app.testing = True

        # Создаем временный файл
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.txt')
        self.temp_filename = self.temp_file.name
        self.temp_file.close()

        # Патчим переменную answers_file в app.py
        self.patcher = patch('app.answers_file', self.temp_filename)
        self.patcher.start()

    def tearDown(self):
        """Очистка после тестов"""
        self.patcher.stop()
        if os.path.exists(self.temp_filename):
            os.unlink(self.temp_filename)

    def assertInResponse(self, text, response):
        """Проверяет наличие русского текста в ответе"""
        self.assertIn(text.encode('utf-8'), response.data)

    # --- ТЕСТЫ ДЛЯ GET-ЗАПРОСОВ ---

    def test_get_main_page(self):
        """Тест: GET запрос к главной странице возвращает форму"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertInResponse('Анкета', response)
        self.assertIn(b'<form', response.data)

    def test_get_answers_page_empty(self):
        """Тест: GET запрос к странице ответов (пустой файл)"""
        # Убеждаемся, что временный файл пустой
        if os.path.exists(self.temp_filename):
            os.unlink(self.temp_filename)

        response = self.app.get('/answers')
        self.assertEqual(response.status_code, 200)
        self.assertInResponse('нет ни одного ответа', response)

    # --- ТЕСТЫ ДЛЯ POST-ЗАПРОСОВ ---

    def test_post_valid_form_data(self):
        """Тест: отправка валидных данных формы"""
        test_data = {
            'name': 'Тестовый Пользователь',
            'age': '25',
            'city': 'Тестовый Город',
            'hobby': 'Тестирование',
            'reason': 'Проверка работы приложения'
        }

        response = self.app.post('/', data=test_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertInResponse('Спасибо, Тестовый Пользователь!', response)

        # Проверяем, что данные записались в файл
        with open(self.temp_filename, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('Тестовый Пользователь', content)
            self.assertIn('25', content)

    def test_post_valid_form_data_redirect(self):
        """Тест: проверка редиректа после успешной отправки"""
        test_data = {
            'name': 'Тестовый Пользователь',
            'age': '25',
            'city': 'Тестовый Город',
            'hobby': 'Тестирование',
            'reason': 'Проверка работы приложения'
        }

        response = self.app.post('/', data=test_data)
        # POST запрос должен редиректить (302) или показывать страницу (200)
        self.assertIn(response.status_code, [200, 302])

    def test_file_write_on_post(self):
        """Тест: проверка записи в файл при POST запросе"""
        test_data = {
            'name': 'Иван Петров',
            'age': '30',
            'city': 'Москва',
            'hobby': 'Программирование',
            'reason': 'Интересно'
        }

        self.app.post('/', data=test_data)

        # Проверяем, что файл создан и содержит данные
        self.assertTrue(os.path.exists(self.temp_filename))

        with open(self.temp_filename, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('Иван Петров', content)
            self.assertIn('30', content)
            self.assertIn('Москва', content)

    def test_multiple_submissions(self):
        """Тест: несколько отправок формы"""
        submissions = [
            {'name': 'User1', 'age': '20', 'city': 'City1', 'hobby': 'Hobby1', 'reason': 'Reason1'},
            {'name': 'User2', 'age': '30', 'city': 'City2', 'hobby': 'Hobby2', 'reason': 'Reason2'},
            {'name': 'User3', 'age': '40', 'city': 'City3', 'hobby': 'Hobby3', 'reason': 'Reason3'}
        ]

        for data in submissions:
            self.app.post('/', data=data)

        # Проверяем, что все записи сохранены
        with open(self.temp_filename, 'r', encoding='utf-8') as f:
            content = f.read()
            for user in submissions:
                self.assertIn(user['name'], content)
                self.assertIn(user['age'], content)

    # --- ТЕСТЫ ДЛЯ СТРАНИЦЫ /answers ---

    def test_answers_page_with_data(self):
        """Тест: страница ответов с данными"""
        with open(self.temp_filename, 'w', encoding='utf-8') as f:
            f.write(
                "[2024-01-15 10:00:00] Имя: Test, Возраст: 25, Город: TestCity, Хобби: TestHobby, Информация о себе: TestReason\n")

        response = self.app.get('/answers')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test', response.data)
        self.assertIn(b'TestCity', response.data)

    # --- ТЕСТЫ ДЛЯ ПРОВЕРКИ ФОРМАТА ДАННЫХ ---

    def test_data_format(self):
        """Тест: проверка формата сохраняемых данных"""
        test_data = {
            'name': 'Анна Иванова',
            'age': '22',
            'city': 'Казань',
            'hobby': 'Музыка',
            'reason': 'Учеба'
        }

        self.app.post('/', data=test_data)

        with open(self.temp_filename, 'r', encoding='utf-8') as f:
            line = f.readline().strip()
            # Проверяем формат строки (наличие временной метки)
            import re
            self.assertRegex(line, r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]')
            self.assertIn('Имя: Анна Иванова', line)
            self.assertIn('Возраст: 22', line)

    def test_special_characters(self):
        """Тест: отправка данных со специальными символами"""
        test_data = {
            'name': 'Иван "Кавычки" Петров',
            'age': '35',
            'city': 'Город, с запятой',
            'hobby': 'Программирование & Тестирование',
            'reason': 'Символы: @#$%^&*()'
        }

        self.app.post('/', data=test_data)

        with open(self.temp_filename, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('Иван "Кавычки" Петров', content)
            self.assertIn('Город, с запятой', content)
            self.assertIn('Программирование & Тестирование', content)

    def test_boundary_values(self):
        """Тест: граничные значения возраста"""
        # Минимальный возраст (1)
        data_min = {
            'name': 'Min Age',
            'age': '1',
            'city': 'Test',
            'hobby': 'Test',
            'reason': 'Test'
        }
        self.app.post('/', data=data_min)

        # Максимальный возраст (120)
        data_max = {
            'name': 'Max Age',
            'age': '120',
            'city': 'Test',
            'hobby': 'Test',
            'reason': 'Test'
        }
        self.app.post('/', data=data_max)

        # Проверяем, что оба значения сохранены
        with open(self.temp_filename, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('Возраст: 1', content)
            self.assertIn('Возраст: 120', content)

    # --- ТЕСТЫ ДЛЯ ПРОВЕРКИ HTML ---

    def test_required_fields(self):
        """Тест: проверка наличия всех полей в форме"""
        response = self.app.get('/')
        html_content = response.data.decode('utf-8')

        self.assertIn('name="name"', html_content)
        self.assertIn('name="age"', html_content)
        self.assertIn('name="city"', html_content)
        self.assertIn('name="hobby"', html_content)
        self.assertIn('name="reason"', html_content)

    def test_thankyou_page_links(self):
        """Тест: проверка наличия ссылок на странице благодарности"""
        test_data = {
            'name': 'Test User',
            'age': '25',
            'city': 'Test City',
            'hobby': 'Test Hobby',
            'reason': 'Test Reason'
        }

        response = self.app.post('/', data=test_data, follow_redirects=True)
        html_content = response.data.decode('utf-8')

        self.assertIn('href="/"', html_content)
        self.assertIn('href="/answers"', html_content)

    # --- ТЕСТЫ ДЛЯ ОБРАБОТКИ ОШИБОК ---

    def test_wrong_method(self):
        """Тест: отправка PUT запроса на главную страницу"""
        response = self.app.put('/')
        self.assertEqual(response.status_code, 405)

    def test_not_found_route(self):
        """Тест: обращение к несуществующему маршруту"""
        response = self.app.get('/nonexistent')
        self.assertEqual(response.status_code, 404)

    def test_long_strings(self):
        """Тест: отправка очень длинных строк"""
        long_string = 'A' * 1000
        test_data = {
            'name': long_string,
            'age': '25',
            'city': long_string[:100],  # Укорачиваем для города
            'hobby': long_string[:100],  # Укорачиваем для хобби
            'reason': long_string[:500]  # Укорачиваем для описания
        }

        response = self.app.post('/', data=test_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()