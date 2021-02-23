import mysql.connector as connector
import os
from typing import Tuple, Dict, List

db_password = os.getenv('DB_PASSWORD')
if db_password == None:
    db_password = 'vekselbotpassword'

conn = connector.connect(host='localhost'
                        ,database='veksel'
                        ,user='root'
                        ,password=db_password
                        ,auth_plugin='mysql_native_password')
cursor = conn.cursor()

def insert(table: str, column_values: Dict):
    columns = ', '.join(column_values.keys())
    values = tuple(column_values.values())
    placeholder = ', '.join(['%s'] * len(column_values.keys()))
    cursor.execute(f"insert into {table}"
                   f"({columns}) "
                   f"values({placeholder})"
                   ,values)
    conn.commit()


def update(table: str, id: int ,column_values: Dict):
    columns = column_values.keys()
    values  = tuple(column_values.values())
    columns_with_placeholders = ', '.join(x + ' = %s' for x in columns)
    cursor.execute(f"update {table}"
                   f"   set {columns_with_placeholders}"
                   f" where ID = {id}"
                   ,values)
    conn.commit()

def delete(table: str, row_id:int):
    cursor.execute(f"delete from {table} where ID={row_id}")
    conn.commit()

def fetchall(table: str, columns: List[str]) -> List[Tuple]:
    columns_joined = ', '.join(columns)
    cursor.execute(f"select {columns_joined} from {table}")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result

def isExists(table: str, id: int) -> bool:
    cursor.execute(f"select 1 from {table} where ID = {id}")
    if cursor.fetchall():
        res = True
    else:
        res = False
    return res

def isExistsRelation(chat_id: int, user_id: int) -> bool:
    cursor.execute(f"select 1 from UserChatRelation"
                   f" where ChatID = {chat_id}"
                   f"   and UserID = {user_id}")
    if cursor.fetchall():
        res = True
    else:
        res = False
    return res

def getUsersForChat(id: int) -> List[Dict]:
    cursor.execute(f"select u.ID, u.Brief"
                   f"  from UserChatRelation cr"
                   f"  join Users u"
                   f"    on u.ID = cr.UserID"
                   f" where cr.ChatID = {id}")
    rows = cursor.fetchall()
    return rows

def getOperationsForChat(id: int) -> List[Dict]:
    cursor.execute(f"select ID, UFrom, UTo, Qty, Comment"
                   f"  from Operation"                 
                   f" where ChatID = {id}")
    rows = cursor.fetchall()
    return rows


