import os
import uuid
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Upload, Review, Strike, WithdrawalRequest, AdminAction, Rating
from forms import SignupForm, LoginForm, UploadForm, ReviewForm, WithdrawalForm, RatingForm
from utils import allowed_file, get_file_size, calculate_xp_reward
from openai_service import detect_duplicate_content, check_content_quality

def create_test_files(test_user):
    """Create test files for review demonstration"""
    test_files = [
        {
            'filename': 'sample_video_tutorial.mp4',
            'original_filename': 'Python Programming Tutorial - Basics.mp4',
            'description': 'A comprehensive tutorial covering Python programming fundamentals including variables, loops, and functions.',
            'category': 'video',
            'file_size': 15728640  # 15MB
        },
        {
            'filename': 'machine_learning_paper.pdf',
            'original_filename': 'Deep Learning in Computer Vision - Research Paper.pdf',
            'description': 'Academic research paper discussing the latest advances in deep learning techniques for computer vision applications.',
            'category': 'document',
            'file_size': 2097152  # 2MB
        },
        {
            'filename': 'javascript_project.zip',
            'original_filename': 'React E-commerce Project.zip',
            'description': 'Complete React.js e-commerce website project with shopping cart, user authentication, and payment integration.',
            'category': 'code',
            'file_size': 5242880  # 5MB
        },
        {
            'filename': 'nature_sounds.mp3',
            'original_filename': 'Relaxing Forest Sounds - 1 Hour.mp3',
            'description': 'High-quality audio recording of peaceful forest sounds including birds chirping and gentle wind through trees.',
            'category': 'audio',
            'file_size': 8388608  # 8MB
        },
        {
            'filename': 'website_design.png',
            'original_filename': 'Modern UI Design Mockup.png',
            'description': 'Professional website design mockup showcasing modern UI/UX principles with clean layouts and responsive design.',
            'category': 'image',
            'file_size': 1048576  # 1MB
        },
        {
            'filename': 'react_masterclass.mp4',
            'original_filename': 'React.js Advanced Concepts.mp4',
            'description': 'In-depth React.js tutorial covering hooks, context API, performance optimization, and advanced state management patterns.',
            'category': 'video',
            'file_size': 42000000  # 42MB
        },
        {
            'filename': 'cybersecurity_podcast.wav',
            'original_filename': 'Cybersecurity Weekly Episode 15.wav',
            'description': 'Latest cybersecurity trends discussion including zero-trust architecture, endpoint security, and threat intelligence.',
            'category': 'audio',
            'file_size': 28800000  # 28.8MB
        },
        {
            'filename': 'api_documentation.pdf',
            'original_filename': 'RESTful API Design Guide.pdf',
            'description': 'Comprehensive guide to designing scalable REST APIs with best practices, authentication methods, and documentation standards.',
            'category': 'document',
            'file_size': 3072000  # 3MB
        },
        {
            'filename': 'algorithm_implementation.py',
            'original_filename': 'data_structures_algorithms.py',
            'description': 'Python implementation of essential data structures and algorithms including binary trees, graphs, and dynamic programming.',
            'category': 'code',
            'file_size': 256000  # 256KB
        },
        {
            'filename': 'database_schema.png',
            'original_filename': 'E-commerce Database Design.png',
            'description': 'Detailed database schema diagram for a scalable e-commerce platform with proper normalization and indexing strategies.',
            'category': 'image',
            'file_size': 1536000  # 1.5MB
        },
        {
            'filename': 'devops_tutorial.avi',
            'original_filename': 'Docker & Kubernetes Tutorial.avi',
            'description': 'Complete DevOps tutorial covering containerization with Docker, orchestration with Kubernetes, and CI/CD pipeline setup.',
            'category': 'video',
            'file_size': 38400000  # 38.4MB
        },
        {
            'filename': 'tech_interview.m4a',
            'original_filename': 'Software Engineering Interview Prep.m4a',
            'description': 'Mock technical interview session covering system design, coding challenges, and behavioral questions for senior developers.',
            'category': 'audio',
            'file_size': 22528000  # 22.5MB
        },
        {
            'filename': 'ml_research_notes.txt',
            'original_filename': 'Machine Learning Research Notes.txt',
            'description': 'Detailed notes on latest machine learning research including transformer architectures, attention mechanisms, and neural networks.',
            'category': 'document',
            'file_size': 512000  # 512KB
        },
        {
            'filename': 'web_performance.js',
            'original_filename': 'performance_optimization_utils.js',
            'description': 'JavaScript utilities for web performance optimization including lazy loading, code splitting, and cache management.',
            'category': 'code',
            'file_size': 307200  # 300KB
        },
        {
            'filename': 'system_architecture.svg',
            'original_filename': 'Microservices Architecture Diagram.svg',
            'description': 'Scalable microservices architecture diagram showing service communication, load balancing, and database distribution.',
            'category': 'image',
            'file_size': 204800  # 200KB
        }
    ]
    
    for test_file in test_files:
        # Check if this test file already exists
        existing = Upload.query.filter_by(filename=test_file['filename']).first()
        if not existing:
            upload = Upload()
            upload.user_id = test_user.id
            upload.filename = test_file['filename']
            upload.original_filename = test_file['original_filename']
            upload.file_path = f"uploads/test_{test_file['filename']}"
            upload.file_size = test_file['file_size']
            upload.description = test_file['description']
            upload.category = test_file['category']
            upload.status = 'pending'
            upload.ai_consent = True
            
            db.session.add(upload)
    
    db.session.commit()

@app.route('/')
def index():
    """Landing page redirects directly to dashboard"""
    return redirect(url_for('dashboard'))

# Authentication routes removed - direct access to dashboard

# Logout functionality not needed without authentication

@app.route('/dashboard')
def dashboard():
    # Create or get demo user
    demo_user = User.query.filter_by(email='demo@alphanex.com').first()
    if not demo_user:
        demo_user = User()
        demo_user.name = 'Demo User'
        demo_user.email = 'demo@alphanex.com'
        demo_user.password_hash = generate_password_hash('demo123')
        demo_user.xp_points = 500  # Give some starting XP
        db.session.add(demo_user)
        db.session.commit()
    
    # Create or get a second demo user for test files
    test_user = User.query.filter_by(email='testuser@alphanex.com').first()
    if not test_user:
        test_user = User()
        test_user.name = 'Test User'
        test_user.email = 'testuser@alphanex.com'
        test_user.password_hash = generate_password_hash('test123')
        test_user.xp_points = 300
        db.session.add(test_user)
        db.session.commit()
        
        # Create test files from test user for demo user to review
        create_test_files(test_user)
    
    # Set demo user as current user context (no authentication needed)
    # login_user(demo_user)  # Removed since we don't need sessions
    
    # Get user stats
    upload_count = Upload.query.filter_by(user_id=demo_user.id).count()
    review_count = Review.query.filter_by(reviewer_id=demo_user.id).count()
    
    # Get recent uploads
    recent_uploads = Upload.query.filter_by(user_id=demo_user.id)\
                                .order_by(Upload.uploaded_at.desc()).limit(5).all()
    
    # Check daily upload limit
    daily_remaining = demo_user.get_daily_upload_remaining()
    daily_remaining_mb = daily_remaining / (1024 * 1024)
    
    return render_template('dashboard.html', 
                         upload_count=upload_count,
                         review_count=review_count,
                         recent_uploads=recent_uploads,
                         daily_remaining_mb=daily_remaining_mb,
                         demo_user=demo_user)

@app.route('/leaderboard')
def leaderboard():
    """Enhanced leaderboard with rankings and badges"""
    # Get all users ordered by XP points
    all_users = User.query.order_by(User.xp_points.desc()).all()
    top_users = all_users[:10]  # Top 10 for featured display
    
    return render_template('leaderboard.html', 
                         all_users=all_users,
                         top_users=top_users)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """File upload endpoint"""
    # Get demo user
    demo_user = User.query.filter_by(email='demo@alphanex.com').first()
    if not demo_user:
        return redirect(url_for('dashboard'))
        
    if demo_user.is_banned:
        flash('Your account is banned and cannot upload content.', 'error')
        return redirect(url_for('dashboard'))
    
    form = UploadForm()
    
    if form.validate_on_submit():
        file = form.file.data
        
        if file and allowed_file(file.filename):
            # Check file size and daily limit
            file_size = get_file_size(file)
            
            if not demo_user.can_upload(file_size):
                flash('Upload would exceed daily 500MB limit.', 'error')
                return render_template('uploader/upload.html', form=form)
            
            # Generate secure filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            
            try:
                file.save(file_path)
                
                # Create upload record
                upload = Upload()
                upload.user_id = demo_user.id
                upload.filename = unique_filename
                upload.original_filename = filename
                upload.file_path = file_path
                upload.file_size = file_size
                upload.description = form.description.data
                upload.category = form.category.data
                upload.ai_consent = form.ai_consent.data
                upload.status = 'pending'  # Set initial status to pending review
                
                # Update user's daily upload count and award XP
                demo_user.daily_upload_bytes += file_size
                upload_xp = calculate_xp_reward('upload')
                demo_user.xp_points += upload_xp
                
                db.session.add(upload)
                db.session.commit()
                
                # Run AI analysis with error handling
                try:
                    duplicate_score, spam_score = detect_duplicate_content(file_path, form.description.data)
                    upload.duplicate_score = duplicate_score
                    upload.spam_score = spam_score
                    
                    # Auto-flag if scores are high
                    if duplicate_score > 0.8 or spam_score > 0.7:
                        upload.status = 'flagged'
                        demo_user.add_strike('uploader', f'High duplicate ({duplicate_score:.2f}) or spam ({spam_score:.2f}) score')
                    
                    db.session.commit()
                except Exception as e:
                    # AI analysis failed but upload should still succeed
                    app.logger.error(f"AI analysis failed: {e}")
                    # Set default safe values
                    upload.duplicate_score = 0.0
                    upload.spam_score = 0.0
                    db.session.commit()
                
                flash(f'✅ Upload Complete! File "{filename}" has been successfully uploaded and saved. Status: Pending Review (will be approved within 24 hours). You earned {upload_xp} XP points!', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                app.logger.error(f"Upload failed: {e}")
                flash(f'Upload failed: {str(e)}', 'error')
        else:
            if file:
                flash('File type not supported. Please try a different file.', 'error')
            else:
                flash('Please select a file and ensure all fields are filled.', 'error')
    
    # Calculate remaining daily upload capacity with error handling
    try:
        daily_remaining = demo_user.get_daily_upload_remaining()
        daily_remaining_mb = daily_remaining / (1024 * 1024)
    except Exception as e:
        app.logger.error(f"Daily limit calculation failed: {e}")
        daily_remaining_mb = 500.0  # Default to full limit
    
    return render_template('uploader/upload.html', form=form, daily_remaining_mb=daily_remaining_mb, demo_user=demo_user)

@app.route('/review')
def review_content():
    """Content review endpoint - shows all uploaded files for review"""
    # Get demo user
    demo_user = User.query.filter_by(email='demo@alphanex.com').first()
    if not demo_user:
        return redirect(url_for('dashboard'))
    
    if demo_user.is_banned:
        flash('Your account is banned and cannot review content.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get uploads that need review (not from demo user and not already reviewed by them)
    # Show all uploads except those uploaded by demo user
    reviewed_upload_ids = [r.upload_id for r in demo_user.reviews]
    
    uploads = Upload.query.filter(
        Upload.user_id != demo_user.id,  # Cannot review own uploads
        ~Upload.id.in_(reviewed_upload_ids)  # Haven't reviewed yet
    ).order_by(Upload.uploaded_at.desc()).all()
    
    # Filter out uploads that already have 5 reviews (max reached)
    available_uploads = []
    for upload in uploads:
        review_count = Review.query.filter_by(upload_id=upload.id).count()
        if review_count < 5:  # Max 5 reviews per upload
            available_uploads.append(upload)
    
    return render_template('reviewer/review.html', uploads=available_uploads, demo_user=demo_user)

@app.route('/review/<int:upload_id>', methods=['GET', 'POST'])
def review_upload(upload_id):
    """Review a specific upload"""
    # Get demo user
    demo_user = User.query.filter_by(email='demo@alphanex.com').first()
    if not demo_user:
        return redirect(url_for('dashboard'))
        
    if demo_user.is_banned:
        flash('Your account is banned and cannot review content.', 'error')
        return redirect(url_for('dashboard'))
    
    upload = Upload.query.get_or_404(upload_id)
    
    # Check if user can review this upload
    if upload.user_id == demo_user.id:
        flash('You cannot review your own uploads.', 'error')
        return redirect(url_for('review_content'))
    
    # Check if user already reviewed this upload
    existing_review = Review.query.filter_by(upload_id=upload_id, reviewer_id=demo_user.id).first()
    if existing_review:
        flash('You have already reviewed this upload.', 'error')
        return redirect(url_for('review_content'))
    
    # Check if upload already has 5 reviews (max limit)
    review_count = Review.query.filter_by(upload_id=upload_id).count()
    if review_count >= 5:
        flash('This upload has reached the maximum number of reviews (5).', 'error')
        return redirect(url_for('review_content'))
    
    form = ReviewForm()
    
    if form.validate_on_submit():
        # Validate that bad reviews must have a reason
        if form.rating.data == 'bad' and (not form.description.data or len(form.description.data.strip()) < 10):
            flash('You must provide a detailed reason (at least 10 characters) for negative reviews.', 'error')
            return render_template('reviewer/review_upload.html', upload=upload, form=form)
        
        # Create review
        review = Review()
        review.upload_id = upload.id
        review.reviewer_id = demo_user.id
        review.rating = form.rating.data
        review.description = form.description.data
        review.xp_earned = calculate_xp_reward('review')
        
        # Award XP to reviewer
        demo_user.xp_points += review.xp_earned
        
        db.session.add(review)
        db.session.commit()
        
        # Check if this is the 5th review - make final decision
        total_reviews = Review.query.filter_by(upload_id=upload_id).count()
        if total_reviews >= 5:
            # Calculate final decision based on majority vote
            good_reviews = Review.query.filter_by(upload_id=upload_id, rating='good').count()
            bad_reviews = Review.query.filter_by(upload_id=upload_id, rating='bad').count()
            
            if good_reviews >= 3:
                # Upload accepted - award XP to uploader
                upload.status = 'approved'
                uploader = User.query.get(upload.user_id)
                if uploader:
                    uploader.xp_points += calculate_xp_reward('upload_approved')
                flash(f'Review submitted! Upload approved with {good_reviews} positive reviews. You earned {review.xp_earned} XP!', 'success')
            elif bad_reviews >= 3:
                # Upload denied - take XP from uploader
                upload.status = 'rejected'
                uploader = User.query.get(upload.user_id)
                if uploader:
                    penalty = calculate_xp_reward('upload')  # Same amount as upload reward
                    uploader.xp_points = max(0, uploader.xp_points - penalty)  # Don't go below 0
                flash(f'Review submitted! Upload denied with {bad_reviews} negative reviews. You earned {review.xp_earned} XP!', 'success')
            else:
                upload.status = 'pending'  # Still needs more reviews
                flash(f'Review submitted! Upload still pending ({total_reviews}/5 reviews complete). You earned {review.xp_earned} XP!', 'success')
            
            db.session.commit()
        else:
            flash(f'Review submitted! You earned {review.xp_earned} XP. Upload has {total_reviews}/5 reviews.', 'success')
        
        return redirect(url_for('review_content'))
    
    # Get existing reviews for this upload
    existing_reviews = Review.query.filter_by(upload_id=upload_id).all()
    
    return render_template('reviewer/review_upload.html', upload=upload, form=form, 
                         existing_reviews=existing_reviews, review_count=len(existing_reviews), demo_user=demo_user)

@app.route('/rating', methods=['GET', 'POST'])
def rate_website():
    """Website rating and feedback page"""
    # Get demo user
    demo_user = User.query.filter_by(email='demo@alphanex.com').first()
    if not demo_user:
        return redirect(url_for('dashboard'))
        
    form = RatingForm()
    
    if form.validate_on_submit():
        # Create rating record
        rating = Rating()
        rating.user_id = demo_user.id
        rating.rating = form.rating.data
        rating.category = form.category.data
        rating.description = form.description.data
        rating.contact_email = form.contact_email.data if form.contact_email.data else None
        
        db.session.add(rating)
        db.session.commit()
        
        flash('Thank you for your feedback! Your rating has been submitted and will help us improve Alpha Nex.', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('rating.html', form=form)

@app.route('/profile')
def profile():
    # Get demo user
    demo_user = User.query.filter_by(email='demo@alphanex.com').first()
    if not demo_user:
        return redirect(url_for('dashboard'))
        
    # Get user's strikes and violation history
    strikes = Strike.query.filter_by(user_id=demo_user.id)\
                         .order_by(Strike.created_at.desc()).all()
    
    # Get withdrawal requests
    withdrawals = WithdrawalRequest.query.filter_by(user_id=demo_user.id)\
                                        .order_by(WithdrawalRequest.created_at.desc()).all()
    
    return render_template('profile.html', strikes=strikes, withdrawals=withdrawals, demo_user=demo_user)

@app.route('/delete_upload/<int:upload_id>')
def delete_upload(upload_id):
    # Get demo user
    demo_user = User.query.filter_by(email='demo@alphanex.com').first()
    if not demo_user:
        return redirect(url_for('dashboard'))
        
    upload = Upload.query.get_or_404(upload_id)
    
    if upload.user_id != demo_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    # Calculate penalty if beyond free deletion window
    penalty = upload.get_deletion_penalty()
    
    if penalty > 0:
        if demo_user.xp_points < penalty:
            flash(f'Insufficient XP to delete. Penalty: {penalty} XP (You have: {demo_user.xp_points} XP)', 'error')
            return redirect(url_for('dashboard'))
        
        demo_user.xp_points -= penalty
        flash(f'Content deleted with {penalty} XP penalty.', 'warning')
    else:
        flash('Content deleted within free window.', 'success')
    
    # Delete file and record
    try:
        if os.path.exists(upload.file_path):
            os.remove(upload.file_path)
    except Exception as e:
        app.logger.error(f"Failed to delete file {upload.file_path}: {e}")
    
    db.session.delete(upload)
    db.session.commit()
    
    return redirect(url_for('dashboard'))

@app.route('/request_withdrawal', methods=['GET', 'POST'])
def request_withdrawal():
    # Get demo user
    demo_user = User.query.filter_by(email='demo@alphanex.com').first()
    if not demo_user:
        return redirect(url_for('dashboard'))
        
    form = WithdrawalForm()
    
    if form.validate_on_submit():
        amount_xp = form.amount_xp.data
        
        if amount_xp > demo_user.xp_points:
            flash('Insufficient XP points.', 'error')
            return render_template('profile.html', form=form)
        
        if amount_xp and amount_xp < 100:
            flash('Minimum withdrawal is 100 XP.', 'error')
            return render_template('profile.html', form=form)
        
        # Calculate USD amount (example: 100 XP = $1)
        amount_usd = (amount_xp or 0) / 100.0
        
        withdrawal = WithdrawalRequest()
        withdrawal.user_id = demo_user.id
        withdrawal.amount_xp = amount_xp
        withdrawal.amount_usd = amount_usd
        withdrawal.payment_method = form.payment_method.data
        withdrawal.payment_details = form.payment_details.data
        
        db.session.add(withdrawal)
        db.session.commit()
        
        flash(f'Withdrawal request submitted for {amount_xp} XP (${amount_usd:.2f}).', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', withdrawal_form=form)

@app.route('/admin')
def admin_panel():
    # Get demo user
    demo_user = User.query.filter_by(email='demo@alphanex.com').first()
    if not demo_user:
        return redirect(url_for('dashboard'))
        
    # Simple admin check (in production, use proper role system)
    if demo_user.email not in ['admin@alphanex.com']:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get pending items
    pending_withdrawals = WithdrawalRequest.query.filter_by(status='pending').count()
    flagged_content = Upload.query.filter_by(status='flagged').count()
    total_users = User.query.count()
    
    # Get recent violations
    recent_strikes = Strike.query.order_by(Strike.created_at.desc()).limit(10).all()
    
    return render_template('admin/panel.html', 
                         pending_withdrawals=pending_withdrawals,
                         flagged_content=flagged_content,
                         total_users=total_users,
                         recent_strikes=recent_strikes)

# API endpoint for countdown timer updates
@app.route('/api/upload_status/<int:upload_id>')
def upload_status(upload_id):
    # Get demo user
    demo_user = User.query.filter_by(email='demo@alphanex.com').first()
    if not demo_user:
        return jsonify({'error': 'User not found'}), 404
        
    upload = Upload.query.get_or_404(upload_id)
    
    if upload.user_id != demo_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    time_remaining = upload.deletion_deadline - datetime.utcnow()
    hours_remaining = max(0, time_remaining.total_seconds() / 3600)
    
    return jsonify({
        'hours_remaining': hours_remaining,
        'can_delete_free': upload.can_delete_free(),
        'penalty': upload.get_deletion_penalty()
    })
