from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db_init
from app import util
import json
from bson import json_util

class post_trip(Resource):
    @jwt_required()
    def post(self):
        user = get_jwt_identity()
        print("user", user)
        email = user
        trip_name = request.json.get("trip_name")
        trip_start_date = request.json.get("trip_start_date")
        trip_end_date = request.json.get("trip_end_date")
        trip_budget = request.json.get("trip_budget")
        trip_code = util.generate_trip_code()
        trip_created_by = user
        # add the user to the trip_participants array with the user object id
        trip_participants = [email]
        # trip_participants = [request.json.get("trip_participants")]
        trip_location = request.json.get("trip_location")
        trip_data = {
            "trip_name": trip_name,
            "trip_start_date": trip_start_date,
            "trip_end_date": trip_end_date,
            "trip_budget": trip_budget,
            "trip_code": trip_code,
            "trip_created_by": trip_created_by,
            "trip_participants": trip_participants,
            "trip_location": trip_location
        }
        print("trip_data", trip_data)
        db_init.Trip.insert_one(trip_data)
        return {"msg": "Trip added successfully"}, 



# add the user_id to the trip according to the trip code
class post_trip_participants(Resource):
    @jwt_required()
    def post(self):
        user = get_jwt_identity()
        email = user
        trip_code = request.json.get("trip_code")
        # Ensure trip exists
        trip_data = db_init.Trip.find_one({"trip_code": trip_code})
        if not trip_data:
            return {"msg": "Trip not found"}, 404
        
        # Ensure the user is not already a participant

        if email in trip_data["trip_participants"]:
            return {"msg": "User already a participant"}, 400
        
        # Add the user's email to the trip participants
        db_init.Trip.update_one(
            {"trip_code": trip_code}, 
            {"$addToSet": {"trip_participants": email}}
        )
        # Ensure the user was added successfully
        updated_trip_data = db_init.Trip.find_one({"trip_code": trip_code})
        if email not in updated_trip_data["trip_participants"]:
            return {"msg": "Failed to add user to trip participants"}, 500
        
        return {"msg": "User added to trip participants successfully"}, 200
    
    

class get_trip(Resource):
    @jwt_required()
    def get(self):
        user = get_jwt_identity()
        email = user
        trip_code = request.args.get("trip_code")
        trip_data = db_init.Trip.find_one({"trip_code": trip_code})
        if trip_data:
            return {"msg": "Trip data", "data": json.loads(json_util.dumps(trip_data))}, 200
        else:
            return {"msg": "Trip not found"}, 404
        
class get_all_trips(Resource):
    @jwt_required()
    def get(self):
        user = get_jwt_identity()
        email = user
        # check user is in trip_participants array
        trip_data = db_init.Trip.find({"trip_participants": email})
        if trip_data:
            return {"msg": "Trip data", "data": json.loads(json_util.dumps(trip_data))}, 200
        else:
            return {"msg": "No trips found"}, 404

class delete_trip(Resource):
    # if the user is the creator of the trip, delete the trip
    @jwt_required()
    def delete(self):
        user = get_jwt_identity()
        email = user
        trip_code = request.args.get("trip_code")
        trip_data = db_init.Trip.find_one({"trip_code": trip_code})
        if trip_data:
            if trip_data["trip_created_by"] == email:
                db_init.Trip.delete_one({"trip_code": trip_code})
                return {"msg": "Trip deleted successfully"}, 200
            else:
                return {"msg": "You are not the creator of the trip"}, 401
        else:
            return {"msg": "Trip not found"}, 404
        
class get_trip_participants(Resource):
    @jwt_required()
    def get(self):
        user = get_jwt_identity()
        email = user
        trip_code = request.args.get("trip_code")
        trip_data = db_init.Trip.find_one({"trip_code": trip_code})
        if trip_data:
            return {"msg": "Trip participants", "data": trip_data["trip_participants"]}, 200
        else:
            return {"msg": "Trip not found"}, 404
        
class delete_trip_participants(Resource):
    @jwt_required()
    def delete(self):
        user = get_jwt_identity()
        email = user
        trip_code = request.args.get("trip_code")
        trip_participants = request.args.get("trip_participants")
        trip_data = db_init.Trip.find_one({"trip_code": trip_code})
        if trip_data:
            db_init.Trip.update_one({"trip_code": trip_code}, {"$pull": {"trip_participants": trip_participants}})
            return {"msg": "Trip participants deleted successfully"}, 200
        else:
            return {"msg": "Trip not found"}, 404
        
# delete ttrip with trip code
class delete_trip_with_code(Resource):
    @jwt_required()
    def delete(self):
        user = get_jwt_identity()
        email = user
        trip_code = request.args.get("trip_code")
        trip_data = db_init.Trip.find_one({"trip_code": trip_code})
        if trip_data:
            db_init.Trip.delete_one({"trip_code": trip_code})
            return {"msg": "Trip deleted successfully"}, 200
        else:
            return {"msg": "Trip not found"}, 404

# calculate the trip budget
class calculate_trip_budget(Resource):
    @jwt_required()
    def get(self):
        user = get_jwt_identity()
        email = user
        trip_code = request.args.get("trip_code")
        trip_data = db_init.Trip.find_one({"trip_code": trip_code})
        if trip_data:
            trip_budget = trip_data["trip_budget"]
            trip_participants = len(trip_data["trip_participants"])
            budget_per_person = trip_budget / trip_participants
            return {"msg": "Trip budget", "data": budget_per_person}, 200
        else:
            return {"msg": "Trip not found"}, 404
        
# calulate the trip budget with activity expenses

class calculate_trip_budget_with_activities(Resource):
    @jwt_required()
    def get(self):
        user = get_jwt_identity()
        email = user
        trip_code = request.args.get("trip_code")
        trip_data = db_init.Trip.find_one({"trip_code": trip_code})
        if trip_data:
            trip_budget = trip_data["trip_budget"]
            trip_participants = len(trip_data["trip_participants"])
            
            # Fetch activities associated with the trip
            activities = db_init.Activity.find({"trip_code": trip_code})
            total_activity_cost = sum(activity["estimated_cost"] for activity in activities)
            
            # Calculate total budget including activities
            total_budget = trip_budget + total_activity_cost
            budget_per_person = total_budget / trip_participants
            
            return {
                "msg": "Trip budget with activities",
                "data": {
                    "total_budget": total_budget,
                    "budget_per_person": budget_per_person
                }
            }, 200
        else:
            return {"msg": "Trip not found"}, 404

# {"_id": "ObjectId",
# "trip_id": "trip_id",
# "title": "string",
# "date_time": "datetime",
# "category": "string",
# "estimated_cost": "number",
# "notes": "string",
# "votes": "integer",
# "created_by": "user_id"
# }  
class get_trip_activities(Resource):
    @jwt_required()
    def get(self):
        user = get_jwt_identity()
        email = user
        trip_code = request.args.get("trip_code")
        trip_data = db_init.Trip.find_one({"trip_code": trip_code})
        if trip_data:
            activities = db_init.Activity.find({"trip_code": trip_code})
            return {"msg": "Trip activities", "data": json.loads(json_util.dumps(activities))}, 200
        else:
            return {"msg": "Trip not found"}, 404
        
class CalculateRemainingBudget(Resource):
    @jwt_required()
    def get(self):
        user = get_jwt_identity()
        email = user
        trip_code = request.args.get("trip_code")
        trip_data = db_init.Trip.find_one({"trip_code": trip_code})
        if trip_data:
            trip_budget = trip_data["trip_budget"]
            # Fetch activities associated with the trip
            activities = json.loads(json_util.dumps(db_init.Activity.find({"trip_code": trip_code})))

            print("activities", activities)
            total_activity_cost = 0
            # total_activity_cost = sum(float(activity["estimated_cost"]) for activity in activities)
            for activity in activities:
                print("activity", activity["estimated_cost"])
                total_activity_cost += int(activity["estimated_cost"])
            print("total_activity_cost", total_activity_cost)
            # Calculate remaining budget
            if trip_budget is None:
                return {"msg": "Trip budget not set", "remainingBudget": remaining_budget,
                "spentBudget": total_activity_cost,
                "totalBudget": 0}, 400 
            
            remaining_budget = float(trip_budget) - total_activity_cost
            
            return {
                "msg": "Remaining budget",
                "remainingBudget": remaining_budget,
                "spentBudget": total_activity_cost,
                "totalBudget": trip_budget
            }, 200
        else:
            return {"msg": "Trip not found"}, 404
        
class add_trip_activity(Resource):
    @jwt_required()
    def post(self):
        user = get_jwt_identity()
        email = user
        trip_code = request.json.get("trip_code")
        activity_name = request.json.get("activity_name")
        activity_date = request.json.get("activity_date")
        estimated_cost = request.json.get("activity_estimated_cost")
        category = request.json.get("activity_category")
        notes = request.json.get("activity_notes")

        
        # Ensure trip exists
        trip_data = db_init.Trip.find_one({"trip_code": trip_code})
        if not trip_data:
            return {"msg": "Trip not found"}, 404
        
        # Ensure activity name is provided
        if not activity_name:
            return {"msg": "Activity name is required"}, 400
        # activity_name should be unique in the trip
        existing_activity = db_init.Activity.find_one({"trip_code": trip_code, "activity_name": activity_name})
        if existing_activity:
            return {"msg": "Activity name already exists in the trip"}, 400
        # Add the activity to the trip
        activity_data = {
            "trip_code": trip_code,
            "activity_name": activity_name,
            "activity_date": activity_date,
            "estimated_cost": estimated_cost,
            "category": category,
            "created_by": email,
            "votes": 1,
            "activity_id": util.generate_activity_id(),
            "notes": notes,
            "created_at": util.get_current_time(),
        }
        
        db_init.Activity.insert_one(activity_data)
        return {"msg": "Activity added successfully"}, 200
    

class delete_trip_activity(Resource):
    @jwt_required()
    def delete(self):
        user = get_jwt_identity()
        email = user
        trip_code = request.args.get("trip_code")
        activity_id = request.args.get("activity_id")
        print("activity_id", activity_id)

        # Ensure trip exists
        trip_data = db_init.Trip.find_one({"trip_code": trip_code})
        print("trip_data", trip_data)
        if not trip_data:
            return {"msg": "Trip not found"}, 404
        
        # Delete the activity from the trip
        db_init.Activity.delete_one({"activity_id": activity_id, "trip_code": trip_code})
        return {"msg": "Activity deleted successfully"}, 200
    
class update_trip_activity(Resource):
    @jwt_required()
    def put(self):
        user = get_jwt_identity()
        email = user
        trip_code = request.json.get("trip_code")
        activity_id = request.json.get("activity_id")
        
        # Ensure trip exists
        trip_data = db_init.Trip.find_one({"trip_code": trip_code})
        if not trip_data:
            return {"msg": "Trip not found"}, 404
        
        # Update the activity in the trip
        update_data = {
            "activity_name": request.json.get("activity_name"),
            "activity_date": request.json.get("activity_date"),
            "estimated_cost": request.json.get("activity_estimated_cost"),
            "category": request.json.get("activity_category"),
            "notes": request.json.get("activity_notes", ""),
            "updated_at": util.get_current_time(),
        }
        
        # Ensure activity updated
        existing_activity = db_init.Activity.find_one({"activity_id": activity_id, "trip_code": trip_code})
        if not existing_activity:
            return {"msg": "Activity not found"}, 404
        
        # Update the activity
        res = db_init.Activity.update_one({"activity_id": activity_id, "trip_code": trip_code}, {"$set": update_data})
        print("res", res)
        if res.modified_count == 0:
            return {"msg": "No changes made to the activity"}, 400
        # Check if the activity was updated successfully
        # updated_activity = db_init.Activity.find_one({"activity_id": activity_id, "trip_code": trip_code})
        # if not updated_activity:
        #     return {"msg": "Failed to update activity"}, 500
        return {"msg": "Activity updated successfully"}, 200

# class get_trip_activities(Resource):
