import streamlit as st
import pandas as pd
from utility_function.initilize_dbconnection import supabase
from utility_function.score_tracking_utility import (
    get_archer_scores, get_event_participants, update_score,
    verify_score, get_event_context_info, check_recorder_permission
)

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("Please log in to access this page.")
    st.stop()

st.title("🎯 Score Tracking")
st.write(f"Welcome, {st.session_state.get('fullname')}!")

user_role = st.session_state.get('role')

# Create tabs based on role
if user_role == 'archer':
    tab1, tab2 = st.tabs(["✏️ My Scores", "📊 View Scores"])
elif user_role == 'recorder':
    tab1, tab2, tab3 = st.tabs(["✏️ My Scores", "📊 View Scores", "✅ Verify Scores"])
else:
    st.info("This page is primarily for archers and recorders.")
    st.stop()

# Tab 1: My Scores (Archer)
with tab1:
    st.header("My Scores")
    st.write("View and update your personal scores")
    
    score_type = st.radio("Score Type", ["competition", "practice"])
    
    if st.button("📥 Load My Scores", type="primary"):
        scores_df = get_archer_scores(st.session_state.user_id, score_type)
        st.session_state.my_scores = scores_df
    
    if 'my_scores' in st.session_state and not st.session_state.my_scores.empty:
        st.success(f"Found {len(st.session_state.my_scores)} score record(s)")
        
        # Display scores
        display_df = st.session_state.my_scores.copy()
        
        st.dataframe(display_df, use_container_width=True)
        
        # Update score section
        st.divider()
        st.subheader("✏️ Update a Score")
        st.info("ℹ️ You can only modify scores that have not been verified (status != 'eligible')")
        
        # Select a score to update
        if len(st.session_state.my_scores) > 0:
            score_options = []
            for idx, row in st.session_state.my_scores.iterrows():
                score_options.append(f"Event Context: {row['event_context_id']} (Status: {row.get('status', 'N/A')})")
            
            selected_score_idx = st.selectbox("Select Score to Update", range(len(score_options)), 
                                             format_func=lambda x: score_options[x])
            
            selected_score = st.session_state.my_scores.iloc[selected_score_idx]
            
            # Check if score can be modified
            if selected_score.get('status') == 'eligible':
                st.warning("⚠️ This score has been verified and cannot be modified.")
            else:
                with st.form("update_score_form"):
                    st.write(f"**Event Context ID:** {selected_score['event_context_id']}")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        arrow1 = st.number_input("Arrow 1", min_value=0, max_value=10, 
                                                value=int(selected_score.get('score_1st_arrow', 0)), key="arrow1")
                        arrow2 = st.number_input("Arrow 2", min_value=0, max_value=10, 
                                                value=int(selected_score.get('score_2nd_arrow', 0)), key="arrow2")
                    
                    with col2:
                        arrow3 = st.number_input("Arrow 3", min_value=0, max_value=10, 
                                                value=int(selected_score.get('score_3rd_arrow', 0)), key="arrow3")
                        arrow4 = st.number_input("Arrow 4", min_value=0, max_value=10, 
                                                value=int(selected_score.get('score_4th_arrow', 0)), key="arrow4")
                    
                    with col3:
                        arrow5 = st.number_input("Arrow 5", min_value=0, max_value=10, 
                                                value=int(selected_score.get('score_5th_arrow', 0)), key="arrow5")
                        arrow6 = st.number_input("Arrow 6", min_value=0, max_value=10, 
                                                value=int(selected_score.get('score_6th_arrow', 0)), key="arrow6")
                    
                    total = arrow1 + arrow2 + arrow3 + arrow4 + arrow5 + arrow6
                    st.metric("Total Score", total)
                    
                    update_btn = st.form_submit_button("💾 Update Score", type="primary")
                    
                    if update_btn:
                        arrow_scores = {
                            'arrow_1': arrow1,
                            'arrow_2': arrow2,
                            'arrow_3': arrow3,
                            'arrow_4': arrow4,
                            'arrow_5': arrow5,
                            'arrow_6': arrow6
                        }
                        
                        success = update_score(
                            st.session_state.user_id,
                            selected_score['event_context_id'],
                            score_type,
                            arrow_scores
                        )
                        
                        if success:
                            st.success("✅ Score updated successfully!")
                            st.balloons()
                            # Reload scores
                            scores_df = get_archer_scores(st.session_state.user_id, score_type)
                            st.session_state.my_scores = scores_df
                            st.rerun()
                        else:
                            st.error("Failed to update score. Please try again.")
    else:
        st.info("No scores found. Start competing or practicing to see your scores here!")

# Tab 2: View Scores
with tab2:
    st.header("View Participant Scores")
    st.write("View scores for a specific event context")
    
    event_context_id = st.text_input("Enter Event Context ID", placeholder="e.g., 1-1-1-1")
    
    if st.button("🔍 Load Scores", type="primary"):
        if event_context_id:
            participants_df = get_event_participants(event_context_id)
            st.session_state.participants_scores = participants_df
            
            # Get event context info
            event_info = get_event_context_info(event_context_id)
            st.session_state.event_info = event_info
        else:
            st.error("Please enter an Event Context ID.")
    
    # Display event info
    if 'event_info' in st.session_state and st.session_state.event_info:
        st.divider()
        st.subheader("📋 Event Information")
        
        event = st.session_state.event_info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Competition ID:** {event.get('club_competition_id', 'N/A')}")
        with col2:
            st.write(f"**Round ID:** {event.get('round_id', 'N/A')}")
        with col3:
            st.write(f"**Range ID:** {event.get('range_id', 'N/A')}")
    
    # Display participants
    if 'participants_scores' in st.session_state and not st.session_state.participants_scores.empty:
        st.divider()
        st.subheader("👥 Participant Scores")
        st.success(f"Found {len(st.session_state.participants_scores)} participant(s)")
        
        # Calculate total scores
        score_columns = ['score_1st_arrow', 'score_2nd_arrow', 'score_3rd_arrow', 
                        'score_4th_arrow', 'score_5th_arrow', 'score_6th_arrow']
        
        display_df = st.session_state.participants_scores.copy()
        display_df['total_score'] = display_df[score_columns].sum(axis=1)
        
        st.dataframe(display_df, use_container_width=True, height=400)
    elif 'participants_scores' in st.session_state:
        st.info("No participants found for this event context.")

# Tab 3: Verify Scores (Recorder only)
if user_role == 'recorder':
    with tab3:
        st.header("✅ Verify Participant Scores")
        st.write("Verify and approve participant scores for competitions you manage")
        
        verify_event_id = st.text_input("Enter Event Context ID ", placeholder="e.g., 1-1-1-1", key="verify_event")
        
        if st.button("📥 Load Scores for Verification", type="primary"):
            if verify_event_id:
                participants_df = get_event_participants(verify_event_id)
                st.session_state.verify_participants = participants_df
                
                # Get event info and check permission
                event_info = get_event_context_info(verify_event_id)
                if event_info:
                    competition_id = event_info.get('club_competition_id')
                    has_permission = check_recorder_permission(st.session_state.user_id, competition_id)
                    st.session_state.has_verify_permission = has_permission
                    
                    if not has_permission:
                        st.warning("⚠️ You don't have permission to verify scores for this competition.")
                else:
                    st.error("Could not retrieve event information.")
            else:
                st.error("Please enter an Event Context ID.")
        
        # Display scores for verification
        if 'verify_participants' in st.session_state and not st.session_state.verify_participants.empty:
            if st.session_state.get('has_verify_permission', False):
                st.success(f"Found {len(st.session_state.verify_participants)} participant(s) to verify")
                
                # Display each participant with verify button
                for idx, participant in st.session_state.verify_participants.iterrows():
                    with st.expander(f"Participant ID: {participant['participating_id']} - Status: {participant.get('status', 'N/A')}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write("**Arrow Scores:**")
                            score_data = {
                                'Arrow': ['1st', '2nd', '3rd', '4th', '5th', '6th'],
                                'Score': [
                                    participant.get('score_1st_arrow', 0),
                                    participant.get('score_2nd_arrow', 0),
                                    participant.get('score_3rd_arrow', 0),
                                    participant.get('score_4th_arrow', 0),
                                    participant.get('score_5th_arrow', 0),
                                    participant.get('score_6th_arrow', 0)
                                ]
                            }
                            st.dataframe(pd.DataFrame(score_data), use_container_width=True)
                            
                            total_score = sum(score_data['Score'])
                            st.metric("Total Score", total_score)
                        
                        with col2:
                            st.write("**Actions:**")
                            
                            if participant.get('status') != 'eligible':
                                if st.button("✅ Verify", key=f"verify_{participant['participating_id']}_{idx}", type="primary"):
                                    success = verify_score(
                                        participant['participating_id'],
                                        verify_event_id,
                                        participant['type'],
                                        'eligible'
                                    )
                                    
                                    if success:
                                        st.success("Score verified!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to verify score.")
                            else:
                                st.success("✓ Verified")
                            
                            if st.button("❌ Reject", key=f"reject_{participant['participating_id']}_{idx}"):
                                success = verify_score(
                                    participant['participating_id'],
                                    verify_event_id,
                                    participant['type'],
                                    'ineligible'
                                )
                                
                                if success:
                                    st.info("Score marked as ineligible.")
                                    st.rerun()
                                else:
                                    st.error("Failed to update status.")
            else:
                st.warning("⚠️ You don't have permission to verify scores for this competition.")
        elif 'verify_participants' in st.session_state:
            st.info("No participants found for verification.")
