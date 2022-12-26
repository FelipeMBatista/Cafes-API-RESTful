from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {
            'Amenities': {},
        }
        for colum in self.__table__.columns:
            if isinstance(getattr(self, colum.name), bool):
                dictionary['Amenities'][colum.name] = getattr(self, colum.name)
            else:
                dictionary[colum.name] = getattr(self, colum.name)
        return dictionary

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random", methods=["GET"])
def get_random_cafe():
    all_data = db.session.query(Cafe).all()
    random_cafe = random.choice(all_data)
    return jsonify(cafe=random_cafe.to_dict())
    
@app.route("/all", methods=["GET"])
def get_all_cafes():
    all_data = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_data])

@app.route("/search", methods=["GET"])
def search():
    query_location = request.args.get("loc")
    cafes = db.session.query(Cafe).filter_by(location=query_location).all()
    if cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes])
    else:
        not_found = {
            "Not found":"Sorry, We don't have a cafe at that location."
        }
        return jsonify(error=not_found)

@app.route("/add", methods=["POST"])
def add_cafe():
    auth = request.args.get("api_key")
    if auth == "TopSecretAPIKey":
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            seats=request.form.get("seats"),
            has_toilet=bool(request.form.get("has_toilet")),
            has_wifi=bool(request.form.get("has_wifi")),
            has_sockets=bool(request.form.get("has_sockets")),
            can_take_calls=bool(request.form.get("can_take_calls")),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()

    return jsonify(response={"Success":"Successfully added the new cafe."})

@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    cafe = db.session.query(Cafe).filter_by(id=cafe_id).first()
    if cafe:
        new_price = request.args.get("new_price")
        if new_price is not None:
            cafe.coffee_price = new_price
            db.session.commit()
            return jsonify(success={cafe.name:"Successfully updated the coffee price."}), 200
        else:
            return jsonify(error={"Attention": "Please, insert the new coffee price."}), 200
    else:
        return jsonify(error={"Not Found":"Sorry, a cafe with that ID was not found in the database."}), 404

@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    cafe = db.session.query(Cafe).filter_by(id=cafe_id).first()
    if cafe:
        auth = request.args.get("api_key")
        if auth == "TopSecretAPIKey":
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(success={"Deleted": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403
    else:
        return jsonify(error={"Not Found": "Sorry, a cafe with that ID was not found in the database."}), 404


if __name__ == '__main__':
    app.run(debug=True)
