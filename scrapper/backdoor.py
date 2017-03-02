#! /usr/bin/python

import os
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

def fetch_problems():

    tag_orignal_sql = "INSERT INTO tag (tag, description, time, count) VALUES "
    ptag_original_sql = "INSERT INTO ptag (pid, tag) VALUES "
    problem_original_sql = "INSERT INTO problem (pid, name, attempt_count, correct_count, time) VALUES "
    tags = ['web','crypto', 'misc', 'n00b15CTF', 'scythe15', 'backdoorctf15', 'steganography', 'forensics', 'n00b16CTF', 'scythe16', 'backdoorctf16', 'pwn', 'n00b17CTF', 'recon', 'reversing', 'revcrypt']
    problem_list = []
    problem_db = {}
    for tag in tags:
        tag_sql = tag_orignal_sql + "('" + tag + "','','"  + tag + "','" + 0 + "'), "
        db.write(tag_sql, cursor, conn)

    for i in (0, 12):
        fetch_url = base_url + "/challenges?page=" + i
        data = requests.get(fetch_url).text
        soup = BeautifulSoup(data)
        for link in find_all('a', 'unsolved'):
            problem_list.append(link.get('title'))
    count = 1
    for problem in problem_list:
        code = "bkd" + count
        count = count + 1
        problem_sql = problem_original_sql + "('" + code + "','" + problem + "','" + 0 + "','" + 0 + "','" + 0 + "'), "
        db.write(problem_sql, cursor, conn)
        fetch_url = base_url + "/challenges/" + problem + "tags.json"
        data  = requests.get(fetch_url).json()
        for tag in data["tags"]:
            ptag_sql = ptag_original_sql + "('"+code+"', '"+tag+"'), "
            cursor(ptag_sql, cursor, conn)

fetch_problems()
cursor.close()
