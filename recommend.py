try:
    import requests
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    from problem import problem
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    from user import user
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


class recommend():

	def __init__(self, pid, status):
		self.pid = pid
		self.status = status

	def recommend_most_recent_erdos(self):
		erdos = problem(self.pid)
		res = erdos.find_similar_erdos(self.status)
		print res

	def recommend_most_recent_cfs(self):
		cfs = problem(self.pid)
		res = cfs.find_similar_cfs(self.status)
		print res 

a = recommend("cfs172D",1)
a.recommend_most_recent_erdos()
a.recommend_most_recent_cfs()