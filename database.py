import sqlite3
import pandas as pd
from datetime import datetime
import bcrypt

class Database:
    def __init__(self, db_name="mes_connect.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_database()
    
    def init_database(self):
        # Users table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'alumni', 'admin')),
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            registration_number TEXT,
            batch_year INTEGER,
            department TEXT,
            current_company TEXT,
            position TEXT,
            profile_image TEXT,
            is_verified BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Profiles table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            bio TEXT,
            skills TEXT,
            interests TEXT,
            linkedin_url TEXT,
            github_url TEXT,
            website TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Friends/Connections table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            connection_id INTEGER,
            status TEXT CHECK(status IN ('pending', 'accepted', 'blocked')) DEFAULT 'pending',
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accepted_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (connection_id) REFERENCES users (id),
            UNIQUE(user_id, connection_id)
        )
        ''')
        
        # Groups table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            privacy TEXT CHECK(privacy IN ('public', 'private')) DEFAULT 'public',
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            member_count INTEGER DEFAULT 0,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
        ''')
        
        # Group members table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            user_id INTEGER,
            role TEXT CHECK(role IN ('admin', 'moderator', 'member')) DEFAULT 'member',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(group_id, user_id)
        )
        ''')
        
        # Posts/Confessions table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content TEXT NOT NULL,
            type TEXT CHECK(type IN ('confession', 'announcement', 'normal')) DEFAULT 'normal',
            is_anonymous BOOLEAN DEFAULT 0,
            group_id INTEGER,
            likes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (group_id) REFERENCES groups (id)
        )
        ''')
        
        # Events table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            event_type TEXT CHECK(event_type IN ('campus', 'club', 'alumni', 'charity')),
            organizer_id INTEGER,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            location TEXT,
            max_participants INTEGER,
            current_participants INTEGER DEFAULT 0,
            is_approved BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organizer_id) REFERENCES users (id)
        )
        ''')
        
        # Create indexes for performance
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_type ON posts(type)')
        
        self.conn.commit()
    
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password, hashed):
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_user(self, email, password, role, first_name, last_name, **kwargs):
        hashed_password = self.hash_password(password)
        columns = ['email', 'password', 'role', 'first_name', 'last_name'] + list(kwargs.keys())
        values = [email, hashed_password, role, first_name, last_name] + list(kwargs.values())
        
        placeholders = ', '.join(['?'] * len(values))
        query = f"INSERT INTO users ({', '.join(columns)}) VALUES ({placeholders})"
        
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def authenticate_user(self, email, password):
        self.cursor.execute('SELECT * FROM users WHERE email = ? AND is_active = 1', (email,))
        user = self.cursor.fetchone()
        if user and self.verify_password(password, user[2]):
            columns = [desc[0] for desc in self.cursor.description]
            return dict(zip(columns, user))
        return None
    
    def get_user_by_id(self, user_id):
        self.cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = self.cursor.fetchone()
        if user:
            columns = [desc[0] for desc in self.cursor.description]
            return dict(zip(columns, user))
        return None
    
    def close(self):
        self.conn.close()

# Singleton instance
db = Database()
