# ------------------------------------- IMPORTS ---------------------------------------#

from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy.orm import relationship
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib


# ------------------------------------ START CONNECTION AND VARIABLES MANAGEMENT ------------------------#
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///HealthFitness.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

OUR_EMAIL = "health123fi@gmail.com"
EMAIL_PASSWORD = "HEALTH123FI"

# ------------------------------------- DATABASE MANAGEMENT ------------------------------------#
class Trainer(db.Model):
    trainer_id = db.Column(db.Integer, primary_key=True)
    trainer_name = db.Column(db.String(100))
    trainer_age = db.Column(db.Integer, nullable=False)
    trainer_gender = db.Column(db.String(100), nullable=False)
    users = relationship("User", back_populates="trainer")

db.create_all()


class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), unique=True)
    user_password = db.Column(db.String(100))
    user_name = db.Column(db.String(1000))
    user_age = db.Column(db.Integer, nullable=True)
    user_gender = db.Column(db.String(100), nullable=True)
    user_height = db.Column(db.FLOAT, nullable=True)
    user_weight = db.Column(db.FLOAT, nullable=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.trainer_id'))
    trainer = relationship("Trainer", back_populates="users")

db.create_all()

class Upperbody(db.Model):
    exe_id = db.Column(db.Integer, primary_key=True)
    exe_name = db.Column(db.String(500), unique=True)
    exe_link = db.Column(db.String(500), unique=True)

db.create_all()

class Lowerbody(db.Model):
    exe_id = db.Column(db.Integer, primary_key=True)
    exe_name = db.Column(db.String(500), unique=True)
    exe_link = db.Column(db.String(500), unique=True)

db.create_all()

# class Yoga(db.model):
#     pass

# ----------------------------------------- WTForms MANAGEMENT ---------------------------------------#

class GetUserData(FlaskForm):
    gender = SelectField("Select Gender", choices=["Male 👨🏻", "Female 👩🏻"], validators=[DataRequired()])
    age = StringField("Enter your Age ", validators=[DataRequired()])
    height = StringField("Enter your Height (in cm)", validators=[DataRequired()])
    weight = StringField("Enter your Weight (in kg)", validators=[DataRequired()])
    trainer = SelectField("Select Trainer", choices=[("1", "Rachel James"), ("2","Steve Harvey"), ("3","Self-Training") ], validators=[DataRequired()])
    submit = SubmitField("Submit 💪🏻")


# ------------------------------------- FLASK CONNECTION ROUTING ---------------------------------------------------#
# ------------------------------------- HOMEPAGE ------------------------------------#
@app.route('/')
def homepage():
    return render_template("index.html", logged_in=current_user.is_authenticated)


# -------------------------------------- REGISTERING/LOGGING/LOGOUT ------------------------------------#

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if User.query.filter_by(user_email=request.form.get('email')).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )

        new_user = User(
            user_email=request.form.get('email'),
            user_name=request.form.get('name'),
            user_password=hash_and_salted_password,
        )

        db.session.add(new_user)
        db.session.commit()

        # Log in and authenticate user after adding details to database.
        # login_user(new_user)
        return redirect(url_for("login"))

    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(user_email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.user_password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            # login_user(user)

            return redirect(url_for("selection", u_id=user.user_id))

    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('homepage'))


# ------------------------------------------------- GETTING USER DATA ---------------------------------------------#
@app.route('/edit', methods=['GET', 'POST'])
def get_data():
    form = GetUserData()
    user_id = request.args.get("u_id")
    user = User.query.get(user_id)
    print(user_id)
    print(user)
    if form.validate_on_submit():
        user.user_age = int(form.age.data)
        user.user_gender = form.gender.data
        user.user_height = float(form.height.data)
        user.user_weight = float(form.weight.data)
        trainer_details = Trainer.query.get(form.trainer.data)
        user.trainer_id = int(trainer_details.trainer_id)
        db.session.commit()
        return redirect(url_for('selection', u_id=user.user_id))
    return render_template("get_user_data.html", user=user , form=form)

#----------------------------------------- USER OPTION SELECTION ------------------------------#
@app.route('/selection', methods=['GET', 'POST'])
def selection():
    user_id = request.args.get("u_id")
    user = User.query.get(user_id)
    print(user_id, user.user_id)
    return render_template("selection.html", user=user)

#-------------------------------------- USER PROGRAMS SELECTION ----------------------#
@app.route('/programs', methods=["GET", "POST"])
def program():
    user_id = request.args.get("u_id")
    user = User.query.get(user_id)
    return render_template("program.html", user=user)

@app.route('/programs/upper_body', methods=["GET","POST"])
def upper_body():
    user_id = request.args.get("u_id")
    user = User.query.get(user_id)
    all_upper_exe = db.session.query(Upperbody).all()
    print(all_upper_exe)
    return render_template("upper_body.html", up_exercise=all_upper_exe, user=user)

@app.route('/programs/lower_body', methods=["GET","POST"])
def lower_body():
    user_id = request.args.get("u_id")
    user = User.query.get(user_id)
    all_upper_exe = db.session.query(Lowerbody).all()
    print(all_upper_exe)
    return render_template("upper_body.html", up_exercise=all_upper_exe, user=user)

@app.route('/subscribed', methods=["GET", "POST"])
def subscription():
    user_id = request.args.get("u_id")
    user = User.query.get(user_id)
    user_mail = user.user_email
    email_message = f"Subject:Subscribed\n\nThank You {user.user_name} for subscribing with Healthyfi !! \n Every Weekend you will receive Newsletter from us . \n Below we have attached a diet plan links for your refernce!! \n http://aditi.du.ac.in/uploads/econtent/diet_plan.pdf \n https://www.youtube.com/watch?v=VEKba1nhsB0 "
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(OUR_EMAIL, EMAIL_PASSWORD)
        connection.sendmail(OUR_EMAIL,user_mail , email_message)
    return render_template("thankyou.html", user=user)

    

# -------------------------------------- CONNECTION START ---------------------------#
if __name__ == '__main__':
    app.run(debug=True)
