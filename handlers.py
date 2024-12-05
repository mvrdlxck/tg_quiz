from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F, types
from config import dp, bot 
import logging
import asyncio
from questions import quiz_data
from data_base import create_tables, update_quiz_results, update_quiz_index, show_results, get_quiz_index

logging.basicConfig(level=logging.INFO)

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    if current_question_index >= len(quiz_data):
        await message.answer("Нет доступных вопросов.")
        return

    correct_index = quiz_data[current_question_index]['correct_option']

    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts)
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

async def new_quiz(message):
    user_id = message.from_user.id
    await update_quiz_index(user_id, 0)
    await get_question(message, user_id)

def generate_options_keyboard(answer_options):
    builder = InlineKeyboardBuilder()
    for option in answer_options:
        builder.add(types.InlineKeyboardButton(text=option, callback_data=option))
    builder.adjust(1)
    return builder.as_markup()

@dp.callback_query()
async def answer_question(callback: types.CallbackQuery):
    selected_answer = callback.data
    current_question_index = await get_quiz_index(callback.from_user.id)

    if current_question_index >= len(quiz_data):
        await callback.message.answer("Квиз завершен!")
        return

    correct_option_index = quiz_data[current_question_index]['correct_option']
    correct_option = quiz_data[current_question_index]['options'][correct_option_index]

    await callback.bot.edit_message_reply_markup(chat_id=callback.from_user.id, message_id=callback.message.message_id, reply_markup=None)
    await callback.message.answer(f"Ваш ответ: {selected_answer}")

    is_correct = 1 if selected_answer == correct_option else 0

    if selected_answer == correct_option:
        await callback.message.answer("Верно!")
    else:
        await callback.message.answer(f"Неправильно. Правильный ответ: {correct_option}")

    await update_quiz_results(callback.from_user.id, is_correct)

    await update_quiz_index(callback.from_user.id, current_question_index + 1)
    if current_question_index + 1 < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")
        await show_results(callback.message, callback.from_user.id)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text == "Начать игру")
async def cmd_quiz(message: types.Message):
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message)

async def main():
    await create_tables()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())