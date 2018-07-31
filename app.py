#!/usr/bin/env python3

import pymongo
import pandas as pd
from pymongo import MongoClient
import json
from flask import Flask, jsonify, request, url_for
from flask_caching import Cache
import redis
import warnings
from celery import Celery
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")


app = Flask(__name__)

app.config['CELERY_BROKER_URL'] = 'redis://redis:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_KEY_PREFIX': 'fcache',
    'CACHE_REDIS_HOST': 'redis',
    'CACHE_REDIS_PORT': '6379',
    'CACHE_REDIS_URL': 'redis://redis:6379'
    })

@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = mogoimport.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

@celery.task(bind=True)
def mogoimport(self):
    print('Async Function Called')
    filepath = "data.csv"
    # conn = pymongo.MongoClient('mongodb://admin:admin123@localhost:27017/')
    conn = pymongo.MongoClient('mongo', 27017)
    mng_db = conn['Data']
    collection_name = 'users'
    db_cm = mng_db[collection_name]
    db_cm.remove()
    chunksize = 10 ** 6
    for chunk in pd.read_csv(filepath, chunksize=chunksize, names=["datetime", "user", "os", "device"]):
        data_json = json.loads(chunk.to_json(orient='records'))
        db_cm.insert(data_json)
        print('done')
    conn.close()

@app.route('/import-data/')
def async_mongo_import():
    task = mogoimport.apply_async()
    return jsonify({}), 202, {'Location': url_for('taskstatus',task_id=task.id)}

@app.route("/",methods=['GET'])
def homepage():
    return('Welcome to News360')

@app.route('/unique-users', methods = ['GET'])
def findUnique():
    device_query_parameter = request.args.get('device')
    os_query_parameter = request.args.get('os')
    print("YAY IT WORKED")
    return findUnique(device_query_parameter, os_query_parameter)

@cache.memoize(timeout=500)
def findUnique(device = "" , os="" ):
    query={}
    if (device == None):
        device = "0,1,2,3,4,5"
    if (os == None):
        os = "0,1,2,3,4,5,6"
    if device !="":
        devices = [int(x) for x in device.split(',')]
        query['device'] = {'$in' : devices}
    if os !="":
        oses = [int(x) for x in os.split(',')]
        query['os'] = {'$in' : oses}
    #conn = pymongo.MongoClient('mongodb://admin:admin123@localhost:27017/')
    conn = pymongo.MongoClient('mongo', 27017)
    db = conn['Data']
    distinctusers = db.users.aggregate([{'$match' : query},{'$group': {'_id': '$user'}}, {'$count': "distinctcount"}])
    distinctcount =0
    for user in distinctusers:
        distinctcount = user['distinctcount']
    conn.close()
    return jsonify(distinctcount)

@app.route('/loyal-users', methods = ['GET'])
def findLoyal():
    device_query_parameter = request.args.get('device')
    os_query_parameter = request.args.get('os')
    return findLoyal(device_query_parameter, os_query_parameter)


@cache.memoize(timeout=500)
def findLoyal(device = "" , os="" ):
    query={}
    if (device == None):
        device = "0,1,2,3,4,5"
    if (os == None):
        os = "0,1,2,3,4,5,6"
    if device !="":
        devices = [int(x) for x in device.split(',')]
        query['device'] = {'$in' : devices}
    if os !="":
        oses = [int(x) for x in os.split(',')]
        query['os'] = {'$in' : oses}
    # conn = pymongo.MongoClient('mongodb://admin:admin123@localhost:27017/')
    conn = pymongo.MongoClient('mongo', 27017)
    db = conn['Data']
    loyalusers = db.users.aggregate([{ '$match': query },{'$group' : {'_id' : '$user', 'total' : { '$sum' : 1 }}}, {'$match': {'total':{ '$gte': 10}}}, {'$count': "loyalcount"}],allowDiskUse=True)
    usercount = 0
    for user in loyalusers:
        usercount = user['loyalcount']
    conn.close()
    return jsonify(usercount)

if __name__ == '__main__':
    mogoimport()
    app.run(debug=True, host='0.0.0.0',port='5000')
