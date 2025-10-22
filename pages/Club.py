import streamlit as st
import pandas as pd
import uuid
from datetime import date
from utility_function.initilize_dbconnection import supabase
from utility_function.club_utility import (
    get_all_clubs, get_club_by_id, get_archer_club, create_club,
    join_club, get_club_members, get_pending_enrollment_forms,
    update_enrollment_status, remove_club_member, check_club_creator
)

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("Please log in to access this page.")
    st.stop()

st.title("🏹 Club Management")
st.write(f"Welcome, {st.session_state.get('fullname')}!")

user_role = st.session_state.get('role')

# Create tabs based on role
if user_role == 'archer':
    tab1, tab2, tab3 = st.tabs(["🔍 Browse Clubs", "🏠 My Club", "📝 Manage Enrollment"])
else:
    tab1 = st.tabs(["🔍 Browse Clubs"])[0]

# Tab 1: Browse Clubs
with tab1:
    st.header("Browse Clubs")
    st.write("Search and explore archery clubs")
    
    search_query = st.text_input("🔍 Search clubs", placeholder="Enter club name...")
    
    if st.button("Search", type="primary") or search_query == "":
        clubs_df = get_all_clubs(search_query if search_query else None)
        st.session_state.clubs_df = clubs_df
    
    if 'clubs_df' in st.session_state and not st.session_state.clubs_df.empty:
        st.success(f"Found {len(st.session_state.clubs_df)} club(s)")
        
        # Display clubs
        for idx, club in st.session_state.clubs_df.iterrows():
            with st.expander(f"🏹 {club['name']}"):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    # Display club logo
                    if club.get('club_logo_url'):
                        st.image(club['club_logo_url'], width=150)
                
                with col2:
                    st.write(f"**Club Name:** {club['name']}")
                    st.write(f"**Formation Date:** {club.get('formation_date', 'N/A')}")
                    st.write(f"**Description:**")
                    st.write(club.get('about_club', 'No description available'))
                    st.write(f"**Open to Join:** {'Yes' if club.get('open_to_join', True) else 'No'}")
                    
                    # Join button for archers
                    if user_role == 'archer':
                        # Check if archer already has a club
                        my_club = get_archer_club(st.session_state.user_id)
                        
                        if my_club:
                            if my_club['club_id'] == club['club_id']:
                                st.info("✅ You are already a member of this club")
                            else:
                                st.warning("⚠️ You are already a member of another club")
                        else:
                            with st.form(f"join_form_{club['club_id']}"):
                                join_message = st.text_area(
                                    "Message to Club Creator (Optional)",
                                    placeholder="Tell them why you want to join...",
                                    key=f"msg_{club['club_id']}"
                                )
                                join_btn = st.form_submit_button("📝 Request to Join", type="primary")
                                
                                if join_btn:
                                    result = join_club(
                                        st.session_state.user_id, 
                                        club['club_id'],
                                        join_message if join_message else "I would like to join this club."
                                    )
                                    if result:
                                        st.success("✅ Enrollment request submitted!")
                                        st.balloons()
                                        st.rerun()
                                    else:
                                        st.error("Failed to submit request. You may have already applied.")
    else:
        st.info("No clubs found. Try a different search query.")
    
    # Create club section (Archers only)
    if user_role == 'archer':
        st.divider()
        st.subheader("➕ Create a New Club")
        
        # Check if archer already has a club
        my_club = get_archer_club(st.session_state.user_id)
        
        if my_club:
            st.warning("⚠️ You are already a member of a club. You cannot create or join another club.")
        else:
            with st.form("create_club_form"):
                club_name = st.text_input("Club Name*", placeholder="Enter club name")
                formation_date = st.date_input("Formation Date*", value=date.today(), help="The date this club was formed")
                club_description = st.text_area("Description*", placeholder="Describe your club...")
                
                club_logo = st.file_uploader("Club Logo (Optional)", type=["png", "jpg", "jpeg"])
                
                create_club_btn = st.form_submit_button("🏹 Create Club", type="primary")
                
                if create_club_btn:
                    if not club_name or not formation_date or not club_description:
                        st.error("Please fill in all required fields!")
                    else:
                        # Handle logo upload
                        logo_url = None
                        if club_logo:
                            try:
                                file_bytes = club_logo.read()
                                file_ext = club_logo.name.split(".")[-1]
                                unique_filename = f"club_{uuid.uuid4()}.{file_ext}"
                                
                                upload_res = supabase.storage.from_("User Avatar").upload(unique_filename, file_bytes)
                                logo_url = supabase.storage.from_("User Avatar").get_public_url(unique_filename)
                            except Exception as e:
                                st.warning(f"Logo upload failed: {str(e)}. Using default logo.")
                        
                        # Create club
                        result = create_club(
                            st.session_state.user_id,
                            club_name,
                            club_description,
                            formation_date.isoformat(),
                            logo_url
                        )
                        
                        if result:
                            st.success(f"✅ Club created successfully!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Failed to create club. Please try again.")

# Tab 2: My Club (Archers only)
if user_role == 'archer':
    with tab2:
        st.header("My Club")
        
        my_club = get_archer_club(st.session_state.user_id)
        
        if my_club:
            # Display club information
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if my_club.get('club_logo_url'):
                    st.image(my_club['club_logo_url'], width=200)
            
            with col2:
                st.subheader(my_club['name'])
                st.write(f"**Formation Date:** {my_club.get('formation_date', 'N/A')}")
                st.write(f"**Club ID:** {my_club['club_id']}")
                st.write(f"**Description:**")
                st.write(my_club.get('about_club', 'No description'))
            
            # Check if user is creator
            is_creator = check_club_creator(st.session_state.user_id, my_club['club_id'])
            
            if is_creator:
                st.success("👑 You are the creator of this club")
            
            st.divider()
            st.subheader("👥 Club Members")
            
            members_df = get_club_members(my_club['club_id'])
            
            if not members_df.empty:
                st.success(f"Total Members: {len(members_df)}")
                
                for idx, member in members_df.iterrows():
                    with st.expander(f"👤 {member.get('fullname', 'Unknown')} (ID: {member['archer_id']})"):
                        col1, col2 = st.columns([1, 3])
                        
                        with col1:
                            if member.get('avatar_url'):
                                st.image(member['avatar_url'], width=100)
                        
                        with col2:
                            st.write(f"**Name:** {member.get('fullname', 'N/A')}")
                            st.write(f"**Email:** {member.get('email_address', 'N/A')}")
                            st.write(f"**Level:** {member.get('level', 'N/A')}")
                            st.write(f"**About:** {member.get('about_archer', 'N/A')}")
                            
                            # Remove member button (creator only, cannot remove self)
                            if is_creator and member['archer_id'] != st.session_state.user_id:
                                if st.button(f"🚫 Remove Member", key=f"remove_{member['archer_id']}"):
                                    success = remove_club_member(member['archer_id'])
                                    if success:
                                        st.success("Member removed from club.")
                                        st.rerun()
                                    else:
                                        st.error("Failed to remove member.")
            else:
                st.info("No members found in this club.")
            
            # Leave club option (non-creators only)
            if not is_creator:
                st.divider()
                if st.button("🚪 Leave Club", type="secondary"):
                    success = remove_club_member(st.session_state.user_id)
                    if success:
                        st.success("You have left the club.")
                        st.rerun()
                    else:
                        st.error("Failed to leave club.")
        else:
            st.info("You are not a member of any club. Browse clubs to join one or create your own!")

    # Tab 3: Manage Enrollment (Archers only - creators)
    with tab3:
        st.header("Manage Club Enrollment")
        
        my_club = get_archer_club(st.session_state.user_id)
        
        if my_club:
            is_creator = check_club_creator(st.session_state.user_id, my_club['club_id'])
            
            if is_creator:
                st.write(f"**Managing enrollment for:** {my_club['name']}")
                
                # Get all forms to display based on status
                all_forms = supabase.table("club_enrollment_form").select("*").eq("club_id", my_club['club_id']).execute()
                all_enrollment_forms = pd.DataFrame(all_forms.data) if all_forms.data else pd.DataFrame()
                
                if not all_enrollment_forms.empty:
                    # Separate forms by status
                    pending_forms = all_enrollment_forms[all_enrollment_forms['status'] == 'pending']
                    other_forms = all_enrollment_forms[all_enrollment_forms['status'].isin(['in progress', 'on hold'])]
                else:
                    pending_forms = pd.DataFrame()
                    other_forms = pd.DataFrame()
                
                # Display pending forms
                if not pending_forms.empty:
                    st.success(f"Found {len(pending_forms)} pending enrollment request(s)")
                    
                    for idx, form in pending_forms.iterrows():
                        # Get applicant information
                        applicant = supabase.table("account").select("fullname, email_address, avatar_url").eq("account_id", form['sender_id']).execute()
                        
                        if applicant.data:
                            applicant_info = applicant.data[0]
                            
                            with st.expander(f"📝 Request from {applicant_info['fullname']}"):
                                col1, col2 = st.columns([1, 3])
                                
                                with col1:
                                    if applicant_info.get('avatar_url'):
                                        st.image(applicant_info['avatar_url'], width=100)
                                
                                with col2:
                                    st.write(f"**Name:** {applicant_info['fullname']}")
                                    st.write(f"**Email:** {applicant_info['email_address']}")
                                    st.write(f"**Applicant ID:** {form['sender_id']}")
                                    st.write(f"**Form ID:** {form['form_id']}")
                                    st.write(f"**Message:** {form.get('sender_word', 'N/A')}")
                                    st.write(f"**Submitted:** {form.get('create_at', 'N/A')}")
                                    
                                    st.divider()
                                    st.write("**Actions:**")
                                    
                                    col_progress, col_accept, col_reject = st.columns(3)
                                    
                                    with col_progress:
                                        if st.button("⏳ In Progress", key=f"progress_{form['form_id']}"):
                                            success = update_enrollment_status(form['form_id'], 'in progress')
                                            if success:
                                                st.info("Marked as in progress")
                                                st.rerun()
                                            else:
                                                st.error("Failed to update status")
                                    
                                    with col_accept:
                                        if st.button("✅ Accept", key=f"accept_{form['form_id']}", type="primary"):
                                            success = update_enrollment_status(
                                                form['form_id'],
                                                'eligible',
                                                my_club['club_id'],
                                                form['sender_id']
                                            )
                                            
                                            if success:
                                                st.success("Request accepted! New member added.")
                                                st.info("The enrollment form has been deleted.")
                                                st.balloons()
                                                st.rerun()
                                            else:
                                                st.error("Failed to accept request.")
                                    
                                    with col_reject:
                                        if st.button("❌ Reject", key=f"reject_{form['form_id']}"):
                                            success = update_enrollment_status(form['form_id'], 'ineligible')
                                            
                                            if success:
                                                st.info("Request rejected. The enrollment form has been deleted.")
                                                st.rerun()
                                            else:
                                                st.error("Failed to reject request.")
                else:
                    st.info("✅ No pending enrollment requests.")
                
                # Display forms with other statuses (in progress, on hold, etc.)
                if not other_forms.empty:
                    st.divider()
                    st.subheader("📋 Forms in Progress")
                    
                    for idx, form in other_forms.iterrows():
                        # Get applicant information
                        applicant = supabase.table("account").select("fullname, email_address, avatar_url").eq("account_id", form['sender_id']).execute()
                        
                        if applicant.data:
                            applicant_info = applicant.data[0]
                            
                            with st.expander(f"📝 {applicant_info['fullname']} - Status: {form['status']}"):
                                col1, col2 = st.columns([1, 3])
                                
                                with col1:
                                    if applicant_info.get('avatar_url'):
                                        st.image(applicant_info['avatar_url'], width=100)
                                
                                with col2:
                                    st.write(f"**Name:** {applicant_info['fullname']}")
                                    st.write(f"**Email:** {applicant_info['email_address']}")
                                    st.write(f"**Form ID:** {form['form_id']}")
                                    st.write(f"**Current Status:** {form['status']}")
                                    st.write(f"**Message:** {form.get('sender_word', 'N/A')}")
                                    st.write(f"**Submitted:** {form.get('create_at', 'N/A')}")
                                    
                                    # Allow updating status
                                    st.divider()
                                    st.write("**Update Status:**")
                                    
                                    col_pending, col_accept, col_reject = st.columns(3)
                                    
                                    with col_pending:
                                        if st.button("⏳ Mark Pending", key=f"pending_{form['form_id']}"):
                                            success = update_enrollment_status(form['form_id'], 'pending')
                                            if success:
                                                st.success("Marked as pending")
                                                st.rerun()
                                    
                                    with col_accept:
                                        if st.button("✅ Accept", key=f"accept_other_{form['form_id']}", type="primary"):
                                            success = update_enrollment_status(
                                                form['form_id'],
                                                'eligible',
                                                my_club['club_id'],
                                                form['sender_id']
                                            )
                                            if success:
                                                st.success("Accepted and deleted!")
                                                st.rerun()
                                    
                                    with col_reject:
                                        if st.button("❌ Reject", key=f"reject_other_{form['form_id']}"):
                                            success = update_enrollment_status(form['form_id'], 'ineligible')
                                            if success:
                                                st.info("Rejected and deleted")
                                                st.rerun()
            else:
                st.warning("⚠️ Only the club creator can manage enrollment requests.")
        else:
            st.info("You need to be a member of a club to manage enrollments.")
