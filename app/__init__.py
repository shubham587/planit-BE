from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_pymongo import MongoClient
from flask_jwt_extended import JWTManager
import os, json
from bson import json_util
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()
# Frontend URL for CORS
FRONTEND_URL = "http://localhost:5173/"

# Flask app
app = Flask(__name__)
api = Api(app)
# Configure CORS to allow requests from the frontend URL
# CORS(app, resources={r"/*": {"origins": FRONTEND_URL}}, supports_credentials=True)
# Configure CORS to allow requests from all origins
# CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app, supports_credentials=True)

#DB
client = MongoClient(os.getenv("MONGO_URI"))
db_init = client.Registration

# JWT
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(weeks=1)
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

# JWT Blacklist
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = db_init.BlackList.find_one({"jti": jti})
    return token is not None

# JWT Error Messages
# @jwt.unauthorized_loader
# def unauthorized_response(callback):
#     return json_util.dumps({
#         "status": 401,
#         "message": "Missing Authorization Header"
#     }), 401

# @jwt.invalid_token_loader
# def invalid_token_response(callback):
#     return json_util.dumps({
#         "status": 401,
#         "message": "Invalid token"
#     }), 401

from app.Resource.auth import UserRegistration, UserLogin, UserLogout
from app.Resource.trip import post_trip, post_trip_participants, get_trip, get_trip_participants
from app.Resource.trip import get_all_trips, delete_trip, delete_trip_participants, delete_trip_with_code, calculate_trip_budget
from app.Resource.trip import get_trip_activities, add_trip_activity, delete_trip_activity, update_trip_activity, CalculateRemainingBudget

api.add_resource(UserRegistration, "/register")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(post_trip, "/post_trip")
api.add_resource(post_trip_participants, "/post_trip_participants")
api.add_resource(get_trip, "/get_trip")
api.add_resource(get_trip_participants, "/get_trip_participants")
api.add_resource(get_all_trips, "/get_all_trips")
api.add_resource(delete_trip, "/delete_trip")
api.add_resource(delete_trip_participants, "/delete_trip_participants")
api.add_resource(delete_trip_with_code, "/delete_trip_with_code")
api.add_resource(calculate_trip_budget, "/calculate_trip_budget")
api.add_resource(get_trip_activities, "/get_trip_activities")
api.add_resource(add_trip_activity, "/add_trip_activity")
api.add_resource(delete_trip_activity, "/delete_trip_activity")
api.add_resource(update_trip_activity, "/update_trip_activity")
api.add_resource(CalculateRemainingBudget, "/calculate_remaining_budget")

