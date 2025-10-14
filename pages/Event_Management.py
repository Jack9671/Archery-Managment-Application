import streamlit as st
from datetime import date, datetime
from utility_function.initilize_dbconnection import supabase

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please log in to access the event management page.")
    st.info("Navigate to the 'Sign Up Log In' page to access your account.")
    st.stop()

# Check if user is Recorder
user_id = st.session_state.get('user_id')
try:
    recorder_check = supabase.table("recorder").select("recorder_id, competition_id, round_id").eq("recorder_id", user_id).execute()
    is_recorder = bool(recorder_check.data)
    recorder_assignments = recorder_check.data if recorder_check.data else []
except:
    is_recorder = False
    recorder_assignments = []

if not is_recorder:
    st.error("🚫 Access Denied")
    st.warning("You must be a Recorder to access this page.")
    st.info("Please submit a request form to become a recorder.")
    st.stop()

# Page header
st.title("🎯 Event Management System")
st.write(f"**Logged in as:** {st.session_state.get('fullname', 'N/A')}")
st.write(f"**Role:** Recorder")
st.divider()

# Show recorder assignments
with st.expander("📋 Your Recorder Assignments", expanded=False):
    for assignment in recorder_assignments:
        comp_data = supabase.table("competition").select("name").eq("competition_id", assignment['competition_id']).execute()
        round_data = supabase.table("round").select("name").eq("round_id", assignment['round_id']).execute()
        
        comp_name = comp_data.data[0]['name'] if comp_data.data else "Unknown"
        round_name = round_data.data[0]['name'] if round_data.data else "Unknown"
        
        st.info(f"🏆 Competition: **{comp_name}** | Round: **{round_name}**")

st.divider()

# Main tabs for event management
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏆 Competitions",
    "🎯 Rounds",
    "📏 Ranges",
    "🎪 Yearly Championships",
    "🎪 Event Contexts",
    "👥 Manage Participants"
])

# ==================== COMPETITIONS TAB ====================
with tab1:
    st.subheader("🏆 Competition Management")
    
    # View competitions
    st.write("### View All Competitions")
    try:
        competitions = supabase.table("competition").select("*").order("date_start", desc=True).execute()
        comps = competitions.data if competitions.data else []
        
        if not comps:
            st.info("No competitions found.")
        else:
            for comp in comps:
                with st.expander(f"🏆 {comp['name']} ({comp['date_start']} to {comp['date_end']})"):
                    st.write(f"**Competition ID:** {comp['competition_id']}")
                    st.write(f"**Name:** {comp['name']}")
                    st.write(f"**Address:** {comp['address']}")
                    st.write(f"**Start Date:** {comp['date_start']}")
                    st.write(f"**End Date:** {comp['date_end']}")
                    
                    # Delete competition
                    if st.button(f"🗑️ Delete Competition", key=f"del_comp_{comp['competition_id']}"):
                        try:
                            supabase.table("competition").delete().eq("competition_id", comp['competition_id']).execute()
                            st.success("Competition deleted!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    except Exception as e:
        st.error(f"Error loading competitions: {str(e)}")
    
    st.divider()
    
    # Add new competition
    st.write("### Add New Competition")
    with st.form("add_competition"):
        comp_id = st.number_input("Competition ID*", min_value=1, step=1, help="Unique ID for the competition")
        comp_name = st.text_input("Competition Name*", help="Name of the competition")
        comp_address = st.text_area("Address*", help="Location of the competition")
        
        col1, col2 = st.columns(2)
        with col1:
            comp_start = st.date_input("Start Date*", min_value=date.today())
        with col2:
            comp_end = st.date_input("End Date*", min_value=date.today())
        
        submit_comp = st.form_submit_button("Add Competition", type="primary")
        
        if submit_comp:
            if not all([comp_id, comp_name, comp_address, comp_start, comp_end]):
                st.error("Please fill in all fields!")
            elif comp_start > comp_end:
                st.error("Start date must be before or equal to end date!")
            elif comp_start.year != comp_end.year:
                st.error("Start and end dates must be in the same year!")
            else:
                try:
                    supabase.table("competition").insert({
                        "competition_id": comp_id,
                        "name": comp_name,
                        "address": comp_address,
                        "date_start": comp_start.isoformat(),
                        "date_end": comp_end.isoformat()
                    }).execute()
                    st.success(f"✅ Competition '{comp_name}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# ==================== ROUNDS TAB ====================
with tab2:
    st.subheader("🎯 Round Management")
    
    # View rounds
    st.write("### View All Rounds")
    try:
        rounds = supabase.table("round").select("*").order("round_id").execute()
        rounds_list = rounds.data if rounds.data else []
        
        if not rounds_list:
            st.info("No rounds found.")
        else:
            for rnd in rounds_list:
                with st.expander(f"🎯 {rnd['name']} - {rnd['age_group']}"):
                    st.write(f"**Round ID:** {rnd['round_id']}")
                    st.write(f"**Name:** {rnd['name']}")
                    st.write(f"**Age Group:** {rnd['age_group']}")
                    
                    # Show compatible equipment
                    try:
                        compat = supabase.table("round_equipment_compatibility").select(
                            "equipment:equipment_id(name)"
                        ).eq("round_id", rnd['round_id']).execute()
                        
                        if compat.data:
                            equipment_names = [item['equipment']['name'] for item in compat.data if item.get('equipment')]
                            st.write(f"**Compatible Equipment:** {', '.join(equipment_names)}")
                    except:
                        pass
                    
                    # Delete round
                    if st.button(f"🗑️ Delete Round", key=f"del_round_{rnd['round_id']}"):
                        try:
                            supabase.table("round").delete().eq("round_id", rnd['round_id']).execute()
                            st.success("Round deleted!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    except Exception as e:
        st.error(f"Error loading rounds: {str(e)}")
    
    st.divider()
    
    # Add new round
    st.write("### Add New Round")
    with st.form("add_round"):
        round_id = st.number_input("Round ID*", min_value=1, step=1, help="Unique ID for the round")
        round_name = st.text_input("Round Name*", help="Name of the round")
        age_group = st.selectbox(
            "Age Group*",
            ["open", "50+", "60+", "70+", "under 21", "under 18", "under 16", "under 14"],
            help="Age group for this round"
        )
        
        submit_round = st.form_submit_button("Add Round", type="primary")
        
        if submit_round:
            if not all([round_id, round_name, age_group]):
                st.error("Please fill in all fields!")
            else:
                try:
                    supabase.table("round").insert({
                        "round_id": round_id,
                        "name": round_name,
                        "age_group": age_group
                    }).execute()
                    st.success(f"✅ Round '{round_name}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# ==================== RANGES TAB ====================
with tab3:
    st.subheader("📏 Range Management")
    
    # View ranges
    st.write("### View All Ranges")
    try:
        ranges = supabase.table("range").select("*, target_face:target_face_id(diameter, unit_of_length)").order("range_id").execute()
        ranges_list = ranges.data if ranges.data else []
        
        if not ranges_list:
            st.info("No ranges found.")
        else:
            for rng in ranges_list:
                target_info = ""
                if rng.get('target_face'):
                    target_info = f" | Target: {rng['target_face']['diameter']}{rng['target_face']['unit_of_length']}"
                
                with st.expander(f"📏 Range {rng['range_id']} - {rng['distance']}{rng['unit_of_length']}{target_info}"):
                    st.write(f"**Range ID:** {rng['range_id']}")
                    st.write(f"**Distance:** {rng['distance']} {rng['unit_of_length']}")
                    st.write(f"**Target Face ID:** {rng['target_face_id']}")
                    if rng.get('target_face'):
                        st.write(f"**Target Diameter:** {rng['target_face']['diameter']} {rng['target_face']['unit_of_length']}")
                    
                    # Delete range
                    if st.button(f"🗑️ Delete Range", key=f"del_range_{rng['range_id']}"):
                        try:
                            supabase.table("range").delete().eq("range_id", rng['range_id']).execute()
                            st.success("Range deleted!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    except Exception as e:
        st.error(f"Error loading ranges: {str(e)}")
    
    st.divider()
    
    # Add new range
    st.write("### Add New Range")
    
    # First, show target face management
    with st.expander("🎯 Manage Target Faces"):
        st.write("#### Add New Target Face")
        with st.form("add_target_face"):
            tf_diameter = st.number_input("Diameter*", min_value=1, step=1)
            tf_unit = st.selectbox(
                "Unit*",
                ["mm", "cm", "dm", "m", "in", "ft"],
                help="Unit of measurement"
            )
            
            submit_tf = st.form_submit_button("Add Target Face")
            
            if submit_tf:
                try:
                    result = supabase.table("target_face").insert({
                        "diameter": tf_diameter,
                        "unit_of_length": tf_unit
                    }).execute()
                    st.success(f"✅ Target face added! ID: {result.data[0]['target_face_id']}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with st.form("add_range"):
        # Get target faces
        try:
            target_faces = supabase.table("target_face").select("*").execute()
            tf_list = target_faces.data if target_faces.data else []
            
            if not tf_list:
                st.warning("Please add a target face first!")
                tf_options = {}
            else:
                tf_options = {f"ID {tf['target_face_id']}: {tf['diameter']}{tf['unit_of_length']}": tf['target_face_id'] for tf in tf_list}
        except:
            tf_options = {}
        
        if tf_options:
            selected_tf = st.selectbox("Target Face*", list(tf_options.keys()))
            target_face_id = tf_options[selected_tf]
        else:
            target_face_id = None
        
        range_distance = st.number_input("Distance*", min_value=1, step=1)
        range_unit = st.selectbox(
            "Unit*",
            ["mm", "cm", "dm", "m", "in", "ft", "yd"],
            index=3,
            help="Unit of measurement for distance"
        )
        
        submit_range = st.form_submit_button("Add Range", type="primary")
        
        if submit_range:
            if not target_face_id:
                st.error("Please add a target face first!")
            elif not range_distance:
                st.error("Please fill in all fields!")
            else:
                try:
                    supabase.table("range").insert({
                        "target_face_id": target_face_id,
                        "distance": range_distance,
                        "unit_of_length": range_unit
                    }).execute()
                    st.success(f"✅ Range added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# ==================== YEARLY CHAMPIONSHIPS TAB ====================
with tab4:
    st.subheader("🎪 Yearly Club Championship Management")
    
    # View championships
    st.write("### View All Yearly Championships")
    try:
        championships = supabase.table("yearly_club_championship").select("*").order("year", desc=True).execute()
        champs = championships.data if championships.data else []
        
        if not champs:
            st.info("No yearly championships found.")
        else:
            for champ in champs:
                with st.expander(f"🎪 {champ['name']} ({champ['year']})"):
                    st.write(f"**Championship ID:** {champ['yearly_club_championship_id']}")
                    st.write(f"**Name:** {champ['name']}")
                    st.write(f"**Year:** {champ['year']}")
                    
                    # Show linked competitions
                    try:
                        linked = supabase.table("event_context").select(
                            "competition:competition_id(name)"
                        ).eq("yearly_club_championship_id", champ['yearly_club_championship_id']).execute()
                        
                        if linked.data:
                            comp_names = list(set([item['competition']['name'] for item in linked.data if item.get('competition')]))
                            st.write(f"**Linked Competitions:** {', '.join(comp_names)}")
                    except:
                        pass
                    
                    # Delete championship
                    if st.button(f"🗑️ Delete Championship", key=f"del_champ_{champ['yearly_club_championship_id']}"):
                        try:
                            supabase.table("yearly_club_championship").delete().eq("yearly_club_championship_id", champ['yearly_club_championship_id']).execute()
                            st.success("Championship deleted!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    except Exception as e:
        st.error(f"Error loading championships: {str(e)}")
    
    st.divider()
    
    # Add new championship
    st.write("### Add New Yearly Championship")
    with st.form("add_championship"):
        champ_id = st.number_input("Championship ID*", min_value=1, step=1)
        champ_name = st.text_input("Championship Name*")
        champ_year = st.number_input("Year*", min_value=2000, max_value=2100, value=2025, step=1)
        
        submit_champ = st.form_submit_button("Add Championship", type="primary")
        
        if submit_champ:
            if not all([champ_id, champ_name, champ_year]):
                st.error("Please fill in all fields!")
            else:
                try:
                    supabase.table("yearly_club_championship").insert({
                        "yearly_club_championship_id": champ_id,
                        "name": champ_name,
                        "year": champ_year
                    }).execute()
                    st.success(f"✅ Championship '{champ_name}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# ==================== EVENT CONTEXTS TAB ====================
with tab5:
    st.subheader("🎪 Event Context Management")
    st.info("Event contexts link competitions, rounds, ranges, and ends together to form complete events.")
    
    # View event contexts
    st.write("### View All Event Contexts")
    try:
        contexts = supabase.table("event_context").select(
            "*, yearly_club_championship:yearly_club_championship_id(name), competition:competition_id(name), round:round_id(name), range:range_id(distance, unit_of_length)"
        ).order("event_context_id").execute()
        
        contexts_list = contexts.data if contexts.data else []
        
        if not contexts_list:
            st.info("No event contexts found.")
        else:
            for ctx in contexts_list:
                champ_name = ctx['yearly_club_championship']['name'] if ctx.get('yearly_club_championship') else "N/A"
                comp_name = ctx['competition']['name'] if ctx.get('competition') else "Unknown"
                round_name = ctx['round']['name'] if ctx.get('round') else "Unknown"
                range_info = f"{ctx['range']['distance']}{ctx['range']['unit_of_length']}" if ctx.get('range') else "Unknown"
                
                with st.expander(f"🎯 {ctx['event_context_id']}"):
                    st.write(f"**Event Context ID:** {ctx['event_context_id']}")
                    st.write(f"**Championship:** {champ_name}")
                    st.write(f"**Competition:** {comp_name}")
                    st.write(f"**Round:** {round_name}")
                    st.write(f"**Range:** {range_info}")
                    st.write(f"**End Order:** {ctx['end_order']}")
                    
                    # Delete context
                    if st.button(f"🗑️ Delete Context", key=f"del_ctx_{ctx['event_context_id']}"):
                        try:
                            supabase.table("event_context").delete().eq("event_context_id", ctx['event_context_id']).execute()
                            st.success("Event context deleted!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    except Exception as e:
        st.error(f"Error loading event contexts: {str(e)}")
    
    st.divider()
    
    # Add new event context
    st.write("### Add New Event Context")
    with st.form("add_event_context"):
        # Load options
        try:
            champs = supabase.table("yearly_club_championship").select("*").execute().data or []
            comps = supabase.table("competition").select("*").execute().data or []
            rnds = supabase.table("round").select("*").execute().data or []
            rngs = supabase.table("range").select("*").execute().data or []
        except:
            champs = []
            comps = []
            rnds = []
            rngs = []
        
        # Championship (optional)
        champ_options = ["None (No championship)"] + [f"{c['yearly_club_championship_id']} - {c['name']}" for c in champs]
        selected_champ = st.selectbox("Yearly Championship (Optional)", champ_options)
        champ_id = None if selected_champ == "None (No championship)" else int(selected_champ.split(" - ")[0])
        
        # Competition (required)
        comp_options = [f"{c['competition_id']} - {c['name']}" for c in comps]
        if comp_options:
            selected_comp = st.selectbox("Competition*", comp_options)
            comp_id = int(selected_comp.split(" - ")[0])
        else:
            st.warning("No competitions available!")
            comp_id = None
        
        # Round (required)
        round_options = [f"{r['round_id']} - {r['name']}" for r in rnds]
        if round_options:
            selected_round = st.selectbox("Round*", round_options)
            round_id = int(selected_round.split(" - ")[0])
        else:
            st.warning("No rounds available!")
            round_id = None
        
        # Range (required)
        range_options = [f"{r['range_id']} - {r['distance']}{r['unit_of_length']}" for r in rngs]
        if range_options:
            selected_range = st.selectbox("Range*", range_options)
            range_id = int(selected_range.split(" - ")[0])
        else:
            st.warning("No ranges available!")
            range_id = None
        
        # End order
        end_order = st.number_input("End Order*", min_value=1, step=1, value=1, help="Sequential number for this end")
        
        submit_ctx = st.form_submit_button("Add Event Context", type="primary")
        
        if submit_ctx:
            if not all([comp_id, round_id, range_id, end_order]):
                st.error("Please fill in all required fields!")
            else:
                try:
                    # Generate event context ID
                    event_context_id = f"{comp_id}-{round_id}-{range_id}-{end_order}"
                    
                    supabase.table("event_context").insert({
                        "event_context_id": event_context_id,
                        "yearly_club_championship_id": champ_id,
                        "competition_id": comp_id,
                        "round_id": round_id,
                        "range_id": range_id,
                        "end_order": end_order
                    }).execute()
                    st.success(f"✅ Event context '{event_context_id}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# ==================== MANAGE PARTICIPANTS TAB ====================
with tab6:
    st.subheader("👥 Manage Participants")
    st.info("View, add, delete, and modify participants for competitions you manage.")
    
    # Filter by recorder's assignments
    st.write("### Your Assigned Competitions")
    
    for assignment in recorder_assignments:
        comp_data = supabase.table("competition").select("name").eq("competition_id", assignment['competition_id']).execute()
        round_data = supabase.table("round").select("name").eq("round_id", assignment['round_id']).execute()
        
        comp_name = comp_data.data[0]['name'] if comp_data.data else "Unknown"
        round_name = round_data.data[0]['name'] if round_data.data else "Unknown"
        
        with st.expander(f"🏆 {comp_name} - {round_name}"):
            # Get participants for this competition/round
            try:
                # Get event contexts for this competition/round
                contexts = supabase.table("event_context").select("event_context_id").eq(
                    "competition_id", assignment['competition_id']
                ).eq("round_id", assignment['round_id']).execute()
                
                context_ids = [ctx['event_context_id'] for ctx in (contexts.data or [])]
                
                if context_ids:
                    # Get participants
                    participants_data = []
                    for ctx_id in context_ids:
                        scores = supabase.table("participant_score").select(
                            "participant_id, status, account:participant_id(fullname, email_address)"
                        ).eq("event_context_id", ctx_id).eq("type", "competition").execute()
                        
                        if scores.data:
                            participants_data.extend(scores.data)
                    
                    # Get unique participants
                    unique_participants = {}
                    for p in participants_data:
                        if p['participant_id'] not in unique_participants:
                            unique_participants[p['participant_id']] = p
                    
                    if unique_participants:
                        st.write(f"**Participants:** {len(unique_participants)}")
                        for pid, p in unique_participants.items():
                            if p.get('account'):
                                st.write(f"- {p['account']['fullname']} ({p['account']['email_address']}) - Status: {p['status']}")
                    else:
                        st.info("No participants enrolled yet.")
                else:
                    st.info("No event contexts found for this competition/round.")
                    
            except Exception as e:
                st.error(f"Error loading participants: {str(e)}")
