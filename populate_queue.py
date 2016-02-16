import json
import sqlite3

all_parts = json.load(open('all_parts.json'))

conn = sqlite3.connect('queue.db')
cursor = conn.cursor()

try:
	cursor.execute('DROP TABLE queue')
except:
	pass
cursor.execute('CREATE TABLE queue (title text, part text, status text)')

for title in all_parts:
	for part in all_parts[title]:
		cursor.execute("INSERT INTO queue VALUES('%s', '%s', '%s')" % (title, part, 'NOT_STARTED'))

conn.commit()
cursor.execute("SELECT COUNT(*) from queue")

print '%d jobs added' % cursor.fetchone()[0]
