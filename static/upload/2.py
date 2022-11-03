from datetime import date, datetime, timedelta
import json
import random
import requests
import threading
import queue
try:
    import MySQLdb
except:
    import pymysql
    pymysql.install_as_MySQLdb()
    import MySQLdb

# conn = MySQLdb.connect(host='localhost', user='root', passwd='abcu123456', db='ds', port=3306)
# curs = conn.cursor()

def datespan(startDate, endDate, delta=timedelta(days=1)):
    currentDate = startDate
    while currentDate < endDate:
        yield currentDate
        currentDate += delta

q = queue.Queue()
for day in datespan(date(2011, 7, 1), date(2021, 7, 13), delta=timedelta(days=1)):
    dl = [6, 7]
    if day.isoweekday() not in dl:
        q.put(day)


def aa():
    while True:
        day = q.get()
        d = [{"name": 'A', 'id': 5}, {'name': 'B', 'id': 6}, {'name': 'C', 'id': 7}, {'name': 'D', 'id': 8}]
        for i in d:
            c = [{"category1": f"{i.get('name')}1", "price": random.randint(10, 100)}, {"category2": f"{i.get('name')}2", "price": random.randint(20, 100)},
            {"category3": f"{i.get('name')}3", "price": random.randint(30, 100)}, {"category4": f"{i.get('name')}4", "price": random.randint(40, 100)}]
            # sql = f"INSERT INTO `api_pricedata`(date, categories, user_id, variety_id, update_time, create_time) VALUES('{day}', '{json.dumps(c)}', 9, {i.get('id')}, datetime.now(), datetime.now())"
            # curs.execute(sql)
            # conn.commit()
            data = {"user": 1, "date": day.strftime("%Y-%m-%d"), "variety": i.get('name'), "variety_id": i.get('id'), "categories": c}
            try:
                requests.post('http://nb33.3322.org:8000/api/price/', json=data)
            except Exception as e:
                requests.post('http://nb33.3322.org:8000/api/price/', json=data)
        q.task_done()

for i in range(20):
    t = threading.Thread(target=aa)
    t.start()

q.join()