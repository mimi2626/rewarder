import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from zoneinfo import ZoneInfo


app = Flask(__name__)

log_file = os.path.join(os.path.dirname(__file__), "rewards_log.json")


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
    if data.get("type") == "scored" and data.get("task", {}).get("type") == "reward":
        reward_entry = {
            "time": datetime.now(ZoneInfo("Asia/Jerusalem")).strftime("%d/%m, %H:%M"),
            "reward": data["task"]["text"],
            "cost": data["task"]["value"],
        }
        rewards = read_rewards()
        rewards.append(reward_entry)
        save_rewards(rewards)
        print(f"Logged reward: {reward_entry['reward']} costing {reward_entry['cost']}")
    return "ok", 200


@app.route("/", methods=["GET"])
def view_rewards():
    rewards = read_rewards()
    # Build a simple HTML table
    table_rows = "".join(
        f"<tr><td>{r['time']}</td><td>{r['reward']}</td><td>{r['cost']}</td></tr>"
        for r in rewards
    )
    html = f"""
    <html>
    <head><title>Habitica Rewards</title></head>
    <body>
        <h1>Reward History</h1>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr><th>Time</th><th>Reward</th><th>Cost</th></tr>
            {table_rows}
        </table>
    </body>
    </html>
    """
    return html, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
