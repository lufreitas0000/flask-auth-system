from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
import time
from sqlalchemy import text
from src.extensions import db

main_bp = Blueprint('main',__name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html',user=current_user)


@main_bp.route('/status')
def status():
    """Liveness probe for infrastructure monitoring."""
    start_time = time.perf_counter()
    try:
        db.session.execute(text('SELECT 1'))
        latency_ms = (time.perf_counter()-start_time)*1000
        return jsonify({
            "status": "online",
            "database": "connected",
            "latency_ms": round(latency_ms, 2)
        }), 200
    except Exception as e:
        # 503 service unavailable
        return jsonify({
            "status": "degraded",
            "database": "disconnected",
            "error": str(e)
        }), 503

