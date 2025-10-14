import streamlit as st
from datetime import datetime
from utility_function.initilize_dbconnection import supabase

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please log in to submit a request form.")
    st.info("Navigate to the 'Sign Up Log In' page to access your account.")
    st.stop()

st.title("📋 Request Form Submission")
st.write(f"**Logged in as:** {st.session_state.get('fullname', 'N/A')}")
st.divider()

# Form type selection
form_type = st.radio(
    "Select Form Type",
    ["Enroll in Competition", "Withdraw from Competition"],
    horizontal=True
)

with st.form("request_submission_form"):
    st.subheader(f"{'🎯 Enrollment' if form_type == 'Enroll in Competition' else '🚪 Withdrawal'} Request")
    
    # Role selection
    role = st.selectbox(
        "Select Role*",
        ["", "archer", "participant", "recorder"],
        help="Choose your role for this competition"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Fetch competitions from database
        try:
            competitions_response = supabase.table("competition").select("competition_id, name, date_start, date_end").order("date_start").execute()
            competitions = competitions_response.data if competitions_response.data else []
            
            competition_options = [""] + [f"{comp['competition_id']} - {comp['name']} ({comp['date_start']} to {comp['date_end']})" for comp in competitions]
            competition_selection = st.selectbox(
                "Select Competition*",
                competition_options,
                help="Choose the competition you want to enroll in or withdraw from"
            )
        except Exception as e:
            st.error(f"Error loading competitions: {str(e)}")
            competition_selection = ""
            competitions = []
    
    with col2:
        # Fetch rounds from database
        try:
            rounds_response = supabase.table("round").select("round_id, name, age_group").order("name").execute()
            rounds = rounds_response.data if rounds_response.data else []
            
            round_options = [""] + [f"{rnd['round_id']} - {rnd['name']} ({rnd['age_group']})" for rnd in rounds]
            round_selection = st.selectbox(
                "Select Round*",
                round_options,
                help="Choose the round category"
            )
        except Exception as e:
            st.error(f"Error loading rounds: {str(e)}")
            round_selection = ""
            rounds = []
    
    # Applicant comment
    applicant_comment = st.text_area(
        "Your Comment*",
        height=150,
        help="Provide additional information about your request",
        placeholder="Explain why you want to enroll/withdraw, your experience level, equipment details, etc."
    )
    
    # Display current selections
    if competition_selection and round_selection:
        st.info(f"**Summary:** Requesting to {'enroll as' if form_type == 'Enroll in Competition' else 'withdraw as'} **{role}** from **{competition_selection.split(' - ')[1].split(' (')[0]}** in round **{round_selection.split(' - ')[1].split(' (')[0]}**")
    
    # Submit button
    submit = st.form_submit_button("Submit Request", type="primary", use_container_width=True)
    
    if submit:
        # Validate required fields
        validation_errors = []
        
        if not role:
            validation_errors.append("Role is required")
        if not competition_selection:
            validation_errors.append("Competition is required")
        if not round_selection:
            validation_errors.append("Round is required")
        if not applicant_comment.strip():
            validation_errors.append("Comment is required")
        
        if validation_errors:
            st.error(f"❌ Please fix the following errors:\n" + "\n".join([f"- {err}" for err in validation_errors]))
            st.stop()
        
        # Extract IDs from selections
        try:
            competition_id = int(competition_selection.split(" - ")[0])
            round_id = int(round_selection.split(" - ")[0])
        except (ValueError, IndexError):
            st.error("Invalid competition or round selection")
            st.stop()
        
        # Check if user already has a pending or in-progress request for this competition/round
        try:
            existing_request = supabase.table("request_form").select("*").eq(
                "account_id", st.session_state.get('user_id')
            ).eq(
                "competition_id", competition_id
            ).eq(
                "round_id", round_id
            ).in_(
                "status", ["pending", "in progress"]
            ).execute()
            
            if existing_request.data:
                st.warning("⚠️ You already have a pending or in-progress request for this competition and round.")
                st.stop()
        except Exception as e:
            st.error(f"Error checking existing requests: {str(e)}")
            st.stop()
        
        # If withdrawing, check if user is actually enrolled
        if form_type == "Withdraw from Competition":
            try:
                if role == "archer":
                    # Check if user exists in archer table
                    archer_record = supabase.table("archer").select("*").eq(
                        "archer_id", st.session_state.get('user_id')
                    ).execute()
                    
                    if not archer_record.data:
                        st.error("❌ You are not registered as an archer.")
                        st.stop()
                
                elif role == "participant":
                    # Check if user has participant_score records for this competition/round
                    event_contexts = supabase.table("event_context").select("event_context_id").eq(
                        "competition_id", competition_id
                    ).eq(
                        "round_id", round_id
                    ).execute()
                    
                    if event_contexts.data:
                        event_context_ids = [ec['event_context_id'] for ec in event_contexts.data]
                        participant_records = supabase.table("participant_score").select("*").eq(
                            "participant_id", st.session_state.get('user_id')
                        ).in_(
                            "event_context_id", event_context_ids
                        ).execute()
                        
                        if not participant_records.data:
                            st.error("❌ You are not enrolled as a participant in this competition/round.")
                            st.stop()
                    else:
                        st.error("❌ No event contexts found for this competition/round.")
                        st.stop()
                
                elif role == "recorder":
                    # Check if user is a recorder for this competition/round
                    recorder_record = supabase.table("recorder").select("*").eq(
                        "recorder_id", st.session_state.get('user_id')
                    ).eq(
                        "competition_id", competition_id
                    ).eq(
                        "round_id", round_id
                    ).execute()
                    
                    if not recorder_record.data:
                        st.error("❌ You are not enrolled as a recorder in this competition/round.")
                        st.stop()
                        
            except Exception as e:
                st.error(f"Error verifying enrollment: {str(e)}")
                st.stop()
        
        # If enrolling as archer, check if already an archer
        if form_type == "Enroll in Competition" and role == "archer":
            try:
                existing_archer = supabase.table("archer").select("*").eq(
                    "archer_id", st.session_state.get('user_id')
                ).execute()
                
                if existing_archer.data:
                    st.warning("⚠️ You are already registered as an archer.")
                    st.stop()
            except Exception as e:
                st.error(f"Error checking archer status: {str(e)}")
                st.stop()
        
        # Determine form type
        request_type = "enrol" if form_type == "Enroll in Competition" else "withdraw"
        
        # Special handling for archer role - direct enrollment/withdrawal
        if role == "archer":
            try:
                if request_type == "enrol":
                    # Get default equipment (if exists) or use a placeholder
                    equipment_response = supabase.table("equipment").select("equipment_id").limit(1).execute()
                    default_equipment_id = equipment_response.data[0]['equipment_id'] if equipment_response.data else None
                    
                    if not default_equipment_id:
                        st.error("❌ No equipment found in the system. Please contact an administrator.")
                        st.stop()
                    
                    # Insert into archer table directly
                    archer_response = supabase.table("archer").insert({
                        "archer_id": st.session_state.get('user_id'),
                        "default_equipment_id": default_equipment_id,
                        "club_id": None  # Can be set later
                    }).execute()
                    
                    if archer_response.data:
                        st.success("✅ You have been registered as an archer successfully!")
                        st.balloons()
                        st.info("You can now enroll in competitions as a participant.")
                    else:
                        st.error("❌ Failed to register as archer. Please try again.")
                    
                elif request_type == "withdraw":
                    # Delete from archer table directly
                    delete_response = supabase.table("archer").delete().eq(
                        "archer_id", st.session_state.get('user_id')
                    ).execute()
                    
                    if delete_response.data:
                        st.success("✅ You have been removed from the archer registry.")
                        st.info("You can re-register as an archer at any time.")
                    else:
                        st.error("❌ Failed to remove archer registration. Please try again.")
                        
            except Exception as e:
                st.error(f"❌ Archer registration failed: {str(e)}")
        else:
            # For participant and recorder roles, insert the request form for admin review
            try:
                response = supabase.table("request_form").insert({
                    "account_id": st.session_state.get('user_id'),
                    "role": role,
                    "type": request_type,
                    "competition_id": competition_id,
                    "round_id": round_id,
                    "applicant_comment": applicant_comment.strip(),
                    "status": "pending",
                    "create_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }).execute()
                
                if response.data:
                    st.success("✅ Your request has been submitted successfully!")
                    st.balloons()
                    st.info("Your request is now pending review. You will be notified once it's processed.")
                    
                    # Display submission details
                    with st.expander("📄 Submission Details", expanded=True):
                        st.write(f"**Form ID:** {response.data[0]['form_id']}")
                        st.write(f"**Type:** {request_type.capitalize()}")
                        st.write(f"**Role:** {role.capitalize()}")
                        st.write(f"**Competition:** {competition_selection.split(' - ')[1].split(' (')[0]}")
                        st.write(f"**Round:** {round_selection.split(' - ')[1].split(' (')[0]}")
                        st.write(f"**Status:** Pending")
                        st.write(f"**Submitted:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
                else:
                    st.error("❌ Failed to submit request. Please try again.")
                    
            except Exception as e:
                st.error(f"❌ Submission failed: {str(e)}")

st.divider()

# Display user's previous requests
st.subheader("📜 Your Previous Requests")

try:
    user_requests = supabase.table("request_form").select(
        "*, competition:competition_id(name, date_start, date_end), round:round_id(name, age_group)"
    ).eq(
        "account_id", st.session_state.get('user_id')
    ).order(
        "create_at", desc=True
    ).execute()
    
    if user_requests.data:
        for req in user_requests.data:
            status_emoji = {
                "pending": "⏳",
                "in progress": "🔄",
                "eligible": "✅",
                "ineligible": "❌"
            }.get(req['status'], "❓")
            
            with st.expander(f"{status_emoji} Form #{req['form_id']} - {req['type'].capitalize()} as {req['role'].capitalize()} - {req['status'].upper()}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Competition:** {req['competition']['name']}")
                    st.write(f"**Competition Dates:** {req['competition']['date_start']} to {req['competition']['date_end']}")
                    st.write(f"**Round:** {req['round']['name']} ({req['round']['age_group']})")
                
                with col2:
                    st.write(f"**Type:** {req['type'].capitalize()}")
                    st.write(f"**Role:** {req['role'].capitalize()}")
                    st.write(f"**Status:** {req['status'].capitalize()}")
                    st.write(f"**Submitted:** {req['create_at']}")
                
                st.write(f"**Your Comment:**")
                st.info(req['applicant_comment'])
                
                if req['reviewer_comment']:
                    st.write(f"**Reviewer Comment:**")
                    st.warning(req['reviewer_comment'])
                    st.write(f"**Reviewed by:** Account ID {req['reviewd_by']}")
    else:
        st.info("You haven't submitted any requests yet.")
        
except Exception as e:
    st.error(f"Error loading your requests: {str(e)}")
