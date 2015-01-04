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

import time

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

		
	def __init__(self, erd_handle, cfs_handle = '', options = {}, app_name = "forsit", number_to_recommend = 50):
		self.training_problems = {}
		self.options = {}
		self.options['tag_based'] = 0
		self.options['normalize'] = 0
		self.options['sample_data'] = 1
		self.options['penalize'] = 1
		if 'tag_based' in options:
			self.options['tag_based'] = options['tag_based']
		if 'normalize' in options:
			self.options['normalize'] = options['normalize']
		if 'sample_data' in options:
			self.options['sample_data'] = options['sample_data']
		if 'penalize' in options:
			self.options['penalize'] = options['penalize']

		self.conn=db.connect(app_name)
		self.cursor = self.conn.cursor()

		self.cfs_url = "http://codeforces.com/api/user.status"
		self.erd_url = "http://erdos.sdslabs.co/users/"
		self.cfs_handle = 'cfs' + str(cfs_handle)
		self.erd_handle = 'erd' + str(erd_handle)
		self.number_to_recommend = number_to_recommend
		self.uid = self.get_uid()
		# print self.uid
		self.calculate_difficulty()

	def get_uid(self):
		'''
		| Get uid from database using his erdos handle and also set cfs_handle if provided
		'''
		sql = "SELECT uid, cfs_handle FROM user WHERE erd_handle = \'" + self.erd_handle + "\'"
		res = db.read(sql, self.cursor)
		if not res:
			sql = "INSERT INTO user (erd_handle, cfs_handle, erd_score, cfs_score) VALUES ( \'" + self.erd_handle + "\', \'" + self.cfs_handle + "\', '0', '0')"
			db.write(sql, self.cursor, self.conn)
			sql = "SELECT uid FROM user WHERE erd_handle = \'" + self.erd_handle + "\'"
			uid = db.read(sql, self.cursor)
			return uid[0][0]
		else:
			if self.cfs_handle != res[0][1] :
				sql = "UPDATE user SET cfs_handle = \'" + self.cfs_handle + "\'"
				db.write(sql, self.cursor, self.conn)
			return res[0][0]

	def fetch_user_info_cfs(self):
		'''
		|  Fetch User's information from Codeforces
	    '''
		payload = {}
		payload['handles'] = self.cfs_handle[3:]
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
		url = self.erd_url + self.erd_handle[3:] + ".json"
		r = requests.get(url)
		if(r.status_code != 200 ):
			print r.status_code, " returned from ", r.url
		else:
			solved_problems = r.json()['solved_problems']

	def calculate_difficulty(self):
		'''
		| Calculate difficulty of a problem for a user
		'''
		sql = "UPDATE activity SET difficulty = 1 WHERE status = 0"
		db.write(sql, self.cursor, self.conn)
		sql = "UPDATE activity SET difficulty = 0 WHERE status = 1"
		db.write(sql, self.cursor, self.conn)
		# sql = "UPDATE activity SET difficulty = difficulty + 1 WHERE attempt_count <= 2"
		# db.write(sql, self.cursor, self.conn)
		# sql = "UPDATE activity SET difficulty = difficulty + 2 WHERE attempt_count >= 3 AND attempt_count <= 5"
		# db.write(sql, self.cursor, self.conn)
		# sql = "UPDATE activity SET difficulty = difficulty + 3 WHERE attempt_count > 5;"
		# db.write(sql, self.cursor, self.conn)
		self.create_difficulty_matrix()

	def create_difficulty_matrix(self):
		'''
		| Create user-problem difficulty or user-tag score matrix from the database
		| Set options['tag_based'] = 0 for user-problem difficulty matrix
		| and options['tag_based'] = 1 for user-tag score matrix
		'''
		self.difficulty_matrix = {}
		# sql = "SELECT * FROM activity"
		sql = "SELECT handle, pid, difficulty FROM activity"
		if self.options['tag_based']:
			sql = "SELECT handle, tag, score FROM user_tag_score"
		result = db.read(sql, self.cursor)
		for i in result:
			user = str(i[0].encode('utf8'))
			item = str(i[1].encode('utf8'))

			if user not in self.difficulty_matrix:
			# if not self.difficulty_matrix.has_key(user):
				self.difficulty_matrix[user] = {}
				self.difficulty_matrix[user][item] = i[2]
			else:
				self.difficulty_matrix[user][item] = i[2]

		self_handle = self.erd_handle
		# if self.difficulty_matrix.has_key(self_handle):
		if self_handle in self.difficulty_matrix:
			n = float(len(self.difficulty_matrix[self_handle]))
			s = sum(self.difficulty_matrix[self_handle][it] for it in self.difficulty_matrix[self_handle])
			self.erd_avg = s/n

		self_handle = self.cfs_handle
		if self_handle in self.difficulty_matrix:
		# if self.difficulty_matrix.has_key(self_handle):
			n = float(len(self.difficulty_matrix[self_handle]))
			s = sum(self.difficulty_matrix[self_handle][it] for it in self.difficulty_matrix[self_handle])
			self.cfs_avg = s/n

		if self.options['normalize']:
			self.normalize_difficulty_matrix()

	# def normalize_difficulty_matrix(self, type = 0):
	def normalize_difficulty_matrix(self):
		'''
		| Mean normalization of user-problem difficulty or user-tag score matrix
		'''
		for u in self.difficulty_matrix:
			n = float(len(self.difficulty_matrix[u]))
			s = sum(self.difficulty_matrix[u][it] for it in self.difficulty_matrix[u])
			avg = s/n
			for it in self.difficulty_matrix[u]:
				self.difficulty_matrix[u][it] = self.difficulty_matrix[u][it] - avg

	def find_correlation(self, u1, u2, gamma = 50):
		'''
		| Pearson Correlation Algorith to find similarity between user u1 and u2
		| - *u1* : handle of user #1
		| - *u2* : handle of user #2
    	| - *gamma* : penalizing factor - to penalize users with less than a threshold number of common problems
		'''

		si = {}
		n1 = len(self.difficulty_matrix[u1])
		n2 = len(self.difficulty_matrix[u2])

		if self.options['sample_data']:
			n1 = n1 * 0.8

		i = 0
		for item in self.difficulty_matrix[u1]:
			if item in self.difficulty_matrix[u2] and (i <= n1):
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

		# Calculate penalizing factor relative to number of problems solved by u1
		gamma = (gamma * n1) / 100
		penalizing_factor = float(min(n,gamma))/gamma

		# Penalize rating of users with lesser common problems than the threshold, gamma
		if self.options['penalize']:
			r = penalizing_factor*r

		#print u1, u2, n, r, num, den
		# print n
		return r
		#return (r*n)/(n1+n2)

	def find_similar_users(self):
		'''
		| Calculate similarity with all users
		'''
		self.similar_users = {}
		# for u in self.difficulty_matrix.keys():
		for u in self.difficulty_matrix:
			# if u[:3] == "erd" and u[3:] != self.erd_handle and self_erd_handle in self.difficulty_matrix.keys():
			if u[:3] == "erd" and u != self.erd_handle and self.erd_handle in self.difficulty_matrix:
				self.similar_users[u] = self.find_correlation(self.erd_handle, u, 50)
			# if u[:3] == "cfs" and u[3:] != self.cfs_handle and self_cfs_handle in self.difficulty_matrix.keys():
			if u[:3] == "cfs" and u != self.cfs_handle and self.cfs_handle in self.difficulty_matrix:
				self.similar_users[u] = self.find_correlation(self.cfs_handle, u, 50)
		self.similar_users = sorted(self.similar_users.items(), key=operator.itemgetter(1), reverse = 1)

	def reco_algo(self, mode):
		'''
		| Create list of recommended problems by taking weighted sum of similar users' ratings
		| - *mode* : 1 for difficult problems and 0 for easy problems
		'''
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
				self_handle = self.erd_handle
				avg = self.erd_avg
			if handle[:3] == "cfs":
				self_handle = self.cfs_handle
				avg = self.cfs_avg

			if not options['normalize']:
				avg = 0

			for problem in self.difficulty_matrix[handle]:
				if problem not in self.difficulty_matrix[self_handle]:
					totals.setdefault(problem, 0)
					totals[problem] += ( avg + self.difficulty_matrix[handle][problem] ) * score
					simSum.setdefault(problem, 0)
					simSum[problem] += score

				if self.options['sample_data']:
					# for evaluating the model
					if problem in self.difficulty_matrix[self_handle] and problem not in self.training_problems:
						totals_eval.setdefault(problem, 0)
						totals_eval[problem] += ( avg + self.difficulty_matrix[handle][problem] ) * score
						simSum_eval.setdefault(problem, 0)
						simSum_eval[problem] += score

		plist = [(problem, total/simSum[problem]) for problem,total in totals.items()]
		plist = sorted(plist, key=operator.itemgetter(1), reverse = mode)
		if self.options['sample_data']:
			plist_eval = [(problem, total/simSum_eval[problem]) for problem,total in totals_eval.items()]
			self.evaluate_recommendation( plist_eval )
		# self.log_results_db(plist,50)
		self.number_to_recommend = 50
		self.log_results_db(plist)
		return plist[:50]

	def evaluate_recommendation(self, plist_eval):
		'''
		| Calculate error in recommendation by taking euclidean distance between actual and predicted scores
		| *plist_eval* : list of sampled problems (20% of total solved problems) to evaluate
		'''
		self.error = 0
		for i in plist_eval:
			predicted = i[1]
			if i[0][:3] == "erd":
				self_handle = self.erd_handle
				avg = self.erd_avg
				actual = avg + self.difficulty_matrix[self_handle][i[0]]

			if i[0][:3] == "cfs":
				self_handle = self.erd_handle
				avg = self.cfs_avg
				actual = avg + self.difficulty_matrix[self_handle][i[0]]

			if self.options['tag_based']:
				self_handle = self.erd_handle
				avg = self.erd_avg
				actual = avg + self.difficulty_matrix[self_handle][i[0]]

			if not self.options['normalize']:
				avg = 0

			self.error += pow( (predicted - actual), 2 )
			print i[0] + " " + str(predicted) + " " + str(actual)
		n = len(plist_eval)
		self.error = self.error/n
		self.error = math.sqrt( self.error )

	def rank_erdos_users(self):
		'''
		| Rank erdos users based on the sum of difficulty of problems solved by them
		'''
		score = {}
		for user in self.difficulty_matrix:
			if( user[:3] == "erd" ):
				score[user] = 0
				#print user + ": "
				for prob in self.difficulty_matrix[user]:
					p = problem(prob)
					if p.exists_in_db != -1:
						score[user] += p.difficulty
					#p.print_info()
				#print "\n"
		return sorted(score.items(), key=operator.itemgetter(1), reverse = 1)

	def log_results_db(self, sorted_score):
		'''
    	Input
    	- *sorted_score* : recommendation results
    	Output
    	Logs the results in db with appropriate insertions/updates/deletions
		'''
		sql = "SELECT pid FROM user_reco WHERE uid = \'"+str(self.uid)+"\' AND is_deleted = 0"
		# print sql
		results = db.read(sql, self.cursor)
		if not results:
			#Making entry for the first time
			sql = "INSERT INTO user_reco (uid, pid, score, time_created, time_updated, is_deleted, state) VALUES "
			k = min(len(sorted_score), self.number_to_recommend)
			for i in range(0,k):
				a = str(int(time.time()))
				sql+="(\'"+str(self.uid)+"\', \'"+str(sorted_score[i][0])+"\', \'"+str(sorted_score[i][1])+"\', \'"+a+"\', \'"+a+"\', \'0\', \'0\' ), "
			sql = sql[:-2]
			db.write(sql, self.cursor, self.conn)
		else:
			to_delete = []
			for i in results:
				to_delete.append(i[0])
			to_update = []
			to_insert = []
			k = min(len(sorted_score), self.number_to_recommend)
			for i in range(0,k):
				if sorted_score[i][0] not in to_delete:
					to_insert.append(sorted_score[i])
				else:
					to_update.append(sorted_score[i])
					to_delete.remove(sorted_score[i][0])

			if to_delete:					
				sql_delete = "UPDATE user_reco SET is_deleted = 1, time_updated = "+str(int(time.time()))+" WHERE uid = \'"+str(self.uid)+"\' AND pid IN ("
				for i in to_delete:
					sql_delete+="\'"+str(i)+"\',"
				sql_delete=sql_delete[:-1]
				sql_delete=sql_delete+")"
				db.write(sql_delete, self.cursor, self.conn)

			if to_update:		
				sql_update = "UPDATE user_reco SET score = CASE pid "
				where_clause = " WHERE uid = \'"+str(self.uid)+"\' AND pid IN ("
				for i in to_update:
					sql_update+="WHEN \'"+str(i[0])+"\' THEN "+str(i[1])+"\n"
					where_clause+="\'"+str(i[0])+"\',"
				sql_update+=" END, time_updated = "+str(int(time.time()))
				sql_update+=where_clause[:-1]
				sql_update=sql_update+")"
				db.write(sql_update, self.cursor, self.conn)

			if to_insert:					
				sql_insert = "INSERT INTO user_reco (uid, pid, score, time_created, time_updated, is_deleted, state) VALUES "
				for i in to_insert:
					a = str(int(time.time()))
					sql_insert+="(\'"+str(self.uid)+"\', \'"+str(i[0])+"\', \'"+str(i[1])+"\', \'"+a+"\', \'"+a+"\', \'0\', \'0\' ), "
				sql_insert = sql_insert[:-2]
				db.write(sql_insert, self.cursor, self.conn)

	def recommend_problems_temp(self):
		'''
		| Create list of recommended problems by taking weighted sum of similar users' ratings
		'''
		self.find_weighted_tags()
		sql = "SELECT * FROM ptag WHERE pid NOT IN (SELECT pid FROM activity WHERE uid = \'"+str(self.uid)+"\' AND status = 1)"
		result = db.read(sql, self.cursor)
		plist = defaultdict(list)
		plist_score = {}
		for i in result:
			plist[i[0]].append(i[1])
		for i in plist:
			a = len(plist[i])
			plist_score[i] = 0
			for j in plist[i]:
				plist_score[i]+=self.weighted_tag[j]/a
		plist = sorted(plist, key=operator.itemgetter(1), reverse = 1)
		self.log_results_db(plist)

if __name__ == '__main__':
	options = {}
	options['tag_based'] = 0
	options['normalize'] = 0
	options['sample_data'] = 1
	options['penalize'] = 1
	a = user(erd_handle = 'TheOrganicGypsy', options = options)
	# print a.difficulty_matrix
	# print a.rank_erdos_users()[:10]
	#plot_concept_cfs(a.cfs_handle)
	#graph.plot_difficulty_matrix(a.difficulty_matrix)
	#a.fetch_user_info_cfs()
	#print a.rating, a.rank
	#a.fetch_user_activity_erd("")
	#a.calculate_difficulty()
	#a.fetch_user_activity_cfs("deepalijain")
	#a.fetch_user_activity_all()
	#print a.find_correlation('cfstourist', 'cfsnew')
	# print a.difficulty_matrix['erdTheOrganicGypsy']
	# print a.difficulty_matrix['erdamntri']
	# print a.difficulty_matrix['erdvgupta']
	# print a.find_correlation('erdTheOrganicGypsy', 'erdpriyanshu1994', 50)
	# print a.find_correlation('erdTheOrganicGypsy', 'erdvgupta', 50)
	print a.recommend_problems(1)
	# print a.similar_users
	print a.error
	#print len(a.training_problems)
