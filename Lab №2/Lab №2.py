import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import pandas as pd

logging.basicConfig(level=logging.INFO)

bot = Bot(token="8545506605:AAF2mNHOM0hH4F9MTbMNnoatnexwMbKDM3E")
dp = Dispatcher()

ATTENDANCE_SYMBOLS = {
    '+': 'присутствие',
    'н': 'отсутствие',
    'о': 'опоздание',
    '-': 'нет пары'
}


def load_students_data():
    students = {}
    current_student = None

    try:
        with open('students.txt', 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith(('ПН:', 'ВТ:', 'СР:', 'ЧТ:', 'ПТ:')):
                    current_student = line
                    students[current_student] = {}
                elif line and current_student:
                    try:
                        day, marks = line.split(': ')
                        students[current_student][day] = marks.split(', ')
                    except ValueError:
                        continue
    except FileNotFoundError:
        logging.error("Файл students.txt не найден")
        return {}

    return students


def create_attendance_table(student_data):
    days = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ']
    pairs = list(range(1, 8))

    df = pd.DataFrame(index=pairs, columns=days)

    for day in days:
        if day in student_data:
            marks = student_data[day]
            for i, mark in enumerate(marks):
                if i < 7:
                    df.at[i + 1, day] = mark

    return df


def format_attendance_table(df):
    table = "┌───────┬─────┬─────┬─────┬─────┬─────┐\n"
    table += "│ Пара  │ ПН  │ ВТ  │ СР  │ ЧТ  │ ПТ  │\n"
    table += "├───────┼─────┼─────┼─────┼─────┼─────┤\n"

    for pair_num in df.index:
        row = "│  {:2d}   │".format(pair_num)
        for day in df.columns:
            value = str(df.at[pair_num, day]) if pd.notna(df.at[pair_num, day]) else '-'
            row += f"  {value}  │"
        table += row + "\n"

    table += "└───────┴─────┴─────┴─────┴─────┴─────┘"
    return table


@dp.message(Command('start', 'help'))
async def process_start_command(message: Message):
    help_text = (
        "👋 Привет! Я бот для просмотра посещаемости студентов.\n\n"
        "📝 Доступные команды:\n"
        "/start - показать это сообщение\n"
        "/attendance <ФИО> - получить информацию о посещаемости студента\n"
        "/symbols - показать обозначения посещаемости\n"
        "/list - показать список всех студентов\n\n"
        "Пример: /attendance Иванов Иван Иванович"
    )
    await message.reply(help_text)


@dp.message(Command('symbols'))
async def process_symbols_command(message: Message):
    symbols_text = "📊 Обозначения посещаемости:\n\n"
    for symbol, meaning in ATTENDANCE_SYMBOLS.items():
        symbols_text += f"{symbol} — {meaning}\n"
    await message.reply(symbols_text)


@dp.message(Command('list'))
async def process_list_command(message: Message):
    students = load_students_data()

    if not students:
        await message.reply("❌ Список студентов пуст или файл не найден.")
        return

    student_list = "📋 Список студентов:\n\n"
    for i, student in enumerate(students.keys(), 1):
        student_list += f"{i}. {student}\n"

    await message.reply(student_list)


@dp.message(Command('attendance'))
async def process_attendance_command(message: Message):
    command_parts = message.text.split(maxsplit=1)

    if len(command_parts) < 2:
        await message.reply(
            "❌ Пожалуйста, укажите ФИО студента.\n"
            "Пример: /attendance Иванов Иван Иванович"
        )
        return

    full_name = command_parts[1].strip()

    students = load_students_data()

    if not students:
        await message.reply("❌ Ошибка загрузки данных студентов.")
        return

    found_student = None
    for student in students.keys():
        if student.lower() == full_name.lower():
            found_student = student
            break

    if not found_student:
        await message.reply(f"❌ Студент '{full_name}' не найден.\nИспользуйте /list для просмотра всех студентов.")
        return

    df = create_attendance_table(students[found_student])

    response = f"📊 Посещаемость студента: {found_student}\n\n"
    response += "Обозначения: + (присутствие), н (отсутствие), о (опоздание), - (нет пары)\n\n"

    response += "```\n" + format_attendance_table(df) + "\n```"

    await message.reply(response, parse_mode="Markdown")


@dp.message()
async def process_any_message(message: Message):
    await message.reply(
        "Я понимаю только команды.\n"
        "Используйте /start для просмотра доступных команд."
    )


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
