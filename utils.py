import os
from werkzeug.utils import secure_filename
from datetime import timedelta

# Alpha Nex Utility Functions

ALLOWED_EXTENSIONS = {
    'video': ['mp4', 'avi', 'mov', 'wmv', 'mkv', 'flv', 'webm', 'ogv', '3gp', 'mpg', 'mpeg', 'ts', 'mts', 'm2ts'],
    'audio': ['mp3', 'wav', 'aac', 'm4a', 'flac', 'ogg', 'wma', 'amr', 'aiff', 'ac3', 'opus'],
    'document': ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'pages', 'epub', 'mobi', 'xls', 'xlsx', 'ppt', 'pptx', 'csv'],
    'code': ['py', 'js', 'html', 'css', 'java', 'cpp', 'c', 'php', 'rb', 'go', 'rs', 'swift', 'kt', 'scala', 'r', 'sql', 'sh', 'bat', 'ps1', 'json', 'xml', 'yaml', 'yml', 'toml', 'ini', 'cfg', 'conf', 'md', 'rst', 'tex', 'log'],
    'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'webp', 'svg', 'ico', 'psd', 'ai', 'eps', 'raw', 'cr2', 'nef', 'arw'],
    'archive': ['zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz', 'lzma'],
    'text': ['txt', 'md', 'rst', 'log', 'readme', 'license', 'changelog']
}

def allowed_file(filename):
    """Check if file extension is allowed."""
    if not filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    for category, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return True
    
    return False

def get_file_size(file):
    """Get file size in bytes."""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)  # Reset file pointer
    return size

def calculate_xp_reward(action_type):
    """Calculate XP reward for different platform actions."""
    rewards = {
        'upload': 20,  # File upload reward
        'upload_approved': 10,  # Bonus XP when upload gets approved
        'review': 10,  # Content review reward
        'quality_bonus': 5,  # High quality bonus
        'daily_login': 5  # Daily engagement
    }
    return rewards.get(action_type, 0)

def format_file_size(bytes_size):
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def get_file_category(filename):
    """Determine file category based on extension."""
    if not filename or '.' not in filename:
        return 'unknown'
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    for category, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return category
    
    return 'unknown'

def sanitize_filename(filename):
    """Sanitize and secure filename."""
    return secure_filename(filename)

def is_valid_image(file_path):
    """Check if file is a valid image."""
    try:
        from PIL import Image
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def calculate_deletion_penalty_hours(upload_time, deletion_time):
    """Calculate hours past free deletion window."""
    free_window_hours = 48
    upload_plus_free = upload_time + timedelta(hours=free_window_hours)
    
    if deletion_time <= upload_plus_free:
        return 0
    
    penalty_time = deletion_time - upload_plus_free
    return penalty_time.total_seconds() / 3600

def validate_content_description(description):
    """Validate content description for minimum quality."""
    if not description or len(description.strip()) < 10:
        return False, "Description must be at least 10 characters long."
    
    # Check for spam patterns
    spam_indicators = ['free money', 'click here', 'guaranteed', 'act now']
    description_lower = description.lower()
    
    for indicator in spam_indicators:
        if indicator in description_lower:
            return False, f"Description contains potentially spammy content: '{indicator}'"
    
    return True, "Description is valid."
