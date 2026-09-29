from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Missing JSON body'}), 400

    username = data.get('uname')
    password = data.get('passwd')


    # TODO Check credentials and return auth token

    
    return jsonify({'message': 'Invalid credentials'}), 401