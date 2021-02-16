import db_worker as db


print(db.fetchall('Operation',['ID', 'UTo', 'UFrom', 'Comment', 'Qty', 'ChatID']))

