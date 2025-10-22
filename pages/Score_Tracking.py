import streamlit as st
import pandas as pd
from datetime import datetime
from utility_function.initilize_dbconnection import supabase
from utility_function import score_tracking_utility

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("Please log in to access this page.")
    st.stop()

st.title("🎯 Score Tracking")
st.write(f"Welcome, {st.session_state.get('fullname')}!")

user_role = st.session_state.get('role')
user_id = st.session_state.get('user_id')

# Create tabs based on role
if user_role == 'archer':
    tabs = st.tabs(["➕ Add Score", "📊 My Scores", "✏️ Manage Scores"])
    tab_add, tab_view, tab_manage = tabs
elif user_role == 'recorder':
    tabs = st.tabs(["✅ Verify Scores", "📊 View Scores"])
    tab_verify, tab_view_recorder = tabs
else:
    st.warning("Only archers and recorders can access score tracking.")
    st.stop()

# ========================================
# ARCHER TABS
# ========================================
if user_role == 'archer':
    
    # TAB 1: Add Score
    with tab_add:
        st.header("➕ Add New Score")
        st.info("📝 Add practice or competition scores. Competition scores require recorder verification.")
        
        score_type = st.selectbox("Score Type*", ["practice", "competition"])
        
        # Get competition map
        competition_map = score_tracking_utility.get_competition_map()
        
        if not competition_map:
            st.warning("No competitions available. Please contact a recorder to create competitions.")
        else:
            competition_name = st.selectbox("Select Competition*", list(competition_map.keys()))
            competition_id = competition_map[competition_name]
            
            # Get event contexts for this competition
            event_contexts_df = score_tracking_utility.get_event_contexts_for_competition(competition_id)
            
            if event_contexts_df.empty:
                st.warning("No rounds configured for this competition.")
            else:
                # Create a readable format for event context selection
                event_contexts_df['display'] = event_contexts_df.apply(
                    lambda row: f"Round: {row['round']['name']} | Range: {row['range']['distance']}{row['range']['unit_of_length']} | End: {row['end_order']}", 
                    axis=1
                )
                
                event_context_map = dict(zip(event_contexts_df['display'], event_contexts_df['event_context_id']))
                
                selected_event = st.selectbox("Select Round/Range/End*", list(event_context_map.keys()))
                event_context_id = event_context_map[selected_event]
                
                st.divider()
                st.write("**Enter Arrow Scores (0-10 per arrow)**")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    arrow1 = st.number_input("1st Arrow*", min_value=0, max_value=10, value=0, step=1)
                    arrow2 = st.number_input("2nd Arrow*", min_value=0, max_value=10, value=0, step=1)
                with col2:
                    arrow3 = st.number_input("3rd Arrow*", min_value=0, max_value=10, value=0, step=1)
                    arrow4 = st.number_input("4th Arrow*", min_value=0, max_value=10, value=0, step=1)
                with col3:
                    arrow5 = st.number_input("5th Arrow*", min_value=0, max_value=10, value=0, step=1)
                    arrow6 = st.number_input("6th Arrow*", min_value=0, max_value=10, value=0, step=1)
                
                scores = [arrow1, arrow2, arrow3, arrow4, arrow5, arrow6]
                total = sum(scores)
                
                st.metric("Total Score", f"{total} / 60")
                
                if st.button("💾 Save Score", type="primary", use_container_width=True):
                    result = score_tracking_utility.add_score(user_id, event_context_id, scores, score_type)
                    
                    if result['success']:
                        st.success(result['message'])
                        if score_type == 'competition':
                            st.info("⏳ Your competition score is pending recorder verification.")
                        st.balloons()
                    else:
                        st.error(f"Error: {result['error']}")
    
    # TAB 2: View My Scores
    with tab_view:
        st.header("📊 My Scores")
        
        col1, col2 = st.columns(2)
        with col1:
            view_type = st.selectbox("Score Type", ["All", "competition", "practice"])
        with col2:
            status_filter = st.selectbox("Status", ["All", "eligible", "pending", "ineligible"])
        
        if st.button("🔍 Load Scores", type="primary"):
            score_type_filter = None if view_type == "All" else view_type
            scores_df = score_tracking_utility.get_participant_scores(user_id, score_type=score_type_filter)
            
            if not scores_df.empty:
                # Filter by status
                if status_filter != "All":
                    scores_df = scores_df[scores_df['status'] == status_filter]
                
                if not scores_df.empty:
                    st.success(f"Found {len(scores_df)} score(s)")
                    
                    # Display summary
                    st.write("**Score Summary:**")
                    cols = st.columns(4)
                    cols[0].metric("Total Ends", len(scores_df))
                    cols[1].metric("Average", f"{scores_df['sum_score'].mean():.2f}")
                    cols[2].metric("Highest", scores_df['sum_score'].max())
                    cols[3].metric("Lowest", scores_df['sum_score'].min())
                    
                    st.divider()
                    
                    # Display detailed scores
                    display_df = scores_df[[
                        'club_competition.name', 'round.name', 'range.distance', 'end_order',
                        'score_1st_arrow', 'score_2nd_arrow', 'score_3rd_arrow', 
                        'score_4th_arrow', 'score_5st_arrow', 'score_6st_arrow',
                        'sum_score', 'type', 'status', 'datetime'
                    ]].copy()
                    
                    display_df.columns = [
                        'Competition', 'Round', 'Distance', 'End',
                        '1st', '2nd', '3rd', '4th', '5th', '6th',
                        'Total', 'Type', 'Status', 'Date/Time'
                    ]
                    
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                else:
                    st.info(f"No {status_filter} scores found.")
            else:
                st.info("No scores found. Start adding scores in the 'Add Score' tab!")
    
    # TAB 3: Manage Scores
    with tab_manage:
        st.header("✏️ Manage Scores")
        st.info("⚠️ You can only modify or delete practice scores and pending competition scores.")
        
        # Load all modifiable scores
        scores_df = score_tracking_utility.get_participant_scores(user_id)
        
        if not scores_df.empty:
            # Filter to only modifiable scores
            modifiable = scores_df[
                (scores_df['type'] == 'practice') | 
                ((scores_df['type'] == 'competition') & (scores_df['status'] == 'pending'))
            ]
            
            if not modifiable.empty:
                st.write(f"**{len(modifiable)} modifiable score(s) found**")
                
                # Create selection list
                modifiable['display'] = modifiable.apply(
                    lambda row: f"{row['club_competition.name']} - {row['round.name']} - End {row['end_order']} ({row['type']}, {row['status']}) - {row['sum_score']} pts",
                    axis=1
                )
                
                selected_score_display = st.selectbox("Select Score to Manage", modifiable['display'].tolist())
                selected_row = modifiable[modifiable['display'] == selected_score_display].iloc[0]
                
                st.divider()
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Current Scores:**")
                    st.write(f"Competition: {selected_row['club_competition.name']}")
                    st.write(f"Round: {selected_row['round.name']}")
                    st.write(f"End: {selected_row['end_order']}")
                    st.write(f"Type: {selected_row['type']} | Status: {selected_row['status']}")
                
                with col2:
                    st.metric("Current Total", f"{selected_row['sum_score']} / 60")
                
                st.divider()
                
                tab_edit, tab_delete = st.tabs(["✏️ Edit", "🗑️ Delete"])
                
                with tab_edit:
                    st.write("**Edit Arrow Scores:**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        new_arrow1 = st.number_input("1st Arrow", min_value=0, max_value=10, 
                                                    value=int(selected_row['score_1st_arrow']), step=1, key="edit_1")
                        new_arrow2 = st.number_input("2nd Arrow", min_value=0, max_value=10, 
                                                    value=int(selected_row['score_2nd_arrow']), step=1, key="edit_2")
                    with col2:
                        new_arrow3 = st.number_input("3rd Arrow", min_value=0, max_value=10, 
                                                    value=int(selected_row['score_3rd_arrow']), step=1, key="edit_3")
                        new_arrow4 = st.number_input("4th Arrow", min_value=0, max_value=10, 
                                                    value=int(selected_row['score_4th_arrow']), step=1, key="edit_4")
                    with col3:
                        new_arrow5 = st.number_input("5th Arrow", min_value=0, max_value=10, 
                                                    value=int(selected_row['score_5st_arrow']), step=1, key="edit_5")
                        new_arrow6 = st.number_input("6th Arrow", min_value=0, max_value=10, 
                                                    value=int(selected_row['score_6st_arrow']), step=1, key="edit_6")
                    
                    new_scores = [new_arrow1, new_arrow2, new_arrow3, new_arrow4, new_arrow5, new_arrow6]
                    new_total = sum(new_scores)
                    
                    st.metric("New Total", f"{new_total} / 60")
                    
                    if st.button("💾 Update Score", type="primary", use_container_width=True):
                        result = score_tracking_utility.update_score(
                            user_id, 
                            selected_row['event_context_id'], 
                            selected_row['type'],
                            new_scores
                        )
                        
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(f"Error: {result['error']}")
                
                with tab_delete:
                    st.warning("⚠️ **Warning:** This action cannot be undone!")
                    st.write(f"Are you sure you want to delete this score of **{selected_row['sum_score']} points**?")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🗑️ Yes, Delete", type="primary", use_container_width=True):
                            result = score_tracking_utility.delete_score(
                                user_id,
                                selected_row['event_context_id'],
                                selected_row['type']
                            )
                            
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(f"Error: {result['error']}")
                    with col2:
                        if st.button("❌ Cancel", use_container_width=True):
                            st.info("Deletion cancelled.")
            else:
                st.info("No modifiable scores found. Only practice scores and pending competition scores can be modified.")
        else:
            st.info("No scores found.")

# ========================================
# RECORDER TABS
# ========================================
elif user_role == 'recorder':
    
    # TAB 1: Verify Scores
    with tab_verify:
        st.header("✅ Verify Competition Scores")
        st.write("Review and verify archer scores for competitions you're recording")
        
        # Get competitions where user is a recorder
        try:
            recordings_response = supabase.table("recording").select(
                "club_competition_id, club_competition(name)"
            ).eq("recording_id", user_id).execute()
            
            if recordings_response.data:
                comp_map = {f"{r['club_competition']['name']} (ID: {r['club_competition_id']})": 
                           r['club_competition_id'] for r in recordings_response.data}
                
                selected_comp_name = st.selectbox("Select Competition", list(comp_map.keys()))
                competition_id = comp_map[selected_comp_name]
                
                # Get pending scores for this competition
                pending_response = supabase.table("participating").select(
                    """
                    participating_id,
                    event_context_id,
                    score_1st_arrow,
                    score_2nd_arrow,
                    score_3rd_arrow,
                    score_4th_arrow,
                    score_5st_arrow,
                    score_6st_arrow,
                    sum_score,
                    datetime,
                    archer(account(fullname)),
                    event_context!inner(
                        club_competition_id,
                        round_id,
                        range_id,
                        end_order,
                        round(name),
                        range(distance, unit_of_length)
                    )
                    """
                ).eq("event_context.club_competition_id", competition_id).eq(
                    "type", "competition"
                ).eq("status", "pending").execute()
                
                if pending_response.data:
                    st.success(f"Found {len(pending_response.data)} pending score(s)")
                    
                    # Display pending scores
                    pending_df = pd.DataFrame(pending_response.data)
                    
                    # Flatten nested structures
                    if not pending_df.empty:
                        pending_df['archer_name'] = pending_df['archer'].apply(lambda x: x['account']['fullname'])
                        pending_df['round_name'] = pending_df['event_context'].apply(lambda x: x['round']['name'])
                        pending_df['distance'] = pending_df['event_context'].apply(lambda x: f"{x['range']['distance']}{x['range']['unit_of_length']}")
                        pending_df['end'] = pending_df['event_context'].apply(lambda x: x['end_order'])
                        
                        display_df = pending_df[[
                            'archer_name', 'round_name', 'distance', 'end',
                            'score_1st_arrow', 'score_2nd_arrow', 'score_3rd_arrow',
                            'score_4th_arrow', 'score_5st_arrow', 'score_6st_arrow',
                            'sum_score', 'datetime'
                        ]]
                        
                        display_df.columns = [
                            'Archer', 'Round', 'Distance', 'End',
                            '1st', '2nd', '3rd', '4th', '5th', '6th',
                            'Total', 'Date/Time'
                        ]
                        
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                        
                        st.divider()
                        
                        # Verify all button
                        if st.button("✅ Verify All Pending Scores", type="primary", use_container_width=True):
                            archer_ids = pending_df['participating_id'].unique().tolist()
                            event_context_ids = pending_df['event_context_id'].unique().tolist()
                            
                            result = score_tracking_utility.verify_scores_by_recorder(
                                user_id, archer_ids, event_context_ids
                            )
                            
                            if result['success']:
                                st.success(result['message'])
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"Error: {result['error']}")
                else:
                    st.info("No pending scores to verify for this competition.")
            else:
                st.warning("You are not assigned as a recorder for any competitions.")
        except Exception as e:
            st.error(f"Error loading competitions: {e}")
    
    # TAB 2: View Scores
    with tab_view_recorder:
        st.header("📊 View Competition Scores")
        
        # Get competitions where user is a recorder
        try:
            recordings_response = supabase.table("recording").select(
                "club_competition_id, club_competition(name)"
            ).eq("recording_id", user_id).execute()
            
            if recordings_response.data:
                comp_map = {f"{r['club_competition']['name']} (ID: {r['club_competition_id']})": 
                           r['club_competition_id'] for r in recordings_response.data}
                
                selected_comp_name = st.selectbox("Select Competition", list(comp_map.keys()), key="view_comp")
                competition_id = comp_map[selected_comp_name]
                
                # Get archer map for filtering
                archer_map = score_tracking_utility.get_archer_map()
                
                col1, col2 = st.columns(2)
                with col1:
                    archer_filter = st.selectbox("Filter by Archer", ["All"] + list(archer_map.keys()))
                with col2:
                    status_filter = st.selectbox("Filter by Status", ["All", "eligible", "pending", "ineligible"], key="status_recorder")
                
                if st.button("🔍 Load Scores", type="primary", key="load_recorder"):
                    # Build query
                    query = supabase.table("participating").select(
                        """
                        participating_id,
                        event_context_id,
                        score_1st_arrow,
                        score_2nd_arrow,
                        score_3rd_arrow,
                        score_4th_arrow,
                        score_5st_arrow,
                        score_6st_arrow,
                        sum_score,
                        status,
                        datetime,
                        archer(account(fullname)),
                        event_context!inner(
                            club_competition_id,
                            round_id,
                            end_order,
                            round(name),
                            range(distance, unit_of_length)
                        )
                        """
                    ).eq("event_context.club_competition_id", competition_id).eq("type", "competition")
                    
                    # Apply filters
                    if archer_filter != "All":
                        archer_id = archer_map[archer_filter]
                        query = query.eq("participating_id", archer_id)
                    
                    if status_filter != "All":
                        query = query.eq("status", status_filter)
                    
                    response = query.order("datetime", desc=True).execute()
                    
                    if response.data:
                        st.success(f"Found {len(response.data)} score(s)")
                        
                        scores_df = pd.DataFrame(response.data)
                        
                        # Flatten nested structures
                        scores_df['archer_name'] = scores_df['archer'].apply(lambda x: x['account']['fullname'])
                        scores_df['round_name'] = scores_df['event_context'].apply(lambda x: x['round']['name'])
                        scores_df['distance'] = scores_df['event_context'].apply(lambda x: f"{x['range']['distance']}{x['range']['unit_of_length']}")
                        scores_df['end'] = scores_df['event_context'].apply(lambda x: x['end_order'])
                        
                        display_df = scores_df[[
                            'archer_name', 'round_name', 'distance', 'end',
                            'score_1st_arrow', 'score_2nd_arrow', 'score_3rd_arrow',
                            'score_4th_arrow', 'score_5st_arrow', 'score_6st_arrow',
                            'sum_score', 'status', 'datetime'
                        ]]
                        
                        display_df.columns = [
                            'Archer', 'Round', 'Distance', 'End',
                            '1st', '2nd', '3rd', '4th', '5th', '6th',
                            'Total', 'Status', 'Date/Time'
                        ]
                        
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                    else:
                        st.info("No scores found with the selected filters.")
            else:
                st.warning("You are not assigned as a recorder for any competitions.")
        except Exception as e:
            st.error(f"Error loading scores: {e}")
