from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from app.models import User, Person
import pyotp 
import qrcode
from io import BytesIO




@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/index')
@login_required
def index():
    persons = Person.query.all()
    return render_template('index.html', persons=persons)



import pyotp


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('index'))  # Redirect to index or home page
        else:
            flash('Invalid username or password.')

    return render_template('login.html')






@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Generate TOTP secret key
        otp_secret = pyotp.random_base32()

        # Create User object
        user = User(username=username, email=email, otp_secret=otp_secret)
        user.set_password(password)

        # Commit to database
        db.session.add(user)
        db.session.commit()

        # Generate QR code for TOTP setup
        otp_uri = pyotp.totp.TOTP(otp_secret).provisioning_uri(name=username, issuer_name='YourApp')
        img = qrcode.make(otp_uri)
        buffer = BytesIO()
        img.save(buffer)
        buffer.seek(0)
        qr_code = buffer.getvalue()

        # Display QR code to the user (you might want to render this in your template)
        return render_template('qr_code.html', qr_code=qr_code)

    return render_template('register.html')



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/update-username', methods=['POST'])
@login_required
def update_username():
    new_username = request.form.get('new_username')
    if not new_username:
        flash('Username cannot be empty')
        return redirect(url_for('profile'))
    current_user.username = new_username
    db.session.commit()
    flash('Username updated successfully')
    return redirect(url_for('profile'))

@app.route('/update-password', methods=['POST'])
@login_required
def update_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # Verify current password
    if not current_password or not current_user.check_password(current_password):
        flash('Current password is incorrect')
        return redirect(url_for('profile'))

    # Verify new password and confirmation match
    if not new_password or new_password != confirm_password:
        flash('New password and confirmation do not match')
        return redirect(url_for('profile'))

    # Update password
    current_user.set_password(new_password)
    db.session.commit()
    flash('Password updated successfully')
    return redirect(url_for('profile'))
@app.route('/update-info', methods=['GET', 'POST'])
@login_required
def update_info():
    if request.method == 'POST':
        new_username = request.form.get('new_username')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Verify current password
        if not current_password or not current_user.check_password(current_password):
            flash('Current password is incorrect')
            return redirect(url_for('update_info'))

        # Update username if provided
        if new_username:
            current_user.username = new_username

        # Update password if provided and valid
        if new_password and new_password == confirm_password:
            current_user.set_password(new_password)

        db.session.commit()
        flash('Information updated successfully')
        return redirect(url_for('profile'))

    return render_template('update_info.html')