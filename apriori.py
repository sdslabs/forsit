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
	- *list_pid* : list of pids for which association rules and frequent itemsets are to be mined
	- *app_name* : Name of the app ie forsit
	- *min_support* : The minimum support for generating frequent itemse
	- *min_confidence* : The minimum number for generating association rules.
	- *transaction* : List of all the transactions involving the pids
	- *itemset* : set of items. Each item is itself a set(frozenset to be more precise) of pids. 
	  So it looks like this : itemset = set ( set(pid1, pid2), set(pid3,pid4) )
	- *frequency_itemset* : Mapping of itemset with its frequency. key is itemset, value is frequency
	- *size_to_itemset* : Dictionary mapping size with itemsets ie size_to_itemset[1] = set(all itemsets of size 1)
	- *size_one_candidate_set* : set of items of size 1
	- *max_iterations* : maximum number of iterations for the algorithm to run
	- *count_transaction* : size of transaction list
	- *Final_items* : List of items having support > min_support. Each entry in the list is of the form (item, support)
	- *Final_rules* : List of rules having confidence > min_confidence. Each entry in the list is of the form ( (X,Y), confidence) where rule itself is of the form X -> Y
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
		self.transaction = []
		self.itemset = set()

		sql = "SELECT handle, pid FROM activity WHERE "
		for pid in self.list_pid:
			sql+="pid = \'"+str(pid)+"\' OR "
		sql=sql[:-3] 
		result = db.read(sql, self.cursor)
		Trans = defaultdict(list)
		for i in result :
			Trans[str(i[0])].append(str(i[1]))
		for i in Trans:
			self.transaction.append(frozenset(Trans[i]))
			#frozenset as it can be used as key for dicts
			for j in Trans[i]:
				self.itemset.add(frozenset([j]))
		self.count_transaction = len(self.transaction)

	def prune(self, itemset):
		'''
		|  Prune subset of itemset based on min_support
		'''
		result = set()
		localset = defaultdict(int)
		#default dict with all keys set to 0
	    
		for item in itemset:
			for t in self.transaction:
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
		print "\n\n"
		print "----Rules----"
		for rule in self.Final_rules:
			print "%s -> %s  confidence = %0.6f " % (str(rule[0][0]), str(rule[0][1]), rule[1])

	def run(self):
		'''
		|  Run the Apriori algorithm
		|  Return frequent itemsets and association rules
		'''
		self.initialise()
		self.frequency_itemset = defaultdict(int)
		self.size_to_itemset = {}
		self.size_one_candidate_set = self.prune(itemset = self.itemset)
		current_candidate_set = self.size_one_candidate_set
		k = 2
		while(current_candidate_set != set([]) ): #or k!=self.max_iterations):
			self.size_to_itemset[k-1] = current_candidate_set
			current_candidate_set = helper.join_set(current_candidate_set, k)
			current_candidate_set = self.prune(current_candidate_set)
			k+=1

		print "Number of iterations = ",k-1
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
