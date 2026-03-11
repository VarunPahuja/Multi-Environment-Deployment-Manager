import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    # The environment value comes from the environment variable called APP_ENV.
    return jsonify({
        "service": "Multi-Environment Deployment Manager",
        "environment": os.environ.get("APP_ENV", "unknown"),
        "status": "running"
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    # Run Flask on port 8080
    app.run(host="0.0.0.0", port=8080)
