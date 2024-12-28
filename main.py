from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from logging import basicConfig, getLogger, DEBUG
from modules.functions import hash_password
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from flask_cors import CORS
import hmac
import os

from modules.Dashboard.case_registration_log import case_registration_log_blueprint
from modules.Common.login import login_blueprint

client = MongoClient('mongodb://localhost:27017/')
db = client['sample_try']

app = Flask(__name__)

if not os.path.exists('Logs/'):
    os.makedirs('Logs/')

current_date = datetime.now().strftime('%d-%m-%Y')
basicConfig(filename='Logs/'+current_date+'.log', filemode='a', level=DEBUG, format='%(process)d - %(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%Y %H:%M:%S')
log=getLogger()

# Configure your JWT secret key
secrete_key = '2e765e79e3c8801baec112d68e9b6f28045c348fbb5990bd465aaa0ca4451be7'
app.config['JWT_SECRET_KEY'] =  secrete_key # Change this to a strong secret key
jwt = JWTManager(app)
# CORS(app)

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})


app.register_blueprint(case_registration_log_blueprint(db, app, log))
app.register_blueprint(login_blueprint(db, app, log))

# User login endpoint
# @app.route('/api/login', methods=['POST'])
# def login():

#     users = list(db.User.find())

#     # Get the username and password from the request
#     username = request.json.get('username')
#     password = request.json.get('password')

#     # Validate user credentials
#     user = next((u for u in users if hmac.compare_digest(u['username'], username)), None)
#     if user and hmac.compare_digest(user['password'], hash_password(password, secrete_key)):
#         # Generate JWT token
#         db.User.update_one(
#             {'username': username},
#             {'$set': {'last_login': datetime.now()}}
#         )
#         access_token = create_access_token(identity=user['vkId'])
#         return jsonify(access_token=access_token), 200
#     else:
#         print({'success' : False, 'message' : 'Invalid credentials'},401)
#     return jsonify({"msg": "Invalid credentials"}), 401

@app.route('/api/automation_count', methods=['GET'])
@jwt_required()
def get_automation_count():
    # Optional: You can access the JWT identity here
    cmpy_emp_id = get_jwt_identity()
    
    # Example data; replace with your actual data source
    automation_count = [
        {"count": "600", "process": "Case Registration", "year_base" : [{"2023" : "100"},{"2024" : "200"},{"2022" : "300"},{"2021" : "800"},{"2020" : "150"},{"2019" : "340"},{"2018" : "90"}]},
        {"count": "0", "process": "Case Update", "year_base" : [{"2023" : "100"},{"2024" : "200"}]},
        {"count": "15", "process": "Report Update", "year_base" : [{"2023" : "100"},{"2024" : "200"}]},
        {"count": "90", "process": "Report Download", "year_base" : [{"2023" : "100"},{"2024" : "200"}]},
        {"count": "22", "process": "Employer Verification", "year_base" : [{"2023" : "100"},{"2024" : "200"}]},
    ]

    # Return the data
    return jsonify(automation_count)


@app.route('/api/user', methods=['POST', 'DELETE'])
@jwt_required()
def manage_user():
    token_id = get_jwt_identity()
    current_user = db.User.find_one({'vkId': token_id})

    if current_user['role'] == 'admin':

        data = request.json

        print("METHOD - ", request.method)
        
        if request.method == 'POST':
            # Create a new user
            if ('username' not in data) or ('password' not in data) or ('vkId' not in data) or ('email' not in data):
                return jsonify({'success': False, 'message': 'Missing userID or password'}), 400
            
            existing_user = db.User.find_one({'vkId': data['vkId']})

            if existing_user:
                return jsonify({'success': False, 'message': 'User already exists'}), 400
            
            
            db.User.insert_one({
                'username': data['username'],
                'password': hmac.new(data['password'].encode(), bytes.fromhex(secrete_key), 'sha256').hexdigest(),
                'vkId' : data['vkId'],
                'email' : data['email'],
                'role' : data['role'],
                'hiredDate' : data['hiredDate'],
                'phone' : data['phone'],
                'created_at': datetime.now()
            })

            return jsonify({'success': True, 'message': 'User Created Successfully'}), 201

        elif request.method == 'DELETE':
            if 'vkId' not in data:
                return jsonify({'success': False, 'message': 'Missing username'}), 400
            
            if current_user['password'] == hash_password(data['password'], secrete_key):
                result = db.User.delete_one({'vkId': data['vkId']})
            else:
                return jsonify({'success': False, 'message': 'Invalid Password'}), 404
            
            if result.deleted_count == 0:
                return jsonify({'success': False, 'message': 'User not found'}), 404
            
            
            return jsonify({'success': True, 'message': 'User Deleted Successfully'}), 200

        return jsonify({'success': False, 'message': 'Method not allowed'}), 405


@app.route('/api/usersUpdate', methods=['PUT'])
@jwt_required()
def update_user():

    token_id = get_jwt_identity()
    current_user = db.User.find_one({'vkId': token_id})

    if current_user['role'] == 'admin':

        data = request.json

        if 'vkId' not in data:
            return jsonify({'success': False, 'message': 'Missing userID'}), 400
        print(data )
        result = db.User.update_one(
            {'vkId': data['vkId']},
            {'$set': {
                'username': data['username'],
                'email' : data['email'],
                'role' : data['role'],
                'hiredDate' : data['hiredDate'],
                'phone' : data['phone'],
                'updated_at': datetime.now()
            }}
        )
        
        if result.matched_count == 0:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        return jsonify({'success': True, 'message': 'User Updated Successfully'}), 200


def serialize_user(user):
    user['_id'] = str(user['_id'])  # Convert ObjectId to string
    return user

@app.route('/api/getuser', methods=['GET'])
@jwt_required()
def get_user_data():
    cmpy_emp_id = get_jwt_identity()
    data = list(db.User.find({}))
    user_list = [serialize_user(user) for user in data]
    return jsonify(user_list)


if __name__ == '__main__':
    app.run(debug=True)