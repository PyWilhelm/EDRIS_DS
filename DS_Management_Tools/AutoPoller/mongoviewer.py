import os, subprocess

from pymongo import MongoClient


def start_db():
    lck_file = os.path.join('C:\\li\\dbpath', 'mongod.lock')
    if os.path.exists(lck_file):
        os.remove(lck_file)
    subprocess.Popen(['C:\\li\\mongodb-win32-i386-2.6.1\\bin\\mongod.exe', '--dbpath', 'C:\\li\\dbpath'])
try:
    start_db()
except:
    pass
client = MongoClient('localhost', 27017)
db = client['edris_proj']
projects = db['projects']
components = db['components']
#components.remove()
projects.remove()
res = projects.find()
print type(res)
total = 0
for w in res:
    total += 1
    print w
print 'task total', total

print '------------'
res = components.find()#.sort([('priority', -1)])
total = 0
print type(res)
for w in res:
    total += 1
    print w
print 'res total', total
