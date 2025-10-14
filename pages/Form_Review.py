import streamlit as st
from datetime import datetime
from utility_function.initilize_dbconnection import supabase

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please log in to access the form review page.")
    st.info("Navigate to the 'Sign Up Log In' page to access your account.")
    st.stop()

# Check if user is Admin or Recorder
user_id = st.session_state.get('user_id')

# Check if user is admin
try:
    admin_check = supabase.table("admin").select("admin_id").eq("admin_id", user_id).execute()
    is_admin = bool(admin_check.data)
except:
    is_admin = False

# Check if user is recorder
try:
    recorder_check = supabase.table("recorder").select("recorder_id, competition_id, round_id").eq("recorder_id", user_id).execute()
    is_recorder = bool(recorder_check.data)
    recorder_assignments = recorder_check.data if recorder_check.data else []
except:
    is_recorder = False
    recorder_assignments = []

if not is_admin and not is_recorder:
    st.error("🚫 Access Denied")
    st.warning("You must be an Admin or Recorder to access this page.")
    st.info("Please contact an administrator if you believe you should have access.")
    st.stop()

# Page header
st.title("📋 Form Review & Management")
st.write(f"**Logged in as:** {st.session_state.get('fullname', 'N/A')}")
st.write(f"**Role:** {'Admin' if is_admin else 'Recorder'}")
st.divider()

# Filter options
col1, col2, col3 = st.columns(3)

with col1:
    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "pending", "in progress", "eligible", "ineligible"],
        help="Filter forms by their current status"
    )

with col2:
    role_filter = st.selectbox(
        "Filter by Role",
        ["All", "archer", "participant", "recorder"],
        help="Filter forms by requested role"
    )

with col3:
    type_filter = st.selectbox(
        "Filter by Type",
        ["All", "enrol", "withdraw"],
        help="Filter forms by request type"
    )

st.divider()

# Fetch forms based on user role and filters
try:
    # Base query with joins
    query = supabase.table("request_form").select(
        "*, account:account_id(fullname, email_address, country, avatar_url), competition:competition_id(name, date_start, date_end), round:round_id(name, age_group)"
    )
    
    # Apply status filter
    if status_filter != "All":
        query = query.eq("status", status_filter)
    
    # Apply role filter
    if role_filter != "All":
        query = query.eq("role", role_filter)
    
    # Apply type filter
    if type_filter != "All":
        query = query.eq("type", type_filter)
    
    # For recorders, only show forms for competitions/rounds they manage
    # Admin can review: archer (all), recorder (all)
    # Recorder can review: participant (only their competition/round)
    if is_recorder and not is_admin:
        # Recorder can only review participant requests for their assigned competitions/rounds
        query = query.eq("role", "participant")
        
        # Get forms that match any of the recorder's assignments
        all_forms = query.order("create_at", desc=True).execute()
        
        # Filter to only include forms for competitions/rounds the recorder manages
        filtered_forms = []
        for form in all_forms.data if all_forms.data else []:
            for assignment in recorder_assignments:
                if (form['competition_id'] == assignment['competition_id'] and 
                    form['round_id'] == assignment['round_id']):
                    filtered_forms.append(form)
                    break
        
        forms_data = filtered_forms
    else:
        # Admin sees all forms
        forms_response = query.order("create_at", desc=True).execute()
        forms_data = forms_response.data if forms_response.data else []
    
    if not forms_data:
        st.info("📭 No forms found matching your filters.")
    else:
        st.success(f"📊 Found {len(forms_data)} form(s) matching your criteria")
        
        # Display forms
        for form in forms_data:
            status_emoji = {
                "pending": "⏳",
                "in progress": "🔄",
                "eligible": "✅",
                "ineligible": "❌"
            }.get(form['status'], "❓")
            
            # Determine if this user can review this form
            can_review = False
            if is_admin:
                # Admin can review archer and recorder roles
                can_review = form['role'] in ['archer', 'recorder']
            elif is_recorder:
                # Recorder can review participant roles for their competitions/rounds
                can_review = form['role'] == 'participant'
            
            with st.expander(
                f"{status_emoji} Form #{form['form_id']} - {form['type'].upper()} as {form['role'].upper()} - {form['status'].upper()}",
                expanded=(form['status'] == 'pending')
            ):
                # Applicant Information
                st.subheader("👤 Applicant Information")
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    if form['account'] and form['account'].get('avatar_url'):
                        st.image(form['account']['avatar_url'], width=100)
                
                with col2:
                    if form['account']:
                        st.write(f"**Name:** {form['account']['fullname']}")
                        st.write(f"**Email:** {form['account']['email_address']}")
                        st.write(f"**Country:** {form['account']['country']}")
                    st.write(f"**Account ID:** {form['account_id']}")
                
                st.divider()
                
                # Request Details
                st.subheader("📄 Request Details")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Form ID:** {form['form_id']}")
                    st.write(f"**Type:** {form['type'].capitalize()}")
                    st.write(f"**Role:** {form['role'].capitalize()}")
                    st.write(f"**Status:** {form['status'].capitalize()}")
                
                with col2:
                    if form['competition']:
                        st.write(f"**Competition:** {form['competition']['name']}")
                        st.write(f"**Competition Dates:** {form['competition']['date_start']} to {form['competition']['date_end']}")
                    if form['round']:
                        st.write(f"**Round:** {form['round']['name']} ({form['round']['age_group']})")
                    st.write(f"**Submitted:** {form['create_at']}")
                
                st.write(f"**Applicant's Comment:**")
                st.info(form['applicant_comment'])
                
                # Review section
                if form['reviewer_comment']:
                    st.write(f"**Previous Review Comment:**")
                    st.warning(form['reviewer_comment'])
                    st.write(f"**Reviewed by:** Account ID {form['reviewd_by']}")
                
                st.divider()
                
                # Review actions (only if can review and not already eligible/ineligible)
                if can_review and form['status'] in ['pending', 'in progress']:
                    st.subheader("🔍 Review Actions")
                    
                    with st.form(f"review_form_{form['form_id']}"):
                        new_status = st.selectbox(
                            "Update Status",
                            ["in progress", "eligible", "ineligible"],
                            help="Set the status of this request"
                        )
                        
                        reviewer_comment = st.text_area(
                            "Reviewer Comment",
                            placeholder="Provide feedback or reasons for your decision...",
                            help="Optional comment explaining your decision"
                        )
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            approve_button = st.form_submit_button(
                                "✅ Approve (Eligible)",
                                type="primary",
                                use_container_width=True
                            )
                        
                        with col2:
                            reject_button = st.form_submit_button(
                                "❌ Reject (Ineligible)",
                                type="secondary",
                                use_container_width=True
                            )
                        
                        update_button = st.form_submit_button(
                            "🔄 Update Status Only",
                            use_container_width=True
                        )
                        
                        if approve_button:
                            try:
                                # Additional validation for participant enrollment
                                if form['role'] == 'participant' and form['type'] == 'enrol':
                                    # Check if user is an archer first
                                    archer_check = supabase.table("archer").select("archer_id").eq(
                                        "archer_id", form['account_id']
                                    ).execute()
                                    
                                    if not archer_check.data:
                                        st.error("❌ Cannot approve: The applicant must be registered as an archer first.")
                                        st.stop()
                                    
                                    # Check if event contexts exist
                                    event_check = supabase.table("event_context").select("event_context_id").eq(
                                        "competition_id", form['competition_id']
                                    ).eq(
                                        "round_id", form['round_id']
                                    ).execute()
                                    
                                    if not event_check.data:
                                        st.error("❌ Cannot approve: No event contexts found for this competition and round. Please create them first.")
                                        st.stop()
                                
                                # Update form status to eligible
                                update_response = supabase.table("request_form").update({
                                    "status": "eligible",
                                    "reviewer_comment": reviewer_comment.strip() if reviewer_comment.strip() else None,
                                    "reviewd_by": user_id,
                                    "updated_at": datetime.utcnow().isoformat()
                                }).eq("form_id", form['form_id']).execute()
                                
                                if update_response.data:
                                    st.success("✅ Form approved! The request has been processed automatically by database triggers.")
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error("Failed to approve form.")
                            except Exception as e:
                                st.error(f"Error approving form: {str(e)}")
                        
                        elif reject_button:
                            if not reviewer_comment.strip():
                                st.error("❌ Please provide a comment explaining why this request is being rejected.")
                            else:
                                try:
                                    update_response = supabase.table("request_form").update({
                                        "status": "ineligible",
                                        "reviewer_comment": reviewer_comment.strip(),
                                        "reviewd_by": user_id,
                                        "updated_at": datetime.utcnow().isoformat()
                                    }).eq("form_id", form['form_id']).execute()
                                    
                                    if update_response.data:
                                        st.success("✅ Form rejected successfully.")
                                        st.rerun()
                                    else:
                                        st.error("Failed to reject form.")
                                except Exception as e:
                                    st.error(f"Error rejecting form: {str(e)}")
                        
                        elif update_button:
                            try:
                                update_response = supabase.table("request_form").update({
                                    "status": new_status,
                                    "reviewer_comment": reviewer_comment.strip() if reviewer_comment.strip() else form.get('reviewer_comment'),
                                    "reviewd_by": user_id,
                                    "updated_at": datetime.utcnow().isoformat()
                                }).eq("form_id", form['form_id']).execute()
                                
                                if update_response.data:
                                    st.success(f"✅ Status updated to '{new_status}'")
                                    if new_status == "eligible":
                                        st.info("The request has been processed automatically by database triggers.")
                                        st.balloons()
                                    st.rerun()
                                else:
                                    st.error("Failed to update status.")
                            except Exception as e:
                                st.error(f"Error updating form: {str(e)}")
                
                elif not can_review:
                    st.info(f"ℹ️ You do not have permission to review this form. Only {'Admins can review archer and recorder requests' if form['role'] in ['archer', 'recorder'] else 'Recorders assigned to this competition/round can review participant requests'}.")
                
                elif form['status'] in ['eligible', 'ineligible']:
                    st.info(f"ℹ️ This form has already been {form['status']}. No further action needed.")

except Exception as e:
    st.error(f"Error loading forms: {str(e)}")

# Statistics section
st.divider()
st.subheader("📊 Review Statistics")

try:
    # Get statistics
    if is_admin:
        all_forms = supabase.table("request_form").select("status, role").execute()
    else:
        # For recorders, count only forms they can review
        all_forms = supabase.table("request_form").select("status, role, competition_id, round_id").eq("role", "participant").execute()
        
        # Filter to their assignments
        filtered_data = []
        for form in all_forms.data if all_forms.data else []:
            for assignment in recorder_assignments:
                if (form['competition_id'] == assignment['competition_id'] and 
                    form['round_id'] == assignment['round_id']):
                    filtered_data.append(form)
                    break
        
        all_forms.data = filtered_data
    
    if all_forms.data:
        total_forms = len(all_forms.data)
        pending_count = len([f for f in all_forms.data if f['status'] == 'pending'])
        in_progress_count = len([f for f in all_forms.data if f['status'] == 'in progress'])
        eligible_count = len([f for f in all_forms.data if f['status'] == 'eligible'])
        ineligible_count = len([f for f in all_forms.data if f['status'] == 'ineligible'])
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Forms", total_forms)
        with col2:
            st.metric("⏳ Pending", pending_count)
        with col3:
            st.metric("🔄 In Progress", in_progress_count)
        with col4:
            st.metric("✅ Eligible", eligible_count)
        with col5:
            st.metric("❌ Ineligible", ineligible_count)
        
        # Role breakdown
        st.write("**Forms by Role:**")
        role_col1, role_col2, role_col3 = st.columns(3)
        
        archer_count = len([f for f in all_forms.data if f['role'] == 'archer'])
        participant_count = len([f for f in all_forms.data if f['role'] == 'participant'])
        recorder_count = len([f for f in all_forms.data if f['role'] == 'recorder'])
        
        with role_col1:
            st.metric("🏹 Archer", archer_count)
        with role_col2:
            st.metric("🎯 Participant", participant_count)
        with role_col3:
            st.metric("📝 Recorder", recorder_count)
    else:
        st.info("No forms available for statistics.")
        
except Exception as e:
    st.error(f"Error loading statistics: {str(e)}")

# Show recorder assignments if recorder
if is_recorder and not is_admin:
    st.divider()
    st.subheader("📌 Your Recorder Assignments")
    
    for assignment in recorder_assignments:
        try:
            comp = supabase.table("competition").select("name, date_start, date_end").eq("competition_id", assignment['competition_id']).execute()
            rnd = supabase.table("round").select("name, age_group").eq("round_id", assignment['round_id']).execute()
            
            if comp.data and rnd.data:
                st.info(f"**Competition:** {comp.data[0]['name']} ({comp.data[0]['date_start']} to {comp.data[0]['date_end']}) | **Round:** {rnd.data[0]['name']} ({rnd.data[0]['age_group']})")
        except:
            st.warning(f"Assignment: Competition ID {assignment['competition_id']}, Round ID {assignment['round_id']}")
