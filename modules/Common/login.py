from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from modules.functions import hash_password
from flask import Flask, request, jsonify, Blueprint
from datetime import datetime
import hmac



bp = Blueprint('login', __name__)


def login_blueprint(_db, _app,  _log):
    global db
    global app
    global log
    log = _log
    app = _app
    db = _db
    return bp


secrete_key = '2e765e79e3c8801baec112d68e9b6f28045c348fbb5990bd465aaa0ca4451be7'

@bp.route('/api/login', methods=['POST'])
def login():

    users = list(db.User.find())

    # Get the username and password from the request
    username = request.json.get('username')
    password = request.json.get('password')

    # Validate user credentials
    user = next((u for u in users if hmac.compare_digest(u['username'], username)), None)
    if user and hmac.compare_digest(user['password'], hash_password(password, secrete_key)):
        # Generate JWT token
        db.User.update_one(
            {'username': username},
            {'$set': {'last_login': datetime.now()}}
        )
        access_token = create_access_token(identity=user['vkId'])
        return jsonify(access_token=access_token), 200
    else:
        print({'success' : False, 'message' : 'Invalid credentials'},401)
    return jsonify({"msg": "Invalid credentials"}), 401