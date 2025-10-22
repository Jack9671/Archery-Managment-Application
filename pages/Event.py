import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.express as px
from datetime import datetime, date
from utility_function.initilize_dbconnection import supabase
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
        event_type = st.selectbox("Event Type", ["yearly club championship", "club competition"])
        
        # Initialize all variables at outer scope
        category_id = None
        year = None
        eligible_group_id = None
        list_of_club_name = []
        date_start = None
        date_end = None
        club_option = None
        
        if event_type == "yearly club championship":
            year = st.number_input("Year", value=date.today().year)
            category_map = event_utility.get_category_map()
            category_name = st.selectbox("Category", ["All"] + list(category_map.keys()))
            if category_name != "All":
                category_id = category_map[category_name]
            club_map = event_utility.get_club_map()
            club_option = st.radio("Choose Club Filter Method", ["All Clubs", "Select Clubs"])
            if club_option != "All Clubs":
                list_of_club_name = st.multiselect(
                    "Interested Club*", 
                    options=list(club_map.keys()),
                    help="⚠️ You must select at least one club"
                ) # select a group of clubs, this var is used to find eligible groups of clubs later
                if list_of_club_name:
                    list_of_club_id = [club_map[name] for name in list_of_club_name]
                    # Find eligible group ids that match the selected club ids
                    list_of_eligible_group_id = event_utility.get_list_of_eligible_group_id_from_a_set_of_club_id(set(list_of_club_id))
                    
                    if list_of_eligible_group_id:  # Check if list is not empty
                        #given an eligible_group_of_club_id, display list of name of club where club_id is in eligible_club_member of that eligible_group_of_club_id. Repeat for all eligible_group_of_club_id in list_of_eligible_group_id
                        list_of_eligible_club_names = {}
                        for group_id in list_of_eligible_group_id:
                            club_names = event_utility.get_list_of_member_club_name_from_eligible_group_of_club_id(group_id)
                            list_of_eligible_club_names[group_id] = club_names
                        # Display info
                        info_str = "💡 Those are id of eligible groups that include the clubs you selected, please pick one group id:\n"
                        for group_id, club_names in list_of_eligible_club_names.items():
                            info_str += f" - Group ID {group_id} : {', '.join(club_names)}\n"
                        st.info(info_str)
                        # then let user select one of the eligible_group_of_club_id from the list
                        eligible_group_id = int(st.selectbox("Eligible Group ID", [str(gid) for gid in list_of_eligible_group_id]))
                    else:
                        st.warning("⚠️ No eligible groups found for the selected clubs.")
                        eligible_group_id = None
                else:
                    # User selected "Select Clubs" but hasn't chosen any clubs yet
                    eligible_group_id = None
            else:
                list_of_eligible_group_id = None
                eligible_group_id = None # None means all eligible groups
        elif event_type == "club competition":
            date_start = st.date_input("Start Date (From)", value=None)
            date_end = st.date_input("End Date (To)", value=None)
            category_map = event_utility.get_category_map()
            category_name = st.selectbox("Category", ["All"] + list(category_map.keys()))
            if category_name != "All":
                category_id = category_map[category_name]
            else:
                category_id = None # None means all categories
            club_map = event_utility.get_club_map()
            club_option = st.radio("Choose Club Filter Method", ["All Clubs", "Select Clubs"])
            if club_option != "All Clubs":
                list_of_club_name = st.multiselect(
                    "Interested Club*", 
                    options=list(club_map.keys()),
                    help="⚠️ You must select at least one club"
                ) # select a group of clubs, this var is used to find eligible groups of clubs later
                if list_of_club_name:
                    list_of_club_id = [club_map[name] for name in list_of_club_name]
                    # Find eligible group ids that match the selected club ids
                    list_of_eligible_group_id = event_utility.get_list_of_eligible_group_id_from_a_set_of_club_id(set(list_of_club_id))
                    
                    if list_of_eligible_group_id:  # Check if list is not empty
                        #given an eligible_group_of_club_id, display list of name of club where club_id is in eligible_club_member of that eligible_group_of_club_id. Repeat for all eligible_group_of_club_id in list_of_eligible_group_id
                        list_of_eligible_club_names = {}
                        for group_id in list_of_eligible_group_id:
                            club_names = event_utility.get_list_of_member_club_name_from_eligible_group_of_club_id(group_id)
                            list_of_eligible_club_names[group_id] = club_names
                        # Display info
                        info_str = "💡 Those are id of eligible groups that include the clubs you selected, please pick one group id:\n"
                        for group_id, club_names in list_of_eligible_club_names.items():
                            info_str += f" - Group ID {group_id} : {', '.join(club_names)}\n"
                        st.info(info_str)
                        # then let user select one of the eligible_group_of_club_id from the list
                        eligible_group_id = int(st.selectbox("Eligible Group ID", [str(gid) for gid in list_of_eligible_group_id]))
                    else:
                        st.warning("⚠️ No eligible groups found for the selected clubs.")
                        eligible_group_id = None
                else:
                    # User selected "Select Clubs" but hasn't chosen any clubs yet
                    eligible_group_id = None
                    st.warning("⚠️ Please select at least one club to filter by clubs.")
            else:
                list_of_eligible_group_id = None
                eligible_group_id = None # None means all eligible groups
    
    # Disable Apply button if "Select Clubs" is chosen but no clubs selected
    disable_apply = False
    if club_option != "All Clubs" and not list_of_club_name:
        disable_apply = True
    
    apply_filter_btn = st.button("🔍 Apply Filters", type="primary", use_container_width=True, disabled=disable_apply)
    if apply_filter_btn:
        with st.spinner("Fetching events..."):
            if event_type == "yearly club championship":
                #apply filter for year, category_id, eligible_group_id by supabase query
                #for filtering based on category_id, we need to explore event_context table:
                #particularly, fisrtly we need to exclude rows with "yearly_club_championship_id" == NULL
                #then only keep rows where round_id is in round table where category_id == selected category_id
                yearly_championships_df = supabase.table("yearly_club_championship").select("*").eq("year", year).execute().data
                yearly_championships_df = pd.DataFrame(yearly_championships_df)
                if not yearly_championships_df.empty:
                    # Only filter by category if a specific category is selected
                    if category_id is not None:
                        event_contexts = supabase.table("event_context").select("yearly_club_championship_id, round_id").not_.is_("yearly_club_championship_id", "null").execute().data
                        event_contexts_df = pd.DataFrame(event_contexts)
                        
                        rounds = supabase.table("round").select("round_id").eq("category_id", category_id).execute().data
                        rounds_df = pd.DataFrame(rounds)
                        
                        # Only filter if we have data
                        if not event_contexts_df.empty and not rounds_df.empty:
                            filtered_event_contexts = event_contexts_df[event_contexts_df['round_id'].isin(rounds_df['round_id'])]
                            if not filtered_event_contexts.empty:
                                valid_championship_ids = filtered_event_contexts['yearly_club_championship_id'].unique().tolist()
                                yearly_championships_df = yearly_championships_df[yearly_championships_df['yearly_club_championship_id'].isin(valid_championship_ids)]
                            else:
                                # No matching championships for this category
                                yearly_championships_df = pd.DataFrame()
                        else:
                            # No rounds or event contexts found
                            yearly_championships_df = pd.DataFrame()
                    
                    # Filter by eligible group if specified
                    if eligible_group_id is not None and not yearly_championships_df.empty:
                        yearly_championships_df = yearly_championships_df[yearly_championships_df['eligible_group_of_club_id'] == eligible_group_id]
                    
                    # Save to session state
                    st.session_state["yearly_championships_df"] = yearly_championships_df
                else:
                    st.session_state["yearly_championships_df"] = pd.DataFrame()
                
                # Display the results
                if not st.session_state.get("yearly_championships_df", pd.DataFrame()).empty:
                    st.dataframe(st.session_state["yearly_championships_df"], use_container_width=True)
                else:
                    st.info("No yearly club championships found matching the filters.")
                    
            elif event_type == "club competition":
                #apply filter for date range, category_id, eligible_group_id by supabase query
                club_competitions_df = supabase.table("club_competition").select("*").execute().data
                club_competitions_df = pd.DataFrame(club_competitions_df)
                if not club_competitions_df.empty:
                    if date_start:
                        club_competitions_df = club_competitions_df[pd.to_datetime(club_competitions_df['start_date']) >= pd.to_datetime(date_start)]
                    if date_end:
                        club_competitions_df = club_competitions_df[pd.to_datetime(club_competitions_df['end_date']) <= pd.to_datetime(date_end)]
                    
                    # Only filter by category if a specific category is selected
                    if category_id is not None and not club_competitions_df.empty:
                        event_contexts = supabase.table("event_context").select("club_competition_id, round_id").not_.is_("club_competition_id", "null").execute().data
                        event_contexts_df = pd.DataFrame(event_contexts)
                        rounds = supabase.table("round").select("round_id").eq("category_id", category_id).execute().data
                        rounds_df = pd.DataFrame(rounds)
                        
                        # Only filter if we have data
                        if not event_contexts_df.empty and not rounds_df.empty:
                            filtered_event_contexts = event_contexts_df[event_contexts_df['round_id'].isin(rounds_df['round_id'])]
                            if not filtered_event_contexts.empty:
                                valid_competition_ids = filtered_event_contexts['club_competition_id'].unique().tolist()
                                club_competitions_df = club_competitions_df[club_competitions_df['club_competition_id'].isin(valid_competition_ids)]
                            else:
                                # No matching competitions for this category
                                club_competitions_df = pd.DataFrame()
                        else:
                            # No rounds or event contexts found
                            club_competitions_df = pd.DataFrame()
                    
                    # Filter by eligible group if specified
                    if eligible_group_id is not None and not club_competitions_df.empty:
                        club_competitions_df = club_competitions_df[club_competitions_df['eligible_group_of_club_id'] == eligible_group_id]
                    
                    # Save to session state
                    st.session_state["club_competitions_df"] = club_competitions_df
                else:
                    st.session_state["club_competitions_df"] = pd.DataFrame()
                
                # Display the results
                if not st.session_state.get("club_competitions_df", pd.DataFrame()).empty:
                    st.dataframe(st.session_state["club_competitions_df"], use_container_width=True)
                else:
                    st.info("No club competitions found matching the filters.")


    # Section 3: Event Hierarchy Visualization
    st.divider()
    st.subheader("📊 Event Hierarchy Visualization")
    st.write("Visualize the structure of an event)")
    
    # Show available IDs from the filtered events
    if 'events_df' in st.session_state and not st.session_state.events_df.empty:
        event_type_for_hierarchy = st.session_state.get('current_event_type', 'yearly_club_championship')
        if event_type_for_hierarchy == 'yearly_club_championship':
            available_ids = st.session_state.events_df['yearly_club_championship_id'].unique().tolist()
        else:
            available_ids = st.session_state.events_df['club_competition_id'].unique().tolist()
    
    #Section 2
    hierarchy_event_type = st.selectbox("Event Type ", ["yearly club championship", "club competition"], key="hierarchy_type")
    
    # Use search bar for event name
    if hierarchy_event_type == 'yearly club championship':
        yearly_championship_map = event_utility.get_yearly_club_championship_map()
        event_name = st.selectbox(
            "🔍 Search Yearly Club Championship",
            options=list(yearly_championship_map.keys()),
            help="Select a yearly club championship to visualize its hierarchy"
        )
        hierarchy_event_id = yearly_championship_map[event_name]
    else:
        club_competition_map = event_utility.get_club_competition_map()
        event_name = st.selectbox(
            "🔍 Search Club Competition",
            options=list(club_competition_map.keys()),
            help="Select a club competition to visualize its hierarchy"
        )
        hierarchy_event_id = club_competition_map[event_name]
        
    visualize_btn = st.button("🎨 Show Hierarchy", type="primary")
    
    if visualize_btn:
        with st.spinner("Building hierarchy visualization..."):
            # Get hierarchy data using utility function
            hierarchy_df = event_utility.get_event_hierarchy_for_icicle(
                event_type=hierarchy_event_type,
                event_id=hierarchy_event_id
            )
            
            if not hierarchy_df.empty:
                # Create icicle chart using graph_objects for better control
                fig = go.Figure()
                
                fig.add_trace(go.Icicle(
                    ids=hierarchy_df['ids'],
                    labels=hierarchy_df['labels'],
                    parents=hierarchy_df['parents'],
                    customdata=hierarchy_df[['hover_info']] if 'hover_info' in hierarchy_df.columns else None,
                    hovertemplate='<b>%{label}</b><br>%{customdata[0]}<extra></extra>' if 'hover_info' in hierarchy_df.columns else '<b>%{label}</b><extra></extra>',
                    textinfo="label",  # Only show label, no percentages
                    textposition="middle center",  # Center text in boxes
                    root_color="lightblue",
                    tiling=dict(
                        orientation='h'  # Horizontal orientation (children span parent height)
                    ),
                    textfont=dict(size=16)  # Bigger font size
                ))
                
                fig.update_layout(
                    title=f"Event Hierarchy: {event_name}",
                    margin=dict(t=80, l=25, r=25, b=25),
                    height=700,
                    font=dict(size=14)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add instructions
                st.info("💡 **Interactive Chart**: Click on any block to zoom in and explore deeper levels. Click on the parent (top bar) to zoom out. Hover over blocks to see more information. The deepest children are always **End**.")
                
                # Display data summary
                with st.expander("📊 Hierarchy Data Summary"):
                    st.write(f"**Total nodes**: {len(hierarchy_df)}")
                    st.write(f"**Hierarchy levels**: {hierarchy_df['level'].max() + 1}")
                    st.dataframe(hierarchy_df, use_container_width=True)
            else:
                st.warning("No hierarchy data found for this event. The event may not have any rounds or competitions configured.")
    


# Tab 2: Event Enrollment/Withdraw
with tab_enroll:
    yearly_club_championship_map = event_utility.get_yearly_club_championship_map()
    club_competition_map = event_utility.get_club_competition_map()
    st.header("Event Enrollment / Withdraw")
    if user_role not in ["archer", "recorder"]:
        st.info("⚠️ Only archers and recorders can submit event enrollment or withdrawal requests.")
        st.stop()

    # Tab 2.1: Submit Form
    st.subheader("📝 Submit Request Form") 
    # Move apply_for_option OUTSIDE the form so it can dynamically control form contents
    apply_for_option = st.radio("Apply For", ["yearly club championship", "club competition"], key="apply_for_radio")
    
    with st.form("event_request_form"):
        if user_role == 'archer':
            type = "participating"
            col1, col2 = st.columns(2)
            with col1:
                action = st.selectbox("Action*", ["enrol", "withdraw"])
            with col2:
                if apply_for_option == "yearly club championship":
                    yearly_club_championship_name = st.selectbox("yearly club championship*", list(yearly_club_championship_map.keys()))
                    yearly_club_championship_id = yearly_club_championship_map[yearly_club_championship_name]
                    club_competition_id = None
                else:
                    club_competition_name = st.selectbox("club competition*", list(club_competition_map.keys()))
                    club_competition_id = club_competition_map[club_competition_name]
                    yearly_club_championship_id = None
            sender_word = st.text_area("Write something you want to tell to the creator of the event", placeholder="Enter any additional information or message")


        elif user_role == 'recorder':           
            col1, col2 = st.columns(2)
            type = "recording"
            with col1:
                action = st.selectbox("Action*", ["enrol", "withdraw"])
            with col2:
                if apply_for_option == "yearly club championship":
                    yearly_club_championship_name = st.selectbox("yearly club championship*", list(yearly_club_championship_map.keys()))
                    yearly_club_championship_id = yearly_club_championship_map[yearly_club_championship_name]
                    club_competition_id = None
                else:
                    club_competition_name = st.selectbox("club competition*", list(club_competition_map.keys()))
                    club_competition_id = club_competition_map[club_competition_name]
                    yearly_club_championship_id = None
            sender_word = st.text_area("Write something you want to tell to the creator of the event", placeholder="Enter any additional information or message")
        #find creator of the event to set as reviewer by looks at "creator_id" field in yearly_club_championship or club_competition table
        if apply_for_option == "yearly club championship":
            event_creator = supabase.table("yearly_club_championship").select("creator_id").eq("yearly_club_championship_id", yearly_club_championship_id).execute().data
            if event_creator:
                reviewer_id = event_creator[0]['creator_id']
            else:
                reviewer_id = None
        else:
            event_creator = supabase.table("club_competition").select("creator_id").eq("club_competition_id", club_competition_id).execute().data
            if event_creator:
                reviewer_id = event_creator[0]['creator_id']
            else:
                reviewer_id = None
        submit_button = st.form_submit_button("📤 Submit Request")
        if submit_button:
            try:
                response = supabase.table("request_competition_form").insert({
                    "sender_id": st.session_state.user_id,
                    "type": type,
                    "action": action,
                    "yearly_club_championship_id": yearly_club_championship_id,
                    "club_competition_id": club_competition_id,
                    "sender_word": sender_word,
                    "status": "pending",
                    "reviewer_word": "waiting for reviewing",
                    "reviewed_by": reviewer_id
                }).execute()


            except Exception as e:
                print(f"Error submitting form: {e}")
    # Tab 2.2: View My Forms
    st.divider()
    st.subheader("📋 My Request Forms")
    
    user_forms = event_utility.get_request_forms(user_id=st.session_state.user_id, is_creator=False)
    
    if not user_forms.empty:
        st.dataframe(user_forms, use_container_width=True)
    else:
        st.info("You haven't submitted any request forms yet.")

# Tab 3: Event Schedule
with tab_schedule:
    st.header("📅 Event Schedule")
    st.write("View round schedules in Gantt chart format")
    
    club_competition_map = event_utility.get_club_competition_map()
    club_competition_name = st.selectbox("Select club competition", list(club_competition_map.keys()))
    competition_id_input = club_competition_map[club_competition_name]

    if st.button("🔍 View Schedule", type="primary"):
        if competition_id_input:
            schedule_df = event_utility.get_round_schedule(competition_id_input)
            
            if not schedule_df.empty:
                # Prepare data for Gantt chart
                gantt_data = []
                resource_name = f"Competition {competition_id_input}"
                for _, row in schedule_df.iterrows():
                    gantt_data.append({
                        'Task': row.get('round_name', f"Round {row['round_id']}"),
                        'Start': row['datetime_to_start'],
                        'Finish': row['expected_datetime_to_end'],
                        'Resource': resource_name
                    })
                
                if gantt_data:
                    # Create Gantt chart with proper color mapping
                    fig = ff.create_gantt(
                        gantt_data,
                        colors={resource_name: 'rgb(46, 137, 205)'},
                        index_col='Resource',
                        show_colorbar=True,
                        group_tasks=True,
                        showgrid_x=True,
                        showgrid_y=True,
                        title=f'Round Schedule for {club_competition_name}'
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
            forms_df = event_utility.get_request_forms(
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
                        success = event_utility.update_form_status(form_id, new_status)
                        
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
            all_clubs = event_utility.get_all_clubs()
            
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
                            group_id = event_utility.create_eligible_group_with_clubs(selected_club_ids)
                            
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
                all_groups = event_utility.get_all_eligible_groups()
            
            if all_groups:
                st.success(f"Found {len(all_groups)} eligible group(s)")
                
                # Build info string with all groups
                info_str = "💡 Eligible club groups in the system:\n\n"
                for group in all_groups:
                    club_names = [club['name'] for club in group['clubs']]
                    info_str += f"**Group ID {group['eligible_group_id']}** ({len(club_names)} clubs):\n"
                    if club_names:
                        info_str += f"  - {', '.join(club_names)}\n\n"
                    else:
                        info_str += f"  - (No member clubs)\n\n"
                
                info_str += "**Usage:** Use a Group ID when creating events to restrict participation to those specific clubs only."
                st.info(info_str)
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
            steps = ["Event Type", "Basic Info", "Competitions", "Rounds", "Schedule", "Ranges & Ends", "Review & Create"]
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
                    all_groups = event_utility.get_all_eligible_groups()
                    
                    if all_groups:
                        group_options = {f"All (No Restriction)": None}
                        for group in all_groups:
                            group_label = f"Group ID {group['eligible_group_id']} ({len(group['clubs'])} clubs)"
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
                            help="Choose which clubs can participate. Select 'All' for no restrictions."
                        )
                        
                        eligible_group_id = group_options[selected_group_label]
                        
                        # Show preview of selected group
                        if eligible_group_id:
                            group_details = event_utility.get_eligible_group_details(eligible_group_id)
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
                    all_groups = event_utility.get_all_eligible_groups()
                    
                    if all_groups:
                        group_options = {f"All (No Restriction)": None}
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
                            help="Choose which clubs can participate. Select 'All' for no restrictions."
                        )
                        
                        eligible_group_id = group_options[selected_group_label]
                        
                        # Show preview of selected group
                        if eligible_group_id:
                            group_details = event_utility.get_eligible_group_details(eligible_group_id)
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
                                st.write(f"{idx + 1}. {round_info['name']} ")
                            with col2:
                                if st.button("🗑️", key=f"del_round_{idx}"):
                                    st.session_state.event_builder_data['rounds'].pop(idx)
                                    st.rerun()
                
                # Add round selector
                if rounds_response.data:
                    round_options = {f"{r['name']}": r['round_id'] for r in rounds_response.data}
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
            
            # STEP 5: Schedule Rounds (timing)
            elif current_step == 5:
                st.write("**Schedule Rounds**")
                st.info("ℹ️ Set the date and time for each round")
                
                # Initialize round_schedules
                if 'round_schedules' not in st.session_state.event_builder_data:
                    st.session_state.event_builder_data['round_schedules'] = {}
                
                # Get round info
                rounds_response = supabase.table("round").select("*").execute()
                
                for round_id in st.session_state.event_builder_data['rounds']:
                    round_info = next((r for r in rounds_response.data if r['round_id'] == round_id), None)
                    round_name = round_info['name'] if round_info else f"Round {round_id}"
                    
                    with st.expander(f"📅 {round_name}", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        current_schedule = st.session_state.event_builder_data['round_schedules'].get(round_id, {})
                        
                        with col1:
                            start_date = st.date_input(
                                "Start Date*",
                                value=current_schedule.get('start_date', date.today()),
                                key=f"round_start_date_{round_id}"
                            )
                            start_time = st.time_input(
                                "Start Time*",
                                value=current_schedule.get('start_time', datetime.now().time()),
                                key=f"round_start_time_{round_id}"
                            )
                        
                        with col2:
                            end_date = st.date_input(
                                "Expected End Date*",
                                value=current_schedule.get('end_date', date.today()),
                                key=f"round_end_date_{round_id}"
                            )
                            end_time = st.time_input(
                                "Expected End Time*",
                                value=current_schedule.get('end_time', datetime.now().time()),
                                key=f"round_end_time_{round_id}"
                            )
                        
                        # Store the schedule
                        st.session_state.event_builder_data['round_schedules'][round_id] = {
                            'start_date': start_date,
                            'start_time': start_time,
                            'end_date': end_date,
                            'end_time': end_time
                        }
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("⬅️ Back"):
                        st.session_state.event_builder_step = 4
                        st.rerun()
                with col2:
                    if st.button("Next ➡️", type="primary", use_container_width=True):
                        # Validate all rounds have schedules
                        all_scheduled = all(round_id in st.session_state.event_builder_data['round_schedules'] 
                                          for round_id in st.session_state.event_builder_data['rounds'])
                        if not all_scheduled:
                            st.error("Please set schedule for all rounds!")
                        else:
                            st.session_state.event_builder_step = 6
                            st.rerun()
            
            # STEP 6: Add Ranges and Ends
            elif current_step == 6:
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
                        st.session_state.event_builder_step = 5
                        st.rerun()
                with col2:
                    if st.button("Next ➡️", type="primary", use_container_width=True):
                        # Validate all rounds have ranges configured
                        all_configured = all(st.session_state.event_builder_data['ranges_config'].get(r_id, []) 
                                           for r_id in st.session_state.event_builder_data['rounds'])
                        if not all_configured:
                            st.error("Please configure ranges for all rounds!")
                        else:
                            st.session_state.event_builder_step = 7
                            st.rerun()
            
            # STEP 7: Review and Create
            elif current_step == 7:
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
                        st.session_state.event_builder_step = 6
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
