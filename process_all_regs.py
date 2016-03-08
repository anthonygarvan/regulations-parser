import os
from Queue import Queue, Empty
from threading import Thread
import json
from time import sleep
import sys
from getopt import getopt
from random import shuffle, seed

def worker(thread_id):
	logfile = 'parse_%d.log' % thread_id
	if os.path.exists(logfile):
		os.remove(logfile)
	while True:
		try: 
			title, part = q.get(False)
		except Empty:
			break
		title_number = title.split('-')[1]
		output_dir = 'parsed/' + title

		output_dir = 'parsed/' + title
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)
		os.system("(echo processing %s, part %s, approximately %d left && date) >> status.log >> %s" % (title, part, q.qsize(), logfile))
		cmd = 'timeout 120 eregs pipeline %s %s %s --only-latest 2>&1 | tee -a %s' % (title_number, part, output_dir, logfile)
		print cmd
		os.system(cmd)
		q.task_done()

num_worker_threads = 4
opts, args = getopt(sys.argv[1:], "t:d")
debug = False
for opt, val in opts:
	if opt == '-t':
		num_worker_threads = int(val)
	if opt == '-d':
		debug = True

all_parts = json.load(open('all_parts.json'))

q = Queue()

job_queue = []
if debug:
	for title in all_parts.keys()[:3]:
		for part in all_parts[title][:3]:
			job_queue.append((title, part))
else:
	for title in all_parts:
		for part in all_parts[title]:
			job_queue.append((title, part))

seed(42)
shuffle(job_queue)

for item in job_queue:
	q.put(item)

for i in range(num_worker_threads):
	t = Thread(target=worker, args=[i])
	t.daemon = True
	t.start()

q.join()       # block until all tasks are done
os.system('cat parse_*.log > all_parses.log')