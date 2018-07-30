#!/usr/bin/env python3

import pymongo
import pandas as pd
from pymongo import MongoClient
import json
from flask import Flask, jsonify, request
import os
from flask_caching import Cache

app = Flask(__name__)

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_KEY_PREFIX': 'fcache',
    'CACHE_REDIS_HOST': 'redis',
    'CACHE_REDIS_PORT': '6379',

    })
# 'CACHE_REDIS_URL': 'redis://localhost:6379'

@app.route("/")
def hello_world():
	return( "Welcome to News360!!" )

def mogoimport():
	filepath = os.getcwd() + "/data.csv/"
	#conn = pymongo.MongoClient('mongodb://admin:admin123@localhost:27017/')
	conn = pymongo.MongoClient('mongo', 27017)
	mng_db = conn['Data']
	collection_name = 'users'
	db_cm = mng_db[collection_name]
	db_cm.remove()
	chunksize = 10 ** 6
	i = 0
	for chunk in pd.read_csv(filepath, chunksize=chunksize, names=["datetime", "user", "os", "device"]):

		i +=1
		data_json = json.loads(chunk.to_json(orient='records'))
		db_cm.insert(data_json)
		print('done')

		if ( i>2 ):
			break


	conn.close()

@app.route('/unique-users', methods = ['GET'])
@cache.cached(timeout=500 ,key_prefix = 'fcache')
def findUnique():
	device_query_parameter = request.args.get('device')
	os_query_parameter = request.args.get('os')
	print("YAY IT WORKED")
	return findUnique(device_query_parameter, os_query_parameter)


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
	print("For Debugging: >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" + os.listdir(os.getcwd()))
	mogoimport()
	app.run(debug=True, host='0.0.0.0',port='5000')
