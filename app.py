import os
import json
from datetime import datetime
from flask import Flask, request

app = Flask(__name__)

log_file = "rewards_log.json"


def read_rewards():
    try:
        with open(log_file, "r") as f:
            return json.load(f)
    except:
        return []


def save_rewards(rewards):
    with open(log_file, "w") as f:
        json.dump(rewards, f, indent=2)


@app.route("/", methods=["POST"])
def home():
    data = request.json
    print(data)
    if data.get("type") == "scored" and data.get("task", {}).get("type") == "reward":
        reward_entry = {
            "time": datetime.now().strftime("%d/%m, %H:%M"),
            "reward": data["task"]["text"],
            "cost": data["task"]["value"],
        }
        rewards = read_rewards()
        rewards.append(reward_entry)
        save_rewards(rewards)
        print(f"Logged reward: {reward_entry['reward']} costing {reward_entry['cost']}")
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
