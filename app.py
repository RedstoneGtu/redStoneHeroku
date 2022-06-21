from pymongo import MongoClient
from pymongo.server_api import ServerApi
from flask import Flask, request
import os
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from scipy.fft import rfft, irfft

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
    pred = pickle_mo.predict_proba(last)
    return pred

def predict_dummy(col):
    return [[0.1, 0.2, 0.1, 0.25, 0.35]]

def proba_to_str(pred):
    str_ = ''
    for i in range(len(pred[0])):
        str_ += '{:s}: {:d}%\n'.format(NAMES[i], int(100 * pred[0][i]))
    return str_

def filter_range(arr, begin, end):
    L = len(arr)
    for i in range(0, begin):
        arr[i] = 0
    for i in range(end, L):
        arr[i] = 0

def add_fft(req_dict):
    req_dict['rfft'] = [[], [], [], []]
    req_dict['irfft'] = [[], [], [], []]
    req_dict['rfft_small'] = [[], [], [], []]
    req_dict['irfft_small'] = [[], [], [], []]
    SPLIT = len(req_dict['raw'][0]) // 6
    for i in range(4):
        fft = rfft(req_dict['raw'][i])
        temp = np.convolve(fft, np.ones(10, dtype=int), 'valid')[20:]
        idx = np.argmax(temp) + 20 + 5
        filter_range(fft, idx - 25, idx + 25)
        req_dict['rfft'][i] = fft.tolist()
        req_dict['irfft'] = irfft(fft).tolist()
        small_fft = np.array([])
        small_ifft = np.array([])
        for j in range(6):
            begin = SPLIT * j
            end = SPLIT * (j + 1)
            sfft = rfft(req_dict['raw'][i][begin : end])
            temp = np.convolve(sfft, np.ones(6, dtype=int), 'valid')[10:]
            idx = np.argmax(temp) + 10 + 3
            filter_range(sfft, idx - 13, idx + 13)
            small_fft = np.append(small_fft, sfft)
            small_ifft = np.append(small_ifft, irfft(sfft))
        req_dict['rfft_small'][i] = small_fft.tolist()
        req_dict['irfft_small'][i] = small_ifft.tolist()

basedir = os.path.abspath(os.path.dirname(__file__))

@app.route('/sendvalue', methods=['POST', 'GET'])
def results():
    print(request.data)
    req_dict = json.loads(request.data)
    req_dict['version'] = 2
    req_dict['raw'] = [[], [], [], []]
    for line in req_dict['raw_string'].split(';')[:-1]:
        try:
            vals = line.split(',')
            for i in range(4):
                req_dict['raw'][i].append(int(vals[i]))
        except:
            print('err')
            pass
    for i in range(4):
        add_fft(req_dict)
    if 'result' not in req_dict.keys():
        for i in range(4):
            length = len(req_dict['raw'][i])
            if 600 > length:
                return 'Sorry, your data is too short.'
            m = length % 6
            req_dict['raw'][i] = req_dict['raw'][i][:length - m]
        prediction = predict_dummy(req_dict)
        return proba_to_str(prediction)
    else:
        res = req_dict['result']
        res = res.replace('[', '')
        res = res.replace(']', '')
        res = [1 == int(s.strip()) for s in res.split(',')]
        req_dict['result'][i] = res
        collection.insert_one(req_dict)
        return 'Added to the database'


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port, debug=True)