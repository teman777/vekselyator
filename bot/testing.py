import db_worker as db


print(db.fetchall('Operations', ['ID', 'UserFrom']))