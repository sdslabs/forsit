#! /usr/bin/python

try:
    import os
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import sys
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if not path in sys.path:
    sys.path.insert(1, path)
del path

try:
    import db
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import requests
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import ast
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    from bs4 import BeautifulSoup
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    from time import sleep
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    from time import time
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import string
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

print "script was run at ", time()

tags = {}
precise = {}
problem_list = []
new_problem = {}
tag_data = {}

def fetch_tag_from_page(pageno):
    url = "http://codeforces.com/problemset/page/"
    r = requests.get(url+str(pageno))
    if(r.status_code != 200):
        print r.status_code, " returned from ", url
        return -1
    else:
        soup = BeautifulSoup(r.text)
        pagenext = soup.findAll("span", {"class" : "inactive"})
        results = soup.findAll("a", {"class" : "notice"})
        for i in results:
            a = i['title'].encode('utf8')
            temp = i['href'].split('/tags/')
            tags[a] = temp[1]
    
        print pageno, " pages done"
        if(pagenext!=[]):
            return -1
        return 0

def fetch_all_tags():
    pageno = 1        
    fetch_tag_from_page(pageno)
    pageno+=1
    while(1):
        if(fetch_tag_from_page(pageno)<0):
            break        
        pageno+=1

def insert_all_tags():
    sql = "INSERT INTO tag (tag, description, time) VALUES "
    for i in tags.keys():
        a = str(i).replace('"','\\"')
        a = a.replace("'","\\'")
        b = str(tags[i]).replace('"','\\"')
        b = str(tags[i]).replace("'","\\'")
        sql+="('" + str(b) + "','" + str(a) + "','" + str(int(time())) + "'), "
    sql = sql[:-2]
    conn = db.connect('forsit')
    cursor=conn.cursor()
    result = db.write(sql, cursor, conn)
    cursor.close()
    
def fetch_all_problems():
    sql = "SELECT tag from tag"
    conn = db.connect('forsit')
    cursor=conn.cursor()
    a = db.read(sql, cursor)
    cursor.close()
    for i in a:
        url = "http://codeforces.com/api/problemset.problems"
        payload = {'tags':str(i[0].encode('utf8'))}
        r = requests.get(url, params=payload)
        if(r.status_code != 200 ):
            print r.status_code, " returned from ", r.url
            continue
        else:
            res = r.json()
            problems = res['result']['problems']    
            problemStatistics = res['result']['problemStatistics']  
            print problems
            print "\n\n\n"      
            for j in problems:
                code = str(j['contestId'])+str(j['index'].encode('utf8'))
                if(code not in precise.keys()):
                    temp_list = []
                    code = "cfs"+code
                    name = j['name']
                    if 'points' in j.keys():
                        points = j['points']
                    else:
                        points=-1
                    temp_list.append(code)
                    temp_list.append(name)
                    temp_list.append(points)
                    temp_list.append(str(j['contestId']))
                    precise[code]=temp_list

            for j in problemStatistics:
                code = 'cfs'+str(j['contestId'])+str(j['index'])
                precise[code].append(j['solvedCount'])

def insert_all_problems():
    sql = "INSERT INTO problem (pid, name, points, correct_count, time, contestId) VALUES "
    for j in precise:
        i = precise[j]
        a = str(i[0].encode('utf8')).replace('"','\\"')
        a = a.replace("'","\\'")
        b = i[1].encode('utf8')
        b = str(b).replace('"','\\"')
        b = b.replace("'","\\'")
        c = str(int(i[2]))
        d = str(i[4]) 
        e = str(i[3].encode('utf8'))
        sql+="('" + str(a) + "','" + str(b) + "','" + str(c) + "','" + str(d) + "','" + str(int(time())) + "', '" + str(e) + "'), "

    sql = sql[:-2]
    # print sql
    conn = db.connect('forsit')
    cursor=conn.cursor()
    result = db.write(sql, cursor, conn)
    cursor.close()

def increment_tags():
    fetch_all_tags()
    new_tags = []
    tag_list = []
    sql = "SELECT tag from tag"
    conn = db.connect('forsit')
    cursor=conn.cursor()
    a = db.read(sql, cursor)
    for i in a:
        print i
        tag = str(i[0].encode('utf8'))
        tag_list.append(tag)

    for i in tags.keys():
        if tags[i] not in tag_list:
            new_tags.append(i)

    if(len(new_tags)>0):
        sql = "INSERT INTO tag (tag, description, time) VALUES "
        for i in new_tags:
            a = str(i).replace('"','\\"')
            a = a.replace("'","\\'")
            b = str(tags[i]).replace('"','\\"')
            b = str(tags[i]).replace("'","\\'")
            sql+="('" + str(b) + "','" + str(a) + "','" + str(int(time())) + "'), "
        sql = sql[:-2]
        result = db.write(sql, cursor, conn)
    cursor.close()

def increment_problem_from_page(pageno, problem_list):
    url = "http://codeforces.com/problemset/page/"
    r = requests.get(url+str(pageno))
    if(r.status_code != 200):
        print r.status_code, " returned from ", url
        return -1
    else:
        soup = BeautifulSoup(r.text)
        p = soup.findAll("tr")
        for i in p:
            j = i.find("td", {"class" : "id"})
            if(j==None):
                continue
            new_pid = "cfs" + str( (j.text).strip() )
            if new_pid not in problem_list:
                new_problem[new_pid] = []
                temp = []
                k = i.find("div")
                l = k.find("a")
                new_name =  str(l.text.strip())
                temp.append(new_pid)
                temp.append(new_name)
                new_problem[new_pid] = temp
            else:
                return -1
        print pageno, " pages done"
        return 0

def increment_problem():
    # function to fetch newly added problems
    sql = "SELECT pid FROM `problem` WHERE MID(pid, 1, 3) = \"cfs\""
    conn = db.connect('forsit')
    cursor=conn.cursor()
    a = db.read(sql, cursor)
    problem_list = []
    for i in a:
        pid = str(i[0].encode('utf8'))
        problem_list.append(pid)
    pageno = 1        
    while(increment_problem_from_page(pageno, problem_list)==0):
        pageno+=1

    if(len(new_problem)>0):
        sql = "INSERT INTO problem (pid, name, time) VALUES "
        for i in new_problem.keys():
            j = new_problem[i]
            a = str(j[0]).replace('"','\\"')
            a = a.replace("'","\\'")
            b = j[1].encode('utf8')
            b = str(b).replace('"','\\"')
            b = b.replace("'","\\'")
            sql+="('" + str(a) + "','" + str(b) + "','" + str(int(time())) + "'), "

        sql = sql[:-2]
        conn = db.connect('forsit')
        cursor=conn.cursor()
        result = db.write(sql, cursor, conn)
        cursor.close()

def fetch_tags_problems():
    sql = "SELECT DISTINCT(pid) from ptag"
    conn = db.connect('forsit')
    cursor=conn.cursor()
    res = db.read(sql, cursor)
    problem_list = []
    for i in res:
        problem = str(i[0])
        if problem not in problem_list:
            problem_list.append(problem)

    sql = "SELECT tag from tag"
    conn = db.connect('forsit')
    cursor=conn.cursor()
    a = db.read(sql, cursor)
    for i in a:
        url = "http://codeforces.com/api/problemset.problems"
        tag = str(i[0].encode('utf8'))
        payload = {'tags':tag}
        r = requests.get(url, params=payload)
        if(r.status_code != 200 ):
            print r.status_code, " returned from ", r.url
            continue
        else:
            res = r.json()
            problems = res['result']['problems']    
            problemStatistics = res['result']['problemStatistics']
            sql = ""    
            for j in problems:
                code = str(j['contestId'])+str(j['index'])
                code = "cfs"+code
                if code not in problem_list:
                    sql +="(\'"+code+"\', \'"+tag+"\'), "
            if(sql!=""):
                print sql
                sql = sql[:-2]
                sql = "INSERT INTO ptag (pid, tag) VALUES " + sql
                print sql
                conn = db.connect('forsit')
                cursor=conn.cursor()
                result = db.write(sql, cursor, conn)
    cursor.close()

def update_tag_count():
    sql = "SELECT tag FROM tag"

    conn = db.connect('forsit')
    cursor=conn.cursor()
    a = db.read(sql, cursor)
    for i in a:
        tag = str(i[0].encode('utf8'))
        sql = "UPDATE tag SET count = (SELECT COUNT(*) FROM ptag WHERE tag = \'" + str(tag) + "\' ) WHERE tag = \'" + tag + "\'" 

        print sql
        conn = db.connect('forsit')
        cursor=conn.cursor()
        result = db.write(sql, cursor, conn)

def update_problem():

    fetch_all_problems()
    sql = "INSERT INTO problem (pid, name, points, correct_count, time) VALUES "
    for j in precise.keys():
        i = precise[j]
        a = str(i[0]).replace('"','\\"')
        a = a.replace("'","\\'")
        b = i[1].encode('utf8')
        b = str(b).replace('"','\\"')
        b = b.replace("'","\\'")
        b = b.replace(",","\,")
        c = str(int(i[2]))
        d = str(i[3]) 
        sql+="('" + str(a) + "','" + str(b) + "','" + str(c) + "','" + str(d) + "','" + str(int(time())) + "'), "

    sql = sql[:-2]
    sql+="ON DUPLICATE KEY UPDATE points=VALUES(points),correct_count=VALUES(correct_count),time=VALUES(time);"
    print sql
    conn = db.connect('forsit')
    cursor=conn.cursor()
    result = db.write(sql, cursor, conn)
    cursor.close()

def fetch_user_list_cfs():
    '''
    |  Fetch List of all the users from Codeforces
    '''
    cfs_users = []
    url = "http://codeforces.com/api/user.ratedList?activeOnly=true"
    r = requests.get(url)
    if(r.status_code != 200 ):
        print r.status_code, " returned from ", r.url
    else:
        result = r.json()['result']
        for i in result:
            cfs_users.append(i['handle'])
    return cfs_users

def fetch_user_activity_cfs(handle=""):
    '''
    |  Fetch User's activity from Codeforces
    '''
    conn = db.connect('forsit')
    cursor=conn.cursor()
    payload = {}
    payload['handle'] = handle
    handle = 'cfs' + handle
    sql = "SELECT created_at FROM activity WHERE handle = \'" + handle + "\' ORDER BY created_at DESC LIMIT 1;"
    res = db.read(sql, cursor)
    if res == ():
        last_activity = 0
    else:
        last_activity = res[0][0]
    last_activity = int(last_activity)
    r = requests.get(cfs_url, params=payload)
    if(r.status_code != 200 ):
        print r.status_code, " returned from ", r.url
    else:
        result = r.json()['result']
        result.reverse()
        for act in result:
            if int(act['creationTimeSeconds']) > last_activity:
                sql = "SELECT * FROM activity WHERE pid = \'cfs" + str(act['problem']['contestId']) + str(act['problem']['index']) + "\' AND handle = \'" + handle + "\'"
                check = db.read(sql, cursor)
                difficulty = 0
                if act['verdict'] == "OK":
                    status = 1
                else:
                    status = 0
                if check == ():
                    sql = "INSERT INTO activity (handle, pid, attempt_count, status, difficulty, created_at) VALUES ( \'" + handle + "\', \'cfs" + str(act['problem']['contestId']) + str(act['problem']['index']) + "\', '1', " + str(status) + ", " + str(difficulty) + ", " + str(act['creationTimeSeconds']) +" )"
                    db.write(sql, cursor, conn)
                else:
                    sql = "UPDATE activity SET attempt_count = attempt_count + 1, status = " + str(status) + ", difficulty = " + str(difficulty) + ", created_at = " + str(act['creationTimeSeconds']) + " WHERE pid = \'cfs" + str(act['problem']['contestId']) + str(act['problem']['index']) + "\' AND handle = \'" + handle + "\'"
                    db.write(sql, cursor, conn)

# @profile                  
def fetch_all_user_activity_cfs(handle=""):
    '''
    |  Fetch User's activity from Codeforces
    |  It is different from *fetch_user_activity_cfs()* as it logs each submission as a seperate entry to plot the concept trail
    '''
    difficulty = 0
    payload = {}
    payload['handle'] = handle
    handle = 'cfs' + handle
    sql = "SELECT created_at FROM activity_concept WHERE handle = \'" + handle + "\' ORDER BY created_at DESC LIMIT 1;"
    res = db.read(sql, cursor)
    if res == ():
        last_activity = 0
    else:
        last_activity = int(res[0][0])
    r = requests.get(cfs_url, params=payload)
    if(r.status_code != 200 ):
        print r.status_code, " returned from ", r.url
    else:
        result = r.json()['result']
        #profile reverse operation 
        result.reverse()
        count = 1
        sql = "INSERT INTO activity_concept (handle, pid, attempt_count, status, difficulty, created_at) VALUES "
        for act in result:
            #checking for min of the 2 values as for some cases, codeforces api is returning absured results for relatice time
            relative_time = min(7200, int(act['relativeTimeSeconds']))
            submission_time = int(act['creationTimeSeconds']) + relative_time
            if submission_time > last_activity:
                status = str(act['verdict'])
                if(status == "OK"):
                    status = "1"
                else:
                    status = "0"

                sql+="(\'" + handle + "\', \'cfs" + str(act['problem']['contestId']) + str(act['problem']['index']) + "\', '1', " + status + ", " + str(difficulty) + ", " + str(submission_time) +" ), "
                count+=1;
                if(count%5000 == 0):
                    sql = sql[:-2]
                    db.write(sql, cursor, conn)
                    print count, " entries made in the database"
                    sql = "INSERT INTO activity_concept (handle, pid, attempt_count, status, difficulty, created_at) VALUES " 
            else:
                break
        # print sql
        # print count
        if(sql[-2] == ","):
            sql = sql[:-2]
            db.write(sql, cursor, conn)

def fetch_user_activity_all():
    cfs_users = fetch_user_list_erd()
    for handle in cfs_users:
        fetch_user_activity_cfs(handle)
        print "User activity for " + handle

# fetch_all_tags()
# insert_all_tags()
# increment_tags()
fetch_all_problems()
insert_all_problems()
# increment_problem()
fetch_tags_problems()
update_tag_count()
# fetch_tags_problems()
# update_problem()