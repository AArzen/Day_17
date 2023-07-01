from flask import Flask, render_template, request, make_response
import random

app = Flask(__name__)


@app.route("/", methods=["GET"])
def secret_number():
    answer = request.cookies.get("answer")

    if not answer or answer == 0:
        answer = random.randint(1, 10)
        response = make_response(render_template("secretNumber.html"))
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


if __name__ == "__main__":
    app.run()
