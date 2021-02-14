import sqlite3
import os
from typing import Tuple, Dict, List
import model

import db_worker as db


print(db.fetchall('Operations', ['ID', 'Qty']))


