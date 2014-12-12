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

try:
	import time
except ImportError as exc:
	print("Error: failed to import settings module ({})".format(exc))

try:
	import matplotlib.pyplot as plt
except ImportError as exc:
	print("Error: failed to import settings module ({})".format(exc))
    

class problem(base):

	'''
	|  Class to handle the problem details
	'''
	
	def __init__(self, pid, app_name = "forsit", greatest = 3000, lower_threshold = 25, upper_threshold = 25):
		
		'''
		Input 
		- pid : problem id. For erdos problems, it starts with *erd* and for codeforces problems it starts with *cfs*
		- app_name : Name of the app ie forsit
		- greatest : Defines the default max score for a competiton. The codeforces API has some bugs and it does not return all the problems.
		- lower_threshold : The minimum number of problems, of difficulty less that of pid, which are to be considered for recommendation. It defines the candidate set on lower side. 
		- upper_threshold : The maximum number of problems, of difficulty more than or equal to that of pid, which are to be considered for recommendation. It defines the candidate set on upper side. 

		'''

		self.pid = str(pid)
		self.greatest = str(greatest)
		self.conn = db.connect(app_name)
		self.cursor = self.conn.cursor()
		self.exists_in_db = self.fetch_info()
		self.lower_threshold = lower_threshold
		self.upper_threshold = upper_threshold
		# self.create_difficulty_matrix()

	def fetch_info(self):

		# '''function to fetch problem information from problem table from the db'''
		
		sql = "SELECT points, correct_count, attempt_count, (SELECT MAX(points) FROM problem \
			   WHERE contestId = P.contestId ) AS max_points FROM problem P \
			   WHERE pid = \'" + self.pid + "\'"
		
		# print sql
		result = db.read(sql, self.cursor)
		if result == ():
			print "No Results Found!"
			return -1

		for i in result :
			self.points = float(i[0])
			self.correct_count = float(i[1])
			self.attempt_count = float(i[2])
			if(self.points>0):
				self.difficulty = round( (self.points/( max (3000.0,float( i[3] ) ) ) ), 6)
			else:
				self.difficulty = round(self.correct_count/self.attempt_count, 6)
		
		sql = "SELECT count(*) FROM problem WHERE MID(pid,1,3) = \'" + self.pid[0:3] + "\'"
		
		# print sql
		result = db.read(sql, self.cursor)				
		number_of_problems = result[0][0]
		self.tag = {}

		# using tf-idf approach for assigning weights to tags
		# tf(tag, problem) = 1/(number of tags in the given problem)
		# idf(tag, problem) = log(total number of problems/number of problems with that tag)
		# tf tells how important a tag is for a given problem.
		# idf tell how common a tag is across all the problems

		sql = "SELECT ptag.tag, ROUND( LOG2("+str(number_of_problems)+"/count), 6) FROM ptag, tag WHERE \
		       ptag.tag = tag.tag AND pid = \'" + self.pid + "\'"
		
		# print sql
		result = db.read(sql, self.cursor)
		number_of_tags = len(result)
		normalisation_factor = 0 
		#Since the weights are exceeding 1, we normalise using sum of weights of tags

		checksum = 0
		#a redundant checksum to make sure that the weights add up to 1

		for i in result :
			tag = str(i[0].encode('utf8'))
			self.tag[tag] = float(i[1]) / number_of_tags
			self.tag[tag] = round(self.tag[tag],6)
			normalisation_factor+=self.tag[tag]

		for tag in self.tag:
			self.tag[tag]/=normalisation_factor
			self.tag[tag] = round(self.tag[tag],6)
			checksum+=self.tag[tag]
		# print "the final checksum = ", checksum	
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
		result = db.read(sql, self.cursor)
		problem = {}
		#mapping of problem code with a list of tags
		score = {}
		#mapping of score of problem code with its score 
		difficulty = {}
		#mapping of problem code with difficulty
		for i in result:
			code = str(i[0].encode('utf8'))
			tag = str(i[1].encode('utf8'))
			if code not in problem:
				problem[code] = []
				score[code] = 0
				difficulty[code] = round (abs(float(i[2])-self.difficulty), 6)
			problem[code].append(tag)
		for code in problem:
			# instead of using nfactor as the number of tags, we should normalise only for those 
			# tags which do not occur in self.tag else the results are biased towards the highest
			# weighted tag. We can still improve the normalisation factor by using a slow
			# growing function. Also currently the common tags are being penalised just once 
			# ie while calculating the idf score for the problem.

			nfactor = 1
			for tag in problem[code]:
				if tag not in self.tag:
					nfactor+=1
					continue
				score[code]+=self.tag[tag]
			score[code]=round( (score[code]/nfactor), 6)
		sorted_score = sorted(score.items(), key=operator.itemgetter(1), reverse = 1)	
		print "top 15 results : "
		for i in range(1,15):
			print "problem id, score : ", sorted_score[i]
			print "tags : ", problem[sorted_score[i][0]]
		return sorted_score

	def plot_difficulty_distribution(self):
		a=time.time()
		sql = "SELECT P.pid, P.points, P.points/GREATEST("+self.greatest+", (SELECT MAX(points) FROM problem \
			WHERE contestId = P.contestId)) as difficulty FROM problem P \
			WHERE MID(P.pid,1,3) = \"cfs\" AND P.points>0"
		# print sql
		result = db.read(sql, self.cursor)
		print "time to execute sql = ", time.time()-a
		difficulty = {}

		for i in result:
			pid = str(i[0].encode('utf8'))
			point = float(i[2])
			if point in difficulty:
				difficulty[point]+=1
			else:
				difficulty[point] = 1
		sorted_difficulty = sorted(difficulty.items(), key=operator.itemgetter(0), reverse = 1)
		x = []
		y = []

		for i in sorted_difficulty:
			x.append(i[0])
			y.append(i[1])
			print i, " ", i[0]*3000
		plt.figure()
		plt.plot(difficulty.keys(), difficulty.values(), 'ro')
		plt.plot(x, y)
		plt.show()	

	def plot_points_distribution(self, max_flag = 1, min_flag = 0):

		'''plot the distribution of max and min points for a competiton'''
		a=time.time()
		sql = "SELECT (SELECT MAX(points) FROM problem WHERE contestId = P.contestId), \
			   (SELECT MIN(points) FROM problem WHERE contestId = P.contestId) \
			   FROM problem P WHERE P.pid in (SELECT pid FROM problem GROUP BY \
			   contestId HAVING MID( pid, 1, 3 ) = \"cfs\") AND points > 0 "

		print sql
		result = db.read(sql, self.cursor)
		print "time to execute sql = ", time.time()-a
		max_score = {}
		min_score = {}

		for i in result:
			max_point = float(i[0])
			min_point = float(i[1])
			if max_point in max_score:
				max_score[max_point]+=1
			else:
				max_score[max_point] = 1
			if min_point in min_score:
				min_score[min_point]+=1
			else:
				min_score[min_point] = 1
		if(max_flag == 1):
			sorted_max_score = sorted(max_score.items(), key=operator.itemgetter(1), reverse = 1)
			print "Plot of Max Score"
			for i in sorted_max_score:
				print i
			plt.figure()
			plt.plot(max_score.keys(), max_score.values(), 'ro')
			plt.show()
		if(min_flag == 1):
			sorted_min_score = sorted(min_score.items(), key=operator.itemgetter(1), reverse = 1)
			print "Plot of Min Score"
			for i in sorted_min_score:
				print i
			plt.figure()
			plt.plot(min_score.keys(), min_score.values(), 'bs')
			plt.show()	

	def find_similar_erdos(self, status = 0):
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
		print sql
		return self.reco_algo(sql)
	
	def find_similar_cfs(self, status = 0):

		res = self.gen_window_cfs(status)
		# print res
		upper = res[0]
		lower = res[1]
		sql = "	SELECT ptag.pid, ptag.tag, P.points/GREATEST(3000, (SELECT MAX(points) FROM problem \
			    WHERE contestId = P.contestId)) as difficulty FROM problem P, ptag \
			   	WHERE P.pid != \'" + self.pid + "\' AND P.pid = ptag.pid AND P.pid IN \
				(SELECT ptag.pid FROM problem, ptag WHERE ptag.tag IN \
				(SELECT tag FROM ptag where pid = \'" + self.pid + "\') \
				AND MID(problem.pid,1,3)=\'cfs\' ) \
				HAVING difficulty BETWEEN " + str(upper) + " AND " + str(lower)
		# print sql
		return self.reco_algo(sql)

	def gen_window_cfs(self, status = 0):
		'''generate the optimal size window for codeforces submissions'''
		sql = "SELECT P.points/GREATEST("+self.greatest+", (SELECT MAX(points) FROM problem \
			WHERE contestId = P.contestId)) as difficulty FROM problem P \
			WHERE MID(P.pid,1,3) = \"cfs\" AND P.points>0"
		# print sql
		result = db.read(sql, self.cursor)
		difficulty = {}
		for i in result:
			point = float(i[0])
			if point in difficulty:
				difficulty[point]+=1
			else:
				difficulty[point] = 1
		sorted_difficulty = sorted(difficulty.items(), key=operator.itemgetter(0), reverse = 0)
		
		# print len(sorted_difficulty)
		# for i in sorted_difficulty:
		# 	print i
		i = 0
		imax = len(sorted_difficulty)-1
		hi = imax
		lo = 0
		i = (hi+lo)/2
		while(hi>=lo):
			i = (hi+lo)/2
			a = sorted_difficulty[i][0] - self.difficulty
			if(a>0):
				hi = i-1
			elif(a<0):
				lo = i+1
			else:
				break
		# print i
		if status == 1:
			#correct submission
			upper = sorted_difficulty[i][1]
			j = i
			#increase the right end of the window till the upper threshold is met
			while(upper < self.upper_threshold):
				j+=1
				upper+=sorted_difficulty[j][1]
			x = sorted_difficulty[j][0] - self.difficulty
			# print x
			# how much deviation we allowed on the right side of self.difficulty
			# we allow only half of this deviation on the left hand side
			# the reason is that the difficulty of the problem will lie either 
			# on one of the peaks in which case x = 0 or near a right peak in which case 
			# we wont need many values on the left or near a left peak in which case our x
			# would be large enough to cover the left peak as well. Same logic for the next
			# part of the condition
			return (self.difficulty+x, self.difficulty-x/2)

		else:
			#incorrect submission
			lower = sorted_difficulty[i-1][1]
			print lower
			print i
			print sorted_difficulty[i-1]
			k=i-1
			while(lower < self.lower_threshold):
				k-=1
				lower+=sorted_difficulty[k][1]
				print lower
			x = self.difficulty - sorted_difficulty[k][0]
			# print x
			return (self.difficulty-x, self.difficulty+x/2)

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

		si = {}
		for item in self.difficulty_matrix[u1]:
			if item in self.difficulty_matrix[u2]:
				si[item] = 1
		n = len(si)

		n1 = len(self.difficulty_matrix[u1])
		n2 = len(self.difficulty_matrix[u2])

		# if there are no common users, return 0
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
		den = math.sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))

		if den == 0:
			return 0
		r = num/den
		return (r*n)/(n1+n2)

	def find_correlated_problems(self):
		self.correlated_problems = {}
		for p in self.difficulty_matrix.keys():
			if p != self.pid:
				self.correlated_problems[p] = self.find_correlation(self.pid, p)
		self.correlated_problems = sorted(self.correlated_problems.items(), key=operator.itemgetter(1), reverse = 1)

if __name__ == "__main__":

	a = problem('cfs175E')
	print time.strftime("%d-%m-%Y %H:%M")
	a.print_info()
	a.find_similar_cfs(0)
	# a.find_similar_erdos()
	print "\n\n\n\n"
	# a.plot_points_distribution(max_flag=0, min_flag = 1)
	# a.plot_difficulty_distribution()
	# a.gen_window_cfs()

	# print "\n"
	# print "\n"
	# for item in a.find_similar_cfs(1)[:10]:
	# 	print item
	# 	b = problem(item[0])
	# 	b.print_info()
	# 	print "\n"
	# a.find_correlated_problems()
	# print "\n"
	# print "\n"
	# print "\n"
	# for item in a.correlated_problems[:10]:
	# 	print item
	# 	b = problem(item[0])
	# 	b.print_info()
	# 	print "\n"