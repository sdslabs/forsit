import time 

try:
    from problem import problem
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
remote_conn = db.connect('remote')
remote_cursor = remote_conn.cursor()

sql = "SELECT (correct_count)/(attempt_count) as difficulty FROM problem \
			WHERE MID(pid,1,3) = \"erd\" AND attempt_count>5"
erd_problem_difficulty = db.read(sql, cursor)

sql = "SELECT uid, erd_score/(SELECT MAX(erd_score) FROM user), cfs_score/(SELECT MAX(cfs_score) FROM user) FROM user "
user_result = db.read(sql, cursor)

sql = "UPDATE problem_reco SET is_deleted = 1"
db.write(sql, cursor, conn)

sql = "CREATE table IF NOT EXISTS problem_reco_new LIKE problem_reco"
db.write(sql, cursor, conn)

sql = "SELECT pid FROM problem WHERE MID(pid, 1, 3)='erd' "
problem_result = db.read(sql, cursor)

count = 0

sql = "INSERT INTO problem_reco_new (uid, base_pid, status, reco_pid, score, time_created, time_updated, state, is_deleted) VALUES "

for i in problem_result:
	pid = str(i[0])
	a = problem(pid = pid, erd_problem_difficulty = erd_problem_difficulty, conn = conn, cfs_max_score = cfs_max_score, lower_threshold = lower_threshold, upper_threshold = upper_threshold, number_to_recommend = number_to_recommend, batchmode = 1)
	for j in user_result:

		#erdos recommendations
		sql+=a.find_similar_erdos(uid = str(j[0]), user_difficulty = float(j[1]))
		count+=1
		# print count
		if(count%20000 == 0):
			sql = sql[:-2]
			if(sql[-1] == ')'):
				db.write(sql, remote_cursor, remote_conn)
			sql = "INSERT INTO problem_reco_new (uid, base_pid, status, reco_pid, score, time_created, time_updated, state, is_deleted) VALUES "
			print count," insertions done"


if(sql[-1] == ')'):
	db.write(sql, remote_cursor, remote_conn)
	sql = "INSERT INTO problem_reco_new (uid, base_pid, status, reco_pid, score, time_created, time_updated, state, is_deleted) VALUES "
	print count," insertions done"			

print "Finished generating problem based reco : ", time.strftime("%d-%m-%Y %H:%M")

# # create table new_table like old_table;
sql = "RENAME table problem_reco to problem_reco_old, problem_reco_new to problem_reco"
print sql
db.write(sql, remote_cursor, remote_conn)
sql = "DROP table problem_reco_old"
print sql
db.write(sql, remote_cursor, remote_conn)