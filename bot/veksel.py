import os
import re
from typing import Dict

from aiogram import Bot, Dispatcher, executor, types

import model
from model import User, Chat, Operations

api = os.getenv('TG_API')
bot = Bot(token=api)
dp = Dispatcher(bot)

"""Блок с обработкой команд через /"""
"""Сначала самые основные команды"""


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    chat = model.getChatById(message.chat.id)
    if message.from_user.username is None:
        brief = message.from_user.first_name
    else:
        brief = message.from_user.username
    user = User(id=message.from_user.id, brief=brief)
    chat.addUser(user)
    chat.save()
    await message.reply(text="Зарегистрировал тебя в этом чате.\nПоловина дает вексели, половина гасит. ☝"
                        , disable_notification=True)


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    msg = "Это бот векселятор - сохраняет долги в этом чате.\n" + "/start - Зарегистрироваться в этом чате. Можно обновить свой ник\n" + "/help - Помощь.\n" + "/add - Добавить вексель. Жми это, если тебе задолжали.\n" + "/my - Список векселей, где ты участвуешь.\n" + "/all - Список вообще всех векселей в этом чате.\n" + "/saldo - Расчитать общее сальдо для всех участников чата."
    await message.reply(text=msg, disable_notification=True)


# Ниже идет логика основных команд

# Добавляем запись в Operation 
# Так как добавление происходит в несколько этапов и мы не можем сразу сохранить все в Operation
# то добавим сначала в Operations - что-то вроде буферной таблицы

@dp.message_handler(commands=['add'])
async def add(message: types.Message):
    chat = model.getChatById(message.chat.id)
    oper = Operations(userFrom=message.from_user.id
                      , chatId=chat.id)
    oper.save()
    buttons = buildButtonsAdd(chat, oper.id)
    text = 'Выбери, тех, кто задолжал'
    await message.reply(text=text
                        , reply_markup=buttons
                        , disable_notification=True)


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
    oper = model.getOperations(operID)
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
    operations = model.getOperations(operID)
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
    operations = model.getOperations(operID)
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
    oper = model.getOperations(operID)
    oper.type = tp
    oper.save()
    cancel_bt = types.InlineKeyboardButton(text='Отмена'
                                           , callback_data='deloper/' + str(operID))
    buttons = types.InlineKeyboardMarkup()
    buttons.add(cancel_bt)
    await callback_query.message.edit_text(
        'Чтобы закончить вексель - ответь на это сообщение в формате Сумма + комментарий\nПример: 1234.34 За еблю с гнилозубом')
    await callback_query.message.edit_reply_markup(buttons)


@dp.message_handler(lambda c: c.is_command() != True and re.match(r'\d+\.?\d*\ ?\w*', c.text))
async def finish(message: types.Message):
    # Ебанистическая цепочка, чтобы проконтроллировать, что ответил тот, кто надо
    data = message.reply_to_message.reply_markup.inline_keyboard[0][0].callback_data
    dt = parseCallback(data)
    operID = dt['operID']
    oper = model.getOperations(operID)
    if oper.userFrom != message.from_user.id:
        return

    parsable_text = message.text
    qtytext = re.findall(r'\d+\.?\d*', parsable_text)[0]
    qty = round(float(qtytext), 2)
    comment = parsable_text[re.match(r'\d+\.?\d*', parsable_text).end() + 1:]
    oper.qty = qty
    oper.comment = comment
    oper.save()
    oper.resolve()
    oper.delete()
    await message.reply_to_message.edit_text('Вексель добавлен')


# Сальдо
@dp.message_handler(commands=['saldo'])
async def saldo(message: types.Message):
    chat = model.getChatById(message.chat.id)
    opers = chat.operations
    user_pairs = {}
    for oper in opers:
        if (oper.userFrom, oper.userTo) in user_pairs.keys():
            qty = user_pairs[(oper.userFrom, oper.userTo)]
            qty = qty + oper.qty
            user_pairs[(oper.userFrom, oper.userTo)] = qty
        elif (oper.userTo, oper.userFrom) in user_pairs.keys():
            qty = user_pairs[(oper.userTo, oper.userFrom)]
            qty = qty - oper.qty
            user_pairs[(oper.userTo, oper.userFrom)] = qty
        else:
            user_pairs[(oper.userFrom, oper.userTo)] = oper.qty
    text = getTextForSaldo(user_pairs, chat)
    await message.reply(text=text, disable_notification=True)


# Ниже блок со списком векселей - команды /my, /all
# Команды очень похожи, list векселей только будет отличаться

@dp.message_handler(commands=['my', 'all'])
async def listCommand(message: types.Message):
    chat = model.getChatById(message.chat.id)
    user_id = 0
    if message.text == '/my':
        user_id = message.from_user.id
    operations = model.getOperationsIdList(chat, user_id)
    if len(operations) > 0:
        oper_id = operations[0]
        text = 'Твои вексели:\n' if message.text == '/my' else 'Вексели чата:\n'
        text = text + getTextForOperation(oper_id)

    else:
        oper_id = 0
        if message.text == '/all':
            text = 'В этом чате нет открытых векселей.'
        else:
            text = 'У тебя нет открытых векселей.'
    tp = 0 if message.text == '/all' else 1
    buttons = buildButtonsList(oper_id, message.from_user.id, operations, tp)
    await message.reply(text=text, reply_markup=buttons)


@dp.callback_query_handler(lambda c: c.data.startswith('get'))
async def getOper(callback_query: types.CallbackQuery):
    src_user = callback_query.message.reply_to_message.from_user.id
    if src_user != callback_query.from_user.id:
        return
    dt = parseCallback(callback_query.data)
    oper_id = dt['operID']
    tp = dt['command']
    chat = model.getChatById(callback_query.message.chat.id)
    user_id = 0 if tp == 0 else callback_query.from_user.id
    l = model.getOperationsIdList(chat, user_id)
    user_id = callback_query.from_user.id
    buttons = buildButtonsList(oper_id, user_id, l, tp)
    if tp == 0:
        text = 'Вексели чата:\n'
    else:
        text = 'Твои вексели:\n'
    text = text + getTextForOperation(oper_id)
    await callback_query.message.edit_text(text)
    await callback_query.message.edit_reply_markup(buttons)


@dp.callback_query_handler(lambda c: c.data.startswith('delete'))
async def deleteOper(callback_query: types.CallbackQuery):
    src_user = callback_query.message.reply_to_message.from_user.id
    if src_user != callback_query.from_user.id:
        return
    dt = parseCallback(callback_query.data)
    operID = dt['operID']
    chat = model.getChatById(callback_query.from_user.id)
    tp = dt['command']
    user_id = 0 if tp == 0 else callback_query.from_user.id
    l = model.getOperationsIdList(chat, user_id)
    oper = model.getOperation(operID)
    buttons = buildButtonsList(operID, 0, l, tp)
    oper.delete()
    text = 'Удалено'
    await callback_query.message.edit_text(text)
    await callback_query.message.edit_reply_markup(buttons)


@dp.callback_query_handler(lambda c: c.data.startswith('cancel'))
async def cancel(callback_query: types.CallbackQuery):
    src_user = callback_query.message.reply_to_message.from_user.id
    if src_user != callback_query.from_user.id:
        return
    await callback_query.message.delete()


# Суперсальдо
@dp.message_handler(commands=['supersaldo'])
async def superSaldo(message: types.Message):
    chat = model.getChatById(message.chat.id)
    newOperations = model.getSuperSaldo(chat.id)
    model.deleteAllOperation(chat.id)
    for op in newOperations:
        op.save()
    await message.reply('Суперсальдо!')
    await saldo(message)


# Пасхалочка
@dp.message_handler(commands=['da?'])
async def rolfMsg(message: types.Message):
    await message.reply('Как говорит Ян - это нормальная тема.')


# Технические процедурки
def getTextForSaldo(dt: Dict, chat: Chat) -> str:
    users = chat.users
    res = ''
    for key in dt.keys():
        s = ''
        qty = dt[key]
        u1 = key[0]
        u2 = key[1]
        u1_brier = next(x.brief for x in users if x.id == u1)
        u2_brier = next(x.brief for x in users if x.id == u2)
        separator = "<--"
        qty_str = "{:10.2f}".format(abs(qty))
        s = (u1_brier if qty > 0 else u2_brier) + ' ' + separator + ' ' + (
            u2_brier if qty > 0 else u1_brier) + '\n' + qty_str + '\n----------------------------\n'
        res = res + s
    return res


def getTextForOperation(operation_id: int) -> str:
    dt = model.getOperationText(operation_id)

    res = 'От: ' + dt['UserFrom'] + '\nКому: ' + dt['UserTo'] + '\nСумма: ' + str(dt['Qty']) + '\n' + dt['Comment']
    return res


def buildButtonsList(operation_id: int, user: int = 0, operations=None,
                     tp: int = 0) -> types.InlineKeyboardMarkup():
    if operations is None:
        operations = []
    buttons = types.InlineKeyboardMarkup()
    if len(operations) != 0:
        if len(operations) > 1:
            curr_index = operations.index(operation_id)
            prev_index = curr_index - 1 if curr_index > 0 else len(operations) - 1
            next_index = curr_index + 1 if curr_index < len(operations) - 1 else 0
            next_item = operations[next_index]
            prev_item = operations[prev_index]
            next_button = types.InlineKeyboardButton(text='>'
                                                     , callback_data='get/' + str(next_item) + '/' + str(tp))
            prev_button = types.InlineKeyboardButton(text='<'
                                                     , callback_data='get/' + str(prev_item) + '/' + str(tp))
            buttons.row(prev_button, next_button)
        oper = model.getOperation(operation_id)
        if oper.userFrom == user:
            buttons.add(
                types.InlineKeyboardButton(text='Удалить', callback_data='delete/' + str(operation_id) + '/' + str(tp)))

    buttons.add(types.InlineKeyboardButton(text='Закрыть', callback_data='cancel'))

    return buttons


def parseCallback(callback_data: str) -> Dict:
    splitted = callback_data.split('/')
    if splitted[0] in ('adduser', 'deluser'):
        result = {'type': splitted[0], 'userID': int(splitted[1]), 'operID': int(splitted[2])}
    elif splitted[0] in ('next', 'deloper'):
        result = {'type': splitted[0], 'operID': int(splitted[1])}
    elif splitted[0] == 'settype':
        result = {'type': splitted[0], 'typenew': int(splitted[1]), 'operID': int(splitted[2])}
    elif splitted[0] in ('get', 'delete'):
        result = {'type': splitted[0], 'operID': int(splitted[1]), 'command': int(splitted[2])}
    return result


def buildButtonsNext(operation_id: int) -> types.InlineKeyboardMarkup:
    buttons = types.InlineKeyboardMarkup()
    operations = model.getOperations(operation_id)
    if len(operations.userTo) > 1:
        type_1 = types.InlineKeyboardButton(text='Делим на всех'
                                            , callback_data='settype/2/' + str(operation_id))
        type_2 = types.InlineKeyboardButton(text='С каждого по'
                                            , callback_data='settype/3/' + str(operation_id))
        buttons.row(type_1, type_2)
    cancel = types.InlineKeyboardButton(text='Отмена'
                                        , callback_data='deloper/' + str(operation_id))
    buttons.add(cancel)
    return buttons


def buildButtonsAdd(chat: Chat, operation_id: int) -> types.InlineKeyboardMarkup:
    buttons = types.InlineKeyboardMarkup()
    operations = model.getOperations(operation_id)
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
        button = types.InlineKeyboardButton(text=text
                                            , callback_data=first_url + str(user.id) + '/' + str(operation_id))
        buttons.add(button)
    cancel_button = types.InlineKeyboardButton(text='Отмена'
                                               , callback_data='deloper/' + str(operation_id))
    if need_next:
        buttons.row(cancel_button
                    , types.InlineKeyboardButton(text='Далее'
                                                 , callback_data='next/' + str(operation_id)))
    else:
        buttons.add(cancel_button)
    return buttons


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
