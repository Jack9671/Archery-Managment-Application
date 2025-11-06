import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.express as px
from datetime import datetime, date
import time
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
    tabs = st.tabs(["🔍 Browse Events", "📝 Event Enrollment/Withdraw", "📋 Review Forms", "📅 Event Schedule", "🎯 My Events", "🏢 Club Groups", "⚙️ Event Management"])
    tab_browse, tab_enroll, tab_review, tab_schedule, tab_my_events, tab_club_groups, tab_manage = tabs
else:
    tabs = st.tabs(["🔍 Browse Events", "📝 Event Enrollment/Withdraw", "📅 Event Schedule", "🎯 My Events"])
    tab_browse = tabs[0]
    tab_enroll = tabs[1]
    tab_schedule = tabs[2]
    tab_my_events = tabs[3]

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
    
    apply_filter_btn = st.button("🔍 Apply Filters", type="primary", use_container_width=True, disabled=disable_apply, key="apply_filters_events")
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
        
    visualize_btn = st.button("🎨 Show Hierarchy", type="primary", key="visualize_hierarchy")
    
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

    st.header("Event Enrollment / Withdraw")
    if user_role not in ["archer", "recorder"]:
        st.info("⚠️ Only archers and recorders can submit event enrollment or withdrawal requests.")
        st.stop()

    # Tab 2.1: Submit Form
    st.subheader("📝 Submit Request Form") 
    # Move apply_for_option OUTSIDE the form so it can dynamically control form contents
    apply_for_option = st.radio("Apply For", ["yearly club championship", "club competition"], key="apply_for_radio")
    with st.container(border =True):
        if user_role == 'archer':
            type = "participating"

            action = st.selectbox("Action", ["enrol", "withdraw"])
            if apply_for_option == "yearly club championship":
                yearly_club_championship_options = list(yearly_club_championship_map.keys())
                yearly_club_championship_name = st.selectbox("yearly club championship*", yearly_club_championship_options if yearly_club_championship_options else ["No championships available"])
                if yearly_club_championship_name and yearly_club_championship_name != "No championships available":
                    yearly_club_championship_id = yearly_club_championship_map[yearly_club_championship_name]
                    club_competition_id = None
                    round_map = event_utility.get_round_map_of_an_event('yearly club championship', yearly_club_championship_id)
                    round_options = list(round_map.keys()) if round_map else ["No rounds available"]
                    round_name = st.selectbox("Round", round_options)
                    round_id = round_map.get(round_name) if round_name and round_name != "No rounds available" else None
                else:
                    yearly_club_championship_id = None
                    club_competition_id = None
                    round_id = None
            else:
                club_competition_map = event_utility.get_club_competition_map_of_no_yearly_club_championship()
                club_competition_options = list(club_competition_map.keys())
                club_competition_name = st.selectbox("club competition", club_competition_options if club_competition_options else ["No competitions available"])
                if club_competition_name and club_competition_name != "No competitions available":
                    club_competition_id = club_competition_map[club_competition_name]
                    yearly_club_championship_id = None
                    round_map = event_utility.get_round_map_of_an_event('club competition', club_competition_id)
                    round_options = list(round_map.keys()) if round_map else ["No rounds available"]
                    round_name = st.selectbox("Round", round_options)
                    round_id = round_map.get(round_name) if round_name and round_name != "No rounds available" else None
                else:
                    club_competition_id = None
                    yearly_club_championship_id = None
                    round_id = None

            sender_word = st.text_area("Write something you want to tell to the creator of the event", placeholder="Enter any additional information or message")


        elif user_role == 'recorder':           
            col1, col2 = st.columns(2)
            type = "recording"
            with col1:
                action = st.selectbox("Action*", ["enrol", "withdraw"])
            with col2:
                if apply_for_option == "yearly club championship":
                    yearly_club_championship_options = list(yearly_club_championship_map.keys())
                    yearly_club_championship_name = st.selectbox("yearly club championship*", yearly_club_championship_options if yearly_club_championship_options else ["No championships available"])
                    if yearly_club_championship_name and yearly_club_championship_name != "No championships available":
                        yearly_club_championship_id = yearly_club_championship_map[yearly_club_championship_name]
                        club_competition_id = None
                    else:
                        yearly_club_championship_id = None
                        club_competition_id = None
                    round_id = None
                else:
                    club_competition_map = event_utility.get_club_competition_map_of_no_yearly_club_championship()
                    club_competition_options = list(club_competition_map.keys())
                    club_competition_name = st.selectbox("club competition*", club_competition_options if club_competition_options else ["No competitions available"])
                    if club_competition_name and club_competition_name != "No competitions available":
                        club_competition_id = club_competition_map[club_competition_name]
                        yearly_club_championship_id = None
                    else:
                        club_competition_id = None
                        yearly_club_championship_id = None
                    round_id = None
            sender_word = st.text_area("Write something you want to tell to the creator of the event", placeholder="Enter any additional information or message")
        
        submit_button = st.button("📤 Submit Request", type="primary", use_container_width=True, key="submit_request_form_btn")
        if submit_button:
            try:
                # Find creator of the event to set as reviewer
                reviewer_id = None
                if apply_for_option == "yearly club championship" and yearly_club_championship_id:
                    event_creator = supabase.table("yearly_club_championship").select("creator_id").eq("yearly_club_championship_id", yearly_club_championship_id).execute().data
                    if event_creator:
                        reviewer_id = event_creator[0]['creator_id']
                elif apply_for_option == "club competition" and club_competition_id:
                    event_creator = supabase.table("club_competition").select("creator_id").eq("club_competition_id", club_competition_id).execute().data
                    if event_creator:
                        reviewer_id = event_creator[0]['creator_id']
                
                # Validate that we have required IDs
                if not yearly_club_championship_id and not club_competition_id:
                    st.error("Please select a valid event before submitting.")
                else:
                    response = supabase.table("request_competition_form").insert({
                        "sender_id": st.session_state.user_id,
                        "type": type,
                        "action": action,
                        "yearly_club_championship_id": yearly_club_championship_id,
                        "club_competition_id": club_competition_id,
                        "round_id": round_id,
                        "sender_word": sender_word,
                        "status": "pending",
                        "reviewer_word": "waiting for reviewing",
                        "reviewed_by": reviewer_id
                    }).execute()
                    
                    if response.data:
                        st.success("✅ Request submitted successfully!")
                        st.rerun()

            except Exception as e:
                st.error(f"Error submitting form: {e}")
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

    if st.button("🔍 View Schedule", type="primary", key="view_schedule_btn"):
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
                        'Finish': row['datetime_to_end'],
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

# Tab: My Events (for all users)
with tab_my_events:
    st.header("🎯 My Events")
    st.write("View events you have enrolled in")
    
    # Section 1: Time Filter
    st.subheader("⏰ Time Filter")
    time_filter = st.radio(
        "Show events:",
        ["All", "Upcoming", "History"],
        horizontal=True,
        help="Filter events by time period"
    )
    
    # Convert radio selection to filter value
    filter_value = "all"
    if time_filter == "Upcoming":
        filter_value = "upcoming"
    elif time_filter == "History":
        filter_value = "history"
    
    # Fetch joined events
    with st.spinner("Loading your events..."):
        joined_events = event_utility.get_user_joined_events(
            user_id=st.session_state.user_id,
            time_filter=filter_value
        )
    
    # Section 2: Yearly Club Championships
    st.divider()
    st.subheader("🏆 Yearly Club Championships")
    
    championships_df = joined_events['championships']
    
    if not championships_df.empty:
        st.success(f"You are enrolled in **{len(championships_df)}** yearly club championship(s)")
        
        # Display championships with expandable details
        for idx, row in championships_df.iterrows():
            with st.expander(f"📅 {row['name']} ({row['year']})", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Championship ID:** {row['yearly_club_championship_id']}")
                    st.write(f"**Year:** {row['year']}")
                    st.write(f"**Creator ID:** {row['creator_id']}")
                
                with col2:
                    if row.get('eligible_group_of_club_id'):
                        st.write(f"**Eligible Group ID:** {row['eligible_group_of_club_id']}")
                        # Get club names in the group
                        club_names = event_utility.get_list_of_member_club_name_from_eligible_group_of_club_id(
                            row['eligible_group_of_club_id']
                        )
                        if club_names:
                            st.write(f"**Eligible Clubs:** {', '.join(club_names)}")
                    else:
                        st.write("**Eligibility:** All clubs")
                    
                    st.write(f"**Created:** {row['created_at'][:10]}")
                
                # Show competitions under this championship
                st.write("---")
                st.write("**Competitions in this Championship:**")
                
                # Query competitions linked to this championship
                event_contexts = supabase.table("event_context")\
                    .select("club_competition_id")\
                    .eq("yearly_club_championship_id", row['yearly_club_championship_id'])\
                    .execute()
                
                if event_contexts.data:
                    comp_ids = list(set([ec['club_competition_id'] for ec in event_contexts.data if ec.get('club_competition_id')]))
                    
                    if comp_ids:
                        comps = supabase.table("club_competition")\
                            .select("*")\
                            .in_("club_competition_id", comp_ids)\
                            .execute()
                        
                        if comps.data:
                            comp_df = pd.DataFrame(comps.data)
                            st.dataframe(
                                comp_df[['club_competition_id', 'name', 'address', 'date_start', 'date_end']],
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.info("No competitions found")
                    else:
                        st.info("No competitions linked yet")
                else:
                    st.info("No competitions linked yet")
    else:
        if time_filter == "All":
            st.info("You haven't enrolled in any yearly club championships yet.")
        elif time_filter == "Upcoming":
            st.info("You don't have any upcoming yearly club championships.")
        else:
            st.info("You don't have any past yearly club championships.")
    
    # Section 3: Club Competitions
    st.divider()
    st.subheader("🎯 Club Competitions")
    
    competitions_df = joined_events['competitions']
    
    if not competitions_df.empty:
        st.success(f"You are enrolled in **{len(competitions_df)}** club competition(s)")
        
        # Display competitions with expandable details
        for idx, row in competitions_df.iterrows():
            # Determine if competition has ended
            end_date = pd.to_datetime(row['date_end']).date()
            current_date = datetime.now().date()
            status_emoji = "✅" if end_date < current_date else "🔵"
            status_text = "Completed" if end_date < current_date else "Active/Upcoming"
            
            with st.expander(f"{status_emoji} {row['name']} - {status_text}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Competition ID:** {row['club_competition_id']}")
                    st.write(f"**Address:** {row['address']}")
                    st.write(f"**Start Date:** {row['date_start']}")
                    st.write(f"**End Date:** {row['date_end']}")
                
                with col2:
                    st.write(f"**Creator ID:** {row['creator_id']}")
                    
                    if row.get('eligible_group_of_club_id'):
                        st.write(f"**Eligible Group ID:** {row['eligible_group_of_club_id']}")
                        # Get club names in the group
                        club_names = event_utility.get_list_of_member_club_name_from_eligible_group_of_club_id(
                            row['eligible_group_of_club_id']
                        )
                        if club_names:
                            st.write(f"**Eligible Clubs:** {', '.join(club_names)}")
                    else:
                        st.write("**Eligibility:** All clubs")
                    
                    st.write(f"**Created:** {row['created_at'][:10]}")
                
                # Show round schedule if available
                st.write("---")
                st.write("**Round Schedule:**")
                
                schedule_df = event_utility.get_round_schedule(row['club_competition_id'])
                
                if not schedule_df.empty:
                    st.dataframe(
                        schedule_df[['round_name', 'datetime_to_start', 'datetime_to_end']],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No rounds scheduled yet")
    else:
        if time_filter == "All":
            st.info("You haven't enrolled in any club competitions yet.")
        elif time_filter == "Upcoming":
            st.info("You don't have any upcoming club competitions.")
        else:
            st.info("You don't have any past club competitions.")
    
    # Summary statistics
    st.divider()
    st.subheader("📊 Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Championships", len(championships_df))
    
    with col2:
        st.metric("Total Competitions", len(competitions_df))
    
    with col3:
        total_events = len(championships_df) + len(competitions_df)
        st.metric("Total Events", total_events)

# Recorder-only tabs
if user_role == 'recorder':
    # Tab 4: Review Forms (All recorders who are member of an event can view forms for that event, only creator recorders can edit)
    with tab_review:
        st.header("📋 Review Request Forms")
        st.write("View and review enrollment/withdrawal forms, please configure your filters below to find the forms you want to review.")
        st.info("Options for you to select come from the events you have created or have been applied to record for.")
        with st.container(border =True):
            # Filter options
            #yearly_club_championship or club_competition
            option = st.radio("View Forms For", ["yearly club championship", "club competition"], horizontal=True)  
            col1, col2, col3, col4 = st.columns(4)
            with col1: 
                if option == "yearly club championship":
                    yearly_championship_map = event_utility.get_yearly_club_championship_map_of_a_recorder(user_id=st.session_state.user_id)
                    filter_event_name = st.selectbox("yearly club championship", list(yearly_championship_map.keys()))
                    filter_event_id = yearly_championship_map[filter_event_name]
                else:
                    club_competition_map = event_utility.get_club_competition_map_of_a_recorder(user_id=st.session_state.user_id)
                    filter_event_name = st.selectbox("club competition", list(club_competition_map.keys()))
                    filter_event_id = club_competition_map[filter_event_name]
            with col2:
                filter_type = st.selectbox("type", [ "participating", "recording"])
                round_map = event_utility.get_round_map_of_an_event(event_type=option, event_id=filter_event_id)
                    
            with col3:
                if filter_type == "recording":
                    filter_round_id = None
                elif filter_type == "participating":
                    filter_round_name = st.selectbox("round", ["All"] + list(round_map.keys()))  
                    if filter_round_name == "All":
                        filter_round_id = None
                    else:
                        filter_round_id = round_map[filter_round_name]
            with col4:
                filter_status = st.selectbox("status", [ "pending", "in progress", "eligible", "ineligible"])
            apply_filter_button = st.button("🔍 Apply Filters", type="primary", use_container_width=True, key="apply_filters_forms")
            
            # Store filter parameters in session state when button is clicked
            if apply_filter_button:
                if option == "yearly club championship":
                    query = supabase.table("request_competition_form").select("*") \
                        .eq("yearly_club_championship_id", filter_event_id)
                    if filter_round_id is not None:
                        query = query.eq("round_id", filter_round_id)
                    response = query.eq("type", filter_type).eq("status", filter_status).execute()
                else:
                    query = supabase.table("request_competition_form").select("*") \
                        .eq("club_competition_id", filter_event_id)
                    if filter_round_id is not None:
                        query = query.eq("round_id", filter_round_id)
                    response = query.eq("type", filter_type).eq("status", filter_status).execute()
                
                forms_data = response.data
                
                # Check if current user is the creator of the event
                if option == "yearly club championship":
                    event_creator = supabase.table("yearly_club_championship").select("creator_id")\
                        .eq("yearly_club_championship_id", filter_event_id).execute().data
                    is_creator = st.session_state.user_id == event_creator[0]['creator_id'] if event_creator else False
                else:
                    event_creator = supabase.table("club_competition").select("creator_id")\
                        .eq("club_competition_id", filter_event_id).execute().data
                    is_creator = st.session_state.user_id == event_creator[0]['creator_id'] if event_creator else False
                
                # Store in session state
                if forms_data:
                    st.session_state['review_forms_data'] = pd.DataFrame(forms_data)
                    st.session_state['review_forms_is_creator'] = is_creator
                    st.session_state['review_forms_filter_status'] = filter_status
                    st.session_state['review_forms_filter_type'] = filter_type
                else:
                    st.session_state['review_forms_data'] = pd.DataFrame()
                    st.session_state['review_forms_is_creator'] = is_creator
        
        # Display forms outside the button click handler using session state
        if 'review_forms_data' in st.session_state and not st.session_state['review_forms_data'].empty:
            forms_df = st.session_state['review_forms_data']
            is_creator = st.session_state.get('review_forms_is_creator', False)
            filter_status = st.session_state.get('review_forms_filter_status', 'pending')
            filter_type = st.session_state.get('review_forms_filter_type', 'participating')
            
            if is_creator and filter_status != "eligible":
                st.success("You are the creator of this event. You can review and update the forms below.")
                edited_df = st.data_editor(
                    forms_df,
                    use_container_width=True,
                    num_rows="dynamic",
                    disabled=[col for col in forms_df.columns if col not in ["status", "reviewer_word"]],
                    column_config={
                        "status": st.column_config.SelectboxColumn(
                            "Status",
                            options=['pending', 'in progress', 'eligible', 'ineligible'],
                            required=True,
                            help="Select the status of this request"
                        )
                    },
                    key="review_forms_editor"
                )
                
                if st.button("💾 Save Changes", type="primary", key="save_form_changes"):
                    with st.spinner("Saving changes..."):
                        # Track newly eligible forms
                        newly_eligible_rows = []
                        
                        for _, row in edited_df.iterrows():
                            # Update the database
                            supabase.table("request_competition_form").update({
                                "status": row['status'],
                                "reviewer_word": row['reviewer_word'],
                                "reviewed_by": st.session_state.user_id
                            }).eq("form_id", row['form_id']).execute()
                            
                            # Track if this row was just marked as eligible
                            original_row = forms_df[forms_df['form_id'] == row['form_id']]
                            if not original_row.empty and row['status'] == 'eligible' and original_row.iloc[0]['status'] != 'eligible':
                                newly_eligible_rows.append(row)
                        
                        st.success("✅ Changes saved successfully!")
                        
                        # Add participants/recorders for newly eligible forms
                        if newly_eligible_rows:
                            if filter_type == "participating":
                                for row in newly_eligible_rows:
                                    event_utility.add_participant_to_participating_table(
                                        user_id=row['sender_id'],
                                        event_type=option, 
                                        event_id=row['yearly_club_championship_id'] if option == "yearly club championship" else row['club_competition_id'],
                                        round_id=row['round_id']
                                    )
                                st.success(f"✅ {len(newly_eligible_rows)} participant(s) added successfully.")
                            
                            elif filter_type == "recording":
                                for row in newly_eligible_rows:
                                    event_utility.add_recorder_to_recording_table(
                                        user_id=row['sender_id'],
                                        event_type=option, 
                                        event_id=row['yearly_club_championship_id'] if option == "yearly club championship" else row['club_competition_id']
                                    )
                                st.success(f"✅ {len(newly_eligible_rows)} recorder(s) added successfully.")
                        
                        # Clear the session state to force refresh
                        del st.session_state['review_forms_data']
                        st.rerun()
                        
            elif is_creator and filter_status == "eligible":
                st.info("These forms have been marked as eligible. No further edits can be made.")
                st.dataframe(forms_df, use_container_width=True)
            else:
                st.info("You are not the creator of this event. You can only view the forms below.")
                st.dataframe(forms_df, use_container_width=True)
        elif 'review_forms_data' in st.session_state and st.session_state['review_forms_data'].empty:
            st.info("No forms found matching the selected filters.")
        

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
                    
                    if st.button("✅ Create Eligible Group", type="primary", use_container_width=True, key="create_eligible_group"):
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
            
            if st.button("🔄 Refresh Groups", type="secondary", key="refresh_groups"):
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
            st.header("⚙️ Event Creation")
            st.subheader("Create New Event")
            st.info("📋 Follow the steps below to create a new event:")
            
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
                    if st.button("Next ➡️", type="primary", use_container_width=True, key="next_step1"):
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
                        if st.button("⬅️ Back", key="back_step2_championship"):
                            st.session_state.event_builder_step = 1
                            st.rerun()
                    with col2:
                        if st.button("Next ➡️", type="primary", use_container_width=True, key="next_step2_championship"):
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
                        if st.button("⬅️ Back", key="back_step2_competition"):
                            st.session_state.event_builder_step = 1
                            st.rerun()
                    with col2:
                        if st.button("Next ➡️", type="primary", use_container_width=True, key="next_step2_competition"):
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
                        
                        if st.button("➕ Add Competition", key="add_competition"):
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
                        if st.button("⬅️ Back", key="back_step3_championship"):
                            st.session_state.event_builder_step = 2
                            st.rerun()
                    with col2:
                        if st.button("Next ➡️", type="primary", use_container_width=True, key="next_step3_championship"):
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
                    
                    if st.button("➕ Add Round", key="add_round") and selected_round:
                        round_id = round_options[selected_round]
                        if round_id not in st.session_state.event_builder_data['rounds']:
                            st.session_state.event_builder_data['rounds'].append(round_id)
                            st.success(f"Added {selected_round}")
                            st.rerun()
                        else:
                            st.warning("Round already added!")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("⬅️ Back", key="back_step4"):
                        st.session_state.event_builder_step = 3 if st.session_state.event_builder_data.get('event_type') == "Yearly Club Championship" else 2
                        st.rerun()
                with col2:
                    if st.button("Next ➡️", type="primary", use_container_width=True, key="next_step4"):
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
                    if st.button("⬅️ Back", key="back_step5"):
                        st.session_state.event_builder_step = 4
                        st.rerun()
                with col2:
                    if st.button("Next ➡️", type="primary", use_container_width=True, key="next_step5"):
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
                    if st.button("⬅️ Back", key="back_step6"):
                        st.session_state.event_builder_step = 5
                        st.rerun()
                with col2:
                    if st.button("Next ➡️", type="primary", use_container_width=True, key="next_step6"):
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
                    if st.button("⬅️ Back", key="back_step7"):
                        st.session_state.event_builder_step = 6
                        st.rerun()
                with col2:
                    if st.button("🔄 Start Over", type="secondary", use_container_width=True, key="start_over_step7"):
                        st.session_state.event_builder_step = 1
                        st.session_state.event_builder_data = {}
                        st.rerun()
                with col3:
                    if st.button("✅ Create Event", type="primary", use_container_width=True, key="create_event_step7"):
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
                                error_msg = result.get('error', 'Unknown error')
                                st.error(f"❌ Error: {error_msg}")
                                
                                # Provide helpful hints based on error type
                                if 'duplicate key' in str(error_msg).lower() and 'name' in str(error_msg).lower():
                                    st.warning("💡 **Tip:** An event with this name already exists. Please use a different name.")
                                elif 'foreign key' in str(error_msg).lower():
                                    st.warning("💡 **Tip:** One or more selected items (rounds, ranges, clubs) may not exist in the database.")
                                else:
                                    st.write("Please try again or contact an administrator.")
                                
                                # Show technical details in expander
                                with st.expander("🔍 Technical Details"):
                                    st.code(error_msg)
        