# Alpha Nex - Content Platform Replit Guide

## Overview

Alpha Nex is a comprehensive content management platform that combines user-generated content collection with AI-powered quality assurance and a gamified reward system. The platform allows users to upload various types of content (videos, audio, documents, code, images), review others' submissions, and earn XP points that can be converted to monetary rewards. The system includes sophisticated moderation, KYC verification, and administrative controls.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web application with SQLAlchemy ORM
- **Database**: SQLite by default (configurable via DATABASE_URL environment variable)
- **Authentication**: Flask-Login for session management with password hashing
- **File Handling**: Werkzeug secure file uploads with size/type validation
- **Background Tasks**: APScheduler for automated periodic tasks
- **AI Integration**: OpenAI GPT-4o for content quality analysis and duplicate detection

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 responsive design
- **Styling**: Custom CSS with monochrome theme inspired by professional platforms
- **JavaScript**: Vanilla JS for interactive features, form validation, and file upload handling
- **Icons**: Font Awesome for consistent iconography
- **Typography**: Inter font family for modern, clean appearance

### Security Model
- **Authentication**: Email/password with secure hashing using Werkzeug
- **File Validation**: Extension whitelist, file size limits, and secure filename handling
- **Rate Limiting**: Daily upload quotas per user (500MB default)
- **Content Moderation**: AI-powered duplicate/spam detection with human review workflow

## Key Components

### User Management System
- **User Model**: Comprehensive user profiles with XP tracking and strike system
- **Role-Based Access**: Regular users, administrators, and banned user states
- **Strike System**: Separate tracking for uploader and reviewer violations (3-strike rule)
- **Daily Limits**: Upload bandwidth restrictions that reset daily

### Content Management
- **Upload System**: Multi-format file support (video, audio, documents, code, images)
- **Review Workflow**: Peer review system where users evaluate uploaded content quality
- **AI Quality Control**: Automated content analysis for duplicates and spam detection
- **File Organization**: Secure file storage with categorization and metadata tracking

### Gamification & Rewards
- **XP Point System**: Points earned for uploads, reviews, and quality bonuses
- **Withdrawal System**: Mechanism to convert XP points to monetary rewards
- **Achievement Tracking**: User progress monitoring and engagement metrics

### Administrative Tools
- **Admin Panel**: Comprehensive dashboard for managing users, content, and violations
- **User Management**: Account oversight and platform access control
- **Strike Management**: Tools for issuing warnings and managing user violations
- **Content Moderation**: Review queue for flagged or problematic content

## Data Flow

### Upload Process
1. User selects file and provides description/category
2. Frontend validates file type, size, and daily quota
3. AI service analyzes content description for quality/duplicates
4. File is securely stored with metadata in database
5. Upload is queued for peer review
6. User receives XP points for successful upload

### Review Process
1. Reviewers are presented with unreviewed content
2. Reviewers rate content as good/bad with detailed feedback
3. Multiple reviews are aggregated for quality scoring
4. Poor quality content may be flagged or removed
5. Reviewers earn XP points for participation
6. Strike system handles reviewer misconduct

### Admin Workflow
1. Administrators monitor user account activity and behavior
2. Review withdrawal requests and process payments
3. Handle user appeals and strike disputes
4. Oversee platform health metrics and user engagement

## External Dependencies

### Required Services
- **OpenAI API**: Content quality analysis and duplicate detection (GPT-4o model)
- **Database**: SQLite default, PostgreSQL recommended for production
- **File Storage**: Local filesystem (uploads/ directory)

### Optional Integrations
- **Email Service**: User verification and notifications (configuration ready)
- **Payment Gateway**: For XP point to currency conversion
- **Cloud Storage**: Alternative to local file storage for scalability

### Environment Variables
- `SESSION_SECRET`: Flask session encryption key
- `DATABASE_URL`: Database connection string
- `OPENAI_API_KEY`: OpenAI API authentication

## Deployment Strategy

### Development Setup
- Local SQLite database for rapid prototyping
- File uploads stored in local uploads/ directory
- Background scheduler for automated tasks
- Debug logging enabled for troubleshooting

### Production Considerations
- Database migration to PostgreSQL for scalability
- Cloud file storage (AWS S3, Google Cloud Storage)
- Load balancing for high traffic scenarios
- Automated backup systems for user data
- Enhanced security measures and rate limiting

### Scalability Features
- Database connection pooling configured
- Background task scheduling for resource-intensive operations
- Modular architecture allows for microservice migration
- API-ready structure for mobile app integration

The platform is designed to handle growth from small community to large-scale content platform while maintaining data integrity and user experience quality.

## Recent Updates

### January 2025 - Phase 1
- Enhanced code documentation with function docstrings
- Improved logging configuration for better debugging
- Added visual improvements to templates with consistent iconography
- Updated CSS and JavaScript headers for better maintainability
- Fixed Flask-Login routing configuration
- Resolved JavaScript form validation issues

### January 2025 - Phase 2
- Added comprehensive docstrings to all utility functions
- Enhanced database configuration with timeout settings
- Improved template text for better user engagement
- Added visual enhancements with consistent icon usage
- Updated project metadata in pyproject.toml
- Refined user interface copy across all templates

### January 2025 - Phase 3
- Completely removed KYC verification requirements from the platform
- Updated all routes to remove KYC checks for uploads and reviews
- Simplified user onboarding process - users can immediately start using the platform
- Updated templates to remove KYC-related UI elements and messaging
- Modified admin panel to focus on user management instead of KYC processing
- Removed KYC forms and related documentation

### July 2025 - Migration & File Upload Enhancement
- Successfully migrated project from Replit Agent to standard Replit environment
- Expanded file type support to include ALL formats (100+ file extensions)
- Enhanced upload success feedback with clear confirmation messages
- Added comprehensive file type support: videos, audio, documents, code, images, archives, text files
- Improved user experience with detailed upload status and XP point confirmation
- Fixed file upload validation to accept any file type while maintaining security

### July 2025 - Authentication Removal & Demo Mode
- Removed all authentication requirements for seamless user experience
- Landing page now redirects directly to dashboard without login/signup
- Created auto-login system with demo user account
- Added test files from secondary user for review demonstration
- Removed login, signup, and authentication-related routes
- Simplified user flow: immediate access to platform features
- Added 5 sample test files (video, audio, document, code, image) for review testing

### July 2025 - Replit Environment Migration
- Successfully migrated from Replit Agent to standard Replit environment
- All dependencies and packages properly configured
- Flask application running smoothly on port 5000 with gunicorn
- Database connections and file uploads working correctly
- APScheduler background tasks operational
- Full feature specification document received for production enhancement
- Platform ready for full-scale development and deployment

### July 2025 - Replit Environment Migration
- Successfully migrated from Replit Agent to standard Replit environment
- All dependencies and packages properly configured
- Flask application running smoothly on port 5000 with gunicorn
- Database connections and file uploads working correctly
- APScheduler background tasks operational
- Full feature specification document received for production enhancement
- Platform ready for full-scale development and deployment