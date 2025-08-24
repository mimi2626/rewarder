import os
import json
from datetime import datetime
from flask import Flask, request
from zoneinfo import ZoneInfo

app = Flask(__name__)

# Use NDJSON for safe append
log_file = "/data/rewards_log.ndjson"

# --- Helpers ---


def read_rewards():
    rewards = []
    try:
        with open(log_file, "r") as f:
            for line in f:
                rewards.append(json.loads(line))
    except FileNotFoundError:
        pass
    return rewards


def save_reward(reward_entry):
    # Append safely without overwriting
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "a") as f:
        f.write(json.dumps(reward_entry) + "\n")


# --- Routes ---


@app.route("/", methods=["GET"])
def homepage():
    return """
        <h1>Habitica Webhook Receiver</h1>
        <form action="/history" method="get">
            <button type="submit">View History</button>
        </form>
    """


@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    if data.get("task", {}).get("type") == "reward":
        reward_entry = {
            "time": datetime.now(ZoneInfo("Asia/Jerusalem")).strftime("%d/%m, %H:%M"),
            "reward": data["task"]["text"],
            "cost": data["task"]["value"],
        }
        save_reward(reward_entry)
        print(f"Logged reward: {reward_entry['reward']} costing {reward_entry['cost']}")
    return "ok", 200


@app.route("/history", methods=["GET"])
def view_rewards():
    rewards = read_rewards()
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
        <br>
        <a href="/"><button>Back</button></a>
    </body>
    </html>
    """
    return html, 200


# --- Run ---

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
