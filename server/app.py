#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse, abort

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Plants(Resource):

    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()

        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price'],
        )

        db.session.add(new_plant)
        db.session.commit()

        return make_response(new_plant.to_dict(), 201)


api.add_resource(Plants, '/plants')


class PlantByID(Resource):

    def get(self, id):
        plant = Plant.query.filter_by(id=id).first().to_dict()
        return make_response(jsonify(plant), 200)

    def patch(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument("is_in_stock", type=bool, help="Boolean field for is_in_stock")
        args = parser.parse_args()
        
        plant = Plant.query.get(id)
        if plant:
            if args["is_in_stock"] is not None:
                plant.is_in_stock = args["is_in_stock"]
                db.session.commit()
                return {
                    "id": plant.id,
                    "is_in_stock": plant.is_in_stock
                }
            else:
                abort(400, message="Bad request")
        else:
            abort(404, message="Plant not found")

    def delete(self, id):
        plant = Plant.query.get(id)
        if plant:
            db.session.delete(plant)
            db.session.commit()
            return '', 204
        else:
            abort(404, message="Plant not found")

api.add_resource(PlantByID, '/plants/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
