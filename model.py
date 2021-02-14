import db_worker as db

class User:
    def __init__(self, id: int, brief: str):
        self.id = id
        self.brief = brief

    def save(self):
        user = db.cursor.execute(f"select 1 from Users where ID = {self.id}")
        exists = user.fetchall()
        if not exists:
            db.insert('Users', {'ID': self.id})


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
    def __init__(self, id: int):
        self.id = id 
    
    def save(self):
        chat = db.cursor.execute(f"select 1 from Chats where ID = {self.id}")
        exists = chat.fetchall()
        if not exists:
            db.insert('Chats',{'ID': self.id})
