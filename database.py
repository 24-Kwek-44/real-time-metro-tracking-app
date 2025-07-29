import sqlite3

db = sqlite3.connect('db.sqlite')

db.execute('''CREATE TABLE IF NOT EXISTS station(
    station_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    route TEXT NOT NULL,

)''')

db.execute('''
CREATE TABLE IF NOT EXISTS fare_matrix (
    origin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER,
    price REAL
)
''')    

cursor = db.cursor()


db.commit()
db.close()  
