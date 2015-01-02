#!/bin/bash
apt-get install build-essential python-dev libmysqlclient-dev subversion libv8-dev libboost-all-dev
svn checkout http://v8.googlecode.com/svn/trunk/ ~/v8
cd ~/v8
make builddeps
make native
cd -
pip install -r requirements.txt
