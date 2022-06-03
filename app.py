from pymongo import MongoClient
from pymongo.server_api import ServerApi
from flask import Flask, request
import os
import json
import base64
import pickle
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

NAMES = {
    0: 'Classic',
    1: 'Electro',
    2: 'Jazz',
    3: 'Rock',
    4: 'Pop',
    5: 'Hiphop',
}

MONGODB_URL = 'mongodb+srv://redstone_app:huseyinnodejs@cluster0.k4qd1.mongodb.net/?retryWrites=true&w=majority'
app = Flask(__name__)
client = MongoClient(MONGODB_URL, server_api=ServerApi('1'))
db = client['SubjectsDB']
collection = db['subjects']
pickle_mo = pickle.load(open('model.pkl','rb'))

def predict_fun(col):
    a = []
    last = [col]
    df_last = pd.DataFrame(last)
    raw_ = df_last['raw']
    last = []
    last.append([])
    last = list((raw_))
    a = raw_.to_numpy().flatten()
    b = [[] for _ in range(len(raw_))]
    for i in range(len(raw_)):
        for j in range(len(a[i][0])):
            b[i].append(a[i][0][j])
            b[i].append(a[i][1][j])
    for i in range(len(b)):
        b[i] = np.split(np.array(b[i]),6)
    b = np.array(b)
    x = []
    for i in range(len(b)): 
        x.append(b[i].mean(axis=1))
    print(np.array(b[0]).shape)
    last = pd.DataFrame(x)
    pred = pickle_mo.predict(last)
    return pred

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
        for i in range(4):
            length = len(req_dict['raw'][i])
            if 600 > length:
                return 'Sorry, your data is too short.'
            m = length % 6
            req_dict['raw'][i] = req_dict['raw'][i][:length - m]
        prediction = predict_fun(req_dict)
        return NAMES[prediction[0]]
    else:
        collection.insert_one(req_dict)
        return 'Added to the database'


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port, debug=True)