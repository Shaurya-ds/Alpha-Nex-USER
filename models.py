from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta
from sqlalchemy import func

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    xp_points = db.Column(db.Integer, default=0)
    uploader_strikes = db.Column(db.Integer, default=0)
    reviewer_strikes = db.Column(db.Integer, default=0)
    is_banned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # KYC fields
    kyc_verified = db.Column(db.Boolean, default=False)
    document_path = db.Column(db.String(255))
    selfie_path = db.Column(db.String(255))
    
    # Daily upload tracking
    daily_upload_bytes = db.Column(db.Integer, default=0)
    daily_upload_reset = db.Column(db.DateTime, default=datetime.utcnow)
    
    # New fields for gamification
    current_badge = db.Column(db.String(50), default='New User')
    weekly_xp = db.Column(db.Integer, default=0)
    monthly_xp = db.Column(db.Integer, default=0)
    accuracy_percentage = db.Column(db.Float, default=0.0)
    referral_code = db.Column(db.String(20), unique=True)
    referred_by = db.Column(db.String(20))
    seasonal_badges = db.Column(db.Text)  # JSON string for badge collection
    
    # Relationships
    uploads = db.relationship('Upload', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='reviewer', lazy=True)
    strikes = db.relationship('Strike', backref='user', lazy=True)
    withdrawals = db.relationship('WithdrawalRequest', backref='user', lazy=True)
    contest_entries = db.relationship('ContestEntry', backref='user', lazy=True)
    
    def get_daily_upload_remaining(self):
        """Calculate remaining daily upload capacity in bytes"""
        try:
            # Reset daily counter if it's a new day
            if self.daily_upload_reset and datetime.utcnow().date() > self.daily_upload_reset.date():
                self.daily_upload_bytes = 0
                self.daily_upload_reset = datetime.utcnow()
                db.session.commit()
            elif not self.daily_upload_reset:
                # Handle case where daily_upload_reset is None
                self.daily_upload_reset = datetime.utcnow()
                db.session.commit()
            
            max_daily = 500 * 1024 * 1024  # 500MB in bytes
            current_usage = self.daily_upload_bytes or 0
            return max_daily - current_usage
        except Exception as e:
            # Return default full limit on any error
            return 500 * 1024 * 1024
    
    def can_upload(self, file_size):
        """Check if user can upload a file of given size"""
        return self.get_daily_upload_remaining() >= file_size and not self.is_banned
    
    def add_strike(self, strike_type, reason):
        strike = Strike()
        strike.user_id = self.id
        strike.strike_type = strike_type
        strike.reason = reason
        db.session.add(strike)
        
        if strike_type == 'uploader':
            self.uploader_strikes += 1
        elif strike_type == 'reviewer':
            self.reviewer_strikes += 1
            
        # Ban user if they reach 3 strikes in either category
        if self.uploader_strikes >= 3 or self.reviewer_strikes >= 3:
            self.is_banned = True
            
        db.session.commit()
    
    def get_badge_tier(self):
        """Calculate user's badge tier based on XP ranking"""
        try:
            total_users = User.query.count()
            if total_users == 0:
                return 'New User'
            
            # Get user's rank by XP
            users_above = User.query.filter(User.xp_points > self.xp_points).count()
            percentile = (users_above / total_users) * 100
            
            if percentile <= 1:
                return 'Top 1%'
            elif percentile <= 5:
                return 'Top 5%'
            elif percentile <= 10:
                return 'Top 10%'
            elif percentile <= 25:
                return 'Top 25%'
            elif percentile <= 50:
                return 'Top 50%'
            else:
                return 'Active User'
        except:
            return 'New User'
    
    def get_badge_color(self):
        """Get badge color based on tier"""
        badge_colors = {
            'Top 1%': 'danger',  # Fire badge (red)
            'Top 5%': 'warning',  # Gold
            'Top 10%': 'light',   # Silver
            'Top 25%': 'dark',    # Bronze
            'Top 50%': 'primary', # Blue
            'Active User': 'secondary',
            'New User': 'secondary'
        }
        return badge_colors.get(self.get_badge_tier(), 'secondary')
    
    def update_weekly_monthly_xp(self, xp_gained):
        """Update weekly and monthly XP tracking"""
        # Simple implementation - in production, would reset based on actual week/month
        self.weekly_xp += xp_gained
        self.monthly_xp += xp_gained

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    ai_consent = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    deletion_deadline = db.Column(db.DateTime)
    
    # AI analysis results
    duplicate_score = db.Column(db.Float, default=0.0)
    spam_score = db.Column(db.Float, default=0.0)
    
    # Review tracking
    reviews = db.relationship('Review', backref='upload', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Upload, self).__init__(**kwargs)
        # Set deletion deadline to 48 hours from upload
        self.deletion_deadline = datetime.utcnow() + timedelta(hours=48)
    
    def get_average_rating(self):
        reviews_list = list(self.reviews)
        if not reviews_list:
            return None
        good_reviews = sum(1 for r in reviews_list if r.rating == 'good')
        return good_reviews / len(reviews_list)
    
    def can_delete_free(self):
        return datetime.utcnow() < self.deletion_deadline
    
    def get_deletion_penalty(self):
        if self.can_delete_free():
            return 0
        # Penalty increases based on how long after deadline
        hours_late = (datetime.utcnow() - self.deletion_deadline).total_seconds() / 3600
        return min(int(hours_late * 5), 100)  # Max 100 XP penalty

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.Integer, db.ForeignKey('upload.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.String(10), nullable=False)  # 'good' or 'bad'
    description = db.Column(db.Text, nullable=False)
    xp_earned = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Quality tracking for reviewer strikes
    is_flagged = db.Column(db.Boolean, default=False)
    quality_score = db.Column(db.Float, default=1.0)

class Strike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    strike_type = db.Column(db.String(20), nullable=False)  # 'uploader' or 'reviewer'
    reason = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WithdrawalRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount_xp = db.Column(db.Integer, nullable=False)
    amount_usd = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    payment_method = db.Column(db.String(100))
    payment_details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    admin_notes = db.Column(db.Text)

class AdminAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)  # ID of affected user/upload/etc
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    contact_email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='ratings')

# New models for enhanced features
class Contest(db.Model):
    """Weekly contests with upload and review phases"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    upload_phase_end = db.Column(db.DateTime, nullable=False)  # 10 days
    review_phase_end = db.Column(db.DateTime, nullable=False)  # 20 days total
    status = db.Column(db.String(50), default='active')  # active, ended
    total_prize_pool = db.Column(db.Integer, default=16000)  # ₹16,000 total
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContestEntry(db.Model):
    """User participation in contests"""
    id = db.Column(db.Integer, primary_key=True)
    contest_id = db.Column(db.Integer, db.ForeignKey('contest.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploads_count = db.Column(db.Integer, default=0)
    reviews_count = db.Column(db.Integer, default=0)
    xp_earned = db.Column(db.Integer, default=0)
    final_rank = db.Column(db.Integer)
    prize_amount = db.Column(db.Integer, default=0)
    
class Badge(db.Model):
    """Special badges and achievements"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    badge_type = db.Column(db.String(100), nullable=False)  # weekly_award, seasonal, ranking
    badge_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_animated = db.Column(db.Boolean, default=False)  # For fire badges

class WeeklyAward(db.Model):
    """Weekly special awards"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    award_type = db.Column(db.String(100), nullable=False)  # smartest_review, best_detective, fastest_climber, reviewer_hero
    week_start = db.Column(db.DateTime, nullable=False)
    xp_bonus = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Invite(db.Model):
    """Referral and invite tracking"""
    id = db.Column(db.Integer, primary_key=True)
    inviter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    invitee_email = db.Column(db.String(120), nullable=False)
    invitee_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Set when they join
    xp_awarded = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='pending')  # pending, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
