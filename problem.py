try:
    import db
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import requests
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import numpy as np
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    from base import base
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    from graph import plot_points_distribution_cfs
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))
    
try:
    from graph import plot_difficulty_distribution_cfs
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

import math
from math import sqrt
import time
import operator


class problem(base):

    '''
    - *pid* : problem id. For erdos problems, it starts with *erd* and for codeforces problems it starts with *cfs*
    - *cfs_max_score* : Defines the default max score for a competiton on codeforces. 
      The codeforces API has some bugs and it does not return all the problems.
      So for some contests, the max score is returned incorrect. That error is accounted by taking max of cfs_max_score and actual max score of a contest 
    - *lower_threshold* : The minimum number of problems, of difficulty less that of pid, which are to be considered for recommendation. It defines the candidate set on lower side. 
    - *upper_threshold* : The maximum number of problems, of difficulty more than or equal to that of pid, which are to be considered for recommendation. It defines the candidate set on upper side. 
    - *number_to_recommend* : Number of problems to recommend. 

    '''
    
    def __init__(self, pid, erd_problem_difficulty = {}, conn = '', batchmode = 0, cfs_max_score = 3000, lower_threshold = 25, upper_threshold = 25, number_to_recommend = 5):
        
        self.pid = str(pid)
        self.cfs_max_score = str(cfs_max_score)
        # self.conn = db.connect()
        # self.cursor = self.conn.cursor()
        self.lower_threshold = lower_threshold
        self.upper_threshold = upper_threshold
        self.number_to_recommend = number_to_recommend
        self.erd_problem_difficulty = erd_problem_difficulty
        self.batchmode = batchmode
        if self.batchmode :
            self.conn = conn
            self.remote_conn = ''
            self.remote_cursor = ''
        else:
            self.conn = db.connect()
            self.remote_conn = db.connect('remote')
            self.remote_cursor = self.remote_conn.cursor()
        self.cursor = self.conn.cursor() 
        # self.exists_in_db = self.fetch_info()
        # self.create_difficulty_matrix()

    def fetch_info(self):

        '''
        |  Fetch problem information from *problem* table from the db
        |  Return 1 if corresponding entry was found in the db. The variables are initialised as well.
        |  Return -1 if no results found
        '''
        
        sql = "SELECT points, correct_count, attempt_count, (SELECT MAX(points) FROM problem \
               WHERE contestId = P.contestId ) AS max_points FROM problem P \
               WHERE pid = \'" + self.pid + "\'"
        
        # print sql
        result = db.read(sql, self.cursor)
        if result == ():
            return -1

        for i in result :
            self.points = float(i[0])
            self.correct_count = float(i[1])
            self.attempt_count = float(i[2])
            if(self.points>0):
                self.difficulty = round( (self.points/( max (3000.0,float( i[3] ) ) ) ), 6)
            else:
                self.difficulty = round(self.correct_count/self.attempt_count, 6)
        
        sql = "SELECT count(*) FROM problem WHERE MID(pid,1,3) = \'" + self.pid[0:3] + "\'"
        
        # print sql
        result = db.read(sql, self.cursor)              
        number_of_problems = result[0][0]
        self.tag = {}

        # using tf-idf approach for assigning weights to tags
        # tf(tag, problem) = 1/(number of tags in the given problem)
        # idf(tag, problem) = log(total number of problems/number of problems with that tag)
        # tf tells how important a tag is for a given problem.
        # idf tell how common a tag is across all the problems

        sql = "SELECT ptag.tag, ROUND( LOG2("+str(number_of_problems)+"/count), 6) FROM ptag, tag WHERE \
               ptag.tag = tag.tag AND pid = \'" + self.pid + "\'"
        
        # print sql
        result = db.read(sql, self.cursor)
        number_of_tags = len(result)
        normalisation_factor = 0 
        #Since the weights are exceeding 1, we normalise using sum of weights of tags

        checksum = 0
        #a redundant checksum to make sure that the weights add up to 1

        for i in result :
            tag = str(i[0].encode('utf8'))
            self.tag[tag] = float(i[1]) / number_of_tags
            self.tag[tag] = round(self.tag[tag],6)
            normalisation_factor+=self.tag[tag]

        for tag in self.tag:
            self.tag[tag]/=normalisation_factor
            self.tag[tag] = round(self.tag[tag],6)
            checksum+=self.tag[tag]
        # print "the final checksum = ", checksum   
        return 1

    def print_info(self):
        '''Print problem information from *problem* table from the db'''
        if self.exists_in_db != -1:
            print "pid = ", self.pid
            print "points = ", self.points
            print "correct_count = ", self.correct_count
            print "attempt_count = ", self.attempt_count
            print "difficulty = ", self.difficulty 
            print "Tag count : "
            for i in self.tag:
                print i, "    ",self.tag[i]
        else:
            print "No Results Found!"

    #@profile       
    def reco_algo(self, sql):
        '''
        Input 
        - *sql* : sql query which would generate the set of candidates for which similarity would be computed. It is generated via the find_similar_cfs() or find_similar_erdos()
        Return a list of recommended problems. Each entry in the list is a tuple of the 
        form (pid, score) where more score means better results. The list is sorted in desc order
        by score.
        '''
        # sql = "   SELECT ptag.pid, ptag.tag, (correct_count)/attempt_count as difficulty \
        #       FROM problem, ptag \
        #       WHERE problem.pid != \'" + self.pid + "\' AND problem.pid = ptag.pid  \
        #       AND problem.pid IN \
        #       (SELECT ptag.pid FROM problem, ptag WHERE ptag.tag IN \
        #       (SELECT tag FROM ptag where pid = \'" + self.pid + "\') AND MID(problem.pid,1,3)=\'erd\' ) \
        #       AND problem.pid NOT IN (SELECT pid FROM activity WHERE MID(pid,1,3)=\'erd\' AND uid = \'"+str(uid)+"\')\
        #       HAVING difficulty BETWEEN " + str(self.lower_incorrect_attempt) + " AND " + str(self.upper_correct_attempt)             


        result = db.read(sql, self.cursor)
        problem = {}
        #mapping of problem code with a list of tags
        score = {}
        #mapping of score of problem code with its score 
        difficulty = {}
        #mapping of problem code with difficulty
        status = {}
        #mapping of problem code with its status

        for i in result:
            code = str(i[0].encode('utf8'))
            tag = str(i[1].encode('utf8'))
            problem_difficulty = float(i[2])
            
            #status 0 means problem is recommended only if the submission gave wrong answer
            #status 1  means problem is recommended only if the submission gave right answer
            #status 2 means problem is recommended in both the cases

            flag1 = 0
            flag2 = 0
            if(self.lower_incorrect_attempt<=problem_difficulty<=self.upper_incorrect_attempt):
                flag1 = 1
            if(self.lower_correct_attempt<=problem_difficulty<=self.upper_correct_attempt):
                flag2 = 1
            if(flag1 and flag2):
                status[code] = '2'
            elif(flag1):
                status[code] = '0'
            else:
                status[code] = '1'

            if code not in problem:
                problem[code] = []
                score[code] = 0
                difficulty[code] = round (abs(problem_difficulty-self.difficulty), 6)
            problem[code].append(tag)

        for code in problem:
            # instead of using nfactor as the number of tags, we should normalise only for those 
            # tags which do not occur in self.tag else the results are biased towards the highest
            # weighted tag. We can still improve the normalisation factor by using a slow
            # growing function. Also currently the common tags are being penalised just once 
            # ie while calculating the idf score for the problem.

            nfactor = 1
            for tag in problem[code]:
                if tag not in self.tag:
                    nfactor+=1
                    continue
                score[code]+=self.tag[tag]
            score[code]=round( (score[code]/nfactor), 6)
        sorted_score = sorted(score.items(), key=operator.itemgetter(1), reverse = 1)
        return sorted_score, status

    #@profile
    def find_similar_erdos(self, uid = '0', user_difficulty = 0):
        '''
        Input 
        - *uid* : user for whom these recommendations are being generated
        - *user_difficulty* : difficulty rating for the user. difficulty = 0 means the user has not attempted any problem so far 
        Generate an sql query (which would generate the set of candidates for which similarity would be computed) 
        and then calls the reco_algo() with the sql as input. The top k results from this function are then logged
        into mysql with appropriate insertions/updates/deletions
        '''
        # sql = "SELECT erd_score FROM user where uid = \'"+str(uid)+"\'"
        # result = db.read(sql, self.cursor)
        # user_difficulty = 0
        # if result:
        #   user_difficulty = float(result[0][0])

        res_incorrect_attempt = self.gen_window(status=0, user_difficulty = user_difficulty)
        self.upper_incorrect_attempt = res_incorrect_attempt[0]
        self.lower_incorrect_attempt = res_incorrect_attempt[1]

        res_correct_attempt = self.gen_window(status=1, user_difficulty = user_difficulty)
        self.upper_correct_attempt = res_correct_attempt[0]
        self.lower_correct_attempt = res_correct_attempt[1]
            
        sql = " SELECT ptag.pid, ptag.tag, (correct_count)/attempt_count as difficulty \
                FROM problem, ptag \
                WHERE problem.pid != \'" + self.pid + "\' AND problem.pid = ptag.pid  \
                AND problem.pid IN \
                (SELECT ptag.pid FROM problem, ptag WHERE ptag.tag IN \
                (SELECT tag FROM ptag where pid = \'" + self.pid + "\') AND MID(problem.pid,1,3)=\'erd\' ) \
                AND problem.pid NOT IN (SELECT pid FROM activity WHERE MID(pid,1,3)=\'erd\' AND uid = \'"+str(uid)+"\')\
                HAVING difficulty BETWEEN " + str(self.lower_incorrect_attempt) + " AND " + str(self.upper_correct_attempt)             
        # print sql
        if self.batchmode : 
            return self.log_results_db_batchmode(sql, uid, "erd")
        else:
            self.log_results_db(sql, uid, "erd")

    def find_similar_bckdr(self, uid = '0', user_difficulty = 0):
        cursor = self.conn.cursor() 
        chal_sql = "SELECT `pid` FROM `problem`"
        cursor.execute(chal_sql)
        chals = cursor.fetchall()   
        chal_t_sql = "SELECT `pid` FROM `ptag`"
        tag_sql = "SELECT `tag` FROM `ptag`"
        cursor.execute(chal_t_sql)
        chal_t = cursor.fetchall()
        cursor.execute(tag_sql)
        tag = cursor.fetchall()
        tags_sql = "SELECT `tag` FROM `tag`"
        cursor.execute(tags_sql)
        tags_t = cursor.fetchall()
        
        def tags(p_id):
            tag_sql = "SELECT `tag` FROM `ptag` WHERE pid = \'" + p_id + "\'"
            cursor = self.conn.cursor()
            cursor.execute(tag_sql)
            taggsf = cursor.fetchall()
            return taggsf   

        def create_tag_matrix(p_id):
            i = 0
            chals_tag = []
            while(i<len(tags_t)):
                tags_match = tags(p_id)
                if tags_t[i] in tags_match:
                    chals_tag = np.append(chals_tag,1)
                else:
                    chals_tag = np.append(chals_tag,0)
                i = i+1
            return chals_tag

        def tag_dict():
            dict_tag = {}
            for i in chals:
                dict_tag[i[0]] = {}
                k = 0
                for j in tags_t:
                    dict_tag[i[0]][j[0]] = create_tag_matrix(i[0])[k]
                    k = k+1
            return dict_tag



        def sim_pearson(create_tag_matrix,p1,p2):
            # Get the list of mutually rated items
            si={}
            for item in create_tag_matrix[p1]:
                if item in create_tag_matrix[p2]: si[item]=1
            # Find the number of elements
            n=len(si)
            # if they are no ratings in common, return 0
            if n==0: return 0
            # Add up all the preferences
            sum1=sum([create_tag_matrix[p1][it] for it in si])
            sum2=sum([create_tag_matrix[p2][it] for it in si])
            # Sum up the squares
            sum1Sq=sum([pow(create_tag_matrix[p1][it],2) for it in si])
            sum2Sq=sum([pow(create_tag_matrix[p2][it],2) for it in si])
            # Sum up the products
            pSum=sum([create_tag_matrix[p1][it]*create_tag_matrix[p2][it] for it in si])
            # Calculate Pearson score
            num=pSum-(sum1*sum2/n)
            den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
            if den==0: return 0
            r=num/den
            return r


        # Returns the best matches for person from the prefs dictionary.
        # Number of results and similarity function are optional params.
        def topMatches(create_tag_matrix,person,n,similarity = sim_pearson):
            scores=[(similarity(create_tag_matrix,person,other[0]),other[0])
            for other in chals if other[0]!=person]
                # Sort the list so the highest scores appear at the top
            scores.sort( )
            scores.reverse( )
            return scores[0:n]

        reco_problems = topMatches(tag_dict(),self.pid,3)
        for reco in reco_problems:
            sql_insert  = ' INSERT INTO problem_reco (base_pid , reco_pid, score) VALUES (self.pid, reco[1],reco[0])'
            cursor.execute(sql_insert)
        """
        sql = " SELECT ptag.pid, ptag.tag \
                FROM problem, ptag \
                WHERE problem.pid != \'" + self.pid + "\' AND problem.pid = ptag.pid  \
                AND problem.pid IN \
                (SELECT ptag.pid FROM problem, ptag WHERE ptag.tag IN \
                (SELECT tag FROM ptag where pid = \'" + self.pid + "\') AND MID(problem.pid,1,3)=\'bkd\' ) \
                AND problem.pid NOT IN (SELECT pid FROM activity WHERE MID(pid,1,3)=\'bkd\' AND uid = \'"+str(uid)+"\'))                
        # print sql
        if self.batchmode : 
            return self.log_results_db_batchmode(sql, uid, "bkd")
        else:
            self.log_results_db(sql, uid, "bkd")
        """ 

    def find_similar_cfs(self, status = 0, uid = 0, user_difficulty = 0):
        '''
        Input 
        - *status* : status = 1 if problem was solved correctly else 0
        - *uid* : user for whom these recommendations are being generated 
        - *user_difficulty* : difficulty rating for the user. difficulty = 0 means the user has not attempted any problem so far
        Generate an sql query (which would generate the set of candidates for which similarity would be computed) 
        and then calls the reco_algo() with the sql as input. The top k results from this function are then logged
        into mysql with appropriate insertions/updates/deletions
        '''
        
        
        sql = "SELECT P.points/GREATEST("+self.cfs_max_score+", (SELECT MAX(points) FROM problem \
            WHERE contestId = P.contestId)) as difficulty FROM problem P \
            WHERE MID(P.pid,1,3) = \"cfs\" AND P.points>0"
        res = self.gen_window(sql, status, user_difficulty)
        # print res
        upper = res[0]
        lower = res[1]
        sql = " SELECT ptag.pid, ptag.tag, P.points/GREATEST(3000, (SELECT MAX(points) FROM problem \
                WHERE contestId = P.contestId)) as difficulty FROM problem P, ptag \
                WHERE P.pid != \'" + self.pid + "\' AND P.pid = ptag.pid AND P.pid IN \
                (SELECT ptag.pid FROM problem, ptag WHERE ptag.tag IN \
                (SELECT tag FROM ptag where pid = \'" + self.pid + "\') \
                AND MID(problem.pid,1,3)=\'cfs\' ) \
                AND P.pid NOT IN (SELECT pid FROM activity WHERE MID(pid,1,3)=\'cfs\' AND uid = \'"+str(uid)+"\')\
                HAVING difficulty BETWEEN " + str(lower) + " AND " + str(upper)
        # print sql
        self.log_results_db(sql, status, uid, "cfs")

    #@profile
    def log_results_db_batchmode(self, sql, uid = 0, app = "erd"):
        '''
        Input
        - *sql* : query to generate recommendation results  
        - *status* : status = 1 if problem was solved correctly else 0
        - *uid* : user for whom these recommendations are being generated 
        - *app* : "erd" for erdos and "cfs" for codeforces
        Output
        Return the sql query to be run to update the database
        '''
        result = self.reco_algo(sql)
        sorted_score = result[0]
        status = result[1]
        sql = ""
        k = min(len(sorted_score), self.number_to_recommend)
        for i in range(0,k):
            a = str(int(time.time()))
            sql+="(\'"+str(uid)+"\', \'"+str(self.pid)+"\', \'"+status[sorted_score[i][0]]+"\', \'"+str(sorted_score[i][0])+"\', \'"+str(sorted_score[i][1])+"\', \'"+a+"\', \'"+a+"\', \'0\', \'0\' ), "
        return sql
        
    def log_results_db(self, sql, uid = 0, app = "erd"):
        '''
        Input
        - *sql* : query to generate recommendation results  
        - *status* : status = 1 if problem was solved correctly else 0
        - *uid* : user for whom these recommendations are being generated 
        - *app* : "erd" for erdos and "cfs" for codeforces
        Output
        Logs the results in db with appropriate insertions/updates/deletions
        '''
        # print sql
        result = self.reco_algo(sql)
        sorted_score = result[0]
        status = result[1]
        # print sorted_score
        sql = "SELECT reco_pid, status FROM problem_reco WHERE uid = \'"+str(uid)+"\' AND base_pid =\'"+str(self.pid)+"\' AND MID(reco_pid,1,3) = \'"+str(app)+"\'"
        # print sql
        results = db.read(sql, self.remote_cursor)
        if not results:
            #Making entry for the first time
            sql = "INSERT INTO problem_reco (uid, base_pid, status, reco_pid, score, time_created, time_updated, state, is_deleted) VALUES "
            k = min(len(sorted_score), self.number_to_recommend)
            for i in range(0,k):
                a = str(int(time.time()))
                sql+="(\'"+str(uid)+"\', \'"+str(self.pid)+"\', \'"+status[sorted_score[i][0]]+"\', \'"+str(sorted_score[i][0])+"\', \'"+str(sorted_score[i][1])+"\', \'"+a+"\', \'"+a+"\', \'0\', \'0\' ), "
            # print sql
            sql = sql[:-2]
            # print sql
            # print sql[:-1]
            if(sql[-1] == ')'):
                # print "shagun"
                # print sql
                db.write(sql, self.remote_cursor, self.remote_conn)
        else:
            to_delete = []
            for i in results:
                to_delete.append(i[0])
            to_update = []
            to_insert = []
            k = min(len(sorted_score), self.number_to_recommend)
            for i in range(0,k):
                if sorted_score[i][0] not in to_delete:
                    to_insert.append(sorted_score[i])
                else:
                    to_update.append(sorted_score[i])
                    # to_delete.remove(sorted_score[i][0])

            if to_delete:                   
                sql_delete = "DELETE FROM problem_reco WHERE uid = \'"+str(uid)+"\' AND reco_pid IN ("
                for i in to_delete:
                    sql_delete+="\'"+str(i)+"\',"
                sql_delete=sql_delete[:-1]
                sql_delete=sql_delete+")"
                db.write(sql_delete, self.remote_cursor, self.remote_conn)

            if to_update:       
                sql_update = "UPDATE problem_reco SET score = CASE reco_pid "
                status_update = ", status = CASE reco_pid "

                where_clause = " WHERE uid = \'"+str(uid)+"\' AND reco_pid IN ("
                for i in to_update:
                    sql_update+="WHEN \'"+str(i[0])+"\' THEN "+str(i[1])+"\n"
                    status_update+="WHEN \'"+str(i[0])+"\' THEN "+status[i[0]]+"\n"
                    where_clause+="\'"+str(i[0])+"\',"
                sql_update+=" END"+status_update
                sql_update+=" END, time_updated = "+str(int(time.time()))
                sql_update+=where_clause[:-1]
                sql_update=sql_update+")"
                # print sql_update
                # print "shagun"
                db.write(sql_update, self.remote_cursor, self.remote_conn)

            if to_insert:                   
                sql_insert = "INSERT INTO problem_reco (uid, base_pid, status, reco_pid, score, time_created, time_updated, state) VALUES "
                for i in to_insert:
                    a = str(int(time.time()))
                    sql_insert+="(\'"+str(uid)+"\', \'"+str(self.pid)+"\', \'"+status[i[0]]+"\', \'"+str(i[0])+"\', \'"+str(i[1])+"\', \'"+a+"\', \'"+a+"\', \'0\' ), "
                sql_insert = sql_insert[:-2]
                # print sql_insert
                db.write(sql_insert, self.remote_cursor, self.remote_conn)
                            
    #@profile
    def gen_window(self, status = 0, user_difficulty = 0, app = "erd"):
        '''
        Input 
        - *status* : status = 1 if problem was solved correctly else 0
        - *user_difficulty* : difficulty rating for the user. difficulty = 0 means the user has not attempted any problem so far
        Return a difficulty window to be used by find_similar_cfs() or find_similar_erd(). 
        The window is returned as a tuple of form (upper_limit,lower_limit)
        '''
        
        # print sql
        if(app == "erd"):
            result = self.erd_problem_difficulty
        else:
            result = []
        # result = db.read(sql, self.cursor)
        difficulty = {}
        for i in result:
            point = float(i[0])
            if point in difficulty:
                difficulty[point]+=1
            else:
                difficulty[point] = 1
        sorted_difficulty = sorted(difficulty.items(), key=operator.itemgetter(0), reverse = 0)
        
        # print len(sorted_difficulty)
        # for i in sorted_difficulty:
        #   print i
        i = 0
        imax = len(sorted_difficulty)-1
        hi = imax
        lo = 0  
        i = (hi+lo)/2
        while(hi>=lo):
            i = (hi+lo)/2
            a = sorted_difficulty[i][0] - self.difficulty
            if(a>0):
                hi = i-1
            elif(a<0):
                lo = i+1
            else:
                break
        # print i
        if status == 1:
            #correct submission
            upper = sorted_difficulty[i][1]
            max_len = len(sorted_difficulty)-1
            j = i
            #increase the right end of the window till the upper threshold is met
            while(upper < self.upper_threshold and j < max_len):
                # print j
                j+=1
                # print j
                upper+=sorted_difficulty[j][1]
                # print upper
            x = float(sorted_difficulty[j][0] - self.difficulty)
            # print x
            # how much deviation we allowed on the right side of self.difficulty
            # we allow only half of this deviation on the left hand side
            # the reason is that the difficulty of the problem will lie either 
            # on one of the peaks in which case x = 0 or near a right peak in which case 
            # we wont need many values on the left or near a left peak in which case our x
            # would be large enough to cover the left peak as well. Same logic for the next
            # part of the condition
            if (self.difficulty+x > user_difficulty):
                return (self.difficulty+x, self.difficulty-x/2)
            else:
                return(user_difficulty, self.difficulty-x/2)    

        else:
            #incorrect submission
            lower = sorted_difficulty[i-1][1]
            k=i-1
            while(lower < self.lower_threshold):
                k-=1
                lower+=sorted_difficulty[k][1]
            x = self.difficulty - sorted_difficulty[k][0]
            if (self.difficulty+x/2 < user_difficulty or user_difficulty == 0):
                return (self.difficulty+x/2, self.difficulty-x)
            else:
                return (user_difficulty, self.difficulty-x)

    def create_difficulty_matrix(self):
        self.difficulty_matrix = {}
        conn = db.connect()
        cursor=conn.cursor()
        sql = "SELECT * FROM activity"
        result = db.read(sql, cursor)
        for i in result:
            user = str(i[0].encode('utf8'))
            problem = str(i[1].encode('utf8'))
            if not self.difficulty_matrix.has_key(problem):
                self.difficulty_matrix[problem] = {}
            self.difficulty_matrix[problem][user] = i[4]

    def find_correlation(self, u1, u2):

        si = {}
        for item in self.difficulty_matrix[u1]:
            if item in self.difficulty_matrix[u2]:
                si[item] = 1
        n = len(si)

        n1 = len(self.difficulty_matrix[u1])
        n2 = len(self.difficulty_matrix[u2])

        # if there are no common users, return 0
        if n == 0:
            return 0

        sum1 = sum([self.difficulty_matrix[u1][it] for it in si])
        sum2 = sum([self.difficulty_matrix[u2][it] for it in si])

        # Sum up the squares
        sum1Sq = sum([pow(self.difficulty_matrix[u1][it],2) for it in si])
        sum2Sq = sum([pow(self.difficulty_matrix[u2][it],2) for it in si])

        # Sum up the products
        pSum = sum([self.difficulty_matrix[u1][it] * self.difficulty_matrix[u2][it] for it in si])

        # Calculate Pearson score
        num = pSum - (sum1*sum2/n)
        den = math.sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))

        if den == 0:
            return 0
        r = num/den
        return (r*n)/(n1+n2)

    def find_correlated_problems(self):
        self.correlated_problems = {}
        for p in self.difficulty_matrix.keys():
            if p != self.pid:
                self.correlated_problems[p] = self.find_correlation(self.pid, p)
        self.correlated_problems = sorted(self.correlated_problems.items(), key=operator.itemgetter(1), reverse = 1)

if __name__ == "__main__":

    

    # sql = "SELECT cfs_score FROM user where uid = \'"+str(uid)+"\'"
    #   print sql
    #   result = db.read(sql, self.cursor)
    #   user_difficulty = 0
    #   if result:
    #       user_difficulty = float(result[0][0])

    # a.find_similar_erdos()
    print "\n\n\n\n"
    # plot_points_distribution_cfs(max_flag=1, min_flag = 1)
    # plot_difficulty_distribution_cfs(a.cfs_max_score)
    # a.gen_window_cfs()

    # print "\n"
    # print "\n"
    # for item in a.find_similar_cfs(1)[:10]:
    #   print item
    #   b = problem(item[0])
    #   b.print_info()
    #   print "\n"
    # a.find_correlated_problems()
    # print "\n"
    # print "\n"
    # print "\n"
    # for item in a.correlated_problems[:10]:
    #   print item
    #   b = problem(item[0])
    #   b.print_info()
    #   print "\n"
