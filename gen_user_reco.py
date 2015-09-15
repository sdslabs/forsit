import time 

try:
	from problem import problem
except ImportError as exc:
	print("Error: failed to import settings module ({})".format(exc))

try:
	from user import user
except ImportError as exc:
	print("Error: failed to import settings module ({})".format(exc))

try:
	import db
except ImportError as exc:
	print("Error: failed to import settings module ({})".format(exc))

print "Starting generating user based reco : ", time.strftime("%d-%m-%Y %H:%M")

#config
options = {}
options['tag_based'] = 0
options['normalize'] = 0
options['sample_data'] = 0
options['penalize'] = 1

conn = db.connect()
cursor = conn.cursor()

sql = "SELECT erd_handle, cfs_handle FROM user"
result = db.read(sql, cursor)
for u in result:
	a = user(erd_handle = u[0][3:], cfs_handle = u[1][3:], options = options)
	a.reco_algo(1)
	print 'Recommendation generated for ' + u[0][3:]

print "Finished generating user based reco : ", time.strftime("%d-%m-%Y %H:%M")