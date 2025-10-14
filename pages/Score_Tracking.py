import streamlit as st
from datetime import datetime
from utility_function.initilize_dbconnection import supabase

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please log in to access score tracking.")
    st.info("Navigate to the 'Sign Up Log In' page to access your account.")
    st.stop()

# Page header
st.title("📊 Score Tracking System")
st.write(f"**Logged in as:** {st.session_state.get('fullname', 'N/A')}")

# Check user roles
user_id = st.session_state.get('user_id')

try:
    archer_check = supabase.table("archer").select("archer_id").eq("archer_id", user_id).execute()
    is_archer = bool(archer_check.data)
except:
    is_archer = False

try:
    recorder_check = supabase.table("recorder").select("recorder_id, competition_id, round_id").eq("recorder_id", user_id).execute()
    is_recorder = bool(recorder_check.data)
    recorder_assignments = recorder_check.data if recorder_check.data else []
except:
    is_recorder = False
    recorder_assignments = []

if not is_archer and not is_recorder:
    st.error("🚫 Access Denied")
    st.warning("You must be an Archer or Recorder to access this page.")
    st.stop()

st.write(f"**Role:** {'Archer' if is_archer else ''}{' & ' if is_archer and is_recorder else ''}{'Recorder' if is_recorder else ''}")
st.divider()

# Different views based on role
if is_archer and is_recorder:
    view_mode = st.radio("Select View", ["🏹 My Scores (Archer)", "✅ Verify Scores (Recorder)"], horizontal=True)
elif is_archer:
    view_mode = "🏹 My Scores (Archer)"
else:
    view_mode = "✅ Verify Scores (Recorder)"

# ==================== ARCHER VIEW ====================
if "Archer" in view_mode:
    st.subheader("🏹 My Score Management")
    
    # Tabs for competition and practice scores
    tab1, tab2 = st.tabs(["🏆 Competition Scores", "🎯 Practice Scores"])
    
    # ==================== COMPETITION SCORES ====================
    with tab1:
        st.write("### My Competition Scores")
        
        try:
            # Get participant's scores
            scores = supabase.table("participant_score").select(
                "*, event_context:event_context_id(competition:competition_id(name), round:round_id(name), range:range_id(distance, unit_of_length), end_order)"
            ).eq("participant_id", user_id).eq("type", "competition").order("datetime", desc=True).execute()
            
            scores_list = scores.data if scores.data else []
            
            if not scores_list:
                st.info("You don't have any competition scores yet. Register for a competition to start tracking scores!")
            else:
                st.info(f"📊 Found {len(scores_list)} score record(s)")
                
                # Filter by status
                status_filter = st.selectbox("Filter by Status", ["All", "pending", "in progress", "eligible", "ineligible"])
                
                for score in scores_list:
                    if status_filter != "All" and score['status'] != status_filter:
                        continue
                    
                    status_emoji = {
                        "pending": "⏳",
                        "in progress": "🔄",
                        "eligible": "✅",
                        "ineligible": "❌"
                    }.get(score['status'], "❓")
                    
                    event_ctx = score.get('event_context', {})
                    comp_name = event_ctx.get('competition', {}).get('name', 'Unknown') if event_ctx else 'Unknown'
                    round_name = event_ctx.get('round', {}).get('name', 'Unknown') if event_ctx else 'Unknown'
                    range_info = f"{event_ctx.get('range', {}).get('distance', '?')}{event_ctx.get('range', {}).get('unit_of_length', '')}" if event_ctx and event_ctx.get('range') else 'Unknown'
                    end_order = event_ctx.get('end_order', '?') if event_ctx else '?'
                    
                    with st.expander(f"{status_emoji} {comp_name} - {round_name} | End {end_order} | {score['status']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Competition:** {comp_name}")
                            st.write(f"**Round:** {round_name}")
                            st.write(f"**Range:** {range_info}")
                            st.write(f"**End Order:** {end_order}")
                            st.write(f"**Event Context ID:** {score['event_context_id']}")
                        
                        with col2:
                            st.write(f"**Status:** {score['status']}")
                            st.write(f"**Date/Time:** {score['datetime']}")
                            st.write(f"**Sum Score:** {score['sum_score']}/60")
                        
                        st.divider()
                        
                        # Score details
                        st.write("**Arrow Scores:**")
                        cols = st.columns(6)
                        cols[0].metric("Arrow 1", score['score_1st_arrow'])
                        cols[1].metric("Arrow 2", score['score_2nd_arrow'])
                        cols[2].metric("Arrow 3", score['score_3rd_arrow'])
                        cols[3].metric("Arrow 4", score['score_4th_arrow'])
                        cols[4].metric("Arrow 5", score['score_5st_arrow'])
                        cols[5].metric("Arrow 6", score['score_6st_arrow'])
                        
                        # Edit scores (only if not verified as eligible)
                        if score['status'] != 'eligible':
                            st.divider()
                            st.write("**✏️ Edit Score**")
                            
                            with st.form(f"edit_score_{score['event_context_id']}"):
                                cols = st.columns(6)
                                new_score_1 = cols[0].number_input("Arrow 1", 0, 10, score['score_1st_arrow'], key=f"s1_{score['event_context_id']}")
                                new_score_2 = cols[1].number_input("Arrow 2", 0, 10, score['score_2nd_arrow'], key=f"s2_{score['event_context_id']}")
                                new_score_3 = cols[2].number_input("Arrow 3", 0, 10, score['score_3rd_arrow'], key=f"s3_{score['event_context_id']}")
                                new_score_4 = cols[3].number_input("Arrow 4", 0, 10, score['score_4th_arrow'], key=f"s4_{score['event_context_id']}")
                                new_score_5 = cols[4].number_input("Arrow 5", 0, 10, score['score_5st_arrow'], key=f"s5_{score['event_context_id']}")
                                new_score_6 = cols[5].number_input("Arrow 6", 0, 10, score['score_6st_arrow'], key=f"s6_{score['event_context_id']}")
                                
                                new_sum = new_score_1 + new_score_2 + new_score_3 + new_score_4 + new_score_5 + new_score_6
                                st.info(f"New Total: {new_sum}/60")
                                
                                submit_edit = st.form_submit_button("Update Score", type="primary")
                                
                                if submit_edit:
                                    try:
                                        supabase.table("participant_score").update({
                                            "score_1st_arrow": new_score_1,
                                            "score_2nd_arrow": new_score_2,
                                            "score_3rd_arrow": new_score_3,
                                            "score_4th_arrow": new_score_4,
                                            "score_5st_arrow": new_score_5,
                                            "score_6st_arrow": new_score_6,
                                            "sum_score": new_sum,
                                            "datetime": datetime.utcnow().isoformat()
                                        }).eq("participant_id", user_id).eq("event_context_id", score['event_context_id']).eq("type", "competition").execute()
                                        
                                        st.success("✅ Score updated successfully!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error updating score: {str(e)}")
                        else:
                            st.success("✅ This score has been verified and cannot be edited.")
        
        except Exception as e:
            st.error(f"Error loading scores: {str(e)}")
    
    # ==================== PRACTICE SCORES ====================
    with tab2:
        st.write("### My Practice Scores")
        st.info("Practice scores are for your personal tracking and don't require verification.")
        
        # Add new practice score
        st.write("#### Add New Practice Score")
        
        with st.form("add_practice_score"):
            # Select event context
            try:
                # Get all event contexts
                contexts = supabase.table("event_context").select(
                    "event_context_id, competition:competition_id(name), round:round_id(name), range:range_id(distance, unit_of_length), end_order"
                ).execute()
                
                context_list = contexts.data if contexts.data else []
                
                if not context_list:
                    st.warning("No event contexts available for practice.")
                    context_options = {}
                else:
                    context_options = {}
                    for ctx in context_list:
                        comp_name = ctx.get('competition', {}).get('name', 'Unknown') if ctx.get('competition') else 'Unknown'
                        round_name = ctx.get('round', {}).get('name', 'Unknown') if ctx.get('round') else 'Unknown'
                        range_info = f"{ctx.get('range', {}).get('distance', '?')}{ctx.get('range', {}).get('unit_of_length', '')}" if ctx.get('range') else 'Unknown'
                        
                        label = f"{comp_name} - {round_name} - End {ctx['end_order']} ({range_info})"
                        context_options[label] = ctx['event_context_id']
                
                if context_options:
                    selected_context = st.selectbox("Select Event Context*", list(context_options.keys()))
                    event_context_id = context_options[selected_context]
                else:
                    event_context_id = None
                
            except Exception as e:
                st.error(f"Error loading contexts: {str(e)}")
                event_context_id = None
            
            st.write("**Enter Arrow Scores (0-10):**")
            cols = st.columns(6)
            practice_s1 = cols[0].number_input("Arrow 1", 0, 10, 0, key="practice_s1")
            practice_s2 = cols[1].number_input("Arrow 2", 0, 10, 0, key="practice_s2")
            practice_s3 = cols[2].number_input("Arrow 3", 0, 10, 0, key="practice_s3")
            practice_s4 = cols[3].number_input("Arrow 4", 0, 10, 0, key="practice_s4")
            practice_s5 = cols[4].number_input("Arrow 5", 0, 10, 0, key="practice_s5")
            practice_s6 = cols[5].number_input("Arrow 6", 0, 10, 0, key="practice_s6")
            
            practice_sum = practice_s1 + practice_s2 + practice_s3 + practice_s4 + practice_s5 + practice_s6
            st.info(f"Total: {practice_sum}/60")
            
            submit_practice = st.form_submit_button("Add Practice Score", type="primary")
            
            if submit_practice:
                if not event_context_id:
                    st.error("Please select an event context!")
                else:
                    try:
                        supabase.table("participant_score").insert({
                            "participant_id": user_id,
                            "event_context_id": event_context_id,
                            "score_1st_arrow": practice_s1,
                            "score_2nd_arrow": practice_s2,
                            "score_3rd_arrow": practice_s3,
                            "score_4th_arrow": practice_s4,
                            "score_5st_arrow": practice_s5,
                            "score_6st_arrow": practice_s6,
                            "sum_score": practice_sum,
                            "datetime": datetime.utcnow().isoformat(),
                            "type": "practice",
                            "status": "eligible"
                        }).execute()
                        
                        st.success("✅ Practice score added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding practice score: {str(e)}")
        
        st.divider()
        
        # View practice scores
        st.write("#### My Practice Score History")
        try:
            practice_scores = supabase.table("participant_score").select(
                "*, event_context:event_context_id(competition:competition_id(name), round:round_id(name), end_order)"
            ).eq("participant_id", user_id).eq("type", "practice").order("datetime", desc=True).execute()
            
            practice_list = practice_scores.data if practice_scores.data else []
            
            if not practice_list:
                st.info("No practice scores recorded yet.")
            else:
                st.info(f"📊 Found {len(practice_list)} practice score(s)")
                
                for score in practice_list:
                    event_ctx = score.get('event_context', {})
                    comp_name = event_ctx.get('competition', {}).get('name', 'Unknown') if event_ctx else 'Unknown'
                    round_name = event_ctx.get('round', {}).get('name', 'Unknown') if event_ctx else 'Unknown'
                    end_order = event_ctx.get('end_order', '?') if event_ctx else '?'
                    
                    with st.expander(f"🎯 {comp_name} - {round_name} | End {end_order} | Score: {score['sum_score']}/60 | {score['datetime']}"):
                        cols = st.columns(6)
                        cols[0].metric("Arrow 1", score['score_1st_arrow'])
                        cols[1].metric("Arrow 2", score['score_2nd_arrow'])
                        cols[2].metric("Arrow 3", score['score_3rd_arrow'])
                        cols[3].metric("Arrow 4", score['score_4th_arrow'])
                        cols[4].metric("Arrow 5", score['score_5st_arrow'])
                        cols[5].metric("Arrow 6", score['score_6st_arrow'])
                        
                        # Delete practice score
                        if st.button("🗑️ Delete", key=f"del_practice_{score['event_context_id']}_{score['datetime']}"):
                            try:
                                supabase.table("participant_score").delete().eq(
                                    "participant_id", user_id
                                ).eq("event_context_id", score['event_context_id']).eq("type", "practice").execute()
                                st.success("Deleted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
        
        except Exception as e:
            st.error(f"Error loading practice scores: {str(e)}")

# ==================== RECORDER VIEW ====================
if "Recorder" in view_mode:
    st.subheader("✅ Score Verification (Recorder)")
    
    st.info("Review and verify competition scores for events you manage.")
    
    # Show recorder assignments
    with st.expander("📋 Your Assignments"):
        for assignment in recorder_assignments:
            comp_data = supabase.table("competition").select("name").eq("competition_id", assignment['competition_id']).execute()
            round_data = supabase.table("round").select("name").eq("round_id", assignment['round_id']).execute()
            
            comp_name = comp_data.data[0]['name'] if comp_data.data else "Unknown"
            round_name = round_data.data[0]['name'] if round_data.data else "Unknown"
            
            st.write(f"🏆 **{comp_name}** - Round: **{round_name}**")
    
    st.divider()
    
    # For each assignment, show scores to verify
    for assignment in recorder_assignments:
        comp_data = supabase.table("competition").select("name").eq("competition_id", assignment['competition_id']).execute()
        round_data = supabase.table("round").select("name").eq("round_id", assignment['round_id']).execute()
        
        comp_name = comp_data.data[0]['name'] if comp_data.data else "Unknown"
        round_name = round_data.data[0]['name'] if round_data.data else "Unknown"
        
        with st.expander(f"🏆 {comp_name} - {round_name}", expanded=True):
            try:
                # Get event contexts for this competition/round
                contexts = supabase.table("event_context").select("event_context_id").eq(
                    "competition_id", assignment['competition_id']
                ).eq("round_id", assignment['round_id']).execute()
                
                context_ids = [ctx['event_context_id'] for ctx in (contexts.data or [])]
                
                if not context_ids:
                    st.info("No event contexts found for this assignment.")
                    continue
                
                # Get all scores for these contexts
                all_scores = []
                for ctx_id in context_ids:
                    scores = supabase.table("participant_score").select(
                        "*, account:participant_id(fullname, email_address)"
                    ).eq("event_context_id", ctx_id).eq("type", "competition").execute()
                    
                    if scores.data:
                        all_scores.extend(scores.data)
                
                if not all_scores:
                    st.info("No scores to verify yet.")
                    continue
                
                # Filter by status
                verify_status_filter = st.selectbox(
                    "Filter by Status",
                    ["All", "pending", "in progress", "eligible", "ineligible"],
                    key=f"verify_filter_{assignment['competition_id']}_{assignment['round_id']}"
                )
                
                filtered_scores = [s for s in all_scores if verify_status_filter == "All" or s['status'] == verify_status_filter]
                
                st.info(f"📊 Found {len(filtered_scores)} score(s) to review")
                
                for score in filtered_scores:
                    participant_name = score['account']['fullname'] if score.get('account') else "Unknown"
                    participant_email = score['account']['email_address'] if score.get('account') else "Unknown"
                    
                    status_emoji = {
                        "pending": "⏳",
                        "in progress": "🔄",
                        "eligible": "✅",
                        "ineligible": "❌"
                    }.get(score['status'], "❓")
                    
                    with st.container(border=True):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**{status_emoji} Participant:** {participant_name} ({participant_email})")
                            st.write(f"**Event Context:** {score['event_context_id']}")
                            st.write(f"**Date/Time:** {score['datetime']}")
                        
                        with col2:
                            st.write(f"**Status:** {score['status']}")
                            st.write(f"**Total Score:** {score['sum_score']}/60")
                        
                        # Arrow scores
                        cols = st.columns(6)
                        cols[0].metric("Arrow 1", score['score_1st_arrow'])
                        cols[1].metric("Arrow 2", score['score_2nd_arrow'])
                        cols[2].metric("Arrow 3", score['score_3rd_arrow'])
                        cols[3].metric("Arrow 4", score['score_4th_arrow'])
                        cols[4].metric("Arrow 5", score['score_5st_arrow'])
                        cols[5].metric("Arrow 6", score['score_6st_arrow'])
                        
                        # Verification actions
                        if score['status'] != 'eligible':
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                if st.button("✅ Approve", key=f"approve_{score['participant_id']}_{score['event_context_id']}"):
                                    try:
                                        supabase.table("participant_score").update({
                                            "status": "eligible"
                                        }).eq("participant_id", score['participant_id']).eq("event_context_id", score['event_context_id']).eq("type", "competition").execute()
                                        st.success("Score approved!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                            
                            with col2:
                                if st.button("⏳ Mark In Progress", key=f"progress_{score['participant_id']}_{score['event_context_id']}"):
                                    try:
                                        supabase.table("participant_score").update({
                                            "status": "in progress"
                                        }).eq("participant_id", score['participant_id']).eq("event_context_id", score['event_context_id']).eq("type", "competition").execute()
                                        st.success("Status updated!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                            
                            with col3:
                                if st.button("❌ Reject", key=f"reject_{score['participant_id']}_{score['event_context_id']}"):
                                    try:
                                        supabase.table("participant_score").update({
                                            "status": "ineligible"
                                        }).eq("participant_id", score['participant_id']).eq("event_context_id", score['event_context_id']).eq("type", "competition").execute()
                                        st.warning("Score rejected!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                        
                        st.write("")
            
            except Exception as e:
                st.error(f"Error loading scores: {str(e)}")
