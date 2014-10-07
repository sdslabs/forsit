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

proxies = {
    "http": "http://user:pass@10.10.1.10:3128/"
}

tags = {}
precise = {}

def fetch_tag_from_page(pageno):
    url = "http://codeforces.com/problemset/page/"
    r = requests.get(url+str(pageno), proxies=proxies)
    # print r.text
    # print r.status_code
    if(r.status_code != 200):
        print r.status_code, " returned from ", url
        return -1
    else:
        soup = BeautifulSoup(r.text)
        pagenext = soup.findAll("span", {"class" : "inactive"})
        results = soup.findAll("a", {"class" : "notice"})
        for i in results:
            a = i['title'].encode('utf8')
            # print a
            temp = i['href'].split('/tags/')
            # print temp[1]   
            tags[a] = temp[1]
    
        print pageno, " pages done"
        # print pagenext
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

    # print len(tags.keys())    
    # for i in tags.keys():
    #     print i, " ", tags[i]        

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
    # Create a cursor object
    cursor=conn.cursor()
    result = db.write(sql, cursor, conn)
    cursor.close()
    
def fetch_all_problems():
    sql = "SELECT tag from tag"
    # print sql
    conn = db.connect('forsit')
    # Create a cursor object
    cursor=conn.cursor()
    a = db.read(sql, cursor)
    cursor.close()
    for i in a:
        # sleep(10)
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
            for j in problems:
                code = str(j['contestId'])+str(j['index'])
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
                    precise[code]=temp_list
                    # print temp_list

            for j in problemStatistics:
                code = 'cfs'+str(j['contestId'])+str(j['index'])
                precise[code].append(j['solvedCount'])

def insert_all_problems():
    sql = "INSERT INTO problem (pid, name, points, correct_count, time) VALUES "
    for j in precise.keys():
        i = precise[j]
        a = str(i[0]).replace('"','\\"')
        a = a.replace("'","\\'")
        b = i[1].encode('utf8')
        b = str(b).replace('"','\\"')
        b = b.replace("'","\\'")
        c = str(int(i[2]))
        d = str(i[3]) 
        sql+="('" + str(a) + "','" + str(b) + "','" + str(c) + "','" + str(d) + "','" + str(int(time())) + "'), "

    sql = sql[:-2]
    print sql
    # Open database connection
    conn = db.connect('forsit')
    # Create a cursor object
    cursor=conn.cursor()
    # result = db.write(sql, cursor, conn)
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
        if i not in tag_list:
            new_tags.append(i)

    print new_tags
    print "\n"

    print tag_list
    print "\n"

    print tags.keys()
    print "\n"
    if(len(new_tags)>0):
        sql = "INSERT INTO tag (tag, description, time) VALUES "
        for i in new_tags:
            a = str(i).replace('"','\\"')
            a = a.replace("'","\\'")
            b = str(tags[i]).replace('"','\\"')
            b = str(tags[i]).replace("'","\\'")
            sql+="('" + str(b) + "','" + str(a) + "','" + str(int(time())) + "'), "
        sql = sql[:-2]
        print sql
        result = db.write(sql, cursor, conn)
    cursor.close()


# fetch_all_tags()
# insert_all_tags()
increment_tags()
# fetch_all_problems()
# insert_all_problems()