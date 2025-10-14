import streamlit as st
from datetime import datetime
from utility_function.initilize_dbconnection import supabase

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please log in to view events.")
    st.info("Navigate to the 'Sign Up Log In' page to access your account.")
    st.stop()

# Page header
st.title("🎯 Event Browser")
st.write(f"**Logged in as:** {st.session_state.get('fullname', 'N/A')}")
st.write("Browse all available archery events, competitions, and rounds.")
st.divider()

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["🏆 Competitions", "🎪 Yearly Championships", "🔍 Event Details"])

# ==================== COMPETITIONS TAB ====================
with tab1:
    st.subheader("🏆 All Competitions")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        show_past = st.checkbox("Show Past Competitions", value=False)
    
    with col2:
        search_comp = st.text_input("Search Competitions", placeholder="Enter competition name...")
    
    try:
        # Fetch competitions
        competitions = supabase.table("competition").select("*").order("date_start", desc=True).execute()
        comps = competitions.data if competitions.data else []
        
        # Filter competitions
        filtered_comps = []
        today = datetime.now().date()
        
        for comp in comps:
            # Date filter
            comp_end_date = datetime.strptime(comp['date_end'], '%Y-%m-%d').date()
            if not show_past and comp_end_date < today:
                continue
            
            # Search filter
            if search_comp and search_comp.lower() not in comp['name'].lower():
                continue
            
            filtered_comps.append(comp)
        
        st.info(f"📊 Showing {len(filtered_comps)} competition(s)")
        
        if not filtered_comps:
            st.warning("No competitions found matching your criteria.")
        else:
            for comp in filtered_comps:
                # Check if competition has ended
                comp_end_date = datetime.strptime(comp['date_end'], '%Y-%m-%d').date()
                status_emoji = "✅" if comp_end_date >= today else "📅"
                status_text = "Active/Upcoming" if comp_end_date >= today else "Completed"
                
                with st.expander(f"{status_emoji} {comp['name']} - {status_text}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Competition ID:** {comp['competition_id']}")
                        st.write(f"**Name:** {comp['name']}")
                        st.write(f"**Location:** {comp['address']}")
                        st.write(f"**Start Date:** {comp['date_start']}")
                        st.write(f"**End Date:** {comp['date_end']}")
                        st.write(f"**Status:** {status_text}")
                    
                    with col2:
                        # Check if user is already registered
                        user_id = st.session_state.get('user_id')
                        
                        # Check if user is an archer
                        try:
                            archer_check = supabase.table("archer").select("archer_id").eq("archer_id", user_id).execute()
                            is_archer = bool(archer_check.data)
                        except:
                            is_archer = False
                        
                        if is_archer:
                            # Check existing registrations
                            try:
                                existing_forms = supabase.table("request_form").select("form_id, status, round_id").eq(
                                    "account_id", user_id
                                ).eq("competition_id", comp['competition_id']).eq("role", "participant").execute()
                                
                                if existing_forms.data:
                                    st.write("**Your Requests:**")
                                    for form in existing_forms.data:
                                        round_info = supabase.table("round").select("name").eq("round_id", form['round_id']).execute()
                                        round_name = round_info.data[0]['name'] if round_info.data else "Unknown"
                                        st.caption(f"Form #{form['form_id']}: {round_name} - {form['status']}")
                                else:
                                    st.write("**Not registered yet**")
                                    if st.button("📝 Register", key=f"reg_{comp['competition_id']}"):
                                        st.info("Please go to the 'Form Submission' page to register.")
                            except:
                                pass
                        else:
                            st.write("*Become an archer to register*")
                    
                    st.divider()
                    
                    # Show available rounds for this competition
                    st.write("### Available Rounds")
                    try:
                        # Get event contexts for this competition
                        contexts = supabase.table("event_context").select(
                            "round:round_id(round_id, name, age_group)"
                        ).eq("competition_id", comp['competition_id']).execute()
                        
                        if contexts.data:
                            # Get unique rounds
                            rounds_dict = {}
                            for ctx in contexts.data:
                                if ctx.get('round'):
                                    round_id = ctx['round']['round_id']
                                    if round_id not in rounds_dict:
                                        rounds_dict[round_id] = ctx['round']
                            
                            if rounds_dict:
                                for round_id, rnd in rounds_dict.items():
                                    st.write(f"🎯 **{rnd['name']}** - Age Group: {rnd['age_group']}")
                            else:
                                st.info("No rounds configured yet.")
                        else:
                            st.info("No rounds configured yet.")
                    except Exception as e:
                        st.warning(f"Could not load rounds: {str(e)}")
                    
                    # Show ranges and ends
                    st.write("### Event Structure")
                    try:
                        event_contexts = supabase.table("event_context").select(
                            "event_context_id, round:round_id(name), range:range_id(distance, unit_of_length), end_order"
                        ).eq("competition_id", comp['competition_id']).order("end_order").execute()
                        
                        if event_contexts.data:
                            # Group by round
                            rounds_structure = {}
                            for ctx in event_contexts.data:
                                round_name = ctx['round']['name'] if ctx.get('round') else "Unknown"
                                if round_name not in rounds_structure:
                                    rounds_structure[round_name] = []
                                rounds_structure[round_name].append(ctx)
                            
                            for round_name, contexts in rounds_structure.items():
                                st.write(f"**Round: {round_name}**")
                                for ctx in contexts:
                                    range_info = f"{ctx['range']['distance']}{ctx['range']['unit_of_length']}" if ctx.get('range') else "Unknown"
                                    st.caption(f"  • End {ctx['end_order']}: Range {range_info}")
                        else:
                            st.info("No event structure configured yet.")
                    except Exception as e:
                        st.warning(f"Could not load event structure: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading competitions: {str(e)}")

# ==================== YEARLY CHAMPIONSHIPS TAB ====================
with tab2:
    st.subheader("🎪 Yearly Club Championships")
    
    try:
        # Fetch championships
        championships = supabase.table("yearly_club_championship").select("*").order("year", desc=True).execute()
        champs = championships.data if championships.data else []
        
        if not champs:
            st.info("No yearly championships found.")
        else:
            st.info(f"📊 Found {len(champs)} championship(s)")
            
            for champ in champs:
                with st.expander(f"🎪 {champ['name']} ({champ['year']})"):
                    st.write(f"**Championship ID:** {champ['yearly_club_championship_id']}")
                    st.write(f"**Name:** {champ['name']}")
                    st.write(f"**Year:** {champ['year']}")
                    
                    st.divider()
                    
                    # Show linked competitions
                    st.write("### Competitions in This Championship")
                    try:
                        linked_comps = supabase.table("event_context").select(
                            "competition:competition_id(competition_id, name, date_start, date_end, address)"
                        ).eq("yearly_club_championship_id", champ['yearly_club_championship_id']).execute()
                        
                        if linked_comps.data:
                            # Get unique competitions
                            comps_dict = {}
                            for item in linked_comps.data:
                                if item.get('competition'):
                                    comp_id = item['competition']['competition_id']
                                    if comp_id not in comps_dict:
                                        comps_dict[comp_id] = item['competition']
                            
                            if comps_dict:
                                for comp_id, comp in comps_dict.items():
                                    st.write(f"🏆 **{comp['name']}**")
                                    st.write(f"   📍 {comp['address']}")
                                    st.write(f"   📅 {comp['date_start']} to {comp['date_end']}")
                                    st.write("")
                            else:
                                st.info("No competitions linked to this championship yet.")
                        else:
                            st.info("No competitions linked to this championship yet.")
                    except Exception as e:
                        st.warning(f"Could not load competitions: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading championships: {str(e)}")

# ==================== EVENT DETAILS TAB ====================
with tab3:
    st.subheader("🔍 Detailed Event Information")
    st.write("Search for specific event contexts to see complete details.")
    
    # Search filters
    col1, col2 = st.columns(2)
    
    with col1:
        # Get all competitions for filter
        try:
            comps = supabase.table("competition").select("competition_id, name").order("name").execute()
            comp_list = comps.data if comps.data else []
            comp_options = ["All"] + [f"{c['competition_id']} - {c['name']}" for c in comp_list]
            selected_comp_filter = st.selectbox("Filter by Competition", comp_options)
        except:
            selected_comp_filter = "All"
    
    with col2:
        # Get all rounds for filter
        try:
            rnds = supabase.table("round").select("round_id, name").order("name").execute()
            round_list = rnds.data if rnds.data else []
            round_options = ["All"] + [f"{r['round_id']} - {r['name']}" for r in round_list]
            selected_round_filter = st.selectbox("Filter by Round", round_options)
        except:
            selected_round_filter = "All"
    
    try:
        # Build query
        query = supabase.table("event_context").select(
            "event_context_id, end_order, yearly_club_championship:yearly_club_championship_id(name, year), competition:competition_id(name, date_start, date_end), round:round_id(name, age_group), range:range_id(distance, unit_of_length, target_face:target_face_id(diameter, unit_of_length))"
        )
        
        # Apply filters
        if selected_comp_filter != "All":
            comp_id = int(selected_comp_filter.split(" - ")[0])
            query = query.eq("competition_id", comp_id)
        
        if selected_round_filter != "All":
            round_id = int(selected_round_filter.split(" - ")[0])
            query = query.eq("round_id", round_id)
        
        contexts = query.order("event_context_id").execute()
        context_list = contexts.data if contexts.data else []
        
        if not context_list:
            st.info("No event contexts found matching your criteria.")
        else:
            st.info(f"📊 Found {len(context_list)} event context(s)")
            
            for ctx in context_list:
                champ_info = f"{ctx['yearly_club_championship']['name']} ({ctx['yearly_club_championship']['year']})" if ctx.get('yearly_club_championship') else "No championship"
                comp_info = ctx['competition']['name'] if ctx.get('competition') else "Unknown"
                round_info = f"{ctx['round']['name']} ({ctx['round']['age_group']})" if ctx.get('round') else "Unknown"
                
                with st.expander(f"🎯 {ctx['event_context_id']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Event Context ID:** {ctx['event_context_id']}")
                        st.write(f"**Championship:** {champ_info}")
                        st.write(f"**Competition:** {comp_info}")
                        if ctx.get('competition'):
                            st.write(f"**Competition Dates:** {ctx['competition']['date_start']} to {ctx['competition']['date_end']}")
                    
                    with col2:
                        st.write(f"**Round:** {round_info}")
                        if ctx.get('range'):
                            st.write(f"**Range Distance:** {ctx['range']['distance']} {ctx['range']['unit_of_length']}")
                            if ctx['range'].get('target_face'):
                                st.write(f"**Target Face:** {ctx['range']['target_face']['diameter']} {ctx['range']['target_face']['unit_of_length']}")
                        st.write(f"**End Order:** {ctx['end_order']}")
                    
                    # Check if user can register
                    user_id = st.session_state.get('user_id')
                    try:
                        archer_check = supabase.table("archer").select("archer_id").eq("archer_id", user_id).execute()
                        is_archer = bool(archer_check.data)
                        
                        if is_archer and ctx.get('competition'):
                            st.divider()
                            comp_id = ctx['competition_id']
                            round_id = ctx['round_id']
                            
                            # Check if already registered
                            existing = supabase.table("request_form").select("form_id, status").eq(
                                "account_id", user_id
                            ).eq("competition_id", comp_id).eq("round_id", round_id).eq("role", "participant").execute()
                            
                            if existing.data:
                                st.info(f"You have a registration request: Status - {existing.data[0]['status']}")
                            else:
                                if st.button("📝 Register for This Event", key=f"reg_ctx_{ctx['event_context_id']}"):
                                    st.info("Please go to the 'Form Submission' page to complete your registration.")
                    except:
                        pass
    
    except Exception as e:
        st.error(f"Error loading event contexts: {str(e)}")

# ==================== SIDEBAR INFO ====================
with st.sidebar:
    st.subheader("ℹ️ Event Information")
    st.write("**How to Register:**")
    st.write("1. Browse competitions")
    st.write("2. Choose a round that matches your age group")
    st.write("3. Go to 'Form Submission' page")
    st.write("4. Submit a participant enrollment form")
    st.write("5. Wait for recorder approval")
    
    st.divider()
    
    # Show user's registration status
    user_id = st.session_state.get('user_id')
    try:
        archer_check = supabase.table("archer").select("archer_id").eq("archer_id", user_id).execute()
        is_archer = bool(archer_check.data)
        
        if is_archer:
            st.success("✅ You are registered as an Archer")
            
            # Show pending forms
            pending_forms = supabase.table("request_form").select(
                "form_id, status, competition:competition_id(name), round:round_id(name)"
            ).eq("account_id", user_id).eq("role", "participant").execute()
            
            if pending_forms.data:
                st.write("**Your Requests:**")
                for form in pending_forms.data:
                    comp_name = form['competition']['name'] if form.get('competition') else "Unknown"
                    round_name = form['round']['name'] if form.get('round') else "Unknown"
                    status_emoji = {"pending": "⏳", "in progress": "🔄", "eligible": "✅", "ineligible": "❌"}.get(form['status'], "❓")
                    st.caption(f"{status_emoji} {comp_name} - {round_name}: {form['status']}")
        else:
            st.warning("⚠️ You are not an Archer yet")
            st.info("Submit an archer enrollment form to participate in competitions.")
    except:
        pass
