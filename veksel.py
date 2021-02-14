from aiogram import Bot, Dispatcher, executor, types
from model import User, Operation, Chat
import model 

api = '1575260517:AAEXiFbeffmgJXjeNg5Tkyb05EwiIgSUKFU'

bot = Bot(token=api)
dp = Dispatcher(bot)




@dp.message_handler(commands = ['start'])
async def start(message: types.Message):
    chat = message.chat
    user = message.from_user
    chatsav = Chat(id=chat.id)
    usersav = User(id=user.id, brief=user.username)
    chatsav.addUser(usersav)
    chatsav.save()
    
 

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)




