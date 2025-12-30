# auth.py

from flask import Blueprint, request, jsonify
from db import get_connection
from config import SECRET_KEY, GOOGLE_CLIENT_ID
import bcrypt
import jwt
import datetime
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from contextlib import contextmanager

auth_blueprint = Blueprint("auth", __name__)

@contextmanager
def get_cursor():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def _to_bytes(val):
    if isinstance(val, memoryview):
        return val.tobytes()
    return val

def decode_token_from_header():
    auth = (request.headers.get("Authorization") or "").strip()
    if not auth or not auth.startswith("Bearer "):
        return None, "Missing token"
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except Exception:
        return None, "Invalid token"

def generate_jwt(user):
    payload = {
        "user_id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

@auth_blueprint.route("/register", methods=["POST"])
def register():
    try:
        data = request.json or {}
        username = (data.get("username") or "").strip()
        email = (data.get("email") or "").strip().lower()
        phone = (data.get("phone") or "").strip()
        password = data.get("password") or ""
        confirm = data.get("confirm") or data.get("confirm_password") or ""
        question = data.get("question") or ""
        answer = data.get("answer") or ""

        if not username or not email or not password:
            return jsonify({"error": "Required fields missing"}), 400
        if "@" not in email:
            return jsonify({"error": "Invalid email"}), 400
        if password != confirm:
            return jsonify({"error": "Passwords do not match"}), 400
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        with get_cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cursor.fetchone():
                return jsonify({"error": "Email already registered"}), 400
            cursor.execute("""
                INSERT INTO users (username, email, phone, password, question, answer)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, email, phone, hashed, question, answer))
        return jsonify({"message": "Registration successful"}), 200
    except Exception as e:
        return jsonify({"error": "Server error", "detail": str(e)}), 500

@auth_blueprint.route("/login", methods=["POST"])
def login():
    try:
        data = request.json or {}
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()
            if not user:
                return jsonify({"error": "Wrong email"}), 400
            stored_pw = _to_bytes(user.get("password"))
            if not stored_pw or not bcrypt.checkpw(password.encode("utf-8"), stored_pw):
                return jsonify({"error": "Wrong password"}), 400
        token = generate_jwt(user)
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user_id": user["id"],
            "username": user["username"]
        }), 200
    except Exception as e:
        return jsonify({"error": "Server error", "detail": str(e)}), 500

@auth_blueprint.route("/google-login", methods=["POST"])
def google_login():
    try:
        token = (request.json or {}).get("token")
        if not token:
            return jsonify({"error": "Token required"}), 400
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)
        email = idinfo.get("email")
        name = idinfo.get("name") or "Google User"
        if not email:
            return jsonify({"error": "Google token missing email"}), 400
        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()
            if not user:
                dummy_pw = bcrypt.hashpw("google_dummy_password".encode("utf-8"), bcrypt.gensalt())
                cursor.execute("""
                    INSERT INTO users (username, email, phone, password, question, answer)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (name, email, "0000000000", dummy_pw, "none", "none"))
                cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
                user = cursor.fetchone()
        token_out = generate_jwt(user)
        return jsonify({
            "message": "Google login successful",
            "token": token_out,
            "user_id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }), 200
    except ValueError:
        return jsonify({"error": "Invalid Google token"}), 400
    except Exception as e:
        return jsonify({"error": "Server error", "detail": str(e)}), 500

@auth_blueprint.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Something went wrong"}), 500
