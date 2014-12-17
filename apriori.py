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
	- *transaction* : []
    - *itemset* : set
	- *frequency_itemset* : {}
    - *association_rules* : {}

	'''
	
	def __init__(self, app_name = "forsit", min_support = 0.05, min_confidence = 0.95):
		
		self.min_support = min_support
		self.min_confidence = min_confidence
		self.conn = db.connect(app_name)
		self.cursor = self.conn.cursor()

	def initialise(self):
		'''
		|  Generate set of items and list of transactions
		|  Initialise self.transaction and self.item
		'''
		self.transaction = []
		self.itemset = set()
		sql = ""
		result = db.read(sql, self.cursor)
		for i in result : 
			transaction_temp = frozenset(i)
			#frozenset as it can be used as key for dicts
			self.transaction.append(transaction_temp)
			for j in i:
				self.itemset.add(j)	

	def prune(self):
		'''
		|  Prune subset of itemset based on min_support
		'''
		result = set()
		localset = {}
	    
		for item in self.itemset:
			for t in self.transaction:
				if item.issubset(t):
					self.frequency_itemset[item]+=1
					localset[item]+=1

		size_transaction = len(self.transaction)			
		for item in localset:
			support = float(localset[item])/size_transaction
			if support >= self.minSupport:
				result.add(item)

		return result

	def run(self):
		'''
		|  Run the Apriori algorithm
		|  Return frequent itemsets and association rules
		'''
		self.initialise()
		self.frequency_itemset = {}
        self.association_rules = {}
		self.prune()        
