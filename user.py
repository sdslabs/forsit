try:
    import requests
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

class user():
	def __init__(self, uid, cfs_handle = '', erd_handle = ''):
		self.uid = str(uid)
		self.cfs_url = "http://codeforces.com/api/user.status"
		self.erd_url = "http://erdos.sdslabs.co/users/"
		if(cfs_handle == ''):
			cfs_handle = self.uid
		if(erd_handle == ''):
			erd_handle = self.uid	
		self.cfs_handle = str(cfs_handle)
		self.erd_handle = str(erd_handle)

	def fetch_user_info_cfs(self):
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
		url = self.erd_url + self.erd_handle + ".json"
		r = requests.get(url)
		if(r.status_code != 200 ):
			print r.status_code, " returned from ", r.url
		else:
			solved_problems = r.json()['solved_problems']

a = user('shagun')
a.fetch_user_info_erd()