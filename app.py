from flask import Flask, render_template, request
import sqlite3 as db


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        return render_template ("index.html", name=name)
    else:
        return render_template ("index.html", name="YOU")