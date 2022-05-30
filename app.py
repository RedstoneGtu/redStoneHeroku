from pymongo import MongoClient
from pymongo.server_api import ServerApi
from flask import Flask, request
import os

MONGODB_URL = 'mongodb+srv://redstone_app:huseyinnodejs@cluster0.k4qd1.mongodb.net/?retryWrites=true&w=majority'
app = Flask(__name__)
client = MongoClient(MONGODB_URL, server_api=ServerApi('1'))
db = client['SubjectsDB']
collection = db['subjects']


basedir = os.path.abspath(os.path.dirname(__file__))

@app.route('/sendvalue', methods=['POST', 'GET'])
def results():
    collection.insert_one(request.data)
    return ''


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port, debug=True)