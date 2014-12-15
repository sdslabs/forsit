#!/usr/bin/env python

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

try:
	import optparse
except ImportError as exc:
	print("Error: failed to import settings module ({})".format(exc))

try:
	import sys
except ImportError as exc:
	print("Error: failed to import settings module ({})".format(exc))


class recommend():
	"""test"""

	def __init__(self, pid, status, uid=""):
		self.pid = pid
		self.status = status
		self.uid = uid

	def recommend_most_recent_erdos(self):
		erdos = problem(self.pid)
		res = erdos.find_similar_erdos(self.status)
		print res

	def recommend_most_recent_cfs(self):
		cfs = problem(self.pid)
		res = cfs.find_similar_cfs(self.status)
		print res 

	def recommend_similar_users(self, mode):
		a = user(self.uid)
		a.find_similar_users()
		print "User similarity: "
		print a.similar_users
		print "Recommended problems: "
		print a.recommend_problems(mode)
		print "Estimated error in rating: "
		print a.error


	def fetch_activity(self):
		a = user(self.uid)
		a.fetch_user_activity_all()



def main():
	p = optparse.OptionParser(description="Cross platform recommendation system for Erdos and Codeforces")

	p.add_option("--problem", "-p", help="Get list of problems similar to given problem through content based ( tag matching ) algorithm.")
	p.add_option("--site", "-s", help="Site to give recommendations for. Choose from 'erd' and 'cfs'.", default="erd", action="store", type="choice", dest="site", choices=["erd","cfs"])
	p.add_option("--status", "-t", help="Status of the given problem. 1 for correct submission and 0 otherwise.", default=0, action="store", type="choice", dest="status", choices=[1,0])
	p.add_option("--user", "-u", help="Get list of users similar to given user and list of recommended problems through collaborative filtering ( neighbourhood matching ) algorithm.", default="")
	p.add_option("--difficulty_mode", "-d", action="store" ,help="Difficulty mode of problems recommended for a user. 1 for difficult problems and 0 for easy problems.", type="choice", dest="difficulty_mode", choices=[1,0], default=0)
	p.add_option("--fetch_activity", "-f", action="store_true" ,help="Fetch latest user activity and populate the database.", default=False)

	options, arguments = p.parse_args()

	flag = 0

	if options.problem:
		print "Showing recommendations for problem: " + options.problem
		if options.site == "erd":
			pid = "erd" + options.problem
			a = recommend(pid,options.status)
			a.recommend_most_recent_erdos()

		elif options.site == "cfs":
			pid = "cfs" + options.problem
			a = recommend(pid,options.status)
			a.recommend_most_recent_cfs()
		flag = 1

	if options.user:
		print "Showing similar users and problem recommendations for: " + options.user
		a = recommend(0,0,options.user)
		a.recommend_similar_users(options.difficulty_mode)
		flag = 1

	if options.fetch_activity:
		a = recommend(0,0,"")
		a.fetch_activity()
		flag = 1

	if flag == 0:
		p.print_help()

if __name__ == '__main__':
	main()

