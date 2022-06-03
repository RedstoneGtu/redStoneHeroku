from pymongo import MongoClient
from pymongo.server_api import ServerApi
from flask import Flask, request
import os
import json
import base64

MONGODB_URL = 'mongodb+srv://redstone_app:huseyinnodejs@cluster0.k4qd1.mongodb.net/?retryWrites=true&w=majority'
app = Flask(__name__)
client = MongoClient(MONGODB_URL, server_api=ServerApi('1'))
db = client['SubjectsDB']
collection = db['subjects']


basedir = os.path.abspath(os.path.dirname(__file__))

@app.route('/sendvalue', methods=['POST', 'GET'])
def results():
    print(request.data)
    req_dict = json.loads(request.data)
    req_dict['raw'] = [[], [], [], []]
    for elm in req_dict['base64']:
        try:
            vals = base64.b64decode(elm).decode('utf-8').split(',')
            nums = [int(x) for x in vals]
            for i in range(4):
                req_dict['raw'][i].append(nums[i])
        except:
            print('err')
            pass
    if 'result' not in req_dict.keys():
        return 'Hiphop'
    else:
        collection.insert_one(req_dict)
        return 'Added to the database'


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port, debug=True)