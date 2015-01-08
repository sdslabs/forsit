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
    from time import time
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    from time import sleep
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    from problem import problem
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

print "script was run at ", time()

# requests = cfscrape.create_requests()


tags = []
problem_list = []
problem_db = []

conn = db.connect('forsit')
cursor=conn.cursor()

def fetch_all():

    sql = "SELECT pid from problem WHERE MID(pid,1,3)=\"erd\""
    a = db.read(sql, cursor)
    for i in a:
        temp = str(i[0].encode('utf8'))
        problem_db.append(temp)

    sql = "SELECT tag from tag"
    a = db.read(sql, cursor)
    for i in a:
        tag = str(i[0].encode('utf8'))
        tags.append(tag)
    tag_sql = ""
    ptag_sql = ""
    problem_sql = "INSERT INTO problem (pid, name, attempt_count, correct_count, time) VALUES "
    tag_url = "http://erdos.sdslabs.co/tags.json"
    tag_r = requests.get(tag_url)
    if(tag_r.status_code != 200 ):
        print tag_r.status_code, " returned from ", tag_url
    else:
        tag_res = tag_r.json()['list']
        for i in tag_res:
            # print tag
            tag = str(i['name'])
            if(tag not in tags):
                tag_sql+="('" + tag + "','','"  + str(int(time())) + "'), "
            ptag_url = "http://erdos.sdslabs.co/tags/"+tag+".json"
            ptag_r = requests.get(ptag_url)
            if(ptag_r.status_code != 200 ):
                print ptag_r.status_code, " returned from ", ptag_url
            else:
                ptag_res = ptag_r.json()['problems']['list']                
                for i in ptag_res:
                    code = str(i['id'])
                    code = code.replace('"','\\"')
                    code = code.replace("'","\\'")
                    problem_url = "http://erdos.sdslabs.co/problems/"+code+".json"
                    prob = requests.get(problem_url)
                    prob = prob.json()['submissions']
                    correct = prob['correct']
                    total = prob['total']
                    code ="erd"+code
                    name = str(i['name'].encode('utf8'))
                    name = name.replace('"','\\"')
                    name = name.replace("'","\\'")
                    if(code not in problem_list):
                        problem_list.append(code)
                        problem_sql+="('" + code + "','" + name + "','" + str(total) + "','" + str(correct) + "','" + str(int(time())) + "'), "
                    if code not in problem_db:
                        ptag_sql+="('"+code+"', '"+tag+"'), "

        if(tag_sql!=""):
            tag_sql = tag_sql[:-2]
            tag_sql = "INSERT INTO tag (tag, description, time) VALUES " + tag_sql
            print tag_sql
            db.write(tag_sql, cursor, conn)

        problem_sql = problem_sql[:-2]
        problem_sql+=" ON DUPLICATE KEY UPDATE attempt_count=VALUES(attempt_count),correct_count=VALUES(correct_count),time=VALUES(time);"
        print problem_sql
        db.write(problem_sql, cursor, conn)
        
        if(ptag_sql!=""):
            ptag_sql = ptag_sql[:-2]
            ptag_sql = "INSERT INTO ptag (pid, tag) VALUES " + ptag_sql
            print ptag_sql
            db.write(ptag_sql, cursor, conn)

    sql_user = "SELECT cfs_handle FROM user"
    result = db.read(sql_user, cursor)
    user_list = {}
    #using dict for fast lookup
    for i in result:
        user_list[i[0]]=0
    new_user = []

    user_url = "http://erdos.sdslabs.co/users.json"
    user_r = requests.get(user_url)
    if(user_r.status_code != 200 ):
        print user_r.status_code, " returned from ", user_url
    else:
        user_res = user_r.json()['list']
        for i in user_res:
            if(i['username'] not in user_list):
                new_user.append(i['username'])

    if new_user:            
        sql = "INSERT INTO user (erd_handle) VALUES "
        for i in new_user:
            sql+="(\'"+str(i)+"\'), "
        sql=sql[:-2]
        db.write(sql, cursor, conn)
    
    sql = "UPDATE user SET erd_score = \
          (SELECT SUM((correct_count-3)/attempt_count) FROM problem WHERE pid IN \
          (SELECT DISTINCT(pid) FROM activity WHERE uid = user.uid AND MID(pid,1,3)=\'erd\' AND status = 1)\
          AND correct_count>3)"

    print sql
    db.write(sql, cursor, conn)  
    sleep(3)

def fetch_user_list_erd():
    '''
    |  Fetch List of all the users from Erdos
    '''
    erd_users = []
    url = "http://erdos.sdslabs.co/users.json"
    r = requests.get(url)
    if(r.status_code != 200 ):
        print r.status_code, " returned from ", r.url
    else:
        result = r.json()['list']
        for i in result:
            erd_users.append(i['username'])    
    return erd_users

def fetch_user_activity_erd(handle=""):
    '''
    |  Fetch User's activity from Erdos
    '''

    url = "http://erdos.sdslabs.co/activity/users/" + handle + ".json"
    handle = 'erd' + handle
    sql = "SELECT created_at FROM activity WHERE handle = \'" + handle + "\' ORDER BY created_at DESC LIMIT 1;"
    res = db.read(sql, cursor)
    if res == ():
        last_activity = 0
    else:
        last_activity = res[0][0]
    last_activity = int(last_activity)
    r = requests.get(url)
    if(r.status_code != 200 ):
        print r.status_code, " returned from ", r.url
    else:
        result = r.json()['list']
        result.reverse()
        for act in result:
            if int(act['created_at']) > last_activity:
                sql = "SELECT pid FROM activity WHERE pid = \'erd" + act['problem_id'] + "\' AND handle = \'" + handle + "\'"
                check = db.read(sql, cursor)
                difficulty = 0
                if check == ():
                    sql = "INSERT INTO activity (handle, pid, attempt_count, status, difficulty, created_at) VALUES ( \'" + handle + "\', \'erd" + act['problem_id'] + "\', '1', " + str(act['status']) + ", " + str(difficulty) + ", " + str(act['created_at']) + " )"
                    db.write(sql, cursor, conn)
                    p = problem("erd" + act['problem_id'])
                    if p.exists_in_db != -1:
                        tag_data = p.tag
                        for tag in tag_data:
                            sql = "SELECT tag FROM user_tag_score WHERE tag = \'" + tag + "\' AND handle = \'" + handle + "\'"
                            tag_check = db.read(sql, cursor)
                            if tag_check == ():
                                sql = "INSERT INTO user_tag_score (handle, tag, score) VALUES ( \'" + handle + "\' , \'" + tag + "\' , " + str(tag_data[tag]) + " )"
                                db.write(sql, cursor, conn)
                            else:
                                sql = "UPDATE user_tag_score SET score = score +" + str(tag_data[tag]) + " WHERE tag = \'" + tag + "\' AND handle = \'" + handle + "\'"
                                db.write(sql, cursor, conn)

                else:
                    sql = "UPDATE activity SET attempt_count = attempt_count + 1, status = " + str(act['status']) + ", difficulty = " + str(difficulty) + ", created_at = " + str(act['created_at']) + " WHERE pid = \'erd" + act['problem_id'] + "\' AND handle = \'" + handle + "\'"
                    db.write(sql, cursor, conn)

def fetch_user_activity_all():
    erd_users = fetch_user_list_erd()
    for handle in erd_users:
        fetch_user_activity_erd(handle)
        print "User activity for " + handle

fetch_all()
fetch_user_activity_all()
# fetch_user_activity_erd("TheOrganicGypsy")
cursor.close()