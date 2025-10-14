import streamlit as st
from utility_function.initilize_dbconnection import supabase

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please log in to view equipment information.")
    st.info("Navigate to the 'Sign Up Log In' page to access your account.")
    st.stop()

# Page header
st.title("🏹 Equipment & Bow Types")
st.write(f"**Logged in as:** {st.session_state.get('fullname', 'N/A')}")
st.write("Browse different types of archery equipment and see which rounds they're compatible with.")
st.divider()

# Tabs for different views
tab1, tab2 = st.tabs(["🏹 Browse Equipment", "🔗 Round Compatibility"])

# ==================== BROWSE EQUIPMENT TAB ====================
with tab1:
    st.subheader("🏹 All Equipment Types")
    
    # Search filter
    search_equipment = st.text_input(
        "🔍 Search Equipment",
        placeholder="Enter equipment name...",
        help="Search equipment by name"
    )
    
    try:
        # Fetch all equipment
        equipment_response = supabase.table("equipment").select("*").order("equipment_id").execute()
        equipment_list = equipment_response.data if equipment_response.data else []
        
        # Apply search filter
        if search_equipment:
            equipment_list = [eq for eq in equipment_list if search_equipment.lower() in eq['name'].lower()]
        
        if not equipment_list:
            st.info("No equipment found.")
        else:
            st.info(f"📊 Found {len(equipment_list)} equipment type(s)")
            
            for equipment in equipment_list:
                with st.expander(f"🏹 {equipment['name']}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Equipment ID:** {equipment['equipment_id']}")
                        st.write(f"**Name:** {equipment['name']}")
                        
                        if equipment.get('description'):
                            st.write(f"**Description:**")
                            st.info(equipment['description'])
                        else:
                            st.caption("*No description available*")
                    
                    with col2:
                        # Show compatible rounds
                        try:
                            compatible_rounds = supabase.table("round_equipment_compatibility").select(
                                "round:round_id(round_id, name, age_group)"
                            ).eq("equipment_id", equipment['equipment_id']).execute()
                            
                            if compatible_rounds.data:
                                st.write(f"**Compatible Rounds:** ({len(compatible_rounds.data)})")
                                for item in compatible_rounds.data:
                                    if item.get('round'):
                                        rnd = item['round']
                                        st.caption(f"🎯 {rnd['name']} ({rnd['age_group']})")
                            else:
                                st.write("**Compatible Rounds:**")
                                st.caption("*No rounds specified*")
                        except Exception as e:
                            st.warning(f"Could not load compatible rounds: {str(e)}")
                    
                    st.divider()
                    
                    # Check if this is user's default equipment
                    user_id = st.session_state.get('user_id')
                    try:
                        archer_data = supabase.table("archer").select("default_equipment_id").eq("archer_id", user_id).execute()
                        if archer_data.data:
                            default_eq_id = archer_data.data[0]['default_equipment_id']
                            if default_eq_id == equipment['equipment_id']:
                                st.success("✅ This is your default equipment")
                            else:
                                if st.button(f"Set as Default", key=f"set_default_{equipment['equipment_id']}"):
                                    try:
                                        supabase.table("archer").update({
                                            "default_equipment_id": equipment['equipment_id']
                                        }).eq("archer_id", user_id).execute()
                                        st.success("✅ Default equipment updated!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                    except:
                        pass
    
    except Exception as e:
        st.error(f"Error loading equipment: {str(e)}")

# ==================== ROUND COMPATIBILITY TAB ====================
with tab2:
    st.subheader("🔗 Round-Equipment Compatibility")
    st.info("See which equipment types are allowed for each round.")
    
    # View selector
    view_mode = st.radio(
        "View By",
        ["By Round", "By Equipment"],
        horizontal=True,
        help="Choose how to view compatibility information"
    )
    
    if view_mode == "By Round":
        # ==================== VIEW BY ROUND ====================
        st.write("### 🎯 Equipment Compatible with Each Round")
        
        try:
            # Fetch all rounds
            rounds = supabase.table("round").select("*").order("name").execute()
            rounds_list = rounds.data if rounds.data else []
            
            if not rounds_list:
                st.info("No rounds found.")
            else:
                # Search filter
                search_round = st.text_input(
                    "🔍 Search Rounds",
                    placeholder="Enter round name...",
                    key="search_round"
                )
                
                # Age group filter
                age_filter = st.selectbox(
                    "Filter by Age Group",
                    ["All", "open", "50+", "60+", "70+", "under 21", "under 18", "under 16", "under 14"]
                )
                
                # Apply filters
                filtered_rounds = rounds_list
                if search_round:
                    filtered_rounds = [r for r in filtered_rounds if search_round.lower() in r['name'].lower()]
                if age_filter != "All":
                    filtered_rounds = [r for r in filtered_rounds if r['age_group'] == age_filter]
                
                st.info(f"📊 Showing {len(filtered_rounds)} round(s)")
                
                for rnd in filtered_rounds:
                    with st.expander(f"🎯 {rnd['name']} - {rnd['age_group']}"):
                        st.write(f"**Round ID:** {rnd['round_id']}")
                        st.write(f"**Name:** {rnd['name']}")
                        st.write(f"**Age Group:** {rnd['age_group']}")
                        
                        st.divider()
                        
                        # Get compatible equipment
                        try:
                            compatible_equipment = supabase.table("round_equipment_compatibility").select(
                                "equipment:equipment_id(equipment_id, name, description)"
                            ).eq("round_id", rnd['round_id']).execute()
                            
                            if compatible_equipment.data:
                                st.write(f"**✅ Compatible Equipment ({len(compatible_equipment.data)}):**")
                                
                                for item in compatible_equipment.data:
                                    if item.get('equipment'):
                                        eq = item['equipment']
                                        with st.container(border=True):
                                            st.write(f"🏹 **{eq['name']}**")
                                            if eq.get('description'):
                                                st.caption(eq['description'])
                            else:
                                st.warning("⚠️ No equipment compatibility defined for this round yet.")
                                st.caption("Any equipment may be allowed, or restrictions haven't been set.")
                        except Exception as e:
                            st.error(f"Error loading equipment: {str(e)}")
        
        except Exception as e:
            st.error(f"Error loading rounds: {str(e)}")
    
    else:
        # ==================== VIEW BY EQUIPMENT ====================
        st.write("### 🏹 Rounds Compatible with Each Equipment Type")
        
        try:
            # Fetch all equipment
            equipment = supabase.table("equipment").select("*").order("name").execute()
            equipment_list = equipment.data if equipment.data else []
            
            if not equipment_list:
                st.info("No equipment found.")
            else:
                # Search filter
                search_eq = st.text_input(
                    "🔍 Search Equipment",
                    placeholder="Enter equipment name...",
                    key="search_eq"
                )
                
                # Apply filter
                filtered_equipment = equipment_list
                if search_eq:
                    filtered_equipment = [eq for eq in filtered_equipment if search_eq.lower() in eq['name'].lower()]
                
                st.info(f"📊 Showing {len(filtered_equipment)} equipment type(s)")
                
                for eq in filtered_equipment:
                    with st.expander(f"🏹 {eq['name']}"):
                        st.write(f"**Equipment ID:** {eq['equipment_id']}")
                        st.write(f"**Name:** {eq['name']}")
                        
                        if eq.get('description'):
                            st.write(f"**Description:**")
                            st.info(eq['description'])
                        
                        st.divider()
                        
                        # Get compatible rounds
                        try:
                            compatible_rounds = supabase.table("round_equipment_compatibility").select(
                                "round:round_id(round_id, name, age_group)"
                            ).eq("equipment_id", eq['equipment_id']).execute()
                            
                            if compatible_rounds.data:
                                st.write(f"**✅ Compatible Rounds ({len(compatible_rounds.data)}):**")
                                
                                # Group by age group
                                age_groups = {}
                                for item in compatible_rounds.data:
                                    if item.get('round'):
                                        rnd = item['round']
                                        age_group = rnd['age_group']
                                        
                                        if age_group not in age_groups:
                                            age_groups[age_group] = []
                                        
                                        age_groups[age_group].append(rnd)
                                
                                for age_group, rounds in age_groups.items():
                                    st.write(f"**Age Group: {age_group}**")
                                    for rnd in rounds:
                                        st.caption(f"  🎯 {rnd['name']}")
                            else:
                                st.warning("⚠️ No rounds have been configured to use this equipment yet.")
                        except Exception as e:
                            st.error(f"Error loading rounds: {str(e)}")
        
        except Exception as e:
            st.error(f"Error loading equipment: {str(e)}")

# ==================== SIDEBAR INFO ====================
with st.sidebar:
    st.subheader("ℹ️ Equipment Information")
    
    # Show user's default equipment
    user_id = st.session_state.get('user_id')
    try:
        archer_data = supabase.table("archer").select(
            "default_equipment_id, equipment:default_equipment_id(name, description)"
        ).eq("archer_id", user_id).execute()
        
        if archer_data.data and archer_data.data[0].get('equipment'):
            eq = archer_data.data[0]['equipment']
            st.write("**Your Default Equipment:**")
            st.success(f"🏹 {eq['name']}")
            
            if eq.get('description'):
                with st.expander("Details"):
                    st.write(eq['description'])
            
            st.divider()
            
            # Show compatible rounds for user's equipment
            try:
                default_eq_id = archer_data.data[0]['default_equipment_id']
                compatible_rounds = supabase.table("round_equipment_compatibility").select(
                    "round:round_id(name, age_group)"
                ).eq("equipment_id", default_eq_id).execute()
                
                if compatible_rounds.data:
                    st.write("**Rounds You Can Participate In:**")
                    for item in compatible_rounds.data:
                        if item.get('round'):
                            rnd = item['round']
                            st.caption(f"🎯 {rnd['name']} ({rnd['age_group']})")
            except:
                pass
        else:
            st.info("You don't have a default equipment set.")
            st.write("Browse equipment and set one as your default!")
    except:
        st.info("Become an archer to set your default equipment.")
    
    st.divider()
    
    # Equipment statistics
    try:
        total_equipment = supabase.table("equipment").select("equipment_id").execute()
        total_rounds = supabase.table("round").select("round_id").execute()
        total_compat = supabase.table("round_equipment_compatibility").select("*").execute()
        
        st.write("**Database Statistics:**")
        st.metric("Total Equipment Types", len(total_equipment.data) if total_equipment.data else 0)
        st.metric("Total Rounds", len(total_rounds.data) if total_rounds.data else 0)
        st.metric("Compatibility Records", len(total_compat.data) if total_compat.data else 0)
    except:
        pass
