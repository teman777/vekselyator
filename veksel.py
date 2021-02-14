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
                           ,qty = 0)

    operations.save()
    callback = 'adduser'
    for user in chat.users:
        buttons.add(types.InlineKeyboardButton(text=user.brief, callback_data=callback+'/'+str( user.id) + '/' + str(operations.id)))
        print(callback+'/'+str( user.id) + '/' + str(operations.id))
    await message.reply(text="Добавляем вексель\nКто задолжал?"
                       ,disable_notification = True
                       ,reply_markup = buttons)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)




