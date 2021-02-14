import db_worker as db


print(db.fetchall('Users', ['ID', 'Brief']))

