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
    get_available_rounds, create_complete_event,
    get_all_clubs, create_eligible_group_with_clubs,
    get_eligible_group_details, get_all_eligible_groups
)
import utility_function.event_utility as event_utility

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("Please log in to access this page.")
    st.stop()

st.title("📅 Event Management")
st.write(f"Welcome, {st.session_state.get('fullname')}!")

# Create tabs based on user role
user_role = st.session_state.get('role')

if user_role == 'recorder':
    tabs = st.tabs(["🔍 Browse Events", "📝 Event Enrollment/Withdraw", "📋 Review Forms", "📅 Event Schedule", "🏢 Club Groups", "⚙️ Event Management"])
    tab_browse, tab_enroll, tab_review, tab_schedule, tab_club_groups, tab_manage = tabs
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
    #note
    st.warning("""⚠️ **Instruction:** If you fill in an id for a yearly club championship, leave club competition id empty. 
    You can only fill in club competition id that does not belong to any yearly championship and still skip yearly championship id.
    Then if you are recorders, you do not need to fill in round id, as you will be responsible for the whole club competition if the club competition does not belong to any yearly championship; in that case, leave the yearly club championship id empty and fill in the club competition id. If the club competition belongs to a yearly championship, then you are responsible for all club competitions that make up the yearly club championship, so there is no need to fill in club competition id — the yearly club championship id is sufficient.
    If you are archers, you must fill in round id, as you are only participating in a specific round as competitors. If you choose to participate in a round in a club competition that does not belong to any yearly championship, you must fill in the club competition id and round id only. If you want to participate in a round in a club competition that belongs to a yearly championship, you only need to fill in the yearly club championship id and round id as you must participate in the same round in all club competitions that make up the yearly club championship; doing so makes calculating scores easier.""")
    
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
            apply_for_option = st.radio("Apply For*", ["Yearly Championship", "Club Competition"])
            if apply_for_option == "Yearly Championship":
                yearly_championship_id = st.text_input("Yearly Championship ID*", placeholder="Enter Yearly Championship ID")
                club_competition_id = ""
            else:
                club_competition_id = st.text_input("Club Competition ID*", placeholder="Enter Club Competition ID")
                yearly_championship_id = ""

        
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
                    st.error(f"Error submitting request: {str(e)}")
    
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
    
    # Tab 5: Club Groups Management (Recorder only)
    with tab_club_groups:
        st.header("🏢 Eligible Club Groups Management")
        st.write("Create and manage groups of clubs that can participate in events")
        
        club_groups_tab1, club_groups_tab2 = st.tabs(["➕ Create Club Group", "📋 View Existing Groups"])
        
        with club_groups_tab1:
            st.subheader("Create New Eligible Club Group")
            st.info("💡 Create a group of clubs that will be eligible to participate in specific events. Leave empty to allow all clubs.")
            
            # Get all available clubs
            all_clubs = get_all_clubs()
            
            if all_clubs:
                st.write(f"**Available Clubs:** {len(all_clubs)} clubs in database")
                
                # Create a multiselect for clubs
                club_options = {f"{club['name']} (ID: {club['club_id']})": club['club_id'] 
                              for club in all_clubs}
                
                selected_clubs = st.multiselect(
                    "Select Clubs for This Group*",
                    options=list(club_options.keys()),
                    help="Select one or more clubs to include in this eligible group"
                )
                
                if selected_clubs:
                    st.write(f"**Selected:** {len(selected_clubs)} club(s)")
                    
                    # Show preview
                    with st.expander("📋 Preview Selected Clubs"):
                        for club_name in selected_clubs:
                            st.write(f"- {club_name}")
                    
                    if st.button("✅ Create Eligible Group", type="primary", use_container_width=True):
                        with st.spinner("Creating eligible club group..."):
                            # Get club IDs from selected names
                            selected_club_ids = [club_options[club_name] for club_name in selected_clubs]
                            
                            # Create the group
                            group_id = create_eligible_group_with_clubs(selected_club_ids)
                            
                            if group_id:
                                st.success(f"✅ Successfully created Eligible Group with ID: {group_id}")
                                st.balloons()
                                st.info(f"💡 You can now use Group ID **{group_id}** when creating events to restrict participation to these clubs.")
                            else:
                                st.error("❌ Failed to create eligible group. Please try again.")
                else:
                    st.warning("⚠️ Please select at least one club to create a group.")
            else:
                st.warning("No clubs found in the database. Clubs must be created first before creating eligible groups.")
        
        with club_groups_tab2:
            st.subheader("Existing Eligible Club Groups")
            
            if st.button("🔄 Refresh Groups", type="secondary"):
                st.rerun()
            
            # Get all eligible groups
            with st.spinner("Loading eligible groups..."):
                all_groups = get_all_eligible_groups()
            
            if all_groups:
                st.success(f"Found {len(all_groups)} eligible group(s)")
                
                # Display each group
                for group in all_groups:
                    with st.expander(f"🏢 Group ID: {group['eligible_group_id']} ({len(group['clubs'])} clubs)", expanded=False):
                        st.write(f"**Group ID:** {group['eligible_group_id']}")
                        st.write(f"**Number of Clubs:** {len(group['clubs'])}")
                        
                        if group['clubs']:
                            st.write("**Member Clubs:**")
                            
                            # Create a dataframe for better display
                            clubs_df = pd.DataFrame(group['clubs'])
                            st.dataframe(clubs_df, use_container_width=True, hide_index=True)
                        else:
                            st.info("This group has no member clubs.")
                        
                        # Show usage information
                        st.divider()
                        st.write("**💡 Usage:** Use this Group ID when creating events to restrict participation to these clubs only.")
            else:
                st.info("No eligible club groups exist yet. Create one using the 'Create Club Group' tab.")
    
    # Tab 6: Event Management (Recorder only)
    with tab_manage:
        st.header("⚙️ Event Management")
        st.write("Create and manage events")
        
        management_tab1, management_tab2 = st.tabs(["➕ Create Event", "✏️ Modify Event"])
        
        with management_tab1:
            st.subheader("Create New Event")
            st.info("📋 This wizard will guide you through creating a complete event with all its components")
            
            # Initialize event builder state
            if 'event_builder_step' not in st.session_state:
                st.session_state.event_builder_step = 1
                st.session_state.event_builder_data = {}
            
            # Step indicator
            steps = ["Event Type", "Basic Info", "Competitions", "Rounds", "Ranges & Ends", "Review & Create"]
            current_step = st.session_state.event_builder_step
            
            # Progress bar
            st.progress(current_step / len(steps))
            st.write(f"**Step {current_step}/{len(steps)}:** {steps[current_step - 1]}")
            
            # STEP 1: Choose Event Type
            if current_step == 1:
                event_type = st.radio("What would you like to create?*", 
                                     ["Yearly Club Championship", "Club Competition"],
                                     key="event_type_selection")
                
                col1, col2 = st.columns([1, 1])
                with col2:
                    if st.button("Next ➡️", type="primary", use_container_width=True):
                        st.session_state.event_builder_data['event_type'] = event_type
                        st.session_state.event_builder_step = 2
                        st.rerun()
            
            # STEP 2: Basic Information
            elif current_step == 2:
                event_type = st.session_state.event_builder_data.get('event_type')
                st.write(f"**Creating:** {event_type}")
                
                if event_type == "Yearly Club Championship":
                    championship_name = st.text_input("Championship Name*", 
                                                     value=st.session_state.event_builder_data.get('name', ''))
                    year = st.number_input("Year*", min_value=2020, max_value=2100, 
                                          value=st.session_state.event_builder_data.get('year', datetime.now().year))
                    
                    # Eligible Group Selection with better UI
                    st.write("**Club Eligibility**")
                    all_groups = get_all_eligible_groups()
                    
                    if all_groups:
                        group_options = {f"All Clubs (No Restriction)": None}
                        for group in all_groups:
                            group_label = f"Group {group['eligible_group_id']} ({len(group['clubs'])} clubs)"
                            group_options[group_label] = group['eligible_group_id']
                        
                        # Find current selection
                        current_group_id = st.session_state.event_builder_data.get('eligible_group_id')
                        current_index = 0
                        if current_group_id:
                            for idx, (label, gid) in enumerate(group_options.items()):
                                if gid == current_group_id:
                                    current_index = idx
                                    break
                        
                        selected_group_label = st.selectbox(
                            "Select Eligible Club Group",
                            options=list(group_options.keys()),
                            index=current_index,
                            help="Choose which clubs can participate. Select 'All Clubs' for no restrictions."
                        )
                        
                        eligible_group_id = group_options[selected_group_label]
                        
                        # Show preview of selected group
                        if eligible_group_id:
                            group_details = get_eligible_group_details(eligible_group_id)
                            if group_details and group_details['clubs']:
                                with st.expander(f"📋 Preview: {len(group_details['clubs'])} eligible clubs"):
                                    for club in group_details['clubs']:
                                        st.write(f"- {club['name']}")
                    else:
                        st.info("ℹ️ No eligible club groups exist. All clubs will be able to participate.")
                        eligible_group_id = None
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("⬅️ Back"):
                            st.session_state.event_builder_step = 1
                            st.rerun()
                    with col2:
                        if st.button("Next ➡️", type="primary", use_container_width=True):
                            if not championship_name:
                                st.error("Championship name is required!")
                            else:
                                st.session_state.event_builder_data['name'] = championship_name
                                st.session_state.event_builder_data['year'] = year
                                st.session_state.event_builder_data['eligible_group_id'] = eligible_group_id if eligible_group_id else None
                                st.session_state.event_builder_step = 3
                                st.rerun()
                
                else:  # Club Competition
                    competition_name = st.text_input("Competition Name*",
                                                    value=st.session_state.event_builder_data.get('name', ''))
                    address = st.text_input("Address*", 
                                          value=st.session_state.event_builder_data.get('address', ''),
                                          placeholder="e.g., 123 Archery Lane, Sydney NSW 2000")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        date_start = st.date_input("Start Date*", 
                                                  value=st.session_state.event_builder_data.get('date_start', date.today()))
                    with col2:
                        date_end = st.date_input("End Date*",
                                                value=st.session_state.event_builder_data.get('date_end', date.today()))
                    
                    # Eligible Group Selection with better UI
                    st.write("**Club Eligibility**")
                    all_groups = get_all_eligible_groups()
                    
                    if all_groups:
                        group_options = {f"All Clubs (No Restriction)": None}
                        for group in all_groups:
                            group_label = f"Group {group['eligible_group_id']} ({len(group['clubs'])} clubs)"
                            group_options[group_label] = group['eligible_group_id']
                        
                        # Find current selection
                        current_group_id = st.session_state.event_builder_data.get('eligible_group_id')
                        current_index = 0
                        if current_group_id:
                            for idx, (label, gid) in enumerate(group_options.items()):
                                if gid == current_group_id:
                                    current_index = idx
                                    break
                        
                        selected_group_label = st.selectbox(
                            "Select Eligible Club Group",
                            options=list(group_options.keys()),
                            index=current_index,
                            help="Choose which clubs can participate. Select 'All Clubs' for no restrictions."
                        )
                        
                        eligible_group_id = group_options[selected_group_label]
                        
                        # Show preview of selected group
                        if eligible_group_id:
                            group_details = get_eligible_group_details(eligible_group_id)
                            if group_details and group_details['clubs']:
                                with st.expander(f"📋 Preview: {len(group_details['clubs'])} eligible clubs"):
                                    for club in group_details['clubs']:
                                        st.write(f"- {club['name']}")
                    else:
                        st.info("ℹ️ No eligible club groups exist. All clubs will be able to participate.")
                        eligible_group_id = None
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("⬅️ Back"):
                            st.session_state.event_builder_step = 1
                            st.rerun()
                    with col2:
                        if st.button("Next ➡️", type="primary", use_container_width=True):
                            if not competition_name or not address:
                                st.error("Competition name and address are required!")
                            elif date_end < date_start:
                                st.error("End date must be after start date!")
                            else:
                                st.session_state.event_builder_data['name'] = competition_name
                                st.session_state.event_builder_data['address'] = address
                                st.session_state.event_builder_data['date_start'] = date_start
                                st.session_state.event_builder_data['date_end'] = date_end
                                st.session_state.event_builder_data['eligible_group_id'] = eligible_group_id if eligible_group_id else None
                                st.session_state.event_builder_step = 3
                                st.rerun()
            
            # STEP 3: Add Competitions (only for Championships)
            elif current_step == 3:
                event_type = st.session_state.event_builder_data.get('event_type')
                
                if event_type == "Yearly Club Championship":
                    st.write("**Add Club Competitions to Championship**")
                    st.info("ℹ️ All competitions must have the same rounds and participants for consistency")
                    
                    # Initialize competitions list
                    if 'competitions' not in st.session_state.event_builder_data:
                        st.session_state.event_builder_data['competitions'] = []
                    
                    # Display existing competitions
                    if st.session_state.event_builder_data['competitions']:
                        st.write(f"**Added Competitions ({len(st.session_state.event_builder_data['competitions'])}):**")
                        for idx, comp in enumerate(st.session_state.event_builder_data['competitions']):
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.write(f"{idx + 1}. {comp['name']} - {comp['address']}")
                            with col2:
                                if st.button("🗑️", key=f"del_comp_{idx}"):
                                    st.session_state.event_builder_data['competitions'].pop(idx)
                                    st.rerun()
                    
                    # Add new competition
                    with st.expander("➕ Add New Competition", expanded=True):
                        comp_name = st.text_input("Competition Name*", key="new_comp_name")
                        comp_address = st.text_input("Address*", key="new_comp_address")
                        col1, col2 = st.columns(2)
                        with col1:
                            comp_start = st.date_input("Start Date*", value=date.today(), key="new_comp_start")
                        with col2:
                            comp_end = st.date_input("End Date*", value=date.today(), key="new_comp_end")
                        
                        if st.button("➕ Add Competition"):
                            if comp_name and comp_address:
                                st.session_state.event_builder_data['competitions'].append({
                                    'name': comp_name,
                                    'address': comp_address,
                                    'date_start': comp_start,
                                    'date_end': comp_end
                                })
                                st.success(f"Added {comp_name}")
                                st.rerun()
                            else:
                                st.error("Please fill all fields!")
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("⬅️ Back"):
                            st.session_state.event_builder_step = 2
                            st.rerun()
                    with col2:
                        if st.button("Next ➡️", type="primary", use_container_width=True):
                            if not st.session_state.event_builder_data['competitions']:
                                st.error("Please add at least one competition!")
                            else:
                                st.session_state.event_builder_step = 4
                                st.rerun()
                else:
                    # Skip to next step for standalone competitions
                    st.session_state.event_builder_step = 4
                    st.rerun()
            
            # STEP 4: Add Rounds
            elif current_step == 4:
                st.write("**Add Rounds**")
                st.info("ℹ️ Select existing rounds from the database")
                
                # Get available rounds
                rounds_response = supabase.table("round").select("round_id, name, category_id").execute()
                
                if 'rounds' not in st.session_state.event_builder_data:
                    st.session_state.event_builder_data['rounds'] = []
                
                # Display added rounds
                if st.session_state.event_builder_data['rounds']:
                    st.write(f"**Selected Rounds ({len(st.session_state.event_builder_data['rounds'])}):**")
                    for idx, round_id in enumerate(st.session_state.event_builder_data['rounds']):
                        round_info = next((r for r in rounds_response.data if r['round_id'] == round_id), None)
                        if round_info:
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.write(f"{idx + 1}. {round_info['name']} (ID: {round_id})")
                            with col2:
                                if st.button("🗑️", key=f"del_round_{idx}"):
                                    st.session_state.event_builder_data['rounds'].pop(idx)
                                    st.rerun()
                
                # Add round selector
                if rounds_response.data:
                    round_options = {f"{r['name']} (ID: {r['round_id']})": r['round_id'] for r in rounds_response.data}
                    selected_round = st.selectbox("Select Round to Add", [""] + list(round_options.keys()))
                    
                    if st.button("➕ Add Round") and selected_round:
                        round_id = round_options[selected_round]
                        if round_id not in st.session_state.event_builder_data['rounds']:
                            st.session_state.event_builder_data['rounds'].append(round_id)
                            st.success(f"Added {selected_round}")
                            st.rerun()
                        else:
                            st.warning("Round already added!")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("⬅️ Back"):
                        st.session_state.event_builder_step = 3 if st.session_state.event_builder_data.get('event_type') == "Yearly Club Championship" else 2
                        st.rerun()
                with col2:
                    if st.button("Next ➡️", type="primary", use_container_width=True):
                        if not st.session_state.event_builder_data['rounds']:
                            st.error("Please add at least one round!")
                        else:
                            st.session_state.event_builder_step = 5
                            st.rerun()
            
            # STEP 5: Add Ranges and Ends
            elif current_step == 5:
                st.write("**Configure Ranges and Ends**")
                st.info("ℹ️ For each round, specify ranges and number of ends per range")
                
                # Initialize ranges_config
                if 'ranges_config' not in st.session_state.event_builder_data:
                    st.session_state.event_builder_data['ranges_config'] = {}
                
                # Get available ranges
                ranges_response = supabase.table("range").select("*").execute()
                rounds_response = supabase.table("round").select("*").execute()
                
                for round_id in st.session_state.event_builder_data['rounds']:
                    round_info = next((r for r in rounds_response.data if r['round_id'] == round_id), None)
                    round_name = round_info['name'] if round_info else f"Round {round_id}"
                    
                    with st.expander(f"🎯 {round_name}", expanded=True):
                        if round_id not in st.session_state.event_builder_data['ranges_config']:
                            st.session_state.event_builder_data['ranges_config'][round_id] = []
                        
                        # Display configured ranges
                        if st.session_state.event_builder_data['ranges_config'][round_id]:
                            for idx, range_config in enumerate(st.session_state.event_builder_data['ranges_config'][round_id]):
                                col1, col2, col3 = st.columns([2, 2, 1])
                                with col1:
                                    st.write(f"Range ID: {range_config['range_id']}")
                                with col2:
                                    st.write(f"Number of Ends: {range_config['num_ends']}")
                                with col3:
                                    if st.button("🗑️", key=f"del_range_{round_id}_{idx}"):
                                        st.session_state.event_builder_data['ranges_config'][round_id].pop(idx)
                                        st.rerun()
                        
                        # Add new range
                        col1, col2, col3 = st.columns([2, 2, 1])
                        with col1:
                            if ranges_response.data:
                                range_options = {f"Range {r['range_id']} ({r['distance']}{r['unit_of_length']})": r['range_id'] 
                                               for r in ranges_response.data}
                                selected_range = st.selectbox("Select Range", [""] + list(range_options.keys()), 
                                                            key=f"range_select_{round_id}")
                        with col2:
                            num_ends = st.number_input("Number of Ends*", min_value=1, max_value=20, value=6,
                                                      key=f"num_ends_{round_id}")
                        with col3:
                            st.write("")
                            st.write("")
                            if st.button("➕", key=f"add_range_{round_id}") and selected_range:
                                range_id = range_options[selected_range]
                                st.session_state.event_builder_data['ranges_config'][round_id].append({
                                    'range_id': range_id,
                                    'num_ends': num_ends
                                })
                                st.rerun()
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("⬅️ Back"):
                        st.session_state.event_builder_step = 4
                        st.rerun()
                with col2:
                    if st.button("Next ➡️", type="primary", use_container_width=True):
                        # Validate all rounds have ranges configured
                        all_configured = all(st.session_state.event_builder_data['ranges_config'].get(r_id, []) 
                                           for r_id in st.session_state.event_builder_data['rounds'])
                        if not all_configured:
                            st.error("Please configure ranges for all rounds!")
                        else:
                            st.session_state.event_builder_step = 6
                            st.rerun()
            
            # STEP 6: Review and Create
            elif current_step == 6:
                st.write("**📋 Review Your Event Configuration**")
                
                data = st.session_state.event_builder_data
                
                st.write(f"**Event Type:** {data['event_type']}")
                st.write(f"**Name:** {data['name']}")
                
                if data['event_type'] == "Yearly Club Championship":
                    st.write(f"**Year:** {data['year']}")
                    st.write(f"**Competitions:** {len(data['competitions'])}")
                    for comp in data['competitions']:
                        st.write(f"  - {comp['name']}")
                else:
                    st.write(f"**Address:** {data['address']}")
                    st.write(f"**Dates:** {data['date_start']} to {data['date_end']}")
                
                st.write(f"**Rounds:** {len(data['rounds'])}")
                st.write(f"**Total Range Configurations:** {sum(len(ranges) for ranges in data['ranges_config'].values())}")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("⬅️ Back"):
                        st.session_state.event_builder_step = 5
                        st.rerun()
                with col2:
                    if st.button("🔄 Start Over", type="secondary", use_container_width=True):
                        st.session_state.event_builder_step = 1
                        st.session_state.event_builder_data = {}
                        st.rerun()
                with col3:
                    if st.button("✅ Create Event", type="primary", use_container_width=True):
                        with st.spinner("Creating event with all components..."):
                            # Call the complete event creation function
                            result = event_utility.create_complete_event(
                                creator_id=st.session_state.user_id,
                                event_data=st.session_state.event_builder_data
                            )
                            
                            if result['success']:
                                st.success(f"✅ {result['message']}")
                                st.balloons()
                                
                                # Show created IDs
                                st.write("**Created IDs:**")
                                if result['created_ids']['championship_id']:
                                    st.write(f"- Championship ID: {result['created_ids']['championship_id']}")
                                st.write(f"- Competition IDs: {', '.join(map(str, result['created_ids']['competition_ids']))}")
                                st.write(f"- Event Context Records: {len(result['created_ids']['event_context_ids'])}")
                                
                                # Reset wizard after success
                                st.info("Event created successfully! Resetting wizard...")
                                st.session_state.event_builder_step = 1
                                st.session_state.event_builder_data = {}
                                
                                # Wait a moment then refresh
                                import time
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                                st.write("Please try again or contact an administrator.")
        
        with management_tab2:
            st.subheader("Modify Existing Event")
            st.info("⚠️ You can only edit events where the start date has not passed.")
            st.write("This feature allows you to modify event details, add/remove rounds, ranges, and ends.")
            st.write("**Coming soon:** Full event modification interface")
