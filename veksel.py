from aiogram import Bot, Dispatcher, executor, types
from model import User, Operation, Chat, Operations
import model 
import re

api = '1575260517:AAEXiFbeffmgJXjeNg5Tkyb05EwiIgSUKFU'

bot = Bot(token=api)
dp = Dispatcher(bot)


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
    
@dp.message_handler(commands = ['add'])
async def add(message: types.Message):
    chat = model.getChatById(message.chat.id)
    chat.load()
    operations = Operations(chatId=chat.id
                           ,userFrom=message.from_user.id
                           ,userTo=[]
                           ,comment=''
                           ,type = 1
                           ,qty = 0)

    operations.save()
    msg, buttons = buildButtonsSet(operations,'adddel')

    await message.reply(text=msg
                       ,disable_notification = True
                       ,reply_markup = buttons)

@dp.callback_query_handler(lambda c: c.data.startswith('adduser'))
async def addUserInline(callback_query: types.CallbackQuery):
    operid, userid = parseCallback(callback_query.data)
    oper = model.getOperationsForChat(operid)
    oper.userTo.append(userid)
    if len(oper.userTo) > 1:
        oper.type = 2
    oper.save()
    chat = model.getChatById(callback_query.message.chat.id)
    chat.load()
    if callback_query.from_user.id != oper.userFrom:
        await bot.send_message(chat.id, "Хуила, которое жмет лишнее - пошел нахуй\n")
        return
    _, buttons = buildButtonsSet(oper, 'adddel')
    await callback_query.message.edit_reply_markup(buttons)

@dp.callback_query_handler(lambda c: c.data.startswith('deleteuser'))
async def deleteUserInline(callback_query: types.CallbackQuery):
    operid, userid = parseCallback(callback_query.data)
    oper = model.getOperationsForChat(operid)
    oper.userTo.remove(userid)
    if len(oper.userTo) > 1:
        oper.type = 2
    oper.save()
    chat = model.getChatById(callback_query.message.chat.id)
    chat.load()
    if callback_query.from_user.id != oper.userFrom:
        return
    
    _, buttons = buildButtonsSet(oper, 'adddel')
    await callback_query.message.edit_reply_markup(buttons)


@dp.callback_query_handler(lambda c: c.data.startswith('back/'))
async def backButton(callback_query: types.CallbackQuery):
    operid, _ = parseCallback(callback_query.data)
    oper = model.getOperationsForChat(operid)
    if callback_query.from_user.id != oper.userFrom:
        return
    model.db.delete(table='Operations', row_id=operid)
    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data.startswith('forward/'))
async def nextButton(callback_query: types.CallbackQuery):
    operid, _ = parseCallback(callback_query.data)
    oper = model.getOperationsForChat(operid)
    
    if callback_query.from_user.id != oper.userFrom:
        return

    message, buttons = buildButtonsSet(oper, 'type')
    await callback_query.message.edit_text(text=message)
    await callback_query.message.edit_reply_markup(reply_markup=buttons)

@dp.callback_query_handler(lambda c: c.data.startswith('settype/'))
async def setType(callback_query: types.CallbackQuery):
    operid, type = parseCallback(callback_query.data)
    oper = model.getOperationsForChat(operid)
    if callback_query.from_user.id != oper.userFrom:
        return
    oper.type = type
    oper.save()
    message, buttons = buildButtonsSet(oper, 'finish')
    await callback_query.message.edit_text(text=message)
    await callback_query.message.edit_reply_markup(reply_markup=buttons)

@dp.message_handler(lambda c: c.is_command() != True and re.match(r'\d+\.?\d*\ ?\w*',c.text))  
async def finish(message: types.Message):
    data = message.reply_to_message.reply_markup.inline_keyboard[0][0].callback_data.split('/')
    replied_message = message.reply_to_message
    operid = int(data[1])
    parsabletext = message.text
    qtytext = re.findall(r'\d+\.?\d*', parsabletext)[0]
    qty = float(qtytext)
    comment = parsabletext[re.match(r'\d+\.?\d*', parsabletext).end() + 1:]
    oper = model.getOperationsForChat(operid)
    if oper.userFrom != message.from_user.id:
        return
    oper.qty = qty
    oper.comment = comment
    oper.save()
    oper.resolve()
    
    message = "Вексель добавлен"
    await replied_message.edit_text(message)

@dp.message_handler(commands = ['all'])
async def getAllOperationsForChat(message: types.Message):
    chat = model.getChatById(message.chat.id)
    chat.load()
    operations = chat.operations
    if len(operations) > 0:
        oper = operations[0]
        msg = 'Список векселей:\n' + getTextForOper(oper)
        buttons = types.InlineKeyboardMarkup()
        user = message.from_user.id
        index = 0
        buttons.add(types.InlineKeyboardButton(text='Удалить', callback_data='deloper/'+str(oper.id)+'/'+str(user)+'/0'))
        if len(operations) > 1:
            if index + 1 == len(operations):
                nextIndex = 1
                prevIndex = index - 1
            elif index == 0:
                nextIndex = index + 1
                prevIndex = len(operations) - 1
            else:
                nextIndex = index + 1
                prevIndex = index - 1
            buttons.row(types.InlineKeyboardButton(text='<', callback_data='get/'+str(prevIndex)+'/'+str(user)+'/2'), types.InlineKeyboardButton(text='>', callback_data='get/' + str(nextIndex)+'/'+str(user)+'/2'))
        await message.reply(text=msg, reply_markup= buttons, disable_notification=True)
    else:
        await message.reply(text='У тебя нет векселей', disable_notification=True)


@dp.message_handler(lambda m: m.is_command() and re.match(r'/del\d+', m.text))
async def deleteOperation(message: types.Message):
    chat = model.getChatById(message.chat.id)
    chat.load()
    operid = int(message.text[re.match(r'/del',message.text).end():])
    for i in chat.operations:
        if operid == i.id:
            oper = i
    model.db.delete('Operation', oper.id)
    
@dp.message_handler(commands=['my'])
async def getMyOpers(message: types.Message):
    chat = model.getChatById(message.chat.id)
    chat.load()
    opers = []
    for o in chat.operations:
        if message.from_user.id in (o.userFrom, o.userTo):
            opers.append(o)
    if len(opers) > 0:
        oper = opers[0]
        msg = 'Список векселей:\n' + getTextForOper(oper)
        buttons = types.InlineKeyboardMarkup()
        user = message.from_user.id
        index = 0
        buttons.add(types.InlineKeyboardButton(text='Удалить', callback_data='deloper/'+str(oper.id)+'/'+str(user)+'/0'))
        if len(opers) > 1:
            if index + 1 == len(opers):
                nextIndex = 1
                prevIndex = index - 1
            elif index == 0:
                nextIndex = index + 1
                prevIndex = len(opers) - 1
            else:
                nextIndex = index + 1
                prevIndex = index - 1
            buttons.row(types.InlineKeyboardButton(text='<', callback_data='get/'+str(prevIndex)+'/'+str(user)), types.InlineKeyboardButton(text='>', callback_data='get/' + str(nextIndex)+'/'+str(user)))
        await message.reply(text=msg, reply_markup= buttons, disable_notification=True)
    else:
        await message.reply(text='У тебя нет векселей', disable_notification=True)
@dp.callback_query_handler(lambda c: c.data.startswith('get/'))
async def getVekselByIndex(callback_query: types.CallbackQuery):
    user, index = parseCallback(callback_query.data)
    user = int(user)
    index = int(index)
    chat = model.getChatById(callback_query.message.chat.id)
    chat.load()
    userid = callback_query.from_user.id
    
    if callback_query.data.split('/')[3] == '2':
        isAnotherCommand = True
    else:
        isAnotherCommand = False

    if int(user) != userid:
        return
    opers = []
    for o in chat.operations:
        if userid in (o.userFrom, o.userTo) or isAnotherCommand:
            opers.append(o)
    oper = opers[int(index)]
    message = 'Список векселей:\n'
    message = message + getTextForOper(oper)
    buttons = types.InlineKeyboardMarkup()
    buttons.add(types.InlineKeyboardButton(text='Удалить', callback_data='deloper/'+str(oper.id)+'/'+str(user)+'/'+str(index)))
    if len(opers) > 1:
        if index + 1 == len(opers):
            nextIndex = 0
            prevIndex = index - 1
        elif index == 0:
            nextIndex = index + 1
            prevIndex = len(opers) - 1
        else:
            nextIndex = index + 1
            prevIndex = index - 1
        
        if not isAnotherCommand:
            buttons.row(types.InlineKeyboardButton(text='<', callback_data='get/'+str(prevIndex)+'/'+str(user)), types.InlineKeyboardButton(text='>', callback_data='get/' + str(nextIndex)+'/'+str(user)))
        else:
            buttons.row(types.InlineKeyboardButton(text='<', callback_data='get/'+str(prevIndex)+'/'+str(user)+'/2'), types.InlineKeyboardButton(text='>', callback_data='get/' + str(nextIndex)+'/'+str(user)+'/2'))

    await callback_query.message.edit_text(message)
    await callback_query.message.edit_reply_markup(buttons)
    
@dp.callback_query_handler(lambda c: c.data.startswith('deloper/'))
async def delOper(callback_query: types.CallbackQuery):
    operid, user = parseCallback(callback_query.data)
    chat = model.getChatById(callback_query.message.chat.id)
    chat.load()
    operid = int(operid)
    if int(user) != callback_query.from_user.id:
        return
    for op in chat.operations:
        if op.id == operid:
            operation = op
    index = int(callback_query.data.split('/')[3])
    model.db.delete('Operation', operation.id) 
    chat.load()
    opers = []
    for o in chat.operations:
        if int(user) in (o.userFrom, o.userTo):
            opers.append(o)
    buttons = types.InlineKeyboardMarkup()
    nextIndex = index
    prevIndex = index - 1
    if nextIndex > len(opers) - 1:
        nextIndex = 0
    if prevIndex < 0:
        prevIndex = len(opers) - 1
    if len(opers) > 0:
        buttons.row(types.InlineKeyboardButton(text='<', callback_data='get/'+str(prevIndex)+'/'+str(user)), types.InlineKeyboardButton(text='>', callback_data='get/' + str(nextIndex)+'/'+str(user)))
    message = 'Удалено'
    if len(opers) == 0:
        message = message + '\nУ тебя больше нет открытых векселей.'
    await callback_query.message.edit_text(message)
    if len(opers) > 0:
        await callback_query.message.edit_reply_markup(buttons)


def buildButtonsSet(oper:Operations,forcommand: str) -> [str, types.InlineKeyboardMarkup()]:
    message = ''
    buttons = types.InlineKeyboardMarkup()
    chat = model.getChatById(oper.chatId)
    chat.load()
    users = chat.users
    if forcommand == 'adddel':
        message = "Добавляем вексель\nКто задолжал?"
        for user in users:
            if user.id != oper.userFrom:
                if user.id in oper.userTo:
                    buttons.add(types.InlineKeyboardButton(text=user.brief + ' +',callback_data='deleteuser/'+str(user.id)+'/'+str(oper.id)))
                else:
                    buttons.add(types.InlineKeyboardButton(text=user.brief,callback_data='adduser/'+str(user.id)+'/'+str(oper.id)))
        if len(oper.userTo) > 0:
            buttons.row(types.InlineKeyboardButton(text="Отмена",callback_data='back/'+str(oper.id)),types.InlineKeyboardButton(text="Далее",callback_data='forward/'+str(oper.id)))
        else:
            buttons.row(types.InlineKeyboardButton(text="Отмена",callback_data='back/'+str(oper.id)))

    elif forcommand == 'type':
        if oper.type != 1:
            message = "Выбери тип векселя:"
            buttons.add(types.InlineKeyboardButton(text="Разделить сумму на всех", callback_data="settype/2/"+str(oper.id)))
            buttons.add(types.InlineKeyboardButton(text="Сумма с каждого", callback_data="settype/3/"+str(oper.id)))
        else:
            message = "Чтобы закончить вексель - ответь на это сообщение в формате Сумма + комментарий\nПример: 1234.34 За еблю с гнилозубом"
        buttons.row(types.InlineKeyboardButton(text="Отмена",callback_data='back/'+str(oper.id)))
    elif forcommand == 'finish':
        message = "Чтобы закончить вексель - ответь на это сообщение в формате Сумма + комментарий\nПример: 1234.34 За еблю с гнилозубом"
        buttons.row(types.InlineKeyboardButton(text="Отмена",callback_data='back/'+str(oper.id)))

    return message, buttons

def getTextForOper(oper: Operation) -> str:
    chat = model.getChatById(oper.chatId)
    chat.load()
    users = chat.users
    for u in users:
        if u.id == oper.userFrom:
            userFrom = u
        elif u.id == oper.userTo:
            userTo = u
    message = 'От: ' + userFrom.brief + '\nКому: ' + userTo.brief + '\nСумма: ' + str(oper.qty) + '\nКомментарий: ' + oper.comment 
    return message

def parseCallback(callback_data: str) -> [int, int]:
    operid = 0
    dopid = 0
    data = callback_data.split('/')
    if data[0] in  ('adduser', 'deleteuser'):
        operid = int(data[2])
        dopid = int(data[1])
    elif data[0] in ('back', 'forward'):
        operid = int(data[1])
    elif data[0] == 'settype':
        operid = int(data[2])
        dopid = int(data[1])
    elif data[0] == 'get':
        dopid = data[1]
        operid = data[2]
    elif data[0] == 'deloper':
        operid = data[1]
        dopid = data[2]
    return operid, dopid


    





if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)




