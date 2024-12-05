import aiosqlite
from config import DB_NAME

async def create_tables():


    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DROP TABLE IF EXISTS quiz_results')
        await db.execute('DROP TABLE IF EXISTS quiz_state')

        await db.execute('''
                    CREATE TABLE IF NOT EXISTS quiz_state (
                        user_id INTEGER PRIMARY KEY,
                        question_index INTEGER
                    )
                ''')

        await db.execute('''
                    CREATE TABLE IF NOT EXISTS quiz_results (
                        user_id INTEGER PRIMARY KEY,
                        correct_answers INTEGER DEFAULT 0,
                        total_questions INTEGER DEFAULT 0
                    )
                ''')


        await db.commit()

async def update_quiz_results(user_id, is_correct):
    async with aiosqlite.connect(DB_NAME) as db:
        # Увеличиваем общее количество вопросов на 1
        await db.execute('''
                   INSERT INTO quiz_results (user_id, correct_answers, total_questions)
                   VALUES (?, ?, ?)
                   ON CONFLICT(user_id) DO UPDATE SET
                       correct_answers = correct_answers + ?,
                       total_questions = total_questions + 1
               ''', (user_id, is_correct, 1, is_correct))
        await db.commit()

async def show_results(message, user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        result = await db.execute(
            'SELECT correct_answers, total_questions FROM quiz_results WHERE user_id = ?',
            (user_id,)
        )
        row = await result.fetchone()
        if row:
            correct_answers, total_questions = row
            await message.answer(f"Ваш результат: {correct_answers} правильных ответов из {total_questions} вопросов!")
        else:
            await message.answer("Вы еще не проходили квиз!")

async def get_quiz_index(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            results = await cursor.fetchone()
            return results[0] if results else 0

async def update_quiz_index(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        await db.commit()