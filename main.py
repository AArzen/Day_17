from flask import Flask, render_template, request, make_response
import random
from sqla_wrapper import SQLAlchemy

app = Flask(__name__)

db = SQLAlchemy("sqlite:///database.sqlite")


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #user_name = db.Column(db.String, unique=False)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, unique=False)
    secret_number = db.Column(db.Integer, unique=False)


db.create_all()


def get_user():
    return request.cookies.get("user_logged_in")


@app.route("/", methods=["GET"])
def secret_number():
    answer = request.cookies.get("answer")
    user = get_user()

    if not answer or answer == 0:
        answer = random.randint(1, 30)
        response = make_response(render_template("secretNumber.html", answer=answer, user=user))
        response.set_cookie("answer", str(answer))
        return response

    else:
        answer = answer

    return render_template("secretNumber.html", answer=answer, user=user)


@app.route("/answer", methods=["POST"])
def check_answer():
    answer = int(request.cookies.get("answer"))
    secret = int(request.form.get("secret_number"))
    user = get_user()

    if answer == secret:

        dialog = f"{str(secret)}: CORRECT"

        return render_template("checkAnswer.html", answer=answer, result=dialog, user=user)
    else:

        dialog = f"{str(secret)}: INCORRECT"
        return render_template("checkAnswer.html", answer=answer, result=dialog, user=user)


@app.route("/users")
def users():
    users = db.query(Users).all()
    user = get_user()
    return render_template("users.html", users=users, user=user)


@app.route("/users/register", methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        user = get_user()

        return render_template("register.html", user=user)
    else:
        secret_number = random.randint(1, 30)
        email_addr = request.form.get("email")
        password1 = request.form.get("pass1")
        password2 = request.form.get("pass2")
        if password1 != password2 or password1 == '':
            return render_template("register.html", errMsg="Password not match or incorrect")
        if email_addr == '' or email_addr is None:
            return render_template("register.html", errMsg="Email incorrect")
        new_user = Users(email=email_addr, password=password1, secret_number=secret_number)
        new_user.save()

        return render_template('message.html', type='success', message="Successfully created new user", redirect=True)


@app.route("/users/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':

        user = get_user()
        return render_template("login.html", user=user)
    else:
        email_addr = request.form.get("email")
        password = request.form.get("password")

        user = db.query(Users).filter_by(email=email_addr).first()

        if password != user.password:
            return render_template("login.html", errMsg="Password incorrect")
        if user is None:
            return render_template("login.html", errMsg="User not exist")

        response = make_response(render_template("message.html", type="success", message="Succesfuly logged is", redirecti=True))
        response.set_cookie("user_logged_in", "True")
        return response


if __name__ == "__main__":
    app.run()
