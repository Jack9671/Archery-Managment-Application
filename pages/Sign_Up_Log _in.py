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
            email_address = st.text_input("Email Address*", help="Required field - used for login", width="stretch")
            password = st.text_input("Password*", type="password", help="Minimum 6 characters", width="stretch")
            confirm_password = st.text_input("Confirm Password*", type="password", width="stretch", help="Re-enter your password", )
            fullname = st.text_input("Full Name*", help="Required field", width="stretch")

        with col2:
            date_of_birth = st.date_input(
                "Date of Birth*", 
                value=date(2000, 1, 1),
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                help="Required field"
            )
            sex = st.selectbox("Sex*", ["male", "female"], help="Required field", width="stretch")
            
            # Country selection with real data
            countries = get_countries()
            country = st.selectbox("Country*", [""] + countries, help="Required field", width="stretch")

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
                "Country": country
            }
            
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
                hash_password = hashlib.sha256(password.encode()).hexdigest()
                
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
                    "avatar_url": avatar_url
                }).execute()
                
                if response.data:
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
                hash_password = hashlib.sha256(password.encode()).hexdigest()
                
                # Query the account table
                response = supabase.table("account").select("*").eq("email_address", email_address).eq("hash_password", hash_password).execute()
                
                if response.data and len(response.data) > 0:
                    # Login successful
                    user_data = response.data[0]
                    
                    # Store user data in session state
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_data['account_id']
                    st.session_state.email = user_data['email_address']
                    st.session_state.fullname = user_data['fullname']
                    st.session_state.avatar_url = user_data['avatar_url']
                    st.session_state.country = user_data['country']
                    st.session_state.sex = user_data['sex']
                    st.session_state.date_of_birth = user_data['date_of_birth']
                    
                    st.success(f"Welcome back, {user_data['fullname']}!")
                    st.balloons()
                    st.info("You are now logged in. Navigate to other pages using the sidebar.")
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
        
        if st.button("Log Out", type="secondary", width= 400):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
