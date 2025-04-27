from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from flask import request, jsonify
import json, os
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from bson import json_util
from dotenv import load_dotenv

class UserRegistration(Resource):
    def post(self):
        # register the user and provide the access token    


        # parser = reqparse.RequestParser()
        # parser.add_argument("username", type="str", required=True)
        # parser.add_argument("email", type="str", required=True)
        # parser.add_argument("password", type="str", required=True)
        # data = parser.parse_args()

        # username = request.args.get("username")
        # email = request.args.get("email")
        # password = request.args.get("password")
        username = request.json.get("username")
        email = request.json.get("email")
        password = request.json.get("password")
        print(username, email, password)
        
        # Check if the user already exists
        res = db.check_user(email)
        if res:
            return {"msg": "User already exists"}, 400

        # Hash the password and register the user
        hashed_pass = generate_password_hash(password)
        user = db.reqister_user(username, email, hashed_pass)
        if user:
            # Create an access token for the registered user
            access_token = create_access_token(identity=email)
            return {"msg": "User created successfully", "access_token": access_token, "username": username, "email": email}, 201
        else:
            return {"msg": "Something went wrong"}, 500
        # if user:
        #     return {"msg": "user is created successfully"}, 201
        # else:
        #     return {"msg": "something went wrong"}, 500

class UserLogin(Resource):
    def post(self):
        email = request.json.get("email")
        password = request.json.get("password")
        print(email, password, type(email))
        user = db.check_user(email)
        print("user", user)
        if user:
            if check_password_hash(user["password"], password):
                access_token = create_access_token(identity=email)
                username = json.loads(json_util.dumps(db.check_user(email=email)))
                return {"msg": "success","access_token": access_token, "username": username["username"], "email": email}, 200
            else:
                return {"msg": "Invalid credentials"}, 401
        else:
            # User is not signed in eturn {"access_token": access_token}, 200
            return {"msg": "User not found"}, 404
        
class get_username(Resource):
    @jwt_required
    def get(self):
        email = request.args.get('email')
        print("email")
        # user = json.loads(json_util.dumps(db.check_user(email=email)))
        # print(user, "use")
        # return user["username"], 200
        return jsonify(username="shu")



class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        res = db.add_to_blacklist(jti)
        if res.inserted_id:
            return {"msg": "User logout successfully"}, 200


