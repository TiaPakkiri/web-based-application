from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from firebase_setup import db, login_required, role_required, create_user, get_user, update_user_role
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Home page - redirect based on auth status"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role', 'student')
        
        # Validate input
        if not email or not password or not full_name:
            flash('All fields are required', 'error')
            return redirect(url_for('register'))
        
        # Check if user exists
        existing_user = get_user(email)
        if existing_user:
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        # Create user
        user_id = create_user(email, password, full_name, role)
        if user_id:
            # Set session
            session['user_id'] = user_id
            session['email'] = email
            session['full_name'] = full_name
            session['role'] = role
            flash(f'Welcome, {full_name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return redirect(url_for('login'))
        
        # Get user from database
        user = get_user(email)
        if user and user.get('email') == email:
            # In production, use proper password hashing
            session['user_id'] = user.get('id')
            session['email'] = user.get('email')
            session['full_name'] = user.get('full_name')
            session['role'] = user.get('role')
            flash(f'Welcome back, {user.get("full_name")}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# ==================== DASHBOARD ROUTES ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard - role-based view"""
    user_role = session.get('role')
    
    if user_role == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('student_dashboard'))

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    """Student dashboard"""
    projects = []
    user_projects = []
    
    if db:
        try:
            # Get all approved projects
            docs = db.collection('projects').where('status', '==', 'Approved').stream()
            projects = [{'id': doc.id, **doc.to_dict()} for doc in docs]
            
            # Get user's own projects
            user_docs = db.collection('projects').where('user_id', '==', session.get('user_id')).stream()
            user_projects = [{'id': doc.id, **doc.to_dict()} for doc in user_docs]
        except Exception as e:
            print(f"Error fetching projects: {e}")
    
    return render_template('student/dashboard.html', 
                         projects=projects, 
                         user_projects=user_projects,
                         full_name=session.get('full_name'))

@app.route('/admin/dashboard')
@role_required('admin')
def admin_dashboard():
    """Admin dashboard"""
    pending_projects = []
    approved_projects = []
    total_users = 0
    
    if db:
        try:
            # Get pending projects
            pending_docs = db.collection('projects').where('status', '==', 'Pending').stream()
            pending_projects = [{'id': doc.id, **doc.to_dict()} for doc in pending_docs]
            
            # Get approved projects
            approved_docs = db.collection('projects').where('status', '==', 'Approved').stream()
            approved_projects = [{'id': doc.id, **doc.to_dict()} for doc in approved_docs]
            
            # Get total users
            users_docs = db.collection('users').stream()
            total_users = len(list(users_docs))
        except Exception as e:
            print(f"Error fetching admin data: {e}")
    
    return render_template('admin/dashboard.html',
                         pending_projects=pending_projects,
                         approved_projects=approved_projects,
                         total_users=total_users,
                         full_name=session.get('full_name'))

# ==================== PROJECT ROUTES ====================

@app.route('/submit-project', methods=['GET', 'POST'])
@login_required
def submit_project():
    """Submit new project"""
    if session.get('role') == 'admin':
        flash('Admins cannot submit projects', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = {
            'title': request.form.get('title'),
            'short_description': request.form.get('short_description'),
            'detailed_description': request.form.get('detailed_description'),
            'campus': request.form.get('campus'),
            'category': request.form.get('category'),
            'status': 'Pending',
            'user_id': session.get('user_id'),
            'submitted_by': session.get('full_name'),
            'date_submitted': datetime.utcnow().isoformat()
        }
        
        if db:
            try:
                db.collection('projects').add(data)
                flash('Project submitted successfully! Awaiting admin approval.', 'success')
                return redirect(url_for('student_dashboard'))
            except Exception as e:
                print(f"Error submitting project: {e}")
                flash('Failed to submit project', 'error')
        else:
            flash('Database unavailable', 'error')
    
    return render_template('student/submit_project.html')

@app.route('/project/<project_id>')
@login_required
def project_detail(project_id):
    """View project details"""
    if db:
        try:
            project = db.collection('projects').document(project_id).get()
            if project.exists:
                return render_template('shared/project_detail.html', 
                                     project={'id': project.id, **project.to_dict()})
        except Exception as e:
            print(f"Error fetching project: {e}")
    
    flash('Project not found', 'error')
    return redirect(url_for('student_dashboard'))

# ==================== ADMIN ROUTES ====================

@app.route('/admin/pending')
@role_required('admin')
def admin_pending():
    """View pending projects for approval"""
    projects = []
    if db:
        try:
            docs = db.collection('projects').where('status', '==', 'Pending').stream()
            projects = [{'id': doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            print(f"Error fetching pending projects: {e}")
    
    return render_template('admin/pending.html', projects=projects)

@app.route('/admin/approve/<project_id>', methods=['POST'])
@role_required('admin')
def approve_project(project_id):
    """Approve project"""
    if db:
        try:
            db.collection('projects').document(project_id).update({
                'status': 'Approved',
                'approved_at': datetime.utcnow().isoformat()
            })
            flash('Project approved successfully', 'success')
        except Exception as e:
            print(f"Error approving project: {e}")
            flash('Failed to approve project', 'error')
    
    return redirect(url_for('admin_pending'))

@app.route('/admin/reject/<project_id>', methods=['POST'])
@role_required('admin')
def reject_project(project_id):
    """Reject project"""
    if db:
        try:
            db.collection('projects').document(project_id).update({
                'status': 'Rejected',
                'rejected_at': datetime.utcnow().isoformat()
            })
            flash('Project rejected', 'info')
        except Exception as e:
            print(f"Error rejecting project: {e}")
            flash('Failed to reject project', 'error')
    
    return redirect(url_for('admin_pending'))

@app.route('/admin/users')
@role_required('admin')
def manage_users():
    """Manage users"""
    users = []
    if db:
        try:
            docs = db.collection('users').stream()
            users = [{'id': doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            print(f"Error fetching users: {e}")
    
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/<user_id>/role', methods=['POST'])
@role_required('admin')
def update_user_role_route(user_id):
    """Update user role"""
    new_role = request.form.get('role')
    if new_role in ['student', 'admin']:
        if update_user_role(user_id, new_role):
            flash('User role updated', 'success')
        else:
            flash('Failed to update user role', 'error')
    
    return redirect(url_for('manage_users'))

# ==================== NOTIFICATIONS ====================

@app.route('/notifications')
@login_required
def notifications():
    """View notifications"""
    return render_template('shared/notifications.html',
                         full_name=session.get('full_name'))

# ==================== HEALTH CHECK ====================

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'database': 'connected' if db else 'disconnected'})

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(error):
    return render_template('shared/error.html', error_code=404, error_message='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('shared/error.html', error_code=500, error_message='Internal server error'), 500

if __name__ == '__main__':
    print("Starting Flask app on http://127.0.0.1:5000")
    print(f"Firebase configured: {db is not None}")
    app.run(debug=True)
