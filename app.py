import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import hashlib
from database import db

# Page configuration
st.set_page_config(
    page_title="MES Connect",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #3B82F6;
    }
    .success-message {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

class AuthSystem:
    @staticmethod
    def login():
        st.markdown('<h2 class="main-header">MES Connect</h2>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                st.markdown('<h3 class="sub-header">Login</h3>', unsafe_allow_html=True)
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                role = st.selectbox("Role", ["Student", "Alumni", "Admin"])
                
                if st.form_submit_button("Login", use_container_width=True):
                    user = db.authenticate_user(email, password)
                    if user and user['role'].lower() == role.lower():
                        st.session_state.authenticated = True
                        st.session_state.user_id = user['id']
                        st.session_state.user_role = user['role']
                        st.session_state.user_data = user
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials or role mismatch")
            
            st.markdown("---")
            st.markdown("Don't have an account?")
            if st.button("Sign Up", use_container_width=True):
                st.session_state.current_page = "Sign Up"
                st.rerun()
    
    @staticmethod
    def signup():
        st.markdown('<h2 class="main-header">Create Account</h2>', unsafe_allow_html=True)
        
        with st.form("signup_form"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name")
                last_name = st.text_input("Last Name")
                email = st.text_input("Email")
                role = st.selectbox("Role", ["Student", "Alumni"])
            
            with col2:
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                if role == "Student":
                    registration_number = st.text_input("Registration Number")
                    batch_year = st.number_input("Batch Year", min_value=2000, max_value=2030, value=2023)
                    department = st.selectbox("Department", ["CSE", "ECE", "EEE", "MECH", "CIVIL"])
                else:
                    current_company = st.text_input("Current Company")
                    position = st.text_input("Position")
                    batch_year = st.number_input("Batch Year", min_value=1980, max_value=2023, value=2020)
            
            if st.form_submit_button("Create Account", use_container_width=True):
                if password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    user_data = {
                        'email': email,
                        'first_name': first_name,
                        'last_name': last_name,
                        'role': role.lower(),
                        'batch_year': batch_year
                    }
                    
                    if role == "Student":
                        user_data['registration_number'] = registration_number
                        user_data['department'] = department
                    else:
                        user_data['current_company'] = current_company
                        user_data['position'] = position
                    
                    user_id = db.create_user(password=password, **user_data)
                    if user_id:
                        st.success("Account created successfully! Please login.")
                        st.session_state.current_page = "Login"
                        st.rerun()
                    else:
                        st.error("Email already exists!")
        
        if st.button("Back to Login"):
            st.session_state.current_page = "Login"
            st.rerun()

class StudentDashboard:
    @staticmethod
    def display():
        st.markdown('<h1 class="main-header">Student Dashboard</h1>', unsafe_allow_html=True)
        
        # Dashboard metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Friends", "24", "+3")
        with col2:
            st.metric("Groups", "5", "+1")
        with col3:
            st.metric("Events", "3", "0")
        with col4:
            st.metric("Messages", "12", "+2")
        
        st.markdown("---")
        
        # Main content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<h3 class="sub-header">Recent Announcements</h3>', unsafe_allow_html=True)
            
            announcements = [
                {"title": "Campus Hackathon", "date": "2024-03-15", "content": "Annual hackathon registration open"},
                {"title": "Exam Schedule", "date": "2024-03-10", "content": "Final exam schedule released"},
                {"title": "Library Hours", "date": "2024-03-05", "content": "Extended library hours for exams"}
            ]
            
            for ann in announcements:
                with st.expander(f"{ann['title']} - {ann['date']}"):
                    st.write(ann['content'])
                    if st.button("View Details", key=f"ann_{ann['title']}"):
                        st.info("Detailed view would open here")
            
            # Quick actions
            st.markdown('<h3 class="sub-header">Quick Actions</h3>', unsafe_allow_html=True)
            action_col1, action_col2, action_col3 = st.columns(3)
            with action_col1:
                if st.button("Create Group", use_container_width=True):
                    st.session_state.current_page = "Create Group"
                    st.rerun()
            with action_col2:
                if st.button("Find Friends", use_container_width=True):
                    st.session_state.current_page = "Find Friends"
                    st.rerun()
            with action_col3:
                if st.button("Post Confession", use_container_width=True):
                    st.session_state.current_page = "Confessions"
                    st.rerun()
        
        with col2:
            st.markdown('<h3 class="sub-header">Upcoming Events</h3>', unsafe_allow_html=True)
            
            events = [
                {"name": "Alumni Talk", "date": "Mar 20", "time": "3 PM"},
                {"name": "Coding Contest", "date": "Mar 22", "time": "10 AM"},
                {"name": "Career Fair", "date": "Mar 25", "time": "9 AM"}
            ]
            
            for event in events:
                st.markdown(f"""
                <div class="card">
                    <b>{event['name']}</b><br>
                    📅 {event['date']} | ⏰ {event['time']}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<h3 class="sub-header">Suggested Groups</h3>', unsafe_allow_html=True)
            groups = ["Coding Club", "Robotics Team", "Music Society", "Debate Club"]
            for group in groups:
                if st.button(f"Join {group}", key=f"join_{group}", use_container_width=True):
                    st.success(f"Request sent to join {group}")

class AlumniDashboard:
    @staticmethod
    def display():
        st.markdown('<h1 class="main-header">Alumni Dashboard</h1>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Connections", "156", "+8")
        with col2:
            st.metric("Networking Events", "4", "+1")
        with col3:
            st.metric("Mentees", "3", "+1")
        with col4:
            st.metric("Contributions", "$2,500", "+$500")
        
        st.markdown("---")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<h3 class="sub-header">Professional Network</h3>', unsafe_allow_html=True)
            
            # Connection requests
            st.subheader("Connection Requests")
            requests = [
                {"name": "John Doe", "position": "Software Engineer", "company": "Google"},
                {"name": "Jane Smith", "position": "Product Manager", "company": "Microsoft"}
            ]
            
            for req in requests:
                cols = st.columns([3, 1, 1])
                with cols[0]:
                    st.write(f"**{req['name']}** - {req['position']} at {req['company']}")
                with cols[1]:
                    if st.button("Accept", key=f"accept_{req['name']}"):
                        st.success(f"Connected with {req['name']}")
                with cols[2]:
                    if st.button("Ignore", key=f"ignore_{req['name']}"):
                        st.info(f"Ignored {req['name']}")
            
            # Job postings
            st.subheader("Recent Job Postings")
            jobs = [
                {"title": "Senior Dev", "company": "Amazon", "location": "Remote"},
                {"title": "Data Scientist", "company": "Meta", "location": "Seattle"}
            ]
            
            for job in jobs:
                with st.expander(f"{job['title']} - {job['company']}"):
                    st.write(f"Location: {job['location']}")
                    if st.button("Apply/Share", key=f"job_{job['title']}"):
                        st.info("Application process would start here")
        
        with col2:
            st.markdown('<h3 class="sub-header">Upcoming Reunions</h3>', unsafe_allow_html=True)
            
            reunions = [
                {"batch": "2015", "date": "Apr 15", "location": "Main Campus"},
                {"batch": "2010", "date": "May 20", "location": "Virtual"},
                {"batch": "2005", "date": "Jun 10", "location": "City Hotel"}
            ]
            
            for reunion in reunions:
                st.markdown(f"""
                <div class="card">
                    <b>{reunion['batch']} Batch Reunion</b><br>
                    📅 {reunion['date']}<br>
                    📍 {reunion['location']}
                </div>
                """, unsafe_allow_html=True)
            
            # Contribution options
            st.markdown('<h3 class="sub-header">Contribute</h3>', unsafe_allow_html=True)
            contribution_type = st.selectbox("Contribution Type", 
                                            ["Scholarship", "Infrastructure", "Mentorship", "Guest Lecture"])
            amount = st.number_input("Amount ($)", min_value=10, max_value=10000, value=100)
            if st.button("Make Contribution", use_container_width=True):
                st.success(f"Thank you for your ${amount} {contribution_type} contribution!")

class AdminDashboard:
    @staticmethod
    def display():
        st.markdown('<h1 class="main-header">Admin Dashboard</h1>', unsafe_allow_html=True)
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", "1,245", "+23")
        with col2:
            st.metric("Active Today", "342", "-12")
        with col3:
            st.metric("Pending Approvals", "15", "+3")
        with col4:
            st.metric("Groups", "48", "+2")
        
        st.markdown("---")
        
        # Tabs for different admin sections
        tab1, tab2, tab3, tab4 = st.tabs(["User Management", "Content", "Analytics", "Settings"])
        
        with tab1:
            st.subheader("User Management")
            
            # Sample user data
            users = pd.DataFrame({
                'ID': [1, 2, 3, 4, 5],
                'Name': ['John Doe', 'Jane Smith', 'Bob Wilson', 'Alice Brown', 'Charlie Davis'],
                'Email': ['john@mes.edu', 'jane@mes.edu', 'bob@alumni.mes', 'alice@mes.edu', 'charlie@alumni.mes'],
                'Role': ['Student', 'Student', 'Alumni', 'Student', 'Alumni'],
                'Status': ['Active', 'Pending', 'Active', 'Blocked', 'Active']
            })
            
            st.dataframe(users, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                user_action = st.selectbox("Action", ["Approve", "Block", "Delete", "Make Admin"])
            with col2:
                user_id = st.text_input("User ID")
            
            if st.button("Apply Action"):
                st.success(f"Action '{user_action}' applied to user {user_id}")
        
        with tab2:
            st.subheader("Content Moderation")
            
            # Confession moderation queue
            st.write("**Confession Queue**")
            confessions = [
                {"id": 1, "content": "Anonymous confession about campus life...", "reports": 3},
                {"id": 2, "content": "Another anonymous post...", "reports": 1}
            ]
            
            for conf in confessions:
                cols = st.columns([4, 1, 1])
                with cols[0]:
                    st.write(conf['content'])
                    st.caption(f"Reports: {conf['reports']}")
                with cols[1]:
                    if st.button("Approve", key=f"app_c{conf['id']}"):
                        st.success(f"Confession {conf['id']} approved")
                with cols[2]:
                    if st.button("Reject", key=f"rej_c{conf['id']}"):
                        st.info(f"Confession {conf['id']} rejected")
        
        with tab3:
            st.subheader("Analytics Dashboard")
            
            # Sample charts
            data = pd.DataFrame({
                'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                'New Users': [120, 150, 180, 200, 220],
                'Active Users': [300, 320, 350, 380, 400]
            })
            
            fig = px.line(data, x='Month', y=['New Users', 'Active Users'], 
                         title='User Growth Trend')
            st.plotly_chart(fig, use_container_width=True)
            
            # Pie chart for user roles
            role_data = pd.DataFrame({
                'Role': ['Students', 'Alumni', 'Admins'],
                'Count': [800, 400, 45]
            })
            
            fig2 = px.pie(role_data, values='Count', names='Role', title='User Distribution by Role')
            st.plotly_chart(fig2, use_container_width=True)
        
        with tab4:
            st.subheader("System Settings")
            
            col1, col2 = st.columns(2)
            with col1:
                st.checkbox("Allow New Registrations", value=True)
                st.checkbox("Enable Confessions", value=True)
                st.checkbox("Auto-approve Alumni", value=False)
            
            with col2:
                st.number_input("Max Group Size", min_value=10, max_value=500, value=100)
                st.number_input("Session Timeout (minutes)", min_value=5, max_value=120, value=30)
            
            if st.button("Save Settings", use_container_width=True):
                st.success("Settings saved successfully!")

class SidebarNavigation:
    @staticmethod
    def render():
        with st.sidebar:
            st.image("https://via.placeholder.com/150x50/3B82F6/FFFFFF?text=MES+Connect", 
                    use_column_width=True)
            
            if not st.session_state.authenticated:
                return
            
            # User info
            user = st.session_state.user_data
            st.markdown(f"**Welcome, {user['first_name']}!**")
            st.markdown(f"*{user['role'].title()}*")
            st.markdown("---")
            
            # Navigation menu
            menu_options = []
            
            if user['role'] == 'student':
                menu_options = [
                    "Dashboard",
                    "Profile",
                    "Academics",
                    "Friends",
                    "Groups",
                    "Confessions",
                    "Events & Clubs",
                    "Charity",
                    "Settings"
                ]
            elif user['role'] == 'alumni':
                menu_options = [
                    "Dashboard",
                    "Profile",
                    "Networking",
                    "Groups",
                    "Events",
                    "Contributions",
                    "Settings"
                ]
            elif user['role'] == 'admin':
                menu_options = [
                    "Dashboard",
                    "User Management",
                    "Content Management",
                    "Groups Management",
                    "Confession Moderation",
                    "Analytics",
                    "System Settings"
                ]
            
            selected = option_menu(
                menu_title="Navigation",
                options=menu_options,
                icons=['house' if 'Dashboard' in opt else 
                      'person' if 'Profile' in opt else
                      'people' if 'Friends' in opt or 'Networking' in opt else
                      'chat' if 'Confessions' in opt else
                      'calendar-event' if 'Events' in opt else
                      'gear' if 'Settings' in opt else
                      'graph-up' for opt in menu_options],
                menu_icon="cast",
                default_index=0,
                orientation="vertical"
            )
            
            st.session_state.current_page = selected
            
            st.markdown("---")
            
            # Quick actions based on role
            st.markdown("**Quick Actions**")
            
            if user['role'] == 'student':
                if st.button("📝 Post Confession", use_container_width=True):
                    st.session_state.current_page = "Confessions"
                    st.rerun()
                if st.button("👥 Create Group", use_container_width=True):
                    st.session_state.current_page = "Groups"
                    st.rerun()
            
            elif user['role'] == 'alumni':
                if st.button("💼 Post Job", use_container_width=True):
                    st.info("Job posting feature")
                if st.button("👨‍🏫 Offer Mentorship", use_container_width=True):
                    st.info("Mentorship program")
            
            st.markdown("---")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user_id = None
                st.session_state.user_role = None
                st.session_state.current_page = "Login"
                st.rerun()

class ConfessionsModule:
    @staticmethod
    def display():
        st.markdown('<h1 class="main-header">Confessions</h1>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["View Confessions", "Post Confession", "My Posts"])
        
        with tab1:
            st.subheader("Latest Confessions")
            
            # Sample confessions
            confessions = [
                {"id": 1, "content": "I love the new library system! So much easier to find books.", "likes": 24, "comments": 3, "time": "2h ago"},
                {"id": 2, "content": "Anyone else struggling with the advanced algorithms course?", "likes": 15, "comments": 12, "time": "5h ago"},
                {"id": 3, "content": "Shoutout to the cafeteria staff for the amazing food today!", "likes": 42, "comments": 5, "time": "1d ago"},
                {"id": 4, "content": "Looking for study partners for the physics exam next week.", "likes": 8, "comments": 7, "time": "2d ago"}
            ]
            
            for conf in confessions:
                with st.container():
                    st.markdown(f"""
                    <div class="card">
                        <p>{conf['content']}</p>
                        <small>Posted {conf['time']}</small>
                        <br>
                        <small>❤️ {conf['likes']} | 💬 {conf['comments']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([1, 1, 8])
                    with col1:
                        if st.button(f"Like", key=f"like_{conf['id']}"):
                            st.success("Liked!")
                    with col2:
                        if st.button(f"Comment", key=f"comment_{conf['id']}"):
                            st.info("Comment feature")
        
        with tab2:
            st.subheader("Post a Confession")
            
            confession_text = st.text_area("Your confession (anonymous):", 
                                         height=150,
                                         placeholder="Share your thoughts anonymously...")
            
            col1, col2 = st.columns(2)
            with col1:
                is_anonymous = st.checkbox("Post anonymously", value=True)
            with col2:
                confession_type = st.selectbox("Category", ["General", "Academic", "Campus Life", "Relationships"])
            
            if st.button("Post Confession", use_container_width=True):
                if confession_text.strip():
                    st.success("Confession posted successfully!")
                    # Here you would save to database
                else:
                    st.error("Please write something before posting.")
        
        with tab3:
            st.subheader("My Confessions")
            st.info("You have no confessions yet. They appear here only if you post non-anonymously.")

# Main app logic
def main():
    if not st.session_state.authenticated:
        if st.session_state.current_page == "Sign Up":
            AuthSystem.signup()
        else:
            AuthSystem.login()
    else:
        SidebarNavigation.render()
        
        # Route to appropriate dashboard
        if st.session_state.current_page == "Dashboard":
            if st.session_state.user_role == "student":
                StudentDashboard.display()
            elif st.session_state.user_role == "alumni":
                AlumniDashboard.display()
            elif st.session_state.user_role == "admin":
                AdminDashboard.display()
        
        elif "Confessions" in st.session_state.current_page:
            ConfessionsModule.display()
        
        # Add other module displays here...
        else:
            st.markdown(f'<h1 class="main-header">{st.session_state.current_page}</h1>', unsafe_allow_html=True)
            st.info(f"{st.session_state.current_page} module is under development.")

if __name__ == "__main__":
    main()
