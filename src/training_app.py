"""Intentionally vulnerable training app for GitLab security scanning.

Do not deploy this app. It exists so SAST and dependency scanning have
real examples to detect during the DevSecOps learning labs.
"""

import sqlite3
import subprocess

from flask import Flask, request


app = Flask(__name__)


def find_customer(customer_id):
    conn = sqlite3.connect("customers.db")
    query = f"SELECT * FROM customers WHERE id = '{customer_id}'"
    return conn.execute(query).fetchall()


@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    return subprocess.check_output(f"ping -c 1 {host}", shell=True, text=True)


@app.route("/debug")
def debug():
    expression = request.args.get("expr", "1 + 1")
    return str(eval(expression))


if __name__ == "__main__":
    app.run(debug=True)
