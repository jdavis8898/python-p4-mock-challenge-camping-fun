#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def home():
    return ''

class Campers(Resource):
    
    def get(self):
        campers = [camper.to_dict(rules = ("-signups",)) for camper in Camper.query.all()]

        response = make_response(
            campers,
            200
        )

        return response
    
    def post(self):
        form_data = request.get_json()

        try:
            new_camper = Camper(name = form_data["name"], age = form_data["age"])

            db.session.add(new_camper)
            db.session.commit()

            response = make_response(
                new_camper.to_dict(),
                201
            )

        except ValueError:
            response = make_response(
                {"errors": ["validation errors"]},
                400
            )
        
        return response

api.add_resource(Campers, "/campers")

class CampersById(Resource):

    def get(self, id):
        camper = Camper.query.filter(Camper.id == id).first()

        if camper:
            response = make_response(
                camper.to_dict(),
                200
            )
        
        else:
            response = make_response(
                {"error": "Camper not found"},
                404
            )
        
        return response
    
    def patch(self, id):
        camper = Camper.query.filter(Camper.id == id).first()

        if not camper:
            response = make_response(
                {"error": "Camper not found"},
                404
            )
        
        else:
            try:
                form_data = request.get_json()

                for attr in form_data:
                    setattr(camper, attr, form_data[attr])
                
                db.session.commit()
                response = make_response(
                    camper.to_dict(),
                    202
                )

            except ValueError:
                response = make_response(
                    {"errors": ["validation errors"]},
                    400
                )
        
        return response

api.add_resource(CampersById, "/campers/<int:id>")

class Activities(Resource):

    def get(self):
        activities = [activity.to_dict() for activity in Activity.query.all()]

        response = make_response(
            activities,
            200
        )

        return response

api.add_resource(Activities, "/activities")

class ActivitiesById(Resource):

    def delete(self, id):
        activity = Activity.query.filter(Activity.id == id).first()

        if activity:

            db.session.delete(activity)
            db.session.commit()

            response = make_response(
                {},
                204
            )
        
        else:
            response = make_response(
                {"error": "Activity not found"},
                404
            )
        
        return response

api.add_resource(ActivitiesById, "/activities/<int:id>")

class Signups(Resource):

    def post(self):
        form_data = request.get_json()

        try:
            new_signup = Signup(
                time = form_data["time"],
                activity_id = form_data["activity_id"],
                camper_id = form_data["camper_id"]
            )

            db.session.add(new_signup)
            db.session.commit()

            response = make_response(
                new_signup.to_dict(),
                201
            )
        
        except ValueError:
            response = make_response(
                {"errors": ["validation errors"]},
                400
            )
        
        return response

api.add_resource(Signups, "/signups")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
