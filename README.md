forsit
======

A Cross Platform Problem Recommendation Engine

# Usage:

recommend.py [options]

##  Options:

### -h, --help
show this help message and exit
### -p PROBLEM, --problem=PROBLEM
Get list of problems similar to given problem through content based ( tag matching ) algorithm.
### -s SITE, --site=SITE
Site to give recommendations for. Choose from 'erd' and 'cfs'.
### -t STATUS, --status=STATUS
Status of the given problem. 1 for correct submission and 0 otherwise.
### -u USER, --user=USER
Get list of users similar to given user and list of recommended problems through collaborative filtering ( neighbourhood matching ) algorithm.
### -d DIFFICULTY_MODE, --difficulty_mode=DIFFICULTY_MODE
Difficulty mode of problems recommended for a user. 1 for difficult problems and 0 for easy problems.
### -f, --fetch_activity
Fetch latest user activity and populate the database.
