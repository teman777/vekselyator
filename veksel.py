from aiogram import Bot, Dispatcher, executor, types
from model import User, Operation, Chat, Operations
import model 
import json

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
    buttons = types.InlineKeyboardMarkup()
    operations = Operations(chatId=chat.id
                           ,userFrom=message.from_user.id
                           ,userTo=[]
                           ,comment=''
                           ,type = 1
                           ,qty = 0)

    operations.save()
    callback = 'adduser'
    for user in chat.users:
        if user.id != message.from_user.id:
            buttons.add(types.InlineKeyboardButton(text=user.brief, callback_data=callback+'/'+str( user.id) + '/' + str(operations.id)))
    await message.reply(text="Добавляем вексель\nКто задолжал?"
                       ,disable_notification = True
                       ,reply_markup = buttons)

@dp.callback_query_handler(lambda c: c.data.startswith('adduser'))
async def addUserInline(callback_query: types.CallbackQuery):
    data = callback_query.data.split('/')
    operid = int(data[2])
    userid = int(data[1])
    oper = model.getOperationsForChat(operid)
    oper.userTo.append(userid)
    oper.save()
    chat = model.getChatById(callback_query.message.chat.id)
    chat.load()
    buttons = types.InlineKeyboardMarkup()
    for user in chat.users:
        if user.id != callback_query.from_user.id:
            if user.id == userid or user.id in oper.userTo:          
                buttons.add(types.InlineKeyboardButton(text=user.brief + ' +',callback_data='deleteuser/' + str(user.id) + '/' + str(operid)))
            else:
                buttons.add(types.InlineKeyboardButton(text=user.brief,callback_data='adduser/' + str(user.id) + '/' + str(operid)))
    await callback_query.message.edit_reply_markup(buttons)

@dp.callback_query_handler(lambda c: c.data.startswith('deleteuser'))
async def deleteUserInline(callback_query: types.CallbackQuery):
    data = callback_query.data.split('/')
    operid = int(data[2])
    userid = int(data[1])
    oper = model.getOperationsForChat(operid)
    oper.userTo.remove(userid)
    oper.save()
    chat = model.getChatById(callback_query.message.chat.id)
    chat.load()
    buttons = types.InlineKeyboardMarkup()
    for user in chat.users:
        if user.id != callback_query.from_user.id:
            if user.id == userid or user.id not in oper.userTo:
                buttons.add(types.InlineKeyboardButton(text=user.brief,callback_data='adduser/' + str(user.id) + '/' + str(operid)))
            else:
                buttons.add(types.InlineKeyboardButton(text=user.brief + ' +',callback_data='deleteuser/' + str(user.id) + '/' + str(operid)))
    await callback_query.message.edit_reply_markup(buttons)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)




