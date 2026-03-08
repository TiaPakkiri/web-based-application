from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Campus, Category, Project

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your-secret-key"

db.init_app(app)

@app.route("/")
def home():
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    projects = Project.query.filter_by(status="Approved").all()
    return render_template("dashboard.html", projects=projects)

@app.route("/submit-project", methods=["GET", "POST"])
def submit_project():
    campuses = Campus.query.all()
    categories = Category.query.all()

    if request.method == "POST":
        title = request.form["title"]
        short_description = request.form["short_description"]
        detailed_description = request.form["detailed_description"]
        campus_id = request.form["campus_id"]
        category_id = request.form["category_id"]

        demo_user = User.query.first()

        new_project = Project(
            title=title,
            short_description=short_description,
            detailed_description=detailed_description,
            campus_id=campus_id,
            category_id=category_id,
            user_id=demo_user.id,
            status="Pending"
        )

        db.session.add(new_project)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("submit_project.html", campuses=campuses, categories=categories)

@app.route("/project/<int:project_id>")
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template("project_detail.html", project=project)

@app.route("/admin/pending")
def admin_pending():
    pending_projects = Project.query.filter_by(status="Pending").all()
    return render_template("admin_pending.html", projects=pending_projects)

@app.route("/admin/approve/<int:project_id>", methods=["POST"])
def approve_project(project_id):
    project = Project.query.get_or_404(project_id)
    project.status = "Approved"
    db.session.commit()
    return redirect(url_for("admin_pending"))

@app.route("/setup")
def setup():
    db.create_all()

    if not User.query.first():
        admin = User(full_name="Admin User", email="admin@dut.ac.za", role="admin")
        student = User(full_name="Student User", email="student@dut.ac.za", role="student")

        campus1 = Campus(name="Steve Biko")
        campus2 = Campus(name="ML Sultan")
        campus3 = Campus(name="Ritson")

        category1 = Category(name="Energy")
        category2 = Category(name="Recycling")

        db.session.add_all([admin, student, campus1, campus2, campus3, category1, category2])
        db.session.commit()

    return "Database created and sample data inserted."

@app.route("/add-ritson")
def add_ritson():
    existing = Campus.query.filter_by(name="Ritson").first()
    if not existing:
        ritson = Campus(name="Ritson")
        db.session.add(ritson)
        db.session.commit()
        return "Ritson added successfully."
    return "Ritson already exists."

@app.route("/notifications")
def notifications():
    return render_template("notifications.html")

if __name__ == "__main__":
    app.run(debug=True)
