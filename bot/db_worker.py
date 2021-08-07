import os
from typing import Tuple, Dict, List

import mysql.connector as connector

DB_PASSWORD = os.getenv('DB_PASSWORD')
HOST = 'bot-sql-server'
HOST = 'localhost'
DB_PASSWORD = 'vekselbotpassword'


def connect():
    conn = connector.connect(host=HOST
                             , database='veksel'
                             , user='root'
                             , password=DB_PASSWORD
                             , auth_plugin='mysql_native_password')
    return conn


def insert(table: str, column_values: Dict):
    conn = connect()
    cursor = conn.cursor()
    columns = ', '.join(column_values.keys())
    values = tuple(column_values.values())
    placeholder = ', '.join(['%s'] * len(column_values.keys()))
    cursor.execute(f"insert into {table}"
                   f"({columns}) "
                   f"values({placeholder})"
                   , values)
    conn.commit()
    lastrow = cursor.lastrowid
    cursor.close()
    conn.close()
    return lastrow


def update(table: str, id: int, column_values: Dict):
    conn = connect()
    cursor = conn.cursor()
    columns = column_values.keys()
    values = tuple(column_values.values())
    columns_with_placeholders = ', '.join(x + ' = %s' for x in columns)
    cursor.execute(f"update {table}"
                   f"   set {columns_with_placeholders}"
                   f" where ID = {id}"
                   , values)
    conn.commit()
    cursor.close()
    conn.close()


def delete(table: str, row_id: int):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(f"delete from {table} where ID={row_id}")
    conn.commit()
    cursor.close()
    conn.close()


def fetchall(table: str, columns: List[str]) -> List[Tuple]:
    conn = connect()
    cursor = conn.cursor()
    columns_joined = ', '.join(columns)
    cursor.execute(f"select {columns_joined} from {table}")
    rows = cursor.fetchall()
    result = []
    cursor.close()
    conn.close()
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def isExists(table: str, id: int) -> bool:
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(f"select 1 from {table} where ID = {id}")
    if cursor.fetchall():
        res = True
    else:
        res = False
    cursor.close()
    conn.close()
    return res


def isExistsRelation(chat_id: int, user_id: int) -> bool:
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(f"select 1 from UserChatRelation"
                   f" where ChatID = {chat_id}"
                   f"   and UserID = {user_id}")
    if cursor.fetchall():
        res = True
    else:
        res = False
    cursor.close()
    conn.close()
    return res


def getUsersForChat(id: int) -> List[Dict]:
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(f"select u.ID, u.Brief"
                   f"  from UserChatRelation cr"
                   f"  join Users u"
                   f"    on u.ID = cr.UserID"
                   f" where cr.ChatID = {id}")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def getOperationsForChat(id: int) -> List[Dict]:
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(f"select ID, UFrom, UTo, Qty, Comment, ChatID"
                   f"  from Operation"
                   f" where ChatID = {id}")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def getOperationByID(id: int) -> Dict:
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(f"select ID, UFrom, UTo, Qty, Comment, ChatID"
                   f"  from Operation"
                   f" where ID = {id}")
    res = cursor.fetchone()
    cursor.close()
    conn.close()
    return res


def getOperationsBuf(id: int) -> Dict:
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(f"select ID, UserFrom, UserTo, Qty, Comment, Type, ChatId from Operations where ID = {id}")
    res = cursor.fetchone()
    cursor.close()
    conn.close()
    return res


def getOperationsIdList(chat_id: int, user_id: int = 0) -> List[Dict]:
    conn = connect()
    cursor = conn.cursor()
    if user_id != 0:
        cursor.execute(f'select ID as ID'
                       f'  from Operation'
                       f' where (UFrom = {user_id}'
                       f'    or UTo = {user_id})'
                       f'   and ChatID = {chat_id}'
                       f' order by ID')
    else:
        cursor.execute(f'select ID as ID'
                       f'  from Operation'
                       f' where ChatID = {chat_id}'
                       f' order by ID')
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res


def getOperationText(operation_id: int) -> Dict:
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(f"select u1.Brief, u2.Brief, o.Qty, o.Comment"
                   f"  from Operation o"
                   f"  join Users u1"
                   f"    on u1.ID = o.UFrom"
                   f"  join Users u2"
                   f"    on u2.ID = o.UTo "
                   f" where o.ID = {operation_id}")
    res = cursor.fetchone()
    cursor.close()
    conn.close()
    dt = {'UserFrom': res[0], 'UserTo': res[1], 'Qty': float(res[2]), 'Comment': res[3]}
    return dt


def massDeleteOperations(chat_id: int):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(f"delete from Operation where ChatID={chat_id}")
    conn.commit()
    cursor.close()
    conn.close()


def getSuperSaldo(chat_id: int):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(f"select ur.UserID"
                   f"      ,sum(case when o.UTo = ur.UserID "
                   f"                then -o.Qty else o.Qty end) "
                   f"  from UserChatRelation ur "
                   f"  join Operation o "
                   f"    on o.ChatID = ur.ChatID "
                   f"   and (ur.UserID in (o.UFrom, o.UTo)) "
                   f" where ur.ChatID = {chat_id}"
                   f" group by ur.UserID")
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res
