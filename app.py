import os
import json
from datetime import datetime
from flask import Flask, request, render_template, send_file
from zoneinfo import ZoneInfo
import sys

if len(sys.argv) > 1:
    debug = sys.argv[1]
else:
    debug = False

app = Flask(__name__)

# Use NDJSON for safe append
log_file = "/data/rewards_log.ndjson"
if debug:
    log_file = "data/rewards_log.ndjson"

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
    return render_template("home.html")


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
    return render_template("history.html", rewards=rewards)


@app.route("/download", methods=["GET"])
def download_rewards():
    if not os.path.exists(log_file):
        return "No reward log found.", 404
    # Serve the file for download
    return send_file(
        log_file,
        as_attachment=True,
        download_name="rewards_log.ndjson",
        mimetype="application/json",
    )


# --- Run ---

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=debug)
