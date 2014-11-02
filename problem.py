try:
    import db
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import requests
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import operator
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    from base import base
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import math
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

class problem(base):
	def __init__(self, pid):
		self.pid = str(pid)
		self.exists_in_db = self.fetch_info()
		self.create_difficulty_matrix()

	def fetch_info(self):
		sql = "SELECT points, correct_count, attempt_count, (SELECT MAX(points) FROM problem WHERE MID(pid,1,3) = \'" + self.pid[0:3] + "\') AS max_points FROM problem WHERE pid = \'" + self.pid + "\'"
		conn = db.connect('forsit')
		cursor=conn.cursor()
		result = db.read(sql, cursor)
		if result == ():
			print "No Results Found!"
			return 0

		for i in result :
			self.points = float(i[0])
			self.correct_count = float(i[1])
			self.attempt_count = float(i[2])
			if(self.points>0):
				self.difficulty = round(self.points/float(i[3]), 5)
			else:
				self.difficulty = round(self.correct_count/self.attempt_count, 5)
					
		self.tag = {}
		sql = "SELECT ptag.tag, 1 - ROUND( 0.75*(count/(SELECT MAX(count) FROM tag)), 6) FROM ptag, tag WHERE ptag.tag = tag.tag AND pid = \'" + self.pid + "\'"
		result = db.read(sql, cursor)
		for i in result :
			tag = str(i[0].encode('utf8'))
			self.tag[tag] = round(float(i[1]), 5)
		cursor.close() 
		return 1

	def print_info(self):
		if self.exists_in_db:
			print "pid = ", self.pid
			print "points = ", self.points
			print "correct_count = ", self.correct_count
			print "attempt_count = ", self.attempt_count
			print "difficulty = ", self.difficulty 
			print "Tag count : "
			for i in self.tag:
				print i, "    ",self.tag[i]
		else:
			print "No Results Found!"

	def reco_algo(self, sql):
		conn = db.connect('forsit')
		cursor=conn.cursor()
		result = db.read(sql, cursor)
		cursor.close()
		problem = {}
		weight = {}
		difficulty = {}
		for i in result:
			code = str(i[0].encode('utf8'))
			tag = str(i[1].encode('utf8'))
			if code not in problem.keys():
				problem[code] = []
				weight[code] = []
				weight[code].append(0)
				weight[code].append( round (abs(float(i[2])-self.difficulty), 5))
			problem[code].append(tag)
		for code in problem.keys():
			nfactor = float (len(problem[code]) )
			for tag in problem[code]:
				if tag not in self.tag.keys():
					continue
				weight[code][0]+=round( (self.tag[tag]/nfactor), 5)
		sorted_weight = sorted(weight.items(), key=operator.itemgetter(1), reverse = 1)
		return sorted_weight

	def find_similar_erdos(self, status):
		self.fetch_info()
		sql = "	SELECT ptag.pid, ptag.tag, correct_count/attempt_count as difficulty \
			   	FROM problem, ptag \
			   	WHERE problem.pid != \'" + self.pid + "\' AND problem.pid = ptag.pid  \
				AND problem.pid IN \
				(SELECT ptag.pid FROM problem, ptag WHERE ptag.tag IN \
				(SELECT tag FROM ptag where pid = \'" + self.pid + "\') AND MID(problem.pid,1,3)=\'erd\' ) \
				HAVING difficulty BETWEEN "
		if(status == 1):
			#correct submission
			sql+= str(self.difficulty) + " - 0.3 AND " + str(self.difficulty) + " + 0.5 "
		else:
			sql+=str(self.difficulty) + " - 0.5 AND " + str(self.difficulty) + " + 0.3 "
		sql+=" AND difficulty > 0"
		return self.reco_algo(sql)
	
	def find_similar_cfs(self, status):
		sql = "	SELECT ptag.pid, ptag.tag, \
				points/(SELECT MAX(points) FROM problem WHERE MID(pid,1,3) = \"cfs\") as difficulty \
			   	FROM problem, ptag \
			   	WHERE problem.pid != \'" + self.pid + "\' AND problem.pid = ptag.pid  \
				AND problem.pid IN \
				(SELECT ptag.pid FROM problem, ptag WHERE ptag.tag IN \
				(SELECT tag FROM ptag where pid = \'" + self.pid + "\') AND MID(problem.pid,1,3)=\'cfs\' ) \
				HAVING difficulty BETWEEN "
		if(status == 1):
			#correct submission
			sql+= str(self.difficulty) + " - 0.3 AND " + str(self.difficulty) + " - 0.05 "
		else:
			sql+=str(self.difficulty) + " - 0.46 AND " + str(self.difficulty) + " - 0.11 "
		sql+=" AND difficulty > 0"
		return self.reco_algo(sql)

	def create_difficulty_matrix(self):
		self.difficulty_matrix = {}
		conn = db.connect('forsit')
		cursor=conn.cursor()
		sql = "SELECT * FROM activity"
		result = db.read(sql, cursor)
		for i in result:
			user = str(i[0].encode('utf8'))
			problem = str(i[1].encode('utf8'))
			if not self.difficulty_matrix.has_key(problem):
				self.difficulty_matrix[problem] = {}
			self.difficulty_matrix[problem][user] = i[4]

	def find_correlation(self, u1, u2):

		# Get the list of mutually rated items
		si = {}
		for item in self.difficulty_matrix[u1]:
			if item in self.difficulty_matrix[u2]:
				si[item] = 1
		# Find the number of elements
		n = len(si)

		# if they are no ratings in common, return 0
		if n == 0:
			return 0

		# Add up all the preferences
		sum1 = sum([self.difficulty_matrix[u1][it] for it in si])
		sum2 = sum([self.difficulty_matrix[u2][it] for it in si])

		# Sum up the squares
		sum1Sq = sum([pow(self.difficulty_matrix[u1][it],2) for it in si])
		sum2Sq = sum([pow(self.difficulty_matrix[u2][it],2) for it in si])

		# Sum up the products
		pSum = sum([self.difficulty_matrix[u1][it] * self.difficulty_matrix[u2][it] for it in si])

		# Calculate Pearson score
		num = pSum - (sum1*sum2/n)
		den = math.sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))

		if den == 0:
			return 0
		r = num/den
		return r

	def find_correlated_problems(self):
		self.correlated_problems = {}
		for p in self.difficulty_matrix.keys():
			if p != self.pid:
				self.correlated_problems[p] = self.find_correlation(self.pid, p)
		self.correlated_problems = sorted(self.correlated_problems.items(), key=operator.itemgetter(1), reverse = 1)

a = problem('erd13')
# a.fetch_info()
# a.print_info()
print a.find_similar_erdos(1)
a.find_correlated_problems()