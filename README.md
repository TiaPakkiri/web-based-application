
# Sustainability Project Tracker (Firebase Version)

## Overview
A Flask web app for tracking sustainability projects at DUT, now using Firebase (Firestore & Auth) for backend data and authentication.

## Folder Structure
- src/: Flask backend and Firebase admin integration
- public/: Frontend assets and Firebase JS SDK
- templates/: HTML templates
- static/: CSS and JS

## Setup
1. Add your Firebase Admin SDK JSON file and set FIREBASE_ADMIN_CREDENTIAL in .env
2. Install dependencies: `pip install -r requirements.txt`
3. Run Flask app: `python src/app.py`

## Features
- Project submission and dashboard
- Firebase authentication
- Firestore project storage
- Role-based access control

## To Do
- Complete frontend integration
- Add client-side validation
- Implement PDF reporting
- Ensure POPIA compliance

