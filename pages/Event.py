import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.figure_factory as ff
from datetime import datetime, date
from utility_function.initilize_dbconnection import supabase
from utility_function.event_utility import (
    get_all_events, get_event_hierarchy, get_eligible_clubs,
    get_request_forms, update_form_status, get_round_schedule,
    create_yearly_championship, create_club_competition,
    get_available_rounds, get_available_ranges
)

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("Please log in to access this page.")
    st.stop()

st.title("📅 Event Management")
st.write(f"Welcome, {st.session_state.get('fullname')}!")

# Create tabs based on user role
user_role = st.session_state.get('role')

if user_role == 'recorder':
    tabs = st.tabs(["🔍 Browse Events", "📝 Event Enrollment/Withdraw", "📋 Review Forms", "📅 Event Schedule", "⚙️ Event Management"])
    tab_browse, tab_enroll, tab_review, tab_schedule, tab_manage = tabs
else:
    tabs = st.tabs(["🔍 Browse Events", "📝 Event Enrollment/Withdraw", "📅 Event Schedule"])
    tab_browse = tabs[0]
    tab_enroll = tabs[1]
    tab_schedule = tabs[2]

# Tab 1: Browse Events
with tab_browse:
    st.header("Browse Events")
    st.write("View and filter available competitions and championships")
    
    # Section 1: Filter and Display Events
    with st.expander("🔧 Configure Filters", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            event_type = st.selectbox("Event Type*", ["yearly club championship", "club competition"])
        
        with col2:
            date_start_filter = st.date_input("Start Date (From)", value=None)
            date_end_filter = st.date_input("End Date (To)", value=None)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # Get all categories for filter (category is a composite of discipline, age_division, equipment)
            categories_response = supabase.table("category").select("category_id, discipline_id, age_division_id, equipment_id").execute()
            category_options = {}
            if categories_response.data:
                for cat in categories_response.data:
                    # Create a display name from IDs for now
                    display_name = f"Category {cat['category_id']} (D:{cat['discipline_id']}, A:{cat['age_division_id']}, E:{cat['equipment_id']})"
                    category_options[display_name] = cat['category_id']
            category_filter = st.selectbox("Category (Optional)", ["All"] + list(category_options.keys()))
        
        with col4:
            # Get all eligible groups for filter
            eligible_groups_response = supabase.table("eligible_group_of_club").select("eligible_group_of_club_id").execute()
            eligible_group_options = {}
            if eligible_groups_response.data:
                for grp in eligible_groups_response.data:
                    # Display as "Group ID: X"
                    display_name = f"Group {grp['eligible_group_of_club_id']}"
                    eligible_group_options[display_name] = grp['eligible_group_of_club_id']
            club_eligibility_filter = st.selectbox("Club Eligibility (Optional)", ["All"] + list(eligible_group_options.keys()))
        
        apply_filter_btn = st.button("🔍 Apply Filters", type="primary", use_container_width=True)
    
    if apply_filter_btn or 'events_df' not in st.session_state:
        # Prepare filter parameters
        category_id = category_options[category_filter] if category_filter != "All" else None
        eligible_group_id = eligible_group_options[club_eligibility_filter] if club_eligibility_filter != "All" else None
        
        # Convert event type to table name
        event_type_db = event_type.replace(" ", "_")
        
        events_df = get_all_events(
            event_type=event_type_db,
            date_start=date_start_filter,
            date_end=date_end_filter,
            category_id=category_id,
            eligible_group_id=eligible_group_id
        )
        st.session_state.events_df = events_df
        st.session_state.current_event_type = event_type_db
    
    # Display events
    if 'events_df' in st.session_state and not st.session_state.events_df.empty:
        st.success(f"Found {len(st.session_state.events_df)} event(s)")
        st.dataframe(st.session_state.events_df, use_container_width=True, height=300)
    else:
        st.info("No events found with the current filters.")
    
    # Section 2: Event Hierarchy Visualization
    st.divider()
    st.subheader("📊 Event Hierarchy Visualization")
    st.write("Visualize the structure of an event (Competition → Round → Range → End)")
    
    # Show available IDs from the filtered events
    if 'events_df' in st.session_state and not st.session_state.events_df.empty:
        event_type_for_hierarchy = st.session_state.get('current_event_type', 'yearly_club_championship')
        if event_type_for_hierarchy == 'yearly_club_championship':
            available_ids = st.session_state.events_df['yearly_club_championship_id'].unique().tolist()
            st.info(f"💡 Available Championship IDs from filtered results: {', '.join(map(str, available_ids))}")
        else:
            available_ids = st.session_state.events_df['club_competition_id'].unique().tolist()
            st.info(f"💡 Available Competition IDs from filtered results: {', '.join(map(str, available_ids))}")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        hierarchy_event_id = st.text_input("Enter Event ID", placeholder="e.g., 1")
    
    with col2:
        hierarchy_event_type = st.selectbox("Event Type ", ["yearly_club_championship", "club_competition"], key="hierarchy_type")
    
    with col3:
        st.write("")  # Spacer
        st.write("")  # Spacer
        visualize_btn = st.button("🎨 Visualize", type="primary")
    
    if visualize_btn and hierarchy_event_id:
        with st.spinner("Loading hierarchy data..."):
            hierarchy_data = get_event_hierarchy(hierarchy_event_id, hierarchy_event_type)
        
        if hierarchy_data:
            # Prepare data for icicle chart
            ids = []
            labels = []
            parents = []
            
            # Root
            root_id = f"Event_{hierarchy_event_id}"
            ids.append(root_id)
            labels.append(f"Event {hierarchy_event_id}")
            parents.append("")
            
            # Build hierarchy
            for item in hierarchy_data:
                comp_id = f"Comp_{item['club_competition_id']}"
                round_id = f"Round_{item['round_id']}_Comp_{item['club_competition_id']}"
                range_id = f"Range_{item['range_id']}_Round_{item['round_id']}"
                end_id = f"End_{item['end_order']}_Range_{item['range_id']}_Round_{item['round_id']}"
                
                # Add competition if not already added
                if comp_id not in ids:
                    ids.append(comp_id)
                    labels.append(f"Competition {item['club_competition_id']}")
                    parents.append(root_id)
                
                # Add round if not already added
                if round_id not in ids:
                    ids.append(round_id)
                    labels.append(item['round_name'])
                    parents.append(comp_id)
                
                # Add range if not already added
                if range_id not in ids:
                    ids.append(range_id)
                    labels.append(f"Range: {item['range_distance']}m")
                    parents.append(round_id)
                
                # Add end
                if end_id not in ids:
                    ids.append(end_id)
                    labels.append(f"End {item['end_order']}")
                    parents.append(range_id)
            
            # Create icicle chart
            fig = go.Figure(go.Icicle(
                ids=ids,
                labels=labels,
                parents=parents,
                root_color="lightblue",
                tiling=dict(
                    orientation='h',
                    pad=0
                ),
                branchvalues="total"
            ))
            
            fig.update_layout(
                title=f'Event Hierarchy for {hierarchy_event_type.replace("_", " ").title()} {hierarchy_event_id}',
                margin=dict(t=80, l=25, r=25, b=25),
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"No hierarchy data found for this event.")
            st.info(f"🔍 Searched for: {hierarchy_event_type} with ID = {hierarchy_event_id}")
            st.info("💡 Tip: Make sure the Event ID exists and matches the selected Event Type. Check the filtered events table above for valid IDs.")
    
    # Section 3: Club Eligibility
    if 'events_df' in st.session_state and not st.session_state.events_df.empty:
        st.divider()
        st.subheader("🏆 Club Eligibility")
        
        selected_event_idx = st.selectbox(
            "Select an event to view eligible clubs",
            range(len(st.session_state.events_df)),
            format_func=lambda x: f"Event ID: {st.session_state.events_df.iloc[x].get('yearly_club_championship_id') or st.session_state.events_df.iloc[x].get('club_competition_id')}"
        )
        
        if selected_event_idx is not None:
            selected_event = st.session_state.events_df.iloc[selected_event_idx]
            eligible_group_id = selected_event.get('eligible_group_of_club_id')
            
            eligible_clubs = get_eligible_clubs(eligible_group_id)
            
            if eligible_clubs == "All clubs are eligible":
                st.success("✅ " + eligible_clubs)
            elif eligible_clubs:
                st.write("**Eligible Clubs:**")
                for club in eligible_clubs:
                    st.write(f"- {club}")
            else:
                st.info("No specific club eligibility restrictions.")

# Tab 2: Event Enrollment/Withdraw
with tab_enroll:
    st.header("Event Enrollment / Withdraw")
    
    # Tab 2.1: Submit Form
    st.subheader("📝 Submit Request Form")
    
    with st.form("event_request_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Restrict form type based on user role
            if user_role == 'archer':
                form_type = st.selectbox("Request Type*", ["", "participating"], 
                                        help="Archers can only apply to participate as competitors")
            elif user_role == 'recorder':
                form_type = st.selectbox("Request Type*", ["", "recording"],
                                        help="Recorders can only apply to record events")
            else:
                # For other roles (admin, federation) - allow both
                form_type = st.selectbox("Request Type*", ["", "participating", "recording"])
            
            form_action = st.selectbox("Action*", ["", "enrol", "withdraw"])
        
        with col2:
            yearly_championship_id = st.text_input("Yearly Championship ID (Optional)", placeholder="Leave empty if not applicable")
            club_competition_id = st.text_input("Club Competition ID", placeholder="Required for specific competitions")
        
        if form_type == "participating":
            round_id = st.text_input("Round ID*", placeholder="Required for participating")
        else:
            round_id = None
        
        reason_message = st.text_area("Message / Reason", placeholder="Provide additional information...")
        
        submit_form_btn = st.form_submit_button("📤 Submit Request", type="primary")
        
        if submit_form_btn:
            if not form_type or not form_action or not club_competition_id:
                st.error("Please fill in all required fields!")
            elif form_type == "participating" and not round_id:
                st.error("Round ID is required for participating requests!")
            elif not reason_message or reason_message.strip() == "":
                st.error("Please provide a message/reason for your request!")
            else:
                try:
                    insert_data = {
                        "sender_id": st.session_state.user_id,
                        "sender_word": reason_message.strip(),
                        "type": form_type,
                        "action": form_action,
                        "club_competition_id": int(club_competition_id) if club_competition_id else None,
                        "yearly_club_championship_id": int(yearly_championship_id) if yearly_championship_id else None,
                        "status": "pending",
                        "reviewer_word": "Pending review",
                        "reviewed_by": 0  # Placeholder, will be updated when reviewed
                    }
                    
                    if round_id:
                        insert_data["round_id"] = int(round_id)
                    
                    response = supabase.table("request_competition_form").insert(insert_data).execute()
                    
                    if response.data:
                        st.success("✅ Request submitted successfully!")
                        st.balloons()
                    else:
                        st.error("Failed to submit request. Please try again.")
                except Exception as e:
                    error_msg = str(e)
                    if "duplicate key value violates unique constraint" in error_msg and "form_id" in error_msg:
                        st.error("⚠️ Database sequence error detected. Please contact an administrator to reset the sequence.")
                        st.info("Technical details: The auto-increment sequence is out of sync with the database.")
                    else:
                        st.error(f"Error submitting request: {error_msg}")
    
    # Tab 2.2: View My Forms
    st.divider()
    st.subheader("📋 My Request Forms")
    
    user_forms = get_request_forms(user_id=st.session_state.user_id, is_creator=False)
    
    if not user_forms.empty:
        st.dataframe(user_forms, use_container_width=True)
    else:
        st.info("You haven't submitted any request forms yet.")

# Tab 3: Event Schedule
with tab_schedule:
    st.header("📅 Event Schedule")
    st.write("View round schedules in Gantt chart format")
    
    competition_id_input = st.text_input("Enter Club Competition ID", placeholder="e.g., 1")
    
    if st.button("🔍 View Schedule", type="primary"):
        if competition_id_input:
            schedule_df = get_round_schedule(competition_id_input)
            
            if not schedule_df.empty:
                # Prepare data for Gantt chart
                gantt_data = []
                for _, row in schedule_df.iterrows():
                    gantt_data.append({
                        'Task': row.get('round_name', f"Round {row['round_id']}"),
                        'Start': row['datetime_to_start'],
                        'Finish': row['expected_datetime_to_end'],
                        'Resource': f"Competition {competition_id_input}"
                    })
                
                if gantt_data:
                    # Create Gantt chart
                    fig = ff.create_gantt(
                        gantt_data,
                        colors={'Resource': 'rgb(46, 137, 205)'},
                        index_col='Resource',
                        show_colorbar=True,
                        group_tasks=True,
                        showgrid_x=True,
                        showgrid_y=True,
                        title=f'Round Schedule for Competition {competition_id_input}'
                    )
                    
                    # Add "Today" line
                    today = datetime.now()
                    fig.add_shape(
                        type="line",
                        x0=today,
                        x1=today,
                        y0=0,
                        y1=1,
                        yref="paper",
                        line=dict(color="red", width=2, dash="dash")
                    )
                    
                    fig.add_annotation(
                        x=today,
                        y=1,
                        yref="paper",
                        text="Today",
                        showarrow=False,
                        yshift=10,
                        font=dict(color="red", size=12)
                    )
                    
                    fig.update_layout(
                        xaxis_title='Date',
                        yaxis_title='Rounds',
                        height=500,
                        xaxis=dict(type='date', tickformat='%Y-%m-%d')
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No schedule data available for visualization.")
            else:
                st.warning("No schedule found for this competition.")
        else:
            st.error("Please enter a competition ID.")

# Recorder-only tabs
if user_role == 'recorder':
    # Tab 4: Review Forms (Recorder only)
    with tab_review:
        st.header("📋 Review Request Forms")
        st.write("Review and approve/reject forms for events you created")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox("Status", ["all", "pending", "eligible", "ineligible"])
        
        with col2:
            type_filter = st.selectbox("Type", ["all", "participating", "recording"])
        
        with col3:
            action_filter = st.selectbox("Action", ["all", "enrol", "withdraw"])
        
        if st.button("🔍 Load Forms", type="primary"):
            forms_df = get_request_forms(
                status_filter=status_filter,
                type_filter=type_filter,
                action_filter=action_filter,
                user_id=st.session_state.user_id,
                is_creator=True
            )
            st.session_state.forms_df = forms_df
        
        # Display and edit forms
        if 'forms_df' in st.session_state and not st.session_state.forms_df.empty:
            st.write(f"Found {len(st.session_state.forms_df)} form(s)")
            
            edited_df = st.data_editor(
                st.session_state.forms_df,
                column_config={
                    "status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["pending", "eligible", "ineligible"],
                        required=True
                    )
                },
                disabled=["form_id", "sender_id", "type", "action"],
                use_container_width=True,
                key="forms_editor"
            )
            
            if st.button("💾 Save Changes", type="primary"):
                # Compare and update changed rows
                for idx in range(len(st.session_state.forms_df)):
                    original_status = st.session_state.forms_df.iloc[idx]['status']
                    new_status = edited_df.iloc[idx]['status']
                    
                    if original_status != new_status:
                        form_id = edited_df.iloc[idx]['form_id']
                        success = update_form_status(form_id, new_status)
                        
                        if success:
                            st.success(f"Updated form {form_id} to {new_status}")
                        else:
                            st.error(f"Failed to update form {form_id}")
                
                st.rerun()
        else:
            st.info("No forms found with the current filters.")
    
    # Tab 5: Event Management (Recorder only)
    with tab_manage:
        st.header("⚙️ Event Management")
        st.write("Create and manage events")
        
        management_tab1, management_tab2 = st.tabs(["➕ Create Event", "✏️ Modify Event"])
        
        with management_tab1:
            st.subheader("Create New Event")
            
            event_creation_type = st.radio("What would you like to create?", 
                                         ["Yearly Club Championship", "Club Competition"])
            
            if event_creation_type == "Yearly Club Championship":
                with st.form("create_championship"):
                    st.write("**Yearly Club Championship Details**")
                    
                    championship_name = st.text_input("Championship Name*")
                    year = st.number_input("Year*", min_value=2020, max_value=2100, value=datetime.now().year)
                    eligible_group_id = st.text_input("Eligible Group ID (Optional)", 
                                                     help="Leave empty if all clubs are eligible")
                    
                    submit_championship = st.form_submit_button("🏆 Create Championship", type="primary")
                    
                    if submit_championship:
                        if not championship_name:
                            st.error("Championship name is required!")
                        else:
                            result = create_yearly_championship(
                                creator_id=st.session_state.user_id,
                                year=year,
                                championship_name=championship_name,
                                eligible_group_id=int(eligible_group_id) if eligible_group_id else None
                            )
                            
                            if result:
                                st.success(f"✅ Championship created successfully! ID: {result['yearly_club_championship_id']}")
                                st.balloons()
                            else:
                                st.error("Failed to create championship.")
            
            else:  # Club Competition
                with st.form("create_competition"):
                    st.write("**Club Competition Details**")
                    
                    competition_name = st.text_input("Competition Name*")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        date_start = st.date_input("Start Date*", value=date.today())
                    with col2:
                        date_end = st.date_input("End Date*", value=date.today())
                    
                    eligible_group_id = st.text_input("Eligible Group ID (Optional)",
                                                     help="Leave empty if all clubs are eligible")
                    
                    submit_competition = st.form_submit_button("🎯 Create Competition", type="primary")
                    
                    if submit_competition:
                        if not competition_name:
                            st.error("Competition name is required!")
                        elif date_end < date_start:
                            st.error("End date must be after start date!")
                        else:
                            result = create_club_competition(
                                creator_id=st.session_state.user_id,
                                competition_name=competition_name,
                                date_start=date_start.isoformat(),
                                date_end=date_end.isoformat(),
                                eligible_group_id=int(eligible_group_id) if eligible_group_id else None
                            )
                            
                            if result:
                                st.success(f"✅ Competition created successfully! ID: {result['club_competition_id']}")
                                st.balloons()
                            else:
                                st.error("Failed to create competition.")
        
        with management_tab2:
            st.subheader("Modify Existing Event")
            st.info("⚠️ You can only edit events where the start date has not passed.")
            st.write("This feature allows you to modify event details, add/remove rounds, ranges, and ends.")
            st.write("**Coming soon:** Full event modification interface")
