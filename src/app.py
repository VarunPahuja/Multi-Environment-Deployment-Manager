import os
import sys
import json
import urllib.request
import threading
import logging
import time
import zoneinfo
from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, render_template, request
import docker

app = Flask(__name__)

try:
    docker_client = docker.from_env()
except Exception as e:
    docker_client = None

TRAFFIC_FILE = os.path.join(os.environ.get("DATA_DIR", "/app/data"), "traffic.json")

def get_shared_traffic():
    if not os.path.exists(TRAFFIC_FILE):
        return 0
    try:
        with open(TRAFFIC_FILE, "r") as f:
            return json.load(f).get("requests", 0)
    except:
        return 0

def increment_shared_traffic():
    count = get_shared_traffic() + 1
    try:
        with open(TRAFFIC_FILE, "w") as f:
            json.dump({"requests": count}, f)
    except:
        pass
    return count

@app.before_request
def count_requests():
    if request.path not in ['/api/traffic', '/api/environments', '/health']:
        count = increment_shared_traffic()
        app.logger.info(f"Received request: {request.method} {request.path}")

APP_ENV = os.environ.get("APP_ENV", "unknown")
DATA_DIR = os.environ.get("DATA_DIR", "/app/data")
LOGS_DIR = os.environ.get("LOGS_DIR", "/app/logs")
DEPLOYMENTS_FILE = os.path.join(DATA_DIR, "deployments.json")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
log_file_path = os.path.join(LOGS_DIR, f"{APP_ENV}_container_logs.log")

# Configure logging
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler = logging.FileHandler(log_file_path)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

app.logger.addHandler(file_handler)
app.logger.addHandler(stream_handler)
app.logger.setLevel(logging.INFO)

def load_deployments():
    if not os.path.exists(DEPLOYMENTS_FILE):
        return []
    with open(DEPLOYMENTS_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def save_deployments(deployments):
    with open(DEPLOYMENTS_FILE, "w") as f:
        json.dump(deployments, f, indent=4)

def record_deployment(env, version, message):
    deployments = load_deployments()
    deployments.insert(0, {
        "env": env,
        "version": version,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    save_deployments(deployments[:50])

@app.route("/")
def index():
    app.logger.info("Serving dashboard index")
    return render_template("dashboard.html", current_env=APP_ENV)

@app.route("/logs")
def logs_view():
    return render_template("logs.html", current_env=APP_ENV)

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "Multi-Environment Deployment Manager",
        "environment": APP_ENV
    })

@app.route("/api/traffic", methods=["GET"])
def api_traffic():
    return jsonify({"requests": get_shared_traffic()})

@app.route("/api/environments")
def api_environments():
    envs = {
        "dev": {"name": "DEVELOPMENT", "url_env": "development"},
        "staging": {"name": "STAGING", "url_env": "staging"},
        "prod": {"name": "PRODUCTION", "url_env": "production"}
    }
    status_data = {}
    for env_id, env_info in envs.items():
        try:
            url = f"http://{env_id}:8080/health"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.status == 200:
                    status_data[env_id] = {
                        "status": "healthy",
                        "version": "v1.2" if env_id == "dev" else "v1.1"
                    }
                else:
                    status_data[env_id] = {"status": "down"}
        except Exception:
            status_data[env_id] = {"status": "down"}
            
    return jsonify(status_data)

@app.route("/api/internal_restart", methods=["POST"])
def internal_restart():
    app.logger.warning(f"Internal restart triggered for {APP_ENV}...")
    # Exit immediately to let Docker fast-restart policy take over
    os._exit(0)
    return jsonify({"status": "success"})

def background_action(container):
    time.sleep(1.0)
    try:
        container.restart()
    except Exception as e:
        app.logger.error(f"Background restart failed: {e}")

@app.route("/api/restart/<env>", methods=["POST"])
def api_restart(env):
    try:
        env_names = {"dev": "Development", "staging": "Staging", "prod": "Production"}
        env_display = env_names.get(env, env.capitalize())
        record_deployment(env, "v1.0", f"{env_display} container restarted")
        app.logger.info(f"[INFO] Container restarted -> {env}")
        
        if docker_client:
            containers = docker_client.containers.list(filters={"label": f"com.docker.compose.service={env}"})
            if not containers:
                return jsonify({"status": "error", "message": f"Couldn't find container for env: {env}"}), 404
            
            container = containers[0]
            threading.Thread(target=background_action, args=(container,)).start()
            return jsonify({"status": "success", "message": f"Restarted {env}"})
        else:
            return jsonify({"status": "error", "message": "Docker client unavailable"}), 500
    except Exception as e:
        app.logger.error(f"Restart failed for {env}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/deploy/<env>", methods=["POST"])
def api_deploy(env):
    try:
        app.logger.info(f"[INFO] Deployment started -> {env}")
        if env == "dev":
            msg = "Deployment triggered in Development"
            ver = "v2.0"
        elif env == "staging":
            msg = "Deployment promoted to Staging"
            ver = "v1.5"
        else:
            msg = "Deployment promoted to Production"
            ver = "v1.2"
            
        record_deployment(env, ver, msg)
        
        if docker_client:
            containers = docker_client.containers.list(filters={"label": f"com.docker.compose.service={env}"})
            if not containers:
                return jsonify({"status": "error", "message": f"Couldn't find container for env: {env}"}), 404
            
            container = containers[0]
            threading.Thread(target=background_action, args=(container,)).start()
            app.logger.info(f"[INFO] Deployment completed -> {env}")
            return jsonify({"status": "success", "message": f"Deployed to {env}"})
        else:
            return jsonify({"status": "error", "message": "Docker client unavailable"}), 500
    except Exception as e:
        app.logger.error(f"Deploy failed for {env}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/logs/<env>")
def api_logs(env):
    tz_name = request.args.get('tz', 'UTC')
    try:
        user_tz = zoneinfo.ZoneInfo(tz_name)
    except:
        user_tz = timezone.utc

    try:
        env_map = {"dev": "development", "staging": "staging", "prod": "production"}
        app_env_name = env_map.get(env, env)
        log_path = os.path.join(LOGS_DIR, f"{app_env_name}_container_logs.log")
        
        req_count = 0
        if os.path.exists(log_path):
            with open(log_path, "r", errors="ignore") as f:
                content = f.read()
                req_count = content.count("Received request")
                
        deps = [d for d in load_deployments() if d.get("env") == env][:2]
        
        display_name = env_map.get(env, env).capitalize()
        summary = f"{display_name} Environment Activity\n"
        summary += "=" * 40 + "\n\n"
        if req_count > 0:
            summary += f"• {req_count} API requests received\n"
        
        for d in deps:
            action = d.get('message', 'Update triggered')
            ts = d.get('timestamp', '')
            try:
                if 'T' in ts:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                else:
                    dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                time_str = dt.astimezone(user_tz).strftime("%H:%M:%S")
            except:
                time_str = ts.split(' ')[1] if ' ' in ts else 'recently'
                
            summary += f"• {action} at {time_str}\n"
            if "version" in d and d["version"] != "--":
                summary += f"• Deployment version updated to {d['version']}\n"
                
        if not deps and req_count == 0:
            summary += "• No recent activity detected.\n"
            
        return jsonify({"status": "success", "logs": summary})
    except Exception as e:
        app.logger.error(f"Log read failed for {env}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/deployments")
def api_deployments():
    tz_name = request.args.get('tz', 'UTC')
    try:
        user_tz = zoneinfo.ZoneInfo(tz_name)
    except:
        user_tz = timezone.utc
        
    deps = load_deployments()
    for d in deps:
        if 'timestamp' in d:
            ts = d['timestamp']
            try:
                if 'T' in ts:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                else:
                    dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                d['timestamp_local'] = dt.astimezone(user_tz).strftime("%H:%M:%S")
            except Exception:
                d['timestamp_local'] = ts.split(' ')[1] if ' ' in ts else ''
                
    return jsonify(deps)

if __name__ == "__main__":
    app.logger.info(f"Starting {APP_ENV} environment on port 8080")
    app.run(host="0.0.0.0", port=8080)
