try:
    import random
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    from itertools import combinations
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))


def get_random_color(pastel_factor = 0.5):
	'''
	|  Return a random color represented as a list of form [a,b,c] where a,b,c correspond to RGB values of the random color
	'''
	return [round( (x+pastel_factor)/(1.0+pastel_factor), 6) for x in [random.uniform(0,1.0) for i in [1,2,3]]]

def color_distance(c1,c2):
	'''
	|  Return a distance-like measure given 2 colors c1 and c2
	|  Colors are represented as a list of form [a,b,c] where a,b,c correspond to RGB values
	'''
	return sum([abs(x[0]-x[1]) for x in zip(c1,c2)])

def generate_new_color(N,pastel_factor = 0.5):
	'''
    Input 
	- N : Number of colors of be returned
	- pastel_factor : pastel factor of the colors
    Return a list of n colors where each color is represented as a list of form [a,b,c] where a,b,c correspond to RGB values
	'''
	colors_ret = []
	color = get_random_color(pastel_factor = pastel_factor)
	colors_ret.append(color)
	for i in range(1, N):
		max_distance = None
		best_color = None
		for j in range(0,100):
			color = get_random_color(pastel_factor = pastel_factor)
			best_distance = min([color_distance(color,c) for c in colors_ret])
			if not max_distance or best_distance > max_distance:
				max_distance = best_distance
				best_color = color
		colors_ret.append(best_color)
	return colors_ret

def subset(arr):
	'''
	|  Return subsets of set arr
	|  Subsets are returned in form of a list of frozensets
	'''
	ret = []
	for i in range(1,len(arr)+1):
		for j in combinations(arr, i):
			ret.append(frozenset(j))
	return ret

def join_set(item_set, length):
	'''
	|  Return sets of size length by taking join of item_set with itself
	|  Sets are returned in form of a set comprising of the new sets
	'''
	ret = []
	for i in item_set:
		for j in item_set:
			temp_set = i.union(j)
			if(len(temp_set) == length):
				ret.append(temp_set)
	return set(ret)