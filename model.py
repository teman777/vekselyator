import db_worker as db

class User:
    def __init__(self, id: int, brief: str):
        self.id = id
        self.brief = brief

class Operation:
    def __init__(self, id: int, userTo: int, userFrom: int, qty: float, chatId: int):
        self.id = id
        self.userTo = userTo
        self.userFrom = userFrom
        self.qty = qty
        self.chatId = chatId

class Chat:
    def __init__(self, id: int):
        self.id = id 



