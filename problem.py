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


class problem():
	def __init__(self, pid):
		self.pid = str(pid)

	def fetch_info(self):
		sql = "SELECT points, correct_count, attempt_count, (SELECT MAX(points) FROM problem WHERE MID(pid,1,3) = \'" + self.pid[0:3] + "\') AS max_points FROM problem WHERE pid = \'" + self.pid + "\'"
		conn = db.connect('forsit')
		cursor=conn.cursor()
		result = db.read(sql, cursor)
		if result == ():
			print "No Results Found!"
			return

		for i in result :
			self.points = float(i[0])
			self.correct_count = float(i[1])
			self.attempt_count = float(i[2])
			if(self.points>0):
				self.difficulty = round(self.points/float(i[3]), 5)
			else:
				self.difficulty = round(self.correct_count/self.attempt_count, 5)
					
		self.tag = {}
		sql = "SELECT ptag.tag, 1 - ROUND( 0.5*(count/(SELECT MAX(count) FROM tag)), 6) FROM ptag, tag WHERE ptag.tag = tag.tag AND pid = \'" + self.pid + "\'"
		result = db.read(sql, cursor)
		for i in result :
			tag = str(i[0].encode('utf8'))
			self.tag[tag] = round(float(i[1]), 5)

		cursor.close() 

	def print_info(self):
		print "pid = ", self.pid
		print "points = ", self.points
		print "correct_count = ", self.correct_count
		print "attempt_count = ", self.attempt_count
		print "difficulty = ", self.difficulty 
		print "Tag count : "
		for i in self.tag:
			print i, "    ",self.tag[i]

	
a = problem('erd42')
a.fetch_info()
a.print_info()
