from flask import Flask, render_template, request
import sqlite3


app = Flask(__name__)