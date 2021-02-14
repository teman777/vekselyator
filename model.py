import db_worker as db
import json
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



class Operations:
    def __init__(self, id:int = 0 ,userTo: List[int] = [], userFrom: int = 0, qty: float = 0, chatId: int = 0, comment:str = '', type: int = 1):
        self.userTo = userTo
        self.userFrom = userFrom
        self.qty = qty
        self.chatId = chatId
        self.comment = comment
        self.type   = type
        self.id = id
    def save(self):
        db.insert('Operations', {'ChatId': self.chatId, 'UserFrom': self.userFrom, 'UserTo': str(self.userTo), 'Qty': self.qty, 'Type': self.type, 'Comment': self.comment})
        self.id = db.cursor.lastrowid
        
        

class Operation:
    def __init__(self ,userTo: int, userFrom: int, qty: float, chatId: int, comment:str, id: int = 0):
        self.id = id
        self.userTo = userTo
        self.userFrom = userFrom
        self.qty = qty
        self.chatId = chatId
        self.comment = comment

    def save(self):
        operation = db.cursor.execute(f"select 1 from Operation where ID = {self.id}")
        exists = operation.fetchall()
        if not exists or self.id == 0:
            db.insert('Operation', {'UFrom': self.userFrom, 'UTo': self.userTo, 'Qty':self.qty, 'Comment': self.comment, 'ChatID': self.chatId})
            self.id = db.cursor.lastrowid
        elif exists:
            db.update('Operation', self.id ,{'UFrom': self.userFrom, 'UTo': self.userTo, 'Qty':self.qty, 'Comment': self.comment, 'ChatID': self.chatId})

class Chat:
    def __init__(self, id: int, users: List[User] = None, operations: List[Operation] = None):
        self.id = id
        if users == None:
            self.users = [] 
        else:
            self.users = users
        if operations == None:
            self.operations = [] 
        else:
            self.operations = operations
    
    def addUser(self, user: User):
        if user not in self.users:
            self.users.append(user)

    def addOperation(self, operation: Operation):
        self.operations.append(operation)
    
    def load(self):
        self.users = []
        self.operations = []
        us = db.getUsersForChat(self.id)
        op = db.getOperationsForChat(self.id)
        for u in us:
            self.users.append(User(u[0], u[1]))
        for o in op:
            self.operations.append(Operation(id=o[0],userFrom=o[1], userTo=o[2], qty=o[3], comment=o[4], chatId = self.id))
    
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
        for oper in self.operations:
            oper.save()
            
chats = []

def init():
    chats = []
    chatdb = db.fetchall('Chats', ['ID'])
    for chat in chatdb:
        chatsav = Chat(id=chat['ID'])
        chatsav.load()
        chats.append(chatsav)

def update():
    init()

def getChatById(id: int) -> Chat:
    for i in chats:
        if i.id == id:
            return i
    return Chat(id=id)
         

init()


