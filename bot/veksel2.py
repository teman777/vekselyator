from aiogram import Bot, Dispatcher, executor, types
from model import User, Operation, Chat, Operations
import model 
from typing import List, Dict
import re

api = '1575260517:AAEXiFbeffmgJXjeNg5Tkyb05EwiIgSUKFU'

bot = Bot(token=api)
dp = Dispatcher(bot)

"""Блок с обработкой команд через /"""
"""Сначала самые основные команды"""
@dp.message_handler(commands = ['start'])
async def start(message: types.Message):
    chat = model.getChatById(message.chat.id)
    if message.from_user.username == None:
        brief = message.from_user.first_name
    else:
        brief = message.from_user.username
    user = User(id=message.from_user.id, brief=brief)
    chat.addUser(user)
    chat.save()
    await message.reply(text="Зарегистрировал тебя в этом чате.\nПоловина дает вексели, половина гасит. ☝"
                       ,disable_notification = True)

@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    msg = "Это бот векселятор - сохраняет долги в этом чате.\n" + "/start - Зарегистрироваться в этом чате. Можно обновить свой ник\n"+ "/help - Помощь.\n" + "/add - Добавить вексель. Жми это, если тебе задолжали.\n" + "/my - Список векселей, где ты участвуешь.\n" + "/all - Список вообще всех векселей в этом чате.\n" + "/saldo - Расчитать общее сальдо для всех участников чата."
    await message.reply(text = msg, disable_notification = True)

# Ниже идет логика основных команд

# Добавляем запись в Operation 
# Так как добавление происходит в несколько этапов и мы не можем сразу сохранить все в Operation
# то добавим сначала в Operations - что-то вроде буферной таблицы

@dp.message_handler(commands=['add'])
async def add(message: types.Message):
    chat = model.getChatById(message.chat.id)
    oper = Operations(userFrom = message.from_user.id
                     ,chatId = chat.id)
    oper.save()
    buttons = buildButtonsAdd(chat, oper.id)
    text = 'Выбери, тех, кто задолжал'
    await message.reply(text = text 
                       ,reply_markup = buttons
                       ,disable_notification = True)
    

@dp.callback_query_handler(lambda c: c.data.startswith('adduser') 
                                  or c.data.startswith('deluser'))
async def addUser(callback_query: types.CallbackQuery):
    src_user = callback_query.message.reply_to_message.from_user.id
    if src_user != callback_query.from_user.id:
        return   
    dt = parseCallback(callback_query.data)
    chat = model.getChatById(callback_query.message.chat.id)
    operID = dt['operID']
    userID = dt['userID']
    add_or_delete = dt['type']
    oper = model.getOperationsForChat(operID)
    if add_or_delete == 'adduser':
        oper.userTo.append(userID)
    elif add_or_delete == 'deluser':
        oper.userTo.remove(userID)
    oper.save()
    buttons = buildButtonsAdd(chat, operID)
    await callback_query.message.edit_reply_markup(buttons)

@dp.callback_query_handler(lambda c: c.data.startswith('next'))
async def nextInline(callback_query: types.CallbackQuery):
    src_user = callback_query.message.reply_to_message.from_user.id
    if src_user != callback_query.from_user.id:
        return
    dt = parseCallback(callback_query.data)
    operID = dt['operID']
    operations = model.getOperationsForChat(operID)
    buttons = buildButtonsNext(operID)
    if len(operations.userTo) > 1:
        msg = 'Выбери тип векселя' 
    else:
        msg = 'Чтобы закончить вексель - ответь на это сообщение в формате Сумма + комментарий\nПример: 1234.34 За еблю с гнилозубом'
    await callback_query.message.edit_text(msg)
    await callback_query.message.edit_reply_markup(buttons)

@dp.callback_query_handler(lambda c: c.data.startswith('deloper'))
async def deleteOperations(callback_query: types.CallbackQuery):
    src_user = callback_query.message.reply_to_message.from_user.id
    if src_user != callback_query.from_user.id:
        return
    dt = parseCallback(callback_query.data)
    operID = dt['operID']
    operations = model.getOperationsForChat(operID)
    operations.delete()
    await callback_query.message.delete()

@dp.callback_query_handler(lambda c: c.data.startswith('settype'))
async def setType(callback_query: types.CallbackQuery):
    src_user = callback_query.message.reply_to_message.from_user.id
    if src_user != callback_query.from_user.id:
        return
    dt = parseCallback(callback_query.data)
    operID = dt['operID']
    tp = dt['typenew']
    oper = model.getOperationsForChat(operID)
    oper.type = tp
    oper.save()
    cancel_bt = types.InlineKeyboardButton(text = 'Отмена'
                                          ,callback_data='deloper/' + str(operID))
    buttons = types.InlineKeyboardMarkup()
    buttons.add(cancel_bt)
    await callback_query.messagel.edit_text('Чтобы закончить вексель - ответь на это сообщение в формате Сумма + комментарий\nПример: 1234.34 За еблю с гнилозубом')
    await callback_query.message.edit_reply_markup(buttons)
    


@dp.message_handler(lambda c: c.is_command() != True and re.match(r'\d+\.?\d*\ ?\w*',c.text))
async def finish(message: types.Message):
    # Ебанистическая цепочка, чтобы проконтроллировать, что ответил тот, кто надо
    data = message.reply_to_message.reply_markup.inline_keyboard[0][0].callback_data
    dt = parseCallback(data)
    operID = dt['operID']
    oper = model.getOperationsForChat(operID)
    if oper.userFrom != message.from_user.id:
        return
    
    parsable_text = message.text
    qtytext = re.findall(r'\d+\.?\d*', parsable_text)[0]
    qty = float(qtytext)
    comment = parsable_text[re.match(r'\d+\.?\d*', parsable_text).end() + 1:]
    oper.qty = qty
    oper.comment = comment
    oper.save()
    oper.resolve()
    oper.delete()
    await message.reply_to_message.edit_text('Вексель добавлен')


# Пасхалочка
@dp.message_handler(commands=['da?'])
async def rolfMsg(message: types.Message):
    await message.reply('Как говорит Ян - это нормальная тема.')

# Технические процедурки



def parseCallback(callback_data: str) -> Dict:
    splitted = callback_data.split('/')  
    if splitted[0] in ('adduser', 'deluser'):
        result = {'type': splitted[0], 'userID': int(splitted[1]), 'operID': int(splitted[2])}
    elif splitted[0] in ('next', 'deloper'):
        result = {'type': splitted[0], 'operID': int(splitted[1])}
    elif splitted[0] == 'settype':
        result = {'type': splitted[0], 'typenew': int(splitted[1]), 'operID': int(splitted[2])}
    return result

def buildButtonsNext(operation_id: int) -> types.InlineKeyboardMarkup:
    buttons = types.InlineKeyboardMarkup()
    operations = model.getOperationsForChat(operation_id)
    if len(operations.userTo) > 1:
        type_1 = types.InlineKeyboardButton(text = 'Делим на всех'
                                           ,callback_data = 'settype/2/' + str(operation_id))
        type_2 = types.InlineKeyboardButton(text = 'С каждого по'
                                           ,callback_data = 'settype/3/' + str(operation_id))
        buttons.row(type_1, type_2)
    cancel = types.InlineKeyboardButton(text = 'Отмена'
                                       ,callback_data = 'deloper/' + str(operation_id))
    buttons.add(cancel)
    return buttons


def buildButtonsAdd(chat: Chat, operation_id: int) -> types.InlineKeyboardMarkup:
    buttons = types.InlineKeyboardMarkup()
    operations = model.getOperationsForChat(operation_id)
    users = chat.users
    need_next = False
    for user in users:
        if user.id in operations.userTo:
            need_next = True
            text = user.brief + ' ✅'
            first_url = 'deluser/'
        else:
            text = user.brief
            first_url = 'adduser/'
        button = types.InlineKeyboardButton(text = text
                                           ,callback_data = first_url + str(user.id) + '/'+str(operation_id))
        buttons.add(button)   
    cancel_button = types.InlineKeyboardButton(text = 'Отмена'
                                              ,callback_data = 'deloper/' + str(operation_id))
    if need_next:
        buttons.row( cancel_button
                    ,types.InlineKeyboardButton(text = 'Далее'
                                               ,callback_data = 'next/' + str(operation_id)))
    else:
        buttons.add(cancel_button)
    return buttons

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

