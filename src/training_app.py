"""Small training app used by the GitLab DevSecOps learning labs."""

import ipaddress
import sqlite3

from flask import Flask, request


app = Flask(__name__)


def find_customer(customer_id):
    with sqlite3.connect("customers.db") as conn:
        return conn.execute(
            "SELECT * FROM customers WHERE id = ?",
            (customer_id,),
        ).fetchall()


@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return {"error": "host must be an IP address"}, 400

    return {"host": host, "status": "accepted"}


@app.route("/debug")
def debug():
    return {"debug": False, "status": "ok"}


@app.route("/health")
def health():
    return {"status": "ok", "owner_check": True}


if __name__ == "__main__":
    app.run()
