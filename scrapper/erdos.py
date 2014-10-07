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

print "script was run at ", time()

tags = []
problem = []
problem_db = []

def fetch_all():

    sql = "SELECT pid from problem WHERE MID(pid,1,3)=\"erd\""
    conn = db.connect('forsit')
    cursor=conn.cursor()
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
                    if(code not in problem):
                        problem.append(code)
                        problem_sql+="('" + code + "','" + name + "','" + str(total) + "','" + str(correct) + "','" + str(int(time())) + "'), "
                    if code not in problem_db:
                        ptag_sql+="('"+code+"', '"+tag+"'),"

        if(tag_sql!=""):
            tag_sql = ptag_sql[:-2]
            tag_sql = "INSERT INTO tag (tag, description, time) VALUES " + tag_sql
            print tag_sql
            db.write(tag_sql, cursor, conn)

        problem_sql = problem_sql[:-2]
        problem_sql+="ON DUPLICATE KEY UPDATE attempt_count=VALUES(attempt_count),correct_count=VALUES(correct_count),time=VALUES(time);"
        print problem_sql
        db.write(problem_sql, cursor, conn)
        
        if(ptag_sql!=""):
            ptag_sql = ptag_sql[:-1]
            ptag_sql = "INSERT INTO ptag (pid, tag) VALUES " + ptag_sql
            print ptag_sql
            db.write(ptag_sql, cursor, conn)
        cursor.close()

    sleep(3)        

fetch_all()