#!/usr/bin/env python3
"""
DnD 5E AI-Powered Game - Database Initialization
===============================================

Initialize the SQLAlchemy database and create tables
"""

import os
import sys
from pathlib import Path
from sqlalchemy import text

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from shared.models import create_database, get_session, Campaign, CampaignSession, Character, ChatMessage
from cache_manager import cache_manager

def main():
    """Initialize the database and create sample data"""
    print("🚀 Initializing DnD 5E Game Database...")
    
    try:
        # Create database and tables
        engine = create_database()
        print("✅ Database tables created successfully")
        
        # Test database connection
        db_session = get_session()
        db_session.execute(text("SELECT 1"))
        db_session.close()
        print("✅ Database connection test passed")
        
        # Test Redis connection
        if cache_manager.connected:
            print("✅ Redis connection established")
        else:
            print("⚠️  Redis not available - caching will be disabled")
        
        # Create a sample campaign if none exists
        db_session = get_session()
        existing_campaigns = db_session.query(Campaign).count()
        
        if existing_campaigns == 0:
            print("📝 Creating sample campaign...")
            
            # Create a sample campaign
            sample_campaign = Campaign(
                name="Sample Adventure",
                world_name="fantasy campaign setting",
                difficulty="medium",
                magic_level="standard"
            )
            db_session.add(sample_campaign)
            db_session.commit()
            
            print("✅ Sample campaign created: 'Sample Adventure'")
        else:
            print(f"📊 Found {existing_campaigns} existing campaign(s)")
        
        db_session.close()
        
        print("\n🎉 Database initialization complete!")
        print("\nNext steps:")
        print("1. Start Redis server (optional, for caching): redis-server")
        print("2. Run the enhanced web interface: python enhanced_web_interface.py")
        print("3. Open your browser to: http://localhost:5001")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 