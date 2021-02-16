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
    data = callback_query.data.split('/')
    operid = int(data[2])
    userid = int(data[1])
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
    data = callback_query.data.split('/')
    operid = int(data[2])
    userid = int(data[1])
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
    data = callback_query.data.split('/')
    operid = int(data[1])
    oper = model.getOperationsForChat(operid)
    if callback_query.from_user.id != oper.userFrom:
        return
    model.db.delete(table='Operations', row_id=operid)
    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data.startswith('forward/'))
async def nextButton(callback_query: types.CallbackQuery):
    data = callback_query.data.split('/')
    operid = int(data[1])
    oper = model.getOperationsForChat(operid)
    
    if callback_query.from_user.id != oper.userFrom:
        return

    message, buttons = buildButtonsSet(oper, 'type')
    await callback_query.message.edit_text(text=message)
    await callback_query.message.edit_reply_markup(reply_markup=buttons)

@dp.callback_query_handler(lambda c: c.data.startswith('settype/'))
async def setType(callback_query: types.CallbackQuery):
    data = callback_query.data.split('/')
    operid = int(data[2])
    type = int(data[1])
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
 

def buildButtonsSet(oper:Operations, forcommand: str) -> [str, types.InlineKeyboardMarkup()]:
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

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)




