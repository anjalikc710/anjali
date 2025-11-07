from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

if not os.path.exists("instance"):
    os.mkdir("instance")

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Create a database model
class User(db.Model):
    __tablename__ = "users"  # explicit table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"
#create the database
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    users = User.query.all()  # Get all users from the database
    return render_template("index.html", users=users)


@app.route("/add", methods=["POST"])
def add_user():
    name = request.form.get("name")
    email = request.form.get("email")

    if name and email:
        if not User.query.filter_by(email=email).first():
            new_user = User(name=name, email=email)
            db.session.add(new_user)
            db.session.commit()
        else:
            print(f"Email {email} already exist!")

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
