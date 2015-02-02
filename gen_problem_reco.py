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

print "Starting generating problem based reco : ", time.strftime("%d-%m-%Y %H:%M")

#config
cfs_max_score = 3000
lower_threshold = 10
upper_threshold = 10
number_to_recommend = 5

conn = db.connect()
cursor = conn.cursor()

sql = "SELECT (correct_count)/(attempt_count) as difficulty FROM problem \
			WHERE MID(pid,1,3) = \"erd\" AND attempt_count>5"
erd_problem_difficulty = db.read(sql, cursor)

sql = "SELECT uid, erd_score/(SELECT MAX(erd_score) FROM user), cfs_score/(SELECT MAX(cfs_score) FROM user) FROM user"
user_result = db.read(sql, cursor)

sql = "SELECT pid FROM problem WHERE MID(pid, 1, 3)='erd'"
problem_result = db.read(sql, cursor)

count = 0
for i in problem_result:
	pid = str(i[0])
	a = problem(pid = pid, erd_problem_difficulty = erd_problem_difficulty, cfs_max_score = cfs_max_score, lower_threshold = lower_threshold, upper_threshold = upper_threshold, number_to_recommend = number_to_recommend)
	for j in user_result:

		#erdos recommendations
		a.find_similar_erdos(uid = str(j[0]), user_difficulty = float(j[1]))
		count+=1
		print count
		if(count%100 == 0):
			print count," insertions done"
		# a.find_similar_erdos(status = 1, uid = str(j[0]), user_difficulty = float(j[1]))
		#cfs recommendations
		
		# a.find_similar_cfs(status = 0, uid = str(j[0]), user_difficulty = float(j[2]))
		# a.find_similar_cfs(status = 1, uid = str(j[0]), user_difficulty = float(j[2]))
	print pid, " pid finished"	
print "Finished generating problem based reco : ", time.strftime("%d-%m-%Y %H:%M")