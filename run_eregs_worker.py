import sqlite3
import os

conn = sqlite3.connect('queue.db')
cursor = conn.cursor()

while(True):
	cursor.execute("SELECT title, part FROM queue WHERE status = 'NOT_STARTED' LIMIT 1")
	result = cursor.fetchone()

	if result == None:
		break
	(title, part) = result

	title_number = title.split('-')[1]

	cursor.execute("UPDATE queue SET status='STARTED' WHERE title='%s' AND part='%s'" % (title, part))
	conn.commit()

	output_dir = 'parsed/' + title

	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	try:
		os.system('eregs pipeline %s %s %s --only-latest >> parse.log' % (title_number, part, output_dir))
	except Exception as e:
		print 'error: could not parse regulation TITLE=%s, PART=%s' % (title_number, part)
		print e