try:
    import db
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
    import time
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import matplotlib.pyplot as plt
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import matplotlib.patches as mpatches
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

    

def plot_points_distribution_cfs(max_flag = 1, min_flag = 0):

	'''
	|  Plot the distribution of max and min points for a competiton for codeforces

	|  Input 
	|  - *max_flag* : if max_flag = 1 then print the distribution of max points else do not print
	|  - *min_flag* : if min_flag = 1 then print the distribution of min points else do not print
	|  - *app_name* : Name of the app ie forsit

	|  Conclusion from the plots when used with codeforces data : 
	
	|  -  Not all the problems can be fetched by the codeforces API. 
	|  There are many problems with max score as 500 or 1000. Manually checking those problems 
	|  revealed that only problems with code D or E were missing for such contests. 
	|  The same situation exists in reverse as well where problems with code A or B are missing.
	
	|  -  There are few contests which do not follow the standard codeforces scoring criteria. 
	|  These contests had scores in the range 20 to 70 (manually checked)
	'''

	a=time.time()

	sql = "SELECT (SELECT MAX(points) FROM problem WHERE contestId = P.contestId), \
		   (SELECT MIN(points) FROM problem WHERE contestId = P.contestId) \
		   FROM problem P WHERE P.pid in (SELECT pid FROM problem GROUP BY \
		   contestId HAVING MID( pid, 1, 3 ) = \"cfs\") AND points > 0 "

	print sql
	conn = db.connect()
	cursor = conn.cursor()
	result = db.read(sql, cursor)
	print "time to execute sql = ", time.time()-a
	max_score = {}
	min_score = {}

	for i in result:
		max_point = float(i[0])
		min_point = float(i[1])
		if max_point in max_score:
			max_score[max_point]+=1
		else:
			max_score[max_point] = 1
		if min_point in min_score:
			min_score[min_point]+=1
		else:
			min_score[min_point] = 1
	if(max_flag == 1):
		sorted_max_score = sorted(max_score.items(), key=operator.itemgetter(1), reverse = 1)
		print "Plot of Max Score"
		for i in sorted_max_score:
			print i
		plt.figure()
		plt.plot(max_score.keys(), max_score.values(), 'ro')
		plt.show()
	if(min_flag == 1):
		sorted_min_score = sorted(min_score.items(), key=operator.itemgetter(1), reverse = 1)
		print "Plot of Min Score"
		for i in sorted_min_score:
			print i
		plt.figure()
		plt.plot(min_score.keys(), min_score.values(), 'bs')
		plt.show()
	cursor.close()
	conn.close()	

def plot_difficulty_distribution_cfs(cfs_max_score):
	'''
	|  Plot the distribution of number of problems vs difficulty level
	max and min points for a competiton for codeforces

	|  Input 
	|  - *cfs_max_score* : Defines the default max score for a competiton on codeforces.
	   For further information on this variable, check problem module  
	|  - *app_name* : Name of the app ie forsit

	|  Conclusion from the plots when used with codeforces data : 
	
	|  -  Not all the problems can be fetched by the codeforces API. So the initial plots had some outliers.
	   Similar results were discovered using plots from *plot_points_distribution_cfs()*. 
	   Using *cfs_max_score* variable cleared these outliers. 
	'''

	a=time.time()
	sql = "SELECT P.pid, P.points, P.points/GREATEST("+cfs_max_score+", (SELECT MAX(points) FROM problem \
		WHERE contestId = P.contestId)) as difficulty FROM problem P \
		WHERE MID(P.pid,1,3) = \"cfs\" AND P.points>0"
	# print sql
	conn = db.connect()
	cursor = conn.cursor()
	result = db.read(sql, cursor)
	print "time to execute sql = ", time.time()-a
	difficulty = {}

	for i in result:
		pid = str(i[0].encode('utf8'))
		point = float(i[2])
		if point in difficulty:
			difficulty[point]+=1
		else:
			difficulty[point] = 1
	sorted_difficulty = sorted(difficulty.items(), key=operator.itemgetter(0), reverse = 1)
	x = []
	y = []

	for i in sorted_difficulty:
		x.append(i[0])
		y.append(i[1])
		# print i, " ", i[0]*3000
	plt.figure()
	plt.plot(difficulty.keys(), difficulty.values(), 'ro')
	plt.plot(x, y)
	plt.show()
	cursor.close()
	conn.close()	

def plot_concept_cfs(handle, show_legend = 0, show_x_ticks = 0, order = "DESC", upper_limit = 500, lower_limit = 0):
	
	'''
	|  Plot the distribution of tags attempted by the user for codeforces over time.

	|  Input 
	|  - *handle* : user handle on codeforces
	|  - *show_legend* : since legend could be very large, it is shown only if this flag is set on
	|  - *show_x_ticks* : since there are too many enteries along x-axis, a dotted line corresponing to each entry on x-axis is shown only if this flag is set on
	|  - *order* : order in which results are to fetched
	|  - *upper_limit* : upper limit on number of submissions to be fetched from the database. Set it to -1 to fetch all the submissions
	|  - *lower_limit* : lower limit on number of submissions to be fetched from the database. Set it to -1 to fetch all the submissions

	'''

	handle="cfs"+handle
	# sql = "SELECT "
	sql = "SELECT a.pid, p.tag, a.created_at FROM activity_concept as a, ptag as p WHERE a.pid = p.pid ORDER BY a.created_at " + order 
	if(lower_limit !=-1 or upper_limit !=-1):
		sql+=" LIMIT "+str(lower_limit)+","+str(upper_limit)
	conn = db.connect()
	print sql
	cursor = conn.cursor()
	result = db.read(sql, cursor)
	time_x = []
	#list of all discrete times when a problem was submitted
	tag_x = {}
	tag_y = {}
	#x and y coordinates for plotting tag occurence
	start_time = int(result[-1][2])
	time_x.append( (int(result[0][2]) - start_time) / (24*3600))
	for i in result:
		tag = str(i[1])
		submission_time = (int(i[2]) - start_time)/(24*3600)
		#rounded off to a day

		if time_x[-1] != submission_time:
			time_x.append(submission_time)
		if tag not in tag_x:
			tag_x[tag]=[]
			tag_y[tag] = []
			tag_x[tag].append(submission_time)
			tag_y[tag].append(1)
		else:
			if(tag_x[tag][-1]!=submission_time):
				tag_x[tag].append(submission_time)
				tag_y[tag].append(1)
	
	count = 0
	color = helper.generate_new_color(len(tag_x))
	
	plt.figure()

	for tag in tag_x:
		plt.plot(tag_x[tag], [y+count for y in tag_y[tag]], 's', color = color[count], label = tag)
		count+=1
	
	plt.grid(True, which = "both")
	plt.yticks([i for i in range(1,count+1)])
	
	if show_x_ticks == 1:
		plt.xticks(time_x)
		print time_x

	if show_legend == 1:
		plt.legend(loc='best')
		plt.axis(ymin = 0, ymax = count+2, xmax = time_x[0]+30 , xmin = time_x[-1]-1)
		#offset to make space for legend
	else:
		plt.axis(ymin = 0, ymax = count+2, xmax = time_x[0]+1 , xmin = time_x[-1]-1)
	
	plt.show()