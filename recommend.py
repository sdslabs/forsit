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
	import os
except ImportError as exc:
	print("Error: failed to import settings module ({})".format(exc))

try:
	import time
except ImportError as exc:
	print("Error: failed to import settings module ({})".format(exc))

try:
	import pickle
except ImportError as exc:
	print("Error: failed to import settings module ({})".format(exc))

try:
	import json
except ImportError as exc:
	print("Error: failed to import settings module ({})".format(exc))

class recommend():
	"""test"""

	def __init__(self, pid, status, uid=""):
		self.pid = pid
		self.status = status
		self.uid = uid
		self.log_file = os.open('Logs/log.txt', os.O_WRONLY|os.O_APPEND|os.O_CREAT)
		self.result_file = os.open('result.json', os.O_WRONLY|os.O_CREAT)
		os.write(self.log_file, "\n\n\n========================\n" + str(time.strftime("%d-%m-%Y %H:%M")))

	def recommend_most_recent_erdos(self):
		erdos = problem(self.pid)
		res = "\nShowing recommendations for problem: " + self.pid + "\n"
		os.write(self.log_file,res)
		print res
		res = json.dumps(erdos.find_similar_erdos(self.status), indent=4, separators=(',', ': '))
		os.write(self.log_file,res)
		os.write(self.result_file,res)
		print res

	def recommend_most_recent_cfs(self):
		cfs = problem(self.pid)
		res = "\nShowing recommendations for problem: " + self.pid + "\n"
		os.write(self.log_file,res)
		print res 
		res = json.dumps(cfs.find_similar_cfs(self.status), indent=4, separators=(',', ': '))
		os.write(self.log_file,res)
		os.write(self.result_file,res)
		print res

	def recommend_similar_users(self, mode):
		a = user(self.uid)
		a.find_similar_users()
		result = {}
		su = a.similar_users
		rp = a.recommend_problems(mode)
		er = a.error
		result['similar_users'] = su
		result['recommended_problems'] = rp
		result['error'] = er
		result = json.dumps(result, indent=4, separators=(',', ': '))
		os.write(self.result_file,result)
		res = "\nShowing similar users and problem recommendations for: \n" + self.uid + "\nUser similarity: \n"
		os.write(self.log_file,res)
		print res
		res = json.dumps(su, indent=4, separators=(',', ': '))
		os.write(self.log_file,res)
		print res
		res = "\nRecommended problems: \n"
		os.write(self.log_file,res)
		print res
		res = json.dumps(rp, indent=4, separators=(',', ': '))
		os.write(self.log_file,res)
		print res
		res = "\nEstimated error in rating: \n" + str(er)
		os.write(self.log_file,res)
		print res
		


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

