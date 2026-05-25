from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    user = "Jacob Navaratne"
    return render_template("signin.html", user=user)


if __name__ == '__main__':
    app.run(port=4500, debug=True)