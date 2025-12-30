# profile.py

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import pymysql
from config import DB_CONFIG, UPLOAD_FOLDER
from flask import send_from_directory
from datetime import datetime
from flask_cors import CORS

profile_blueprint = Blueprint("profile", __name__)
CORS(profile_blueprint, origins=["http://127.0.0.1:5500"], supports_credentials=True)

def get_db_connection():
    return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

def get_user_id():
    return 1

UPLOAD_FOLDER = "uploads/profile_photos"
@profile_blueprint.route("/photo/upload", methods=["POST"])
def upload_profile_photo():
    user_id = get_user_id()
    if "photo" not in request.files:
        return jsonify({"success": False, "message": "No photo uploaded"})
    file = request.files["photo"]
    filename = secure_filename(file.filename)
    if filename == "":
        return jsonify({"success": False, "message": "Invalid file name"})
    filepath = os.path.join(UPLOAD_FOLDER, f"user_{user_id}_" + filename)
    file.save(filepath)
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM user_profile_photo WHERE user_id=%s", (user_id,))
        cur.execute("""
            INSERT INTO user_profile_photo (user_id, file_name, file_path)
            VALUES (%s, %s, %s)
        """, (user_id, filename, filepath))
        conn.commit()
    conn.close()
    return jsonify({
        "success": True,
        "message": "Profile photo uploaded successfully"
    })

@profile_blueprint.route("/photo/get", methods=["GET"])
def get_profile_photo():
    user_id = get_user_id()
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT file_path FROM user_profile_photo
            WHERE user_id=%s
        """, (user_id,))
        row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"success": False, "message": "No photo found"})
    directory, filename = os.path.split(row["file_path"])
    return send_from_directory(directory, filename)

@profile_blueprint.route("/photo/delete", methods=["DELETE"])
def delete_profile_photo():
    user_id = get_user_id()
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT file_path FROM user_profile_photo WHERE user_id=%s", (user_id,))
        row = cur.fetchone()
        if row:
            if os.path.exists(row["file_path"]):
                os.remove(row["file_path"])
            cur.execute("DELETE FROM user_profile_photo WHERE user_id=%s", (user_id,))
            conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Profile photo deleted"})

@profile_blueprint.route("/get", methods=["GET"])
def get_profile():
    user_id = get_user_id()
    conn = get_db_connection()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                username,
                email,
                phone,
                address,
                work_status,
                linkedin,
                github,
                gender,
                dob,
                marital_status
            FROM user_profile
            WHERE user_id=%s
        """, (user_id,))
        profile = cur.fetchone()
    conn.close()

    if profile:
        return jsonify({**profile, "success": True})
    return jsonify({"success": False, "message": "Profile not found"})


@profile_blueprint.route("/profile/save", methods=["POST", "OPTIONS"])
def save_profile():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200 
    user_id = get_user_id()
    data = request.json
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_profile
                (user_id, username, email, phone, address,
                 work_status, linkedin, github, gender, dob, marital_status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    username=VALUES(username),
                    email=VALUES(email),
                    phone=VALUES(phone),
                    address=VALUES(address),
                    work_status=VALUES(work_status),
                    linkedin=VALUES(linkedin),
                    github=VALUES(github),
                    gender=VALUES(gender),
                    dob=VALUES(dob),
                    marital_status=VALUES(marital_status)
            """, (
                user_id,
                data.get("username"),
                data.get("email"),
                data.get("phone"),
                data.get("address"),
                data.get("work_status"),
                data.get("linkedin"),
                data.get("github"),
                data.get("gender"),
                data.get("dob"),
                data.get("marital_status")
            ))
            conn.commit()
        return jsonify({"success": True, "message": "Profile saved successfully"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        conn.close()

@profile_blueprint.route("/skills/save", methods=["POST"])
def save_skills():
    user_id = get_user_id()
    skills = request.json.get("skills", [])
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM user_skills WHERE user_id=%s", (user_id,))
        for s in skills:
            cur.execute(
                "INSERT INTO user_skills(user_id, skill) VALUES (%s, %s)",
                (user_id, s)
            )
        conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Skills saved successfully"})

@profile_blueprint.route("/skills/delete", methods=["POST"])
def delete_skill():
    user_id = get_user_id()
    skill_id = request.json.get("skill_id")
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM user_skills WHERE id=%s AND user_id=%s",
            (skill_id, user_id)
        )
        conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Skill deleted"})

@profile_blueprint.route("/skills/get", methods=["GET"])
def get_skills():
    user_id = get_user_id()
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, skill FROM user_skills WHERE user_id=%s",
            (user_id,)
        )
        rows = cur.fetchall()
    conn.close()
    return jsonify({"skills": rows})

@profile_blueprint.route("/languages/get", methods=["GET"])
def get_languages():
    user_id = get_user_id()
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, language FROM user_languages WHERE user_id=%s",
            (user_id,)
        )
        rows = cur.fetchall()
    conn.close()
    return jsonify({"languages": rows})

@profile_blueprint.route("/languages/save", methods=["POST"])
def save_languages():
    user_id = get_user_id()
    languages = request.json.get("languages", [])
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM user_languages WHERE user_id=%s", (user_id,))
        for l in languages:
            cur.execute(
                "INSERT INTO user_languages(user_id, language) VALUES (%s, %s)",
                (user_id, l)
            )
        conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Languages saved successfully"})

@profile_blueprint.route("/languages/delete", methods=["POST"])
def delete_language():
    user_id = get_user_id()
    lang_id = request.json.get("language_id")
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM user_languages WHERE id=%s AND user_id=%s",
            (lang_id, user_id)
        )
        conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Language deleted"})

@profile_blueprint.route("/projects/get", methods=["GET"])
def get_projects():
    user_id = get_user_id()
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id,
                   project_name AS name,
                   year,
                   description AS `desc`,
                   project_link AS link
            FROM user_projects
            WHERE user_id=%s
        """, (user_id,))
        rows = cur.fetchall()
    conn.close()
    return jsonify({"projects": rows})

@profile_blueprint.route("/projects/save", methods=["POST"])
def save_projects():
    user_id = get_user_id()
    projects = request.json.get("projects", [])
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM user_projects WHERE user_id=%s", (user_id,))
        for p in projects:
            cur.execute("""
                INSERT INTO user_projects
                (user_id, project_name, year, description, project_link)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                user_id,
                p.get("name"),
                p.get("year"),
                p.get("desc"),
                p.get("link")
            ))
        conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Projects saved successfully"})

@profile_blueprint.route("/projects/delete", methods=["POST"])
def delete_project():
    user_id = get_user_id()
    project_id = request.json.get("project_id")
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM user_projects WHERE id=%s AND user_id=%s",
            (project_id, user_id)
        )
        conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Project deleted"})

DEGREE_ENCODING = {
    "MCA (Post Graduate)": 0,
    "B.Tech (Under Graduate)": 1,
    "BSC (Under Graduate)": 2,
    "BCom": 3,
    "Diploma": 4,
    "Intermediate": 5,
    "10th Class": 6
}

DEGREE_DECODING = {v: k for k, v in DEGREE_ENCODING.items()}
@profile_blueprint.route("/education/save", methods=["POST"])
def save_education():
    user_id = get_user_id()
    education = request.json.get("education", [])

    conn = get_db_connection()
    with conn.cursor() as cur:
        for e in education:
            cur.execute("""
                INSERT INTO user_education
                (user_id, degree, specialization, cgpa, start_year, end_year)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                int(e["degree"]),
                e["spec"],
                e["cgpa"],
                e["start"],
                e["end"]
            ))
        conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Education saved"})

@profile_blueprint.route("/education/get", methods=["GET"])
def get_education():
    user_id = get_user_id()
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, degree, specialization, cgpa, start_year, end_year
            FROM user_education
            WHERE user_id=%s
            ORDER BY start_year DESC
        """, (user_id,))
        rows = cur.fetchall()
    conn.close()
    return jsonify({
        "education": [
            {
                "id": r["id"],
                "degree": DEGREE_DECODING.get(r["degree"], "Unknown"), 
                "spec": r["specialization"],
                "cgpa": r["cgpa"],
                "start": r["start_year"],
                "end": r["end_year"]
            } for r in rows
        ]
    })

@profile_blueprint.route("/education/delete", methods=["POST"])
def delete_education():
    user_id = get_user_id()
    edu_id = request.json.get("id")

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM user_education WHERE id=%s AND user_id=%s",
            (edu_id, user_id)
        )
        conn.commit()
    conn.close()
    return jsonify({"success": True})
def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").date()
    except ValueError:
        return None

@profile_blueprint.route("/experience/get", methods=["GET"])
def get_experience():
    user_id = get_user_id()
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id,
                   company_name AS c,
                   start_date AS s,
                   end_date AS e,
                   description AS d
            FROM user_experience
            WHERE user_id=%s
            ORDER BY start_date DESC
        """, (user_id,))
        rows = cur.fetchall()
    conn.close()
    experiences = []
    for r in rows:
        experiences.append({
            "id": r["id"],
            "c": r["c"],
            "s": r["s"].strftime("%d/%m/%Y") if r["s"] else "",
            "e": r["e"].strftime("%d/%m/%Y") if r["e"] else "",
            "d": r["d"]
        })
    return jsonify({"experiences": experiences})

@profile_blueprint.route("/experience/save", methods=["POST"])
def save_experience():
    user_id = get_user_id()
    experiences = request.json.get("experiences", [])
    conn = get_db_connection()
    with conn.cursor() as cur:
        for ex in experiences:
            if ex.get("id"):
                cur.execute("""
                    UPDATE user_experience
                    SET company_name=%s,
                        start_date=%s,
                        end_date=%s,
                        description=%s
                    WHERE id=%s AND user_id=%s
                """, (
                    ex.get("c"),
                    parse_date(ex.get("s")),
                    parse_date(ex.get("e")),
                    ex.get("d"),
                    ex.get("id"),
                    user_id
                ))
            else:
                cur.execute("""
                    INSERT INTO user_experience
                    (user_id, company_name, start_date, end_date, description)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    user_id,
                    ex.get("c"),
                    parse_date(ex.get("s")),
                    parse_date(ex.get("e")),
                    ex.get("d")
                ))
        conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Experience saved successfully"})

@profile_blueprint.route("/experience/delete", methods=["POST"])
def delete_experience():
    user_id = get_user_id()
    exp_id = request.json.get("id")
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM user_experience WHERE id=%s AND user_id=%s",
            (exp_id, user_id)
        )
        conn.commit()
    conn.close()
    return jsonify({"success": True})

@profile_blueprint.route("/certifications/get", methods=["GET"])
def get_certifications():
    user_id = get_user_id()
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id,
                   company,
                   course,
                   cert_link AS link
            FROM user_certifications
            WHERE user_id=%s
        """, (user_id,))
        rows = cur.fetchall()
    conn.close()
    return jsonify({"certificates": rows})

@profile_blueprint.route("/certifications/save", methods=["POST"])
def save_certifications():
    user_id = get_user_id()
    certificates = request.json.get("certificates", [])
    conn = get_db_connection()
    with conn.cursor() as cur:
        for c in certificates:
            if c.get("id"):
                cur.execute("""
                    UPDATE user_certifications
                    SET company=%s, course=%s, cert_link=%s
                    WHERE id=%s AND user_id=%s
                """, (
                    c.get("company"),
                    c.get("course"),
                    c.get("link"),
                    c.get("id"),
                    user_id
                ))
            else:
                cur.execute("""
                    INSERT INTO user_certifications
                    (user_id, company, course, cert_link)
                    VALUES (%s, %s, %s, %s)
                """, (
                    user_id,
                    c.get("company"),
                    c.get("course"),
                    c.get("link")
                ))
        conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Certifications saved successfully"})

@profile_blueprint.route("/certifications/delete", methods=["POST"])
def delete_certification():
    user_id = get_user_id()
    cert_id = request.json.get("cert_id")

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM user_certifications WHERE id=%s AND user_id=%s",
            (cert_id, user_id)
        )
        conn.commit()
    conn.close()
    return jsonify({"success": True})

@profile_blueprint.route("/resume/upload", methods=["POST"])
def upload_resume():
    user_id = get_user_id()
    if "resume" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"})
    file = request.files["resume"]
    filename = f"user_{user_id}_{secure_filename(file.filename)}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM user_resume WHERE user_id=%s", (user_id,))
        cur.execute("INSERT INTO user_resume(user_id, file_name, file_path) VALUES (%s, %s, %s)",
                    (user_id, filename, filepath))
        conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Resume uploaded successfully"})

@profile_blueprint.route("/resume/delete", methods=["DELETE"])
def delete_resume():
    user_id = get_user_id()
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT file_path FROM user_resume WHERE user_id=%s", (user_id,))
        result = cur.fetchone()
        if result:
            path = result["file_path"]
            if os.path.exists(path):
                os.remove(path)
            cur.execute("DELETE FROM user_resume WHERE user_id=%s", (user_id,))
            conn.commit()
            conn.close()
            return jsonify({"success": True, "message": "Resume deleted successfully"})
    conn.close()
    return jsonify({"success": False, "message": "No resume found"})

@profile_blueprint.route("/resume", methods=["GET"])
def get_resume():
    user_id = get_user_id()
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT file_name FROM user_resume WHERE user_id=%s",
            (user_id,)
        )
        result = cur.fetchone()
    conn.close()
    if result:
        return jsonify({
            "success": True,
            "file_name": result["file_name"]
        })

    return jsonify({"success": False})

@profile_blueprint.route("/resume/view", methods=["GET"])
def view_resume():
    user_id = get_user_id()
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT file_path, file_name FROM user_resume WHERE user_id=%s",
            (user_id,)
        )
        result = cur.fetchone()
    conn.close()
    if not result:
        return jsonify({"success": False, "message": "No resume found"}), 404
    directory = os.path.dirname(result["file_path"])
    filename = os.path.basename(result["file_path"])
    return send_from_directory(directory, filename, as_attachment=False)











