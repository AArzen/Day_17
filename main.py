import hashlib
import uuid
from flask import Flask, render_template, request, make_response, url_for, redirect
import random
from sqla_wrapper import SQLAlchemy

app = Flask(__name__)

db = SQLAlchemy("sqlite:///database.sqlite")


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, unique=False)
    secret_number = db.Column(db.Integer, unique=False)
    session_token = db.Column(db.String, unique=True)


db.create_all()


def get_user():
    session_token = request.cookies.get("session_token")
    if session_token is None:
        return None
    else:
        user = db.query(Users).filter_by(session_token=session_token).first()
    return user


@app.route("/", methods=["GET"])
def secret_number():
    answer = request.cookies.get("answer")
    if get_user() is not None:
        user = get_user()
        user = user.email
    else:
        user = ''

    if not answer or answer == 0:
        answer = random.randint(1, 30)
        response = make_response(render_template("secretNumber.html", answer=answer, user=user))
        response.set_cookie("answer", str(answer))
        return response

    else:
        answer = answer

    return render_template("secretNumber.html", answer=answer)


@app.route("/answer", methods=["POST"])
def check_answer():
    answer = int(request.cookies.get("answer"))
    secret = int(request.form.get("secret_number"))

    if answer == secret:

        dialog = f"{str(secret)}: CORRECT"

        return render_template("checkAnswer.html", answer=answer, result=dialog)
    else:

        dialog = f"{str(secret)}: INCORRECT"
        return render_template("checkAnswer.html", answer=answer, result=dialog)


@app.route("/users")
def users():
    users = db.query(Users).all()
    return render_template("users.html", users=users)


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

        hashed_pass = hashlib.sha256(password1.encode()).hexdigest()

        new_user = Users(email=email_addr, password=hashed_pass, secret_number=secret_number)
        new_user.save()

        return render_template('message.html', type='success', message="Successfully created new user", redirect=True)


@app.route("/users/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':

        return render_template("login.html")
    else:
        email_addr = request.form.get("email")
        password = request.form.get("password")

        user = db.query(Users).filter_by(email=email_addr).first()
        if user is None:
            return render_template("message.html", message="Account not found!", type="danger", redirect=True)
        else:

            hased_password = hashlib.sha256(password.encode()).hexdigest()

            if user.password != hased_password:
                return render_template("login.html", errMsg="Password incorrect")
            if user is None:
                return render_template("login.html", errMsg="User not exist")

            response = make_response(render_template("message.html", type="success", message="Succesfuly logged is", redirecti=True))

            session_token = str(uuid.uuid4())
            user.session_token = session_token
            user.save()
            response.set_cookie("session_token", session_token)
            return response


@app.route("/users/profile")
def profile_page():
    user_data = get_user()

    if user_data is None:
        return redirect(url_for("login"))
    return render_template("profile.html", user_data=user_data)


@app.route("/users/profile/edit", methods=["GET", "POST"])
def profile_page_edit():
    user_data = get_user()
    if user_data is None:
        return redirect(url_for("login"))
    else:
        if request.method == 'GET':
            return render_template("profile_edit.html", user_data=user_data)
        else:
            email = request.form.get("email")
            pass1 = request.form.get("pass1")
            pass2 = request.form.get("pass2")

            if email != user_data.email:
                user_data.email = email

            if pass1 == pass2 and not pass1 == '':
                hased_password = hashlib.sha256(pass1.encode()).hexdigest()
                user_data.password = hased_password
            elif pass1 != pass2:
                return render_template("profile_Edit.html", user_data=user_data, message="password did not match")

            user_data.save()
            return redirect(url_for("profile_page"))


@app.route("/users/profile/delete", methods=["GET", "POST"])
def profile_page_delete():

    if request.method == "POST":
        user = get_user()
        user.delete()
        return render_template("message.html", message="Account deleted!", type="success", redirect=True)
    else:
        return render_template("profile_delete.html")


if __name__ == "__main__":
    app.run()
