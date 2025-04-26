from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

# Create instance of SQLAlchemy for models (initialized in main.py)
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and user management"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship with parcels
    parcels = db.relationship('Parcel', backref='owner', lazy='dynamic')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check password against stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Parcel(db.Model):
    """Field/Parcel model to store field boundaries"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    # GeoJSON stored as text
    geometry = db.Column(db.Text, nullable=False)
    area_hectares = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key to user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship with NDVI analyses
    analyses = db.relationship('NDVIAnalysis', backref='parcel', lazy='dynamic')
    
    def get_geometry_json(self):
        """Return geometry as parsed JSON"""
        return json.loads(self.geometry)
    
    def set_geometry_json(self, geometry_json):
        """Set geometry from JSON object"""
        self.geometry = json.dumps(geometry_json)
        
    def __repr__(self):
        return f'<Parcel {self.name}>'


class NDVIAnalysis(db.Model):
    """Model to store NDVI analysis results"""
    id = db.Column(db.Integer, primary_key=True)
    analysis_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # NDVI statistics
    mean_ndvi = db.Column(db.Float, nullable=False)
    median_ndvi = db.Column(db.Float, nullable=False)
    min_ndvi = db.Column(db.Float, nullable=False)
    max_ndvi = db.Column(db.Float, nullable=False)
    std_dev_ndvi = db.Column(db.Float, nullable=False)
    percentile_10 = db.Column(db.Float, nullable=True)
    percentile_90 = db.Column(db.Float, nullable=True)
    
    # Vegetation distribution (percentage of area)
    low_vegetation = db.Column(db.Float, nullable=True)  # NDVI < 0.2
    moderate_vegetation = db.Column(db.Float, nullable=True)  # 0.2 <= NDVI < 0.5
    high_vegetation = db.Column(db.Float, nullable=True)  # NDVI >= 0.5
    
    # Raw data path (optional, for future use)
    data_path = db.Column(db.String(255), nullable=True)
    
    # Notes about analysis
    notes = db.Column(db.Text, nullable=True)
    
    # Foreign key to parcel
    parcel_id = db.Column(db.Integer, db.ForeignKey('parcel.id'), nullable=False)
    
    def __repr__(self):
        return f'<NDVIAnalysis parcel_id={self.parcel_id} date={self.analysis_date}>'