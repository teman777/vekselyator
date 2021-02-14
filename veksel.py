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
    user = User(id=message.from_user.id, brief=message.from_user.username)
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
                           , qty = 0)
    callback = 'adduser/12345678/1234567543fasdfsdfsdfsdfasdfdsfsdfsdgsdfgewf'
    for user in chat.users:
        if user.id != message.from_user.id:
            buttons.add(types.InlineKeyboardButton(text=user.brief, callback_data=callback))
    await message.reply(text="Добавляем вексель\nКто задолжал?"
                       ,disable_notification = True
                       ,reply_markup = buttons)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)




