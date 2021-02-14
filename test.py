import sqlite3
import os
from typing import Tuple, Dict, List

def update(table: str, id: int ,column_values: Dict):
    upd = column_values.keys()
    upd2 = []
    for up in upd:
        upd2.append(up + ' = ?')
    columns = ', '.join(upd2)
    print(columns)

update('Upr', 2, {'ID': 1 , 'Name':'Str'})
