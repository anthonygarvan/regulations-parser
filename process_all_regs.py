import os
from Queue import Queue, Empty
from threading import Thread
import json
from time import sleep
import sys
from getopt import getopt
from random import shuffle, seed

def worker():
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
		print "processing %s, part %s, approximately %d left" % (title, part, q.qsize())
		os.system('eregs pipeline %s %s %s --only-latest | tee parse.log' % (title_number, part, output_dir))
		q.task_done()

if os.path.exists('parse.log'):
	os.remove('parse.log')

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
	t = Thread(target=worker)
	t.daemon = True
	t.start()

q.join()       # block until all tasks are done