#!/usr/bin/env python3

from flask import Flask, Response, request, render_template, jsonify
import json

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/js/notifications.js')
def notifications_js():
	return app.send_static_file('js/notifications.js')

@app.route('/js/jquery-3.3.1.js')
def jquery():
	return app.send_static_file('js/jquery-3.3.1.js')

app.run(host='0.0.0.0', port=8001, debug=True)