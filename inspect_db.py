import sqlite3

conn = sqlite3.connect('articles.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM articles LIMIT 5")
for row in cursor.fetchall():
    print(row)
conn.close()