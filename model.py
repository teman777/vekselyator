import db_worker as db
from typing import List, Tuple

class User:
    def __init__(self, id: int, brief: str):
        self.id = id
        self.brief = brief

    def save(self):
        user = db.cursor.execute(f"select 1 from Users where ID = {self.id}")
        exists = user.fetchall()
        if not exists:
            db.insert('Users', {'ID': self.id, 'Brief': self.brief})


class Operation:
    def __init__(self, id: int, userTo: int, userFrom: int, qty: float, chatId: int):
        self.id = id
        self.userTo = userTo
        self.userFrom = userFrom
        self.qty = qty
        self.chatId = chatId

    def save(self):
        operation = db.cursor.execute(f"select 1 from Operation where ID = {self.id}")
        exists = operation.fetchall()
        if not exists:
            db.insert('Operation', {'ID': self.id})

class Chat:
    def __init__(self, id: int, users: List[User] = None):
        self.id = id
        if users == None:
            self.users = [] 
        else:
            self.users = users
    
    def addUser(self, user: User):
        if user not in self.users:
            self.users.append(user)
    
    def save(self):
        chat = db.cursor.execute(f"select 1 from Chats where ID = {self.id}")
        exists = chat.fetchall()
        if not exists:
            db.insert('Chats',{'ID': self.id})
        for user in self.users:
            user.save()
            relexist = db.cursor.execute(f"select 1 from UserChatRelation"
                                         f" where ChatID = {self.id}"
                                         f"   and UserID = {user.id}")
            if not relexist.fetchall():
                db.insert('UserChatRelation', {'ChatID':self.id, 'UserID':user.id})
            


operations = []
chats = []

def init():
    chatdb = db.fetchall('Chats', ['ID'])
    for chat in chatdb:
        chatsav = Chat(id=chat['ID'])
        userschatdb = db.getUsersForChat(id=chatsav.id)
        for user in userschatdb:
            usersav = User(id=user[0], brief=user[1])
            chatsav.addUser(usersav)
        chats.append(chatsav)


init()


