import db_worker as db
from typing import List, Tuple, Dict
from datetime import datetime

class User:
    def __init__(self, id: int, brief: str):
        self.id = id
        self.brief = brief

    def save(self):
        exists = db.isExists('Users', self.id)
        if not exists:
            db.insert('Users', {'ID': self.id, 'Brief': self.brief})
        else:
            db.update('Users', self.id ,{'Brief': self.brief})



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
        exists = db.isExists('Operations', self.id)
        if not exists:
            lastid = db.insert('Operations', {'ChatId': self.chatId, 'UserFrom': self.userFrom, 'UserTo': str(self.userTo), 'Qty': self.qty, 'Type': self.type, 'Comment': self.comment})
            self.id = lastid
        else:
            db.update('Operations', self.id, {'UserTo': str(self.userTo), 'UserFrom': self.userFrom, 'Qty': self.qty, 'Type': self.type, 'Comment': self.comment, 'ChatId':self.chatId})

    def delete(self):
        if self.id != 0:
            db.delete('Operations', self.id)

    def resolve(self):
        calc_qty = self.qty
        if self.type == 2:
            calc_qty = calc_qty / len(self.userTo)
        elif self.type in (1,3):
            calc_qty = self.qty
        for i in self.userTo:
            if i != self.userFrom:
                operation = Operation(userTo=i,userFrom=self.userFrom,qty=calc_qty,chatId=self.chatId,comment=self.comment)
                operation.save()

        

class Operation:
    def __init__(self ,userTo: int, userFrom: int, qty: float, chatId: int, comment:str, id: int = 0):
        self.id = id
        self.userTo = userTo
        self.userFrom = userFrom
        self.qty = qty
        self.chatId = chatId
        self.comment = comment
        self.date = datetime.now()

    def delete(self):
        if self.id != 0:
            db.delete('Operation', self.id)

    def save(self):
        exists = db.isExists('Operation', self.id)
        if not exists or self.id == 0:
            lastid = db.insert('Operation', {'UFrom': self.userFrom, 'UTo': self.userTo, 'Qty':self.qty, 'Comment': self.comment, 'ChatID': self.chatId, 'Date': self.date})
            self.id = lastid
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
            self.operations.append(Operation(id=int(o[0]),userFrom=int(o[1]), userTo=int(o[2]), qty=float(o[3]), comment=o[4], chatId = int(self.id)))
    
    def save(self):
        exists = db.isExists('Chats', self.id)
        if not exists:
            db.insert('Chats',{'ID': self.id})
        for user in self.users:
            user.save()
            relexist = db.isExistsRelation(self.id, user.id)
            if not relexist:
                db.insert('UserChatRelation', {'ChatID':self.id, 'UserID':user.id})
        for oper in self.operations:
            oper.save()
            


def getChatById(id: int) -> Chat:
    print(id)
    chat = Chat(id)
    chat.load()
    return chat
    

def getOperations(id: int) -> Operations:
    if id != 0:
        res = db.getOperationsBuf(id)
        if res[2] == '[]':
            userTo = []
        else:
            userTo = [int(x) for x in res[2].replace('[', '').replace(']', '').replace(' ', '').split(',')]
        return Operations(id=res[0], userFrom= res[1], userTo = userTo
                    , qty=res[3], comment=res[4], type= res[5], chatId = res[6])
    return None

def getOperation(id: int) -> Operation:
    if id != 0:
        res = db.getOperationByID(id)
        return Operation(id=res[0], userFrom= res[1], userTo = res[2]
                    , qty=res[3], comment=res[4], chatId = res[5])
    return None


def getOperationsIdList(chat: Chat, user_id: int = 0) -> List[int]:
    res = []
    id_list = db.getOperationsIdList(chat_id = chat.id, user_id = user_id)
    for id in id_list:
        res.append(id[0])
    return res

def getOperationText(operation_id: int) -> Dict:
    dt = db.getOperationText(operation_id)
    return dt


