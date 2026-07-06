from flask import Flask, render_template, request, redirect, session
from flask import send_file
import io
import sqlite3
import pickle
import numpy as np
import bcrypt
from datetime import datetime
from database import create_tables
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.secret_key = "health_secret"

create_tables()

heart_model = pickle.load(open("models/heart_model.pkl", "rb"))
kidney_model = pickle.load(open("models/kidney_model.pkl", "rb"))

# -----------------------------
# FINAL RESULT FUNCTION
# -----------------------------
def get_final_result(heart, kidney):

    if heart and kidney:
        if heart["result"] == "High Risk" or kidney["result"] == "High Risk":
            return "High Risk"
        elif heart["result"] == "Moderate Risk" or kidney["result"] == "Moderate Risk":
            return "Moderate Risk"
        else:
            return "Low Risk"

    elif heart:
        return heart["result"]

    elif kidney:
        return kidney["result"]

    return None



# -----------------------------
# LOGIN PAGE
# -----------------------------
@app.route("/")
def index():
    return render_template("login.html")


# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["POST"])
def login():

    user = request.form["username"].strip()
    pwd = request.form["password"].strip()

    conn = sqlite3.connect("health.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username=?", (user,))
    data = cur.fetchone()
    conn.close()

    if data:
        stored_pwd = data[2]

        if bcrypt.checkpw(pwd.encode('utf-8'), stored_pwd):
            session["user"] = user
            session["city"] = data[3]
            session["profession"] = data[4]
            return redirect("/dashboard")

    return "Invalid Login"


# -----------------------------
# REGISTER PAGE
# -----------------------------
@app.route("/register")
def register_page():
    return render_template("register.html")


# -----------------------------
# REGISTER
# -----------------------------
@app.route("/register_user", methods=["POST"])
def register_user():

    user = request.form["username"]
    pwd = request.form["password"]
    city = request.form["city"]
    profession = request.form["profession"]

    conn = sqlite3.connect("health.db")
    cur = conn.cursor()

    # CHECK EXISTING USER
    cur.execute("SELECT * FROM users WHERE username=?", (user,))
    existing_user = cur.fetchone()

    if existing_user:
        conn.close()
        return "Username already exists"

    # PASSWORD VALIDATION
    if len(pwd) < 6:
        return "Password must be at least 6 characters"
    if not any(c.isupper() for c in pwd):
        return "Must contain uppercase"
    if not any(c.islower() for c in pwd):
        return "Must contain lowercase"
    if not any(c.isdigit() for c in pwd):
        return "Must contain number"
    if not any(c in "@#$%^&*" for c in pwd):
        return "Must contain special character"

    # HASH PASSWORD
    hashed_pwd = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())

    # INSERT USER WITH CITY + PROFESSION
    cur.execute(
        "INSERT INTO users(username,password,city,profession) VALUES(?,?,?,?)",
        (user, hashed_pwd, city, profession)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# -----------------------------
# DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("health.db")
    cur = conn.cursor()

    # ---------------------------------------------------------
    # USER-WISE PREDICTION HISTORY GRAPH
    # ---------------------------------------------------------
    # If user has only one prediction:
    #     X-axis label = user's city name
    #
    # If user has multiple predictions:
    #     X-axis labels = Report 1, Report 2, Report 3, ...
    #
    # This ensures:
    # - Only logged-in user's data is shown
    # - No other users' data is visible
    # - Single prediction shows city name
    # - Multiple predictions show report numbering
    # ---------------------------------------------------------
    cur.execute("""
        SELECT created_at,
               heart_percent,
               kidney_percent
        FROM predictions
        WHERE username = ?
        ORDER BY id ASC
    """, (session["user"],))

    prediction_data = cur.fetchall()

    cities = []   # Used as chart labels in dashboard.html
    values = []   # Used as chart values in dashboard.html

    total_reports = len(prediction_data)

    for i, row in enumerate(prediction_data, start=1):
        heart_percent = row[1] if row[1] else 0
        kidney_percent = row[2] if row[2] else 0

        # Calculate percentage for this specific prediction
        user_percent = round((heart_percent + kidney_percent) / 2, 2)

        # If only one prediction, show city name
        if total_reports == 1:
            label = session["city"]
        else:
            # If multiple predictions, show Report 1, Report 2, etc.
            label = f"Report {i}"

        cities.append(label)
        values.append(user_percent)

    # ---------------------------------------------------------
    # AI SUGGESTION LOGIC
    # ---------------------------------------------------------
    cur.execute("""
        SELECT final_result
        FROM predictions
        WHERE username = ?
        ORDER BY id DESC
        LIMIT 1
    """, (session["user"],))

    last = cur.fetchone()

    if last:
        final_result = last[0]

        if final_result == "High Risk":
            suggestion = "⚠️ High risk detected. Immediate medical consultation is strongly recommended."
        elif final_result == "Moderate Risk":
            suggestion = "⚠️ Moderate risk. Regular monitoring and lifestyle improvements are advised."
        else:
            suggestion = "✅ You are doing well. Maintain your healthy lifestyle."
    else:
        suggestion = "No analysis done yet. Please perform a health check."

    conn.close()

    return render_template(
        "dashboard.html",
        suggestion=suggestion,
        cities=cities,
        values=values
    )


# -----------------------------
# HEART PAGE
# -----------------------------
@app.route("/heart_analyzer")
def heart_analyzer():
    if "user" not in session:
        return redirect("/")
    return render_template("patient_form.html")


# -----------------------------
# KIDNEY PAGE
# -----------------------------
@app.route("/kidney_analyzer")
def kidney_analyzer():
    if "user" not in session:
        return redirect("/")
    return render_template("kidney_form.html")


# -----------------------------
# HEART PREDICTION
# -----------------------------
@app.route("/predict_heart", methods=["POST"])
def predict_heart():

    if "user" not in session:
        return redirect("/")

    age = float(request.form["age"])
    sex = float(request.form["sex"])
    cp = float(request.form["cp"])
    trestbps = float(request.form["trestbps"])
    chol = float(request.form["chol"])
    fbs = float(request.form["fbs"])
    restecg = float(request.form["restecg"])
    thalach = float(request.form["thalach"])
    exang = float(request.form["exang"])
    oldpeak = float(request.form["oldpeak"])
    slope = float(request.form["slope"])
    ca = float(request.form["ca"])
    thal = float(request.form["thal"])

    heart_input = np.array([[age, sex, cp, trestbps, chol, fbs,
                             restecg, thalach, exang, oldpeak,
                             slope, ca, thal]])

    heart_prob = heart_model.predict_proba(heart_input)[0][1] * 100
    percent = round(heart_prob, 2)

    if percent < 40:
        result = "Low Risk"
        suggestion = "Maintain healthy lifestyle, regular exercise and balanced diet."
    elif percent < 70:
        result = "Moderate Risk"
        suggestion = "Monitor your health regularly and consult doctor if symptoms appear."
    else:
        result = "High Risk"
        suggestion = "High risk detected. Please consult a doctor immediately."

    heart_data = {
        "result": result,
        "percent": percent,
        "suggestion": suggestion
    }

    # STORE HEART RESULT IN SESSION
    session["heart_result"] = result


    session["heart_percent"] = percent

    final = get_final_result(heart_data, None)

    return render_template("result.html", heart=heart_data, kidney=None, final=final)


# -----------------------------
# KIDNEY PREDICTION
# -----------------------------
@app.route("/predict_kidney", methods=["POST"])
def predict_kidney():

    if "user" not in session:
        return redirect("/")

    bp = float(request.form["bp"])
    sugar = float(request.form["sugar"])
    creatinine = float(request.form["creatinine"])

    kidney_input = np.array([[bp, sugar, creatinine]])

    kidney_prob = kidney_model.predict_proba(kidney_input)[0][1] * 100
    percent = round(kidney_prob, 2)

    if percent < 40:
        result = "Low Risk"
        suggestion = "Stay hydrated, reduce salt intake and maintain healthy diet."
    elif percent < 70:
        result = "Moderate Risk"
        suggestion = "Regular checkups recommended. Monitor BP and sugar levels."
    else:
        result = "High Risk"
        suggestion = "Serious risk detected. Consult a nephrologist immediately."

    kidney_data = {
        "result": result,
        "percent": percent,
        "suggestion": suggestion
    }

    final = get_final_result(None, kidney_data)

    # INSERT INTO DATABASE (FINAL STEP)
    heart_result = session.get("heart_result", "Not Done")

    # DATE TIME
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    conn = sqlite3.connect("health.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO predictions 
    (username, heart_result, kidney_result, final_result, heart_percent, kidney_percent, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        session["user"],
        heart_result,
        result,
        final,
        session.get("heart_percent", 0),
        percent,
        now
    ))

    conn.commit()
    conn.close()

    # CLEAR SESSION (GOOD PRACTICE)
    session.pop("heart_result", None)

    return render_template("result.html", heart=None, kidney=kidney_data, final=final)

# -----------------------------
# History
# -----------------------------

@app.route("/history")
def history():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("health.db")
    cur = conn.cursor()

    city_filter = request.args.get("city")
    profession_filter = request.args.get("profession")

    query = """
    SELECT p.id, p.username, p.heart_result, p.kidney_result, p.final_result,
           p.created_at, p.heart_percent, p.kidney_percent,
           u.city, u.profession
    FROM predictions p
    JOIN users u ON p.username = u.username
    WHERE p.username=?
    """

    params = [session["user"]]

    if city_filter:
        query += " AND u.city=?"
        params.append(city_filter)

    if profession_filter:
        query += " AND u.profession=?"
        params.append(profession_filter)

    cur.execute(query, tuple(params))

    data = cur.fetchall()
    conn.close()

    # GRAPH DATA (REAL %)
    graph_data = []

    for row in data:
        date = row[5]

        heart_p = row[6] if row[6] else 0
        kidney_p = row[7] if row[7] else 0

        # take average for combined graph
        avg = (heart_p + kidney_p) / 2

        graph_data.append({
            "date": date,
            "value": avg
        })

    return render_template("history.html", data=data, graph_data=graph_data)

# -----------------------------
# DOWNLOAD PDF
# -----------------------------

@app.route("/download_report/<int:id>")
def download_report(id):

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("health.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT username, heart_result, kidney_result, final_result, created_at 
    FROM predictions 
    WHERE id=? AND username=?
    """, (id, session["user"]))

    data = cur.fetchone()
    conn.close()

    if not data:
        return "No record found"

    username, heart, kidney, final, date = data

    # -----------------------------
    # Suggestions logic
    # -----------------------------
    def get_suggestion(result):
        if result == "Low Risk":
            return "Maintain healthy lifestyle and balanced diet."
        elif result == "Moderate Risk":
            return "Regular monitoring and medical checkups recommended."
        else:
            return "Immediate medical consultation required."

    heart_suggestion = get_suggestion(heart)
    kidney_suggestion = get_suggestion(kidney)

    # -----------------------------
    # Create PDF in memory
    # -----------------------------
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    content = []

    # -----------------------------
    # HEADER
    # -----------------------------
    content.append(Paragraph("<b>AI HEALTH ANALYZER REPORT</b>", styles['Title']))
    content.append(Spacer(1, 20))

    content.append(Paragraph(f"<b>Patient:</b> {username}", styles['Normal']))
    content.append(Paragraph(f"<b>Date:</b> {date}", styles['Normal']))
    content.append(Spacer(1, 15))

    # -----------------------------
    # RESULTS TABLE
    # -----------------------------
    table_data = [
        ["Category", "Result"],
        ["Heart", heart],
        ["Kidney", kidney],
        ["Final Status", final]
    ]

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR',(0,0),(-1,0),colors.black),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('BOTTOMPADDING',(0,0),(-1,0),10),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))

    content.append(table)
    content.append(Spacer(1, 20))

    # -----------------------------
    # FINAL STATUS HIGHLIGHT
    # -----------------------------
    content.append(Paragraph(f"<b>FINAL HEALTH STATUS: {final}</b>", styles['Heading2']))
    content.append(Spacer(1, 15))

    # -----------------------------
    # SUGGESTIONS
    # -----------------------------
    content.append(Paragraph("<b>Suggestions:</b>", styles['Heading3']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"• Heart: {heart_suggestion}", styles['Normal']))
    content.append(Paragraph(f"• Kidney: {kidney_suggestion}", styles['Normal']))
    content.append(Spacer(1, 20))

    # -----------------------------
    # DISCLAIMER
    # -----------------------------
    content.append(Paragraph(
        "<i>Note: This report is generated using AI and should not be considered as a medical diagnosis. Please consult a doctor for proper medical advice.</i>",
        styles['Normal']
    ))

    # Build PDF
    doc.build(content)

    buffer.seek(0)

    # -----------------------------
    # DOWNLOAD FILE
    # -----------------------------
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Health_Report_{id}.pdf",
        mimetype='application/pdf'
    )

# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)