from flask import Flask, render_template, request
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3 as db


app = Flask(__name__)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        
