import sqlite3
import os
from typing import Tuple, Dict, List

conn = sqlite3.connect('veksel.db')
cursor = conn.cursor()

def _init_db():
    with open("createdb.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()

def checkdb():
    cursor.execute("select name from sqlite_master "
                   "where type='table' and name='Users'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()

def insert(table: str, column_values: Dict):
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholder = ', '.join("?" * len(column_values.keys()))
    cursor.executemany(f"insert into {table}"
                       f"({columns})"
                       f"values({placeholder})"
                       ,values)
    conn.commit()

def delete(table: str, row_id:int) -> None:
    row_id = int(row_id)
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

checkdb()








