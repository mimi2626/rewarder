from flask import Flask, request
import json
from datetime import datetime

app = Flask(__name__)


@app.route("/habitica", methods=["POST"])
def habitica_webhook():
    data = request.json
    if data.get("type") == "taskScored" and data["task"]["type"] == "reward":
        log = {
            "time": datetime.utcnow().isoformat(),
            "reward": data["task"]["text"],
            "cost": -data["delta"],
        }
        with open("rewards_log.json", "a") as f:
            f.write(json.dumps(log) + "\n")
    return "ok", 200
