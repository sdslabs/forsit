try:
	import db
except ImportError as exc:
	print("Error: failed to import settings module ({})".format(exc))

try:
	import helper
except ImportError as exc:
	print("Error: failed to import settings module ({})".format(exc))

try:
	import time
except ImportError as exc:
	print("Error: failed to import settings module ({})".format(exc))

try:
	from collections import defaultdict
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
	- *size_one_candidate_set* : set
	- *max_iterations*
	count_transaction
	'''
	def __init__(self, list_pid, app_name = "forsit", min_support = 0.15 , min_confidence = 0.6, max_iterations = 50):	
			
		self.min_support = min_support
		self.min_confidence = min_confidence
		self.conn = db.connect(app_name)
		self.cursor = self.conn.cursor()
		self.max_iterations = max_iterations
		self.list_pid = list_pid

	def initialise(self):
		'''
		|  Generate set of items and list of transactions
		|  Initialise self.transaction and self.item
		'''
		# self.transaction = []
		# self.itemset = set()
		# data_iterator = self.inFile
		# for record in data_iterator:
		# 	transaction_temp = frozenset(record)
		# 	self.transaction.append(transaction_temp)
		# 	for item in transaction_temp:
		# 		self.itemset.add(frozenset([item]))              # Generate 1-itemSets

		self.transaction = []
		self.itemset = set()

		sql = "SELECT handle, pid FROM activity WHERE "
		for pid in self.list_pid:
			sql+="pid = \'"+str(pid)+"\' OR "
		sql=sql[:-3] 
		result = db.read(sql, self.cursor)
		print result
		Trans = defaultdict(list)
		for i in result :
			print i 
			Trans[str(i[0])].append(str(i[1]))
		for i in Trans:
			#frozenset as it can be used as key for dicts
			self.transaction.append(frozenset(Trans[i]))
			for j in Trans[i]:
				print j
				self.itemset.add(frozenset([j]))
		self.count_transaction = len(self.transaction)

	def prune(self, itemset):
		'''
		|  Prune subset of itemset based on min_support
		'''
		print self.transaction
		result = set()
		localset = defaultdict(int)
		#default dict with all keys set to 0
	    
		for item in itemset:
			for t in self.transaction:
				print t
				print "item", item
				if item.issubset(t):
					self.frequency_itemset[item]+=1
					localset[item]+=1

		for item in localset:
			support = float(localset[item])/self.count_transaction
			if support >= self.min_support:
				result.add(item)

		return result

	def print_results(self):
		'''
		|  Print generated Itemsets and Confidence Rules
		'''
		print "----Itemset----"
		for item in self.Final_items:
			print "item : %s  support : %0.6f" % (item[0], item[1])
		print "----Rules----"
		for rule in self.Final_rules:
			print "%s -> %s  support = %0.6f " % (str(rule[0][0]), str(rule[0][1]), rule[1])

	def run(self):
		'''
		|  Run the Apriori algorithm
		|  Return frequent itemsets and association rules
		'''
		self.initialise()
		self.frequency_itemset = defaultdict(int)
		self.association_rules = {} 
		self.size_to_itemset = {}
		# Dictionary mapping size with itemsets ie size_to_itemset[1] = set(all itemsets of size 1)
		self.size_one_candidate_set = self.prune(itemset = self.itemset)
		current_candidate_set = self.size_one_candidate_set
		k = 2
		while(current_candidate_set != set([]) ): #or k!=self.max_iterations):
			self.size_to_itemset[k-1] = current_candidate_set
			current_candidate_set = helper.join_set(current_candidate_set, k)
			current_candidate_set = self.prune(current_candidate_set)
			k+=1

		def support(item):
			'''
			|  Return the support of an item
			|  Defining function within a function as python does not have macros by default 
			'''
			return float(self.frequency_itemset[item])/self.count_transaction

		self.Final_items = []

		for size in self.size_to_itemset:
			for item in self.size_to_itemset[size]:
				self.Final_items.append((tuple(item), support(item)))

		self.Final_rules = []
		for size in self.size_to_itemset:
			for item in self.size_to_itemset[size]:
				for x in helper.subset(item):	
					y = item.difference(x)
					if len(y) > 0:
						confidence = support(item)/support(x)
						if confidence >= self.min_confidence:
							self.Final_rules.append(((tuple(x), tuple(y)), confidence))




list_pid = ['cfs2B', 'cfs2A']
a = apriori(list_pid = list_pid)
a.run()
a.print_results()
