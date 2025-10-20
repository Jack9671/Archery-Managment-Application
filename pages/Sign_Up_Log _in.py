import streamlit as st
import hashlib
import uuid
from datetime import date
from utility_function.initilize_dbconnection import supabase
from utility_function.sign_up_log_in_utility import get_countries

tab1, tab2 = st.tabs(["Sign Up", "Log In"])

with tab1:
    """Sign up form component"""
    st.header("Sign Up")
    with st.form("signup_form"):
        st.subheader("Account Information")
        col1, col2 = st.columns(2)
        
        with col1:
            email_address = st.text_input("Email Address*", help="Required field - used for login")
            password = st.text_input("Password*", type="password", help="Minimum 6 characters")
            confirm_password = st.text_input("Confirm Password*", type="password", help="Re-enter your password")
            fullname = st.text_input("Full Name*", help="Required field")
            
            # Role selection - only Archer or Recorder
            role = st.selectbox("Role*", ["", "archer", "recorder"], help="Choose your role in the system")

        with col2:
            date_of_birth = st.date_input(
                "Date of Birth*", 
                value=date(2000, 1, 1),
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                help="Required field"
            )
            sex = st.selectbox("Sex*", ["", "male", "female"], help="Required field")
            
            # Country selection with real data
            countries = get_countries()
            country = st.selectbox("Country*", [""] + countries, help="Required field")

        # Role-specific fields
        if role == "archer":
            st.subheader("Archer-Specific Information")
            
            # Get available equipment
            equipment_list = supabase.table("equipment").select("equipment_id, name").execute()
            equipment_options = {eq['name']: eq['equipment_id'] for eq in equipment_list.data} if equipment_list.data else {}
            
            if equipment_options:
                default_equipment = st.selectbox("Default Equipment (Bow Type)*", 
                                                list(equipment_options.keys()),
                                                help="Select your primary equipment type")
            else:
                st.warning("No equipment available. Please contact administrator.")
                default_equipment = None
            
            level = st.selectbox("Experience Level*", [
                "",
                "beginner (< 1 year of expereince)",
                "semi-intermediate (>= 1 year of experience)",
                "intermediate (>= 2 year of experience )",
                "semi-advanced (>= 4 years of experience )",
                "advanced (>= 6 years of experience)",
                "professional (>= 10 year of experience)",
                "expert (>= 20 year of experience)"
            ], help="Select your archery experience level")
            about_archer = st.text_area("About Me", value="I love archery", help="Tell others about yourself as an archer")
            
        elif role == "recorder":
            st.subheader("Recorder-Specific Information")
            about_recorder = st.text_area("About Me*", help="Tell others about your experience as a recorder")

        st.subheader("Profile Picture (Optional)")
        uploaded_file = st.file_uploader("Choose a profile picture", type=["png", "jpg", "jpeg"], help="Optional - Upload your profile picture", accept_multiple_files=False)

        submit = st.form_submit_button("Sign Up")

        if submit:
            # Validate required fields
            required_fields = {
                "Email Address": email_address,
                "Password": password,
                "Full Name": fullname,
                "Date of Birth": date_of_birth,
                "Sex": sex,
                "Country": country,
                "Role": role
            }
            
            # Add role-specific required fields
            if role == "archer":
                required_fields["Experience Level"] = level
                required_fields["Default Equipment"] = default_equipment
            elif role == "recorder":
                required_fields["About Recorder"] = about_recorder
            
            missing_fields = [field for field, value in required_fields.items() if not value or value == ""]
            
            if missing_fields:
                st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
                st.stop()
                
            if password != confirm_password:
                st.error("Passwords don't match!")
                st.stop()
                
            if len(password) < 6:
                st.error("Password must be at least 6 characters!")
                st.stop()
            
            try:
                # Check if email already exists
                existing_user = supabase.table("account").select("email_address").eq("email_address", email_address).execute()
                
                if existing_user.data:
                    st.error("An account with this email already exists!")
                    st.stop()
                
                # Hash the password
                # TEMPORARY: Disabled hashing for testing - store plain text password
                # hash_password = hashlib.sha256(password.encode()).hexdigest()
                hash_password = password  # Store plain text for testing
                
                # Handle profile picture upload
                avatar_url = "https://ghcpcyvethwdzzgyymfp.supabase.co/storage/v1/object/public/User%20Avatar/Default_Avatar.jpg"  # Default
                
                if uploaded_file is not None:
                    try:
                        # Read file bytes
                        file_bytes = uploaded_file.read()
                        file_ext = uploaded_file.name.split(".")[-1]
                        unique_filename = f"{uuid.uuid4()}.{file_ext}"
                        
                        # Upload to Supabase Storage in "User Avatar" bucket
                        upload_res = supabase.storage.from_("User Avatar").upload(unique_filename, file_bytes)
                        
                        # Get public URL
                        avatar_url = supabase.storage.from_("User Avatar").get_public_url(unique_filename)
                        
                    except Exception as upload_error:
                        st.warning(f"Profile picture upload failed: {str(upload_error)}. Using default avatar.")
                
                # Insert into account table
                response = supabase.table("account").insert({
                    "email_address": email_address,
                    "hash_password": hash_password,
                    "fullname": fullname,
                    "country": country,
                    "date_of_birth": date_of_birth.isoformat(),
                    "sex": sex,
                    "avatar_url": avatar_url,
                    "role": role
                }).execute()
                
                if response.data:
                    account_id = response.data[0]['account_id']
                    
                    # Insert into role-specific table
                    if role == "archer":
                        archer_response = supabase.table("archer").insert({
                            "archer_id": account_id,
                            "level": level,
                            "about_archer": about_archer,
                            "default_equipment_id": equipment_options[default_equipment]
                        }).execute()
                        
                        if not archer_response.data:
                            st.error("Failed to create archer profile. Please contact support.")
                            st.stop()
                            
                    elif role == "recorder":
                        recorder_response = supabase.table("recorder").insert({
                            "recorder_id": account_id,
                            "about_recorder": about_recorder
                        }).execute()
                        
                        if not recorder_response.data:
                            st.error("Failed to create recorder profile. Please contact support.")
                            st.stop()
                    
                    st.success("Account created successfully! You can now log in.")
                    # Clear form by rerunning
                    st.balloons()
                else:
                    st.error("Failed to create account. Please try again.")
                    
            except Exception as e:
                st.error(f"Sign up failed: {str(e)}")

with tab2:
    """Log in form component"""
    st.header("Log In")
    
    with st.form("login_form"):
        email_address = st.text_input("Email Address*", help="Enter your registered email")
        password = st.text_input("Password*", type="password", help="Enter your password")
        
        login_submit = st.form_submit_button("Log In")
        
        if login_submit:
            # Validate inputs
            if not email_address or not password:
                st.error("Please fill in all fields!")
                st.stop()
            
            try:
                # Hash the entered password
                # TEMPORARY: Disabled hashing for testing - compare plain text password
                # hash_password = hashlib.sha256(password.encode()).hexdigest()
                hash_password = password  # Use plain text for testing
                
                # Query the account table
                response = supabase.table("account").select("*").eq("email_address", email_address).eq("hash_password", hash_password).execute()
                
                if response.data and len(response.data) > 0:
                    # Login successful
                    user_data = response.data[0]
                    
                    # Check if account is deactivated
                    if user_data.get('deactivated', False):
                        st.error("This account has been deactivated. Please contact support.")
                        st.stop()
                    
                    # Store user data in session state
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_data['account_id']
                    st.session_state.email = user_data['email_address']
                    st.session_state.fullname = user_data['fullname']
                    st.session_state.avatar_url = user_data['avatar_url']
                    st.session_state.country = user_data['country']
                    st.session_state.sex = user_data['sex']
                    st.session_state.date_of_birth = user_data['date_of_birth']
                    st.session_state.role = user_data['role']
                    
                    st.success(f"Welcome back, {user_data['fullname']}!")
                    st.balloons()
                    st.info(f"You are logged in as a {user_data['role']}. Navigate to other pages using the sidebar.")
                else:
                    st.error("Invalid email or password!")
                    
            except Exception as e:
                st.error(f"Login failed: {str(e)}")
    
    # Display login status
    if st.session_state.get('logged_in', False):
        st.divider()
        st.subheader("Current Session")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image(st.session_state.get('avatar_url', ''), width=100)
        
        with col2:
            st.write(f"**Name:** {st.session_state.get('fullname', 'N/A')}")
            st.write(f"**Email:** {st.session_state.get('email', 'N/A')}")
            st.write(f"**Country:** {st.session_state.get('country', 'N/A')}")
        
        if st.button("Log Out", type="secondary", use_container_width=True):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
