import streamlit as st
import pandas as pd
from utility_function.initilize_dbconnection import supabase
import utility_function.score_tracking_utility  as score_tracking_utility

st.set_page_config(page_title="Score Tracking", layout="wide")
st.title("🎯 Score Tracking")

# Check if user is logged in
if 'user_id' not in st.session_state or 'role' not in st.session_state:
    st.error("Please log in to access this page.")
    st.stop()

# Check if user is Archer or Recorder
if st.session_state['role'] not in ['archer', 'recorder']:
    st.error("This page is only accessible to Archers and Recorders.")
    st.stop()

# Create tabs based on role
if st.session_state['role'] == 'archer':
    # Archer view - single tab
    st.header("Score Tracking for Archer")
    
    # Get available club competitions and rounds
    club_competition_map = score_tracking_utility.get_club_competition_map_of_an_archer(st.session_state['user_id'])
    if not club_competition_map:
        st.warning("No competitions available. Please contact the administrator.")
        st.stop()
    
    # Input widgets for filtering
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_competition_name = st.selectbox(
            "Select Club Competition*",
            list(club_competition_map.keys()),
            help="Select the competition you are participating in"
        )
        
    with col2:
        rounds = score_tracking_utility.get_round_map_of_an_event('club competition', club_competition_map[selected_competition_name])
        selected_round_name = st.selectbox(
            "Select Round*",
            list(rounds.keys()) if rounds else ["No rounds available"],
            help="Select the round you want"
        )
    
    with col3:
        if selected_round_name and selected_round_name != "No rounds available":
            range_map = score_tracking_utility.get_range_map_of_an_event(club_competition_map[selected_competition_name], rounds[selected_round_name])
        else:
            range_map = {}
        selected_range_name = st.selectbox(
            "Select Range*",
            list(range_map.keys()) if range_map else ["No ranges available"],
            help="Select the range you want"
        )

    if (selected_competition_name and 
        selected_round_name and selected_round_name != "No rounds available" and
        selected_range_name and selected_range_name != "No ranges available"):
        # Get IDs from names
        club_competition_id = club_competition_map[selected_competition_name]
        round_id = rounds[selected_round_name]
        range_id = range_map[selected_range_name]
        participating_id = st.session_state['user_id']
        
        # Fetch scores
        scores = score_tracking_utility.get_archer_scores(participating_id, club_competition_id, round_id, range_id)
        
        if not scores and st.session_state.get('role') == 'recorder':
            st.info("the archer does not register for the selected round.")
        elif not scores and st.session_state.get('role') == 'archer':
            st.info("you do not register for this round.")
        else:            
            # Format data for display
            df = score_tracking_utility.format_participating_data_for_display(scores, include_archer_name=False)
            
            # Configure columns that can be edited (only if status is not "eligible")
            column_config = {
                'End Order': st.column_config.NumberColumn('End Order', disabled=True),
                'Arrow 1': st.column_config.NumberColumn('Arrow 1', min_value=0, max_value=10, step=1),
                'Arrow 2': st.column_config.NumberColumn('Arrow 2', min_value=0, max_value=10, step=1),
                'Arrow 3': st.column_config.NumberColumn('Arrow 3', min_value=0, max_value=10, step=1),
                'Arrow 4': st.column_config.NumberColumn('Arrow 4', min_value=0, max_value=10, step=1),
                'Arrow 5': st.column_config.NumberColumn('Arrow 5', min_value=0, max_value=10, step=1),
                'Arrow 6': st.column_config.NumberColumn('Arrow 6', min_value=0, max_value=10, step=1),
                'Total': st.column_config.NumberColumn('Total'),
                'Status': st.column_config.TextColumn('Status', disabled=True),
                '_participating_id': None,  # Hide
                '_event_context_id': None,  # Hide
                '_type': None  # Hide
            }
            
            # Display editable data editor
            st.info("ℹ️ You can only edit scores when the status is NOT 'eligible'. Once a recorder marks your score as 'eligible', it cannot be changed.")
            
            edited_df = st.data_editor(
                df,
                column_config=column_config,
                hide_index=True,
                use_container_width=True,
                disabled=['End Order', 'Status', '_participating_id', '_event_context_id', '_type'],
                key="archer_score_editor"
            )
            
            # Update button
            if st.button("Confirm Update", type="primary", use_container_width=True):
                # Check if any changes were made
                if edited_df.equals(df):
                    st.info("No changes detected.")
                else:
                    # Prepare updates - only for rows where status is not "eligible"
                    updates = []
                    for idx, row in edited_df.iterrows():
                        original_row = df.iloc[idx]
                        
                        # Check if status is "eligible" - if so, skip
                        if original_row['Status'] == 'eligible':
                            # Check if any score was changed
                            score_changed = (
                                row['Arrow 1'] != original_row['Arrow 1'] or
                                row['Arrow 2'] != original_row['Arrow 2'] or
                                row['Arrow 3'] != original_row['Arrow 3'] or
                                row['Arrow 4'] != original_row['Arrow 4'] or
                                row['Arrow 5'] != original_row['Arrow 5'] or
                                row['Arrow 6'] != original_row['Arrow 6']
                            )
                            if score_changed:
                                st.error(f"Cannot update End Order {row['End Order']} - status is 'eligible'")
                                st.stop()
                        else:
                            # Check if this row was modified
                            if not row.equals(original_row):
                                updates.append({
                                    'participating_id': row['_participating_id'],
                                    'event_context_id': row['_event_context_id'],
                                    'type': row['_type'],
                                    'score_1st_arrow': int(row['Arrow 1']),
                                    'score_2nd_arrow': int(row['Arrow 2']),
                                    'score_3rd_arrow': int(row['Arrow 3']),
                                    'score_4th_arrow': int(row['Arrow 4']),
                                    'score_5st_arrow': int(row['Arrow 5']),
                                    'score_6st_arrow': int(row['Arrow 6'])
                                })
                    
                    if updates:
                        if score_tracking_utility.update_participating_scores(updates):
                            st.success(f"Successfully updated {len(updates)} score record(s)!")
                            st.rerun()
                        else:
                            st.error("Failed to update scores. Please try again.")
                    else:
                        st.info("No valid changes to update.")
    else:
        st.info("Please select all filters (competition, round, and range) to view your scores.")

elif st.session_state['role'] == 'recorder':
    # Recorder view - single tab
    st.header("Score Tracking for Recorder")
    
    # Get available club competitions that this recorder is connected with
    club_competition_map = score_tracking_utility.get_club_competition_map_of_a_recorder(st.session_state['user_id'])
    
    if not club_competition_map:
        st.warning("No competitions available. Please write form to apply to record for competitions.")
        st.stop()
    
    # Input widgets for filtering
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_competition_name = st.selectbox(
            "Select Club Competition*",
            list(club_competition_map.keys()),
            help="Select the competition to view"
        )
    
    with col2:
        round_map = score_tracking_utility.get_round_map_of_an_event('club competition', club_competition_map[selected_competition_name])
        selected_round_name = st.selectbox(
            "Select Round",
            list(round_map.keys()) if round_map else ["No rounds available"]
        )
    
    with col3:
        if selected_round_name and selected_round_name != "No rounds available":
            range_map = score_tracking_utility.get_range_map_of_an_event(club_competition_map[selected_competition_name], round_map[selected_round_name])
        else:
            range_map = {}
        selected_range_name = st.selectbox(
            "Select Range",
            list(range_map.keys()) if range_map else ["No ranges available"]
        )
    
    with col4:
        participant_map = score_tracking_utility.get_participant_map_of_a_club_competition(club_competition_map[selected_competition_name])
        selected_archer_name = st.selectbox(
            "Select Participant",
            list(participant_map.keys()) if participant_map else ["No participants available"]
        )
    
    if (selected_competition_name and 
        selected_round_name and selected_round_name != "No rounds available" and
        selected_range_name and selected_range_name != "No ranges available" and
        selected_archer_name and selected_archer_name != "No participants available"):
        # Get IDs from names
        club_competition_id = club_competition_map[selected_competition_name]
        round_id = round_map[selected_round_name]
        range_id = range_map[selected_range_name]
        participating_id = participant_map[selected_archer_name]

        # Fetch scores
        scores = score_tracking_utility.get_recorder_scores(club_competition_id, round_id, range_id, participating_id)
        
        if not scores:
            st.info("No score records found for the selected filters.")
        else:
            st.success(f"Found {len(scores)} score record(s).")
            
            # Format data for display
            df = score_tracking_utility.format_participating_data_for_display(scores, include_archer_name=True)
            
            # Configure columns that can be edited
            column_config = {
                'Archer': st.column_config.TextColumn('Archer', disabled=True),
                'End Order': st.column_config.NumberColumn('End Order', disabled=True),
                'Arrow 1': st.column_config.NumberColumn('Arrow 1', min_value=0, max_value=10, step=1),
                'Arrow 2': st.column_config.NumberColumn('Arrow 2', min_value=0, max_value=10, step=1),
                'Arrow 3': st.column_config.NumberColumn('Arrow 3', min_value=0, max_value=10, step=1),
                'Arrow 4': st.column_config.NumberColumn('Arrow 4', min_value=0, max_value=10, step=1),
                'Arrow 5': st.column_config.NumberColumn('Arrow 5', min_value=0, max_value=10, step=1),
                'Arrow 6': st.column_config.NumberColumn('Arrow 6', min_value=0, max_value=10, step=1),
                'Total': st.column_config.NumberColumn('Total'),
                'Status': st.column_config.SelectboxColumn(
                    'Status',
                    options=['pending', 'in progress', 'eligible', 'ineligible']
                ),
                '_participating_id': None,  # Hide
                '_event_context_id': None,  # Hide
                '_type': None  # Hide
            }
            
            # Display editable data editor
            st.info("ℹ️ As a recorder, you can edit both scores and status fields for participants.")
            
            edited_df = st.data_editor(
                df,
                column_config=column_config,
                hide_index=True,
                use_container_width=True,
                disabled=['Archer', 'End Order', '_participating_id', '_event_context_id', '_type'],
                key="recorder_score_editor"
            )
            
            # Update button
            if st.button("Confirm Update", type="primary", use_container_width=True):
                # Check if any changes were made
                if edited_df.equals(df):
                    st.info("No changes detected.")
                else:
                    # Prepare updates
                    updates = []
                    for idx, row in edited_df.iterrows():
                        original_row = df.iloc[idx]
                        
                        # Check if this row was modified
                        if not row.equals(original_row):
                            updates.append({
                                'participating_id': row['_participating_id'],
                                'event_context_id': row['_event_context_id'],
                                'type': row['_type'],
                                'score_1st_arrow': int(row['Arrow 1']),
                                'score_2nd_arrow': int(row['Arrow 2']),
                                'score_3rd_arrow': int(row['Arrow 3']),
                                'score_4th_arrow': int(row['Arrow 4']),
                                'score_5st_arrow': int(row['Arrow 5']),
                                'score_6st_arrow': int(row['Arrow 6']),
                                'status': row['Status']
                            })
                    
                    if updates:
                        if score_tracking_utility.update_participating_scores(updates):
                            st.success(f"Successfully updated {len(updates)} score record(s)!")
                            st.rerun()
                        else:
                            st.error("Failed to update scores. Please try again.")
                    else:
                        st.info("No changes to update.")
    else:
        st.info("Please select all filters (competition, round, range, and participant) to view scores.")
