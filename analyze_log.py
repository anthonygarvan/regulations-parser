import re
from collections import Counter
log = open('history_run.log')
from pprint import pprint

c = Counter()
for line in log:
	if "Error" in line or "Exception" in line:
		c.update([line])

log.close()
most_common = c.most_common(15)

results = open('common_errors_history.csv', 'w')
results.write('Error,Count\n')
for error, count in most_common:
	results.write('"%s",%d\n' % (error, count))

results.close()
print "output at common_errors.csv"