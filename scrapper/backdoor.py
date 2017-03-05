#! /usr/bin/python

import os,json
import sys
from time import time
from time import sleep

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if not path in sys.path:
    sys.path.insert(1, path)
del path

try:
    import requests
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    import db
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    from problem import problem
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

try:
    from bs4 import BeautifulSoup
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

print "script was run at ", time()

conn = db.connect()
cursor=conn.cursor()

remote_conn = db.connect('remote')
remote_cursor = remote_conn.cursor()

base_url = "https://backdoor.sdslabs.co"
headers = {'X-Requested-With': 'XMLHttpRequest'}

def fetch_problems():

    tag_orignal_sql = "INSERT IGNORE INTO `tag` (`tag`, `description`) VALUES "
    ptag_original_sql = "INSERT IGNORE INTO `ptag` (`pid`, `tag`) VALUES "
    problem_original_sql = "INSERT IGNORE INTO `problem` (`pid`, `name`) VALUES "
    problem_list = []
    problem_db = {}
    for i in range(0, 12):
        fetch_url = base_url + "/challenges?page=" + str(i)
        data = requests.get(fetch_url).text
        soup = BeautifulSoup(data)
        for link in soup.find_all('a', 'unsolved'):
            problem_list.append(link.get('title'))
    count = 1
    for problem in problem_list:
        code = "bkd" + str(count)
        count = count + 1
        problem_sql = problem_original_sql + "('" + code + "','" + problem + "')"
        db.write(problem_sql, cursor, conn)
        fetch_url = base_url + "/challenges/" + problem + "/tags.json"
        data = requests.get(fetch_url,headers=headers).json()
        for tag in data:
            ptag_sql = ptag_original_sql + "('"+code+"', '"+tag+"')"
            tag_sql = tag_orignal_sql + "('"+tag+"', '"+tag+"')"
            db.write(ptag_sql, cursor, conn)
            db.write(tag_sql, cursor, conn)

fetch_problems()    
