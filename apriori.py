try:
	import db
except ImportError as exc:
	print("Error: failed to import settings module ({})".format(exc))

try:
	import sys
except ImportError as exc:
	print("Error: failed to import settings module ({})".format(exc))

try:
	import helper
except ImportError as exc:
	print("Error: failed to import settings module ({})".format(exc))

try:
	import operator
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


class apriori():

	'''
	- *app_name* : Name of the app ie forsit
	- *min_support* : The minimum support for generating frequent itemse
	- *min_confidence* : The minimum number for generating association rules. 
	'''
	
	def __init__(self, app_name = "forsit", min_support = 0.05, min_confidence = 0.95):
		
		self.min_support = min_support
		self.min_confidence = min_confidence