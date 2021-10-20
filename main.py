import asyncio

import aiogram
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

telegram_acceptor = {}
# todo Token of the telegram bot
tbot = aiogram.Bot(token="")
dp = aiogram.Dispatcher(tbot)

remind_list = {'mo': ['Покушать', 'Поиграть в компуктер'], 'tu': [], 'we': [], 'th': [], 'fr': [], 'sa': [], 'su': []}
last_picked_day = None
change_mode = False


async def create_week_markup():
    button = InlineKeyboardButton('ПН', callback_data='mo')
    button2 = InlineKeyboardButton('ВТ', callback_data='tu')
    button3 = InlineKeyboardButton('СР', callback_data='we')
    button4 = InlineKeyboardButton('ЧТ', callback_data='th')
    button5 = InlineKeyboardButton('ПТ', callback_data='fr')
    button6 = InlineKeyboardButton('СБ', callback_data='sa')
    button7 = InlineKeyboardButton('ВС', callback_data='su')
    button8 = InlineKeyboardButton('СБРОСИТЬ ВСЁ', callback_data='clear')

    inline = InlineKeyboardMarkup().add(button, button2, button3, button4, button5, button6, button7, button8)

    return inline


@dp.message_handler()
async def message_handler(msg: aiogram.types.Message):
    global change_mode
    if change_mode:
        text = msg.text

        button2 = InlineKeyboardButton('ЗАКРЫТЬ', callback_data='menu')
        inline = InlineKeyboardMarkup().add(button2)

        cancel_button = InlineKeyboardButton('ОТМЕНА', callback_data='cancel')
        cancel_inline = InlineKeyboardMarkup().add(cancel_button)
        # Добавляем напоминания
        try:
            int(msg.text)
        except:
            data.add_reminder(last_picked_day, msg.text)

            data_list = ''
            n = 0
            for i in data.get_array(last_picked_day):
                data_list = data_list + str(n) + ') ' + i + '\n'
                n += 1

            if data_list == '':
                data_list = 'Напоминанй нет.'

            await msg.reply('Новое напоминание успешно добавлено!\nНовые напоминания: \n' + data_list,
                            reply_markup=inline)
            change_mode = False
            return

        # пробуем убрать напоминание по индексу
        try:
            d: list = data.get_array(last_picked_day).copy()
            d.pop(int(msg.text))
            data.set_array(last_picked_day, d)
            await msg.reply('Напоминание успешно убрано!', reply_markup=inline)

        except:
            await msg.reply('Напоминания с таким индексом не существует, попробуйте снова', reply_markup=cancel_inline)
            return

        change_mode = False
    else:
        await msg.reply('Выбери день недели, чтобы посмотреть напоминания:', reply_markup=await create_week_markup())


@dp.callback_query_handler()
async def process_callback(callback_query: aiogram.types.CallbackQuery):
    global change_mode
    global last_picked_day
    global remind_list

    b = callback_query.data

    if b == 'clear':
        remind_list = {'mo': [], 'tu': [], 'we': [], 'th': [], 'fr': [], 'sa': [], 'su': []}
        await callback_query.message.reply('Все напоминания успешно стерты!')

    if b == 'menu':
        await callback_query.message.reply('Выбери день недели, чтобы посмотреть напоминания:',
                                           reply_markup=await create_week_markup())
    if b == 'cancel':
        await callback_query.message.reply('Выбери день недели, чтобы посмотреть напоминания:',
                                           reply_markup=await create_week_markup())
        change_mode = False

    if b.startswith('change_'):
        change_mode = True

        cancel_button = InlineKeyboardButton('ОТМЕНА', callback_data='cancel')
        cancel_inline = InlineKeyboardMarkup().add(cancel_button)

        await callback_query.message.reply('Напиши новую задачу на этот день недели, или цифру, чтобы убрать задачу:',
                                           reply_markup=cancel_inline)

    if b in remind_list.keys():
        last_picked_day = b
        data_list = ''
        n = 0
        for i in data.get_array(b):
            data_list = data_list + str(n) + ') ' + i + '\n'
            n += 1

        button = InlineKeyboardButton('ИЗМЕНИТЬ', callback_data='change_' + b)
        button2 = InlineKeyboardButton('ЗАКРЫТЬ', callback_data='menu')
        inline = InlineKeyboardMarkup().add(button, button2)

        if data_list == '':
            data_list = 'Напоминанй нет.'
        await callback_query.message.reply(data_list, reply_markup=inline)


class data:
    @staticmethod
    def set_array(day, data):
        remind_list[day] = data

    @staticmethod
    def get_array(day):
        return remind_list[day]

    @staticmethod
    def add_reminder(day, reminder):
        data_array: list = remind_list[day].copy()
        data_array.append(reminder)
        remind_list[day] = data_array


loop = asyncio.get_event_loop()

tasks = [loop.create_task(aiogram.utils.executor.start_polling(dp))]
wait_tasks = asyncio.wait(tasks)

try:
    loop.run_until_complete(wait_tasks)
finally:
    loop.close()
