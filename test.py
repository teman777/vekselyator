from aiogram import Bot, Dispatcher, executor, types
from model import User, Operation, Chat, Operations
import model 
import re

def buildButtonsSet(oper:Operations, forcommand: str, chat: Chat, buttons: types.InlineKeyboardMarkup) -> str:
    users = chat.users
    message = ''
    endbuttons = []
    endbuttons.append(types.InlineKeyboardButton(text="Отмена",callback_data='back/'+str(oper.id)))
    if forcommand == 'adddel':
        message = "Добавляем вексель\nКто задолжал?"
        for user in users:
            if user.id != oper.userFrom:
                if user.id in oper.userTo:
                    buttons.add(types.InlineKeyboardButton(text=user.brief + ' +',callback_data='deleteuser/'+str(user.id)+'/'+str(oper.id)))
                else:
                    buttons.add(types.InlineKeyboardButton(text=user.brief,callback_data='adduser/'+str(user.id)+'/'+str(oper.id)))
        if len(oper.userTo) > 0:
            list.append(types.InlineKeyboardButton(text="Далее",callback_data='forward/'+str(oper.id)))
    elif forcommand == 'type':
        if len(oper.type) > 1:
            message = "Выбери тип векселя:"
            buttons.add(types.InlineKeyboardButton(text="Разделить сумму на всех", callback_data="settype/2/"+str(oper.id)))
            buttons.add(types.InlineKeyboardButton(text="Сумма с каждого", callback_data="settype/3/"+str(oper.id)))
        else:
            message = "Чтобы закончить вексель - ответь на это сообщение в формате Сумма + комментарий\nПример: 1234.34 За еблю с гнилозубом"
    elif forcommand == 'finish':
        message = "Чтобы закончить вексель - ответь на это сообщение в формате Сумма + комментарий\nПример: 1234.34 За еблю с гнилозубом"

    buttons.row(endbuttons)
    return message

buildButtonsSet(Operations(0,[1],2,12,))