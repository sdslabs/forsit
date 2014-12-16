try:
    import requests
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    from base import base
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    from problem import problem
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    from math import exp
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import operator
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import db
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import math
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import graph
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

#generated using http://codeforces.com/blog/entry/3064

# 2600+	Red	International grandmaster	1
# 2200 - 2599	red	Grandmaster	1
# 2050 - 2199	Orange	International master	1
# 1900 - 2049	Orange	Master	1
# 1700 - 1899	Violet	Candidate master	1
# 1500 - 1699	Blue	Expert	2
# 1350 - 1499	Green	Specialist	2
# 1200 - 1349	Green	Pupil	2
# 0 - 1199	Gray	Newbie	2

rating = {}
rank = {}

rank['international grandmaster'] = 1
rank['grandmaster'] = 0.9
rank['international master'] = 0.8
rank['master'] = 0.7
rank['candidate master'] = 0.6
rank['expert'] = 0.5
rank['specialist'] = 0.4
rank['pupil'] = 0.3
rank['newbie'] = 0.2

rating['international grandmaster'] = (2600)
rating['grandmaster'] = (2200,2599)
rating['international master'] = (2050,2199)
rating['master'] = (1900,2049)
rating['candidate master'] = (1700,1899)
rating['expert'] = (1500,1699)
rating['specialist'] = (1350,1499)
rating['pupil'] = (1200,1349)
rating['newbie'] = (0,1199)

class user(base):
	
	'''
	- *uid* : user id. To serve as default value of *cfs_handle* and *erd_handle*
	- *app_name* : Name of the app ie forsit
	- *cfs_handle* : User's handle on Codeforces.
	- *erd_handle* : User's handle on Erdos.
	'''

		
	def __init__(self, uid, app_name = "forsit", cfs_handle = '', erd_handle = ''):
		self.training_problems = {}
		self.uid = str(uid)
		self.cfs_url = "http://codeforces.com/api/user.status"
		self.erd_url = "http://erdos.sdslabs.co/users/"
		if(cfs_handle == ''):
			cfs_handle = self.uid
		if(erd_handle == ''):
			erd_handle = self.uid
		self.cfs_handle = str(cfs_handle)
		self.erd_handle = str(erd_handle)
		self.conn=db.connect(app_name)
		self.cursor = self.conn.cursor()
		self.calculate_difficulty()

	def fetch_user_info_cfs(self):
		'''
		|  Fetch User's information from Codeforces
	    '''
		payload = {}
		payload['handles'] = self.cfs_handle
		url = "http://codeforces.com/api/user.info"
		r = requests.get(url, params=payload)
		if(r.status_code != 200 ):
			print r.status_code, " returned from ", r.url
		else:
			res = r.json()['result'][0]
			self.rank = str(res['rank'])
			self.rating = str(res['rating'])
			self.score  = rating[self.rank]

	def fetch_user_info_erd(self):
		'''
		|  Fetch User's information from Erdos
	    '''
		url = self.erd_url + self.erd_handle + ".json"
		r = requests.get(url)
		if(r.status_code != 200 ):
			print r.status_code, " returned from ", r.url
		else:
			solved_problems = r.json()['solved_problems']

	def fetch_user_list_cfs(self):
		'''
		|  Fetch List of all the users from Codeforces
		|  @todo : move to scrapper module 
	    '''
		self.cfs_users = []
		url = "http://codeforces.com/api/user.ratedList?activeOnly=true"
		r = requests.get(url)
		if(r.status_code != 200 ):
			print r.status_code, " returned from ", r.url
		else:
			result = r.json()['result']
			for i in result:
				self.cfs_users.append(i['handle'])

	def fetch_user_list_erd(self):
		'''
		|  Fetch List of all the users from Erdos
		|  @todo : move to scrapper module 
	    '''
		self.erd_users = []
		url = "http://erdos.sdslabs.co/users.json"
		r = requests.get(url)
		if(r.status_code != 200 ):
			print r.status_code, " returned from ", r.url
		else:
			result = r.json()['list']
			for i in result:
				self.erd_users.append(i['username'])

	def fetch_user_activity_cfs(self, handle=""):
		'''
		|  Fetch User's activity from Codeforces
		|  @todo : move to scrapper module 
	    '''
		if handle == "":
			handle = self.cfs_handle
		payload = {}
		payload['handle'] = handle
		handle = 'cfs' + handle
		sql = "SELECT created_at FROM activity WHERE handle = \'" + handle + "\' ORDER BY created_at DESC LIMIT 1;"
		res = db.read(sql, self.cursor)
		if res == ():
			last_activity = 0
		else:
			last_activity = res[0][0]
		last_activity = int(last_activity)
		r = requests.get(self.cfs_url, params=payload)
		if(r.status_code != 200 ):
			print r.status_code, " returned from ", r.url
		else:
			result = r.json()['result']
			result.reverse()
			for act in result:
				if int(act['creationTimeSeconds']) > last_activity:
					sql = "SELECT * FROM activity WHERE pid = \'cfs" + str(act['problem']['contestId']) + str(act['problem']['index']) + "\' AND handle = \'" + handle + "\'"
					check = db.read(sql, self.cursor)
					difficulty = 0
					if act['verdict'] == "OK":
						status = 1
					else:
						status = 0
					if check == ():
						sql = "INSERT INTO activity (handle, pid, attempt_count, status, difficulty, created_at) VALUES ( \'" + handle + "\', \'cfs" + str(act['problem']['contestId']) + str(act['problem']['index']) + "\', '1', " + str(status) + ", " + str(difficulty) + ", " + str(act['creationTimeSeconds']) +" )"
						db.write(sql, self.cursor, self.conn)
					else:
						sql = "UPDATE activity SET attempt_count = attempt_count + 1, status = " + str(status) + ", difficulty = " + str(difficulty) + ", created_at = " + str(act['creationTimeSeconds']) + " WHERE pid = \'cfs" + str(act['problem']['contestId']) + str(act['problem']['index']) + "\' AND handle = \'" + handle + "\'"
						db.write(sql, self.cursor, self.conn)

	# @profile					
	def fetch_all_user_activity_cfs(self, handle=""):
		'''
		|  Fetch User's activity from Codeforces
		|  It is different from *fetch_user_activity_cfs()* as it logs each submission as a seperate entry to plot the concept trail
		|  @todo : move to scrapper module 
	    '''
		difficulty = 0
		if handle == "":
			handle = self.cfs_handle
		payload = {}
		payload['handle'] = handle
		handle = 'cfs' + handle
		sql = "SELECT created_at FROM activity_concept WHERE handle = \'" + handle + "\' ORDER BY created_at DESC LIMIT 1;"
		res = db.read(sql, self.cursor)
		if res == ():
			last_activity = 0
		else:
			last_activity = int(res[0][0])
		r = requests.get(self.cfs_url, params=payload)
		if(r.status_code != 200 ):
			print r.status_code, " returned from ", r.url
		else:
			result = r.json()['result']
			#profile reverse operation 
			result.reverse()
			count = 1
			sql = "INSERT INTO activity_concept (handle, pid, attempt_count, status, difficulty, created_at) VALUES "
			for act in result:
				#checking for min of the 2 values as for some cases, codeforces api is returning absured results for relatice time
				relative_time = min(7200, int(act['relativeTimeSeconds']))
				submission_time = int(act['creationTimeSeconds']) + relative_time
				if submission_time > last_activity:
					status = str(act['verdict'])
					if(status == "OK"):
						status = "1"
					else:
						status = "0"

					sql+="(\'" + handle + "\', \'cfs" + str(act['problem']['contestId']) + str(act['problem']['index']) + "\', '1', " + status + ", " + str(difficulty) + ", " + str(submission_time) +" ), "
					count+=1;
					if(count%5000 == 0):
						sql = sql[:-2]
						db.write(sql, self.cursor, self.conn)
						print count, " entries made in the database"
						sql = "INSERT INTO activity_concept (handle, pid, attempt_count, status, difficulty, created_at) VALUES " 
				else:
					break
			# print sql
			# print count
			if(sql[-2] == ","):
				sql = sql[:-2]
				db.write(sql, self.cursor, self.conn)							
	
			
			
	def fetch_user_activity_erd(self, handle=""):
		'''
		|  Fetch User's activity from Erdos
		|  @todo : move to scrapper module 
	    '''
		if handle == "":
			handle = self.erd_handle
		url = "http://erdos.sdslabs.co/activity/users/" + handle + ".json"
		handle = 'erd' + handle
		sql = "SELECT created_at FROM activity WHERE handle = \'" + handle + "\' ORDER BY created_at DESC LIMIT 1;"
		res = db.read(sql, self.cursor)
		if res == ():
			last_activity = 0
		else:
			last_activity = res[0][0]
		last_activity = int(last_activity)
		r = requests.get(url)
		if(r.status_code != 200 ):
			print r.status_code, " returned from ", r.url
		else:
			result = r.json()['list']
			result.reverse()
			for act in result:
				if int(act['created_at']) > last_activity:
					sql = "SELECT * FROM activity WHERE pid = \'erd" + act['problem_id'] + "\' AND handle = \'" + handle + "\'"
					check = db.read(sql, self.cursor)
					difficulty = 0
					if check == ():
						sql = "INSERT INTO activity (handle, pid, attempt_count, status, difficulty, created_at) VALUES ( \'" + handle + "\', \'erd" + act['problem_id'] + "\', '1', " + str(act['status']) + ", " + str(difficulty) + ", " + str(act['created_at']) + " )"
						db.write(sql, self.cursor, self.conn)
					else:
						sql = "UPDATE activity SET attempt_count = attempt_count + 1, status = " + str(act['status']) + ", difficulty = " + str(difficulty) + ", created_at = " + str(act['created_at']) + " WHERE pid = \'erd" + act['problem_id'] + "\' AND handle = \'" + handle + "\'"
						db.write(sql, self.cursor, self.conn)

	def calculate_difficulty(self):
		sql = "UPDATE activity SET difficulty = 3 WHERE status = 0"
		db.write(sql, self.cursor, self.conn)
		sql = "UPDATE activity SET difficulty = 0 WHERE status = 1"
		db.write(sql, self.cursor, self.conn)
		sql = "UPDATE activity SET difficulty = difficulty + 1 WHERE attempt_count <= 2"
		db.write(sql, self.cursor, self.conn)
		sql = "UPDATE activity SET difficulty = difficulty + 2 WHERE attempt_count >= 3 AND attempt_count <= 5"
		db.write(sql, self.cursor, self.conn)
		sql = "UPDATE activity SET difficulty = difficulty + 3 WHERE attempt_count > 5;"
		db.write(sql, self.cursor, self.conn)
		self.create_difficulty_matrix()

	def fetch_user_activity_all(self):
		self.fetch_user_list_erd()
		self.fetch_user_list_cfs()
		for handle in self.erd_users:
			self.fetch_user_activity_erd(handle)
			print "User activity for " + handle
		for handle in self.cfs_users:
			self.fetch_user_activity_cfs(handle)
			print "User activity for " + handle
		self.calculate_difficulty()

	def create_difficulty_matrix(self):
		self.difficulty_matrix = {}
		sql = "SELECT * FROM activity"
		result = db.read(sql, self.cursor)
		for i in result:
			user = str(i[0].encode('utf8'))
			problem = str(i[1].encode('utf8'))
			if not self.difficulty_matrix.has_key(user):
				self.difficulty_matrix[user] = {}
			self.difficulty_matrix[user][problem] = i[4]

		self_handle = "erd" + self.erd_handle
		if self.difficulty_matrix.has_key(self_handle):
			n = len(self.difficulty_matrix[self_handle])
			s = sum(self.difficulty_matrix[self_handle][it] for it in self.difficulty_matrix[self_handle])
			self.erd_avg = s/n

		self_handle = "cfs" + self.cfs_handle
		if self.difficulty_matrix.has_key(self_handle):
			n = len(self.difficulty_matrix[self_handle])
			s = sum(self.difficulty_matrix[self_handle][it] for it in self.difficulty_matrix[self_handle])
			self.cfs_avg = s/n

		self.normalize_difficulty_matrix()

	def normalize_difficulty_matrix(self, type = 0):
		for u in self.difficulty_matrix:
			n = len(self.difficulty_matrix[u])
			s = sum(self.difficulty_matrix[u][it] for it in self.difficulty_matrix[u])
			avg = s/n
			for it in self.difficulty_matrix[u]:
				self.difficulty_matrix[u][it] = self.difficulty_matrix[u][it] - avg

	def find_correlation(self, u1, u2, gamma = 100):

		si = {}
		n1 = len(self.difficulty_matrix[u1])
		n2 = len(self.difficulty_matrix[u2])

		i = 0
		for item in self.difficulty_matrix[u1]:
			if item in self.difficulty_matrix[u2] and (i <= (n1*0.8)):
				si[item] = 1
				self.training_problems[item] = 1
			i = i+1

		n = len(si)

		# if there are no common problems, return 0
		if n == 0:
			return 0

		sum1 = sum([self.difficulty_matrix[u1][it] for it in si])
		sum2 = sum([self.difficulty_matrix[u2][it] for it in si])

		# Sum up the squares
		sum1Sq = sum([pow(self.difficulty_matrix[u1][it],2) for it in si])
		sum2Sq = sum([pow(self.difficulty_matrix[u2][it],2) for it in si])

		# Sum up the products
		pSum = sum([self.difficulty_matrix[u1][it] * self.difficulty_matrix[u2][it] for it in si])

		# Calculate Pearson score
		num = pSum - (sum1*sum2/n)
		den = (sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n)

		if den <= 0:
			return 0

		den = math.sqrt( den )

		r = num/den

		penalizing_factor = float(min(n,gamma))/gamma
		r = penalizing_factor*r

		#print u1, u2, n, r, num, den

		return r
		#return (r*n)/(n1+n2)

	def find_similar_users(self):
		self.similar_users = {}
		self_erd_handle = 'erd' + self.erd_handle
		self_cfs_handle = 'cfs' + self.cfs_handle
		for u in self.difficulty_matrix.keys():
			if u[:3] == "erd" and u[3:] != self.erd_handle and self_erd_handle in self.difficulty_matrix.keys():
				self.similar_users[u] = self.find_correlation(self_erd_handle, u, 5)
			if u[:3] == "cfs" and u[3:] != self.cfs_handle and self_cfs_handle in self.difficulty_matrix.keys():
				self.similar_users[u] = self.find_correlation(self_cfs_handle, u, 50)
		self.similar_users = sorted(self.similar_users.items(), key=operator.itemgetter(1), reverse = 1)

	def recommend_problems(self, mode):
		# mode = 1 for difficult problems and 0 for easy problems
		self.find_similar_users()
		top_similar_users = self.similar_users
		totals = {}
		simSum = {}
		totals_eval = {}
		simSum_eval = {}

		for i in top_similar_users:

			handle = i[0]
			score = i[1]

			if score <= 0:
				continue

			if handle[:3] == "erd":
				self_handle = "erd" + self.erd_handle
				avg = self.erd_avg
			if handle[:3] == "cfs":
				self_handle = "cfs" + self.cfs_handle
				avg = self.cfs_avg

			for problem in self.difficulty_matrix[handle]:
				if problem not in self.difficulty_matrix[self_handle]:
					totals.setdefault(problem, 0)
					totals[problem] += ( avg + self.difficulty_matrix[handle][problem] ) * score
					simSum.setdefault(problem, 0)
					simSum[problem] += score

				# for evaluating the model
				if problem in self.difficulty_matrix[self_handle] and problem not in self.training_problems:
					totals_eval.setdefault(problem, 0)
					totals_eval[problem] += ( avg + self.difficulty_matrix[handle][problem] ) * score
					simSum_eval.setdefault(problem, 0)
					simSum_eval[problem] += score

		plist = [(problem, total/simSum[problem]) for problem,total in totals.items()]
		plist = sorted(plist, key=operator.itemgetter(1), reverse = mode)
		plist_eval = [(problem, total/simSum_eval[problem]) for problem,total in totals_eval.items()]
		self.evaluate_recommendation( plist_eval )
		return plist[:50]

	def evaluate_recommendation(self, plist_eval):
		self.error = 0
		for i in plist_eval:
			predicted = i[1]

			if i[0][:3] == "erd":
				self_handle = "erd" + self.erd_handle
				avg = self.erd_avg
				actual = avg + self.difficulty_matrix[self_handle][i[0]]

			if i[0][:3] == "cfs":
				self_handle = "cfs" + self.erd_handle
				avg = self.cfs_avg
				actual = avg + self.difficulty_matrix[self_handle][i[0]]

			self.error += pow( (predicted - actual), 2 )
			#print i[0] + " " + str(predicted) + " " + str(actual)
		n = len(plist_eval)
		self.error = self.error/n
		self.error = math.sqrt( self.error )

if __name__ == '__main__':
	a = user('tourist')
	#plot_concept_cfs(a.cfs_handle)
	graph.plot_difficulty_matrix(a.difficulty_matrix)
	#a.fetch_user_info_cfs()
	#print a.rating, a.rank
	#a.fetch_user_activity_erd("")
	#a.calculate_difficulty()
	#a.fetch_user_activity_cfs("deepalijain")
	#a.fetch_user_activity_all()
	#print a.find_correlation('cfstourist', 'cfsnew')
	#sprint a.similar_users
	#print a.recommend_problems(1)
	#print len(a.training_problems)

