import streamlit as st
import pandas as pd
from utility_function.initilize_dbconnection import supabase
from utility_function.category_utility import (
    get_all_equipment, get_all_disciplines, get_all_age_divisions,
    get_all_categories, get_rounds_by_equipment, add_equipment,
    add_discipline, add_age_division, add_target_face, add_range, add_round
)

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("Please log in to access this page.")
    st.stop()

st.title("📂 Category & Equipment Management")
st.write(f"Welcome, {st.session_state.get('fullname')}!")

user_role = st.session_state.get('role')
is_aaf_member = user_role == 'australia_archery_federation'

# Create tabs
if is_aaf_member:
    tabs = st.tabs(["🎯 Equipment", "🏃 Disciplines", "👶 Age Divisions", "🎪 Categories", "➕ Add Options"])
    tab_equipment, tab_disciplines, tab_age, tab_categories, tab_add = tabs
else:
    tabs = st.tabs(["🎯 Equipment", "🏃 Disciplines", "👶 Age Divisions", "🎪 Categories"])
    tab_equipment = tabs[0]
    tab_disciplines = tabs[1]
    tab_age = tabs[2]
    tab_categories = tabs[3]

# Tab 1: Equipment
with tab_equipment:
    st.header("Equipment Types")
    st.write("Browse different types of archery equipment (bows)")
    
    equipment_df = get_all_equipment()
    
    if not equipment_df.empty:
        st.success(f"Found {len(equipment_df)} equipment type(s)")
        
        for idx, equipment in equipment_df.iterrows():
            with st.expander(f"🎯 {equipment['name']} (ID: {equipment['equipment_id']})"):
                st.write(f"**Equipment Name:** {equipment['name']}")
                st.write(f"**Description:**")
                st.write(equipment.get('description', 'No description available'))
                
                # Show rounds using this equipment
                st.divider()
                st.subheader("Rounds Using This Equipment")
                
                rounds_df = get_rounds_by_equipment(equipment['equipment_id'])
                
                if not rounds_df.empty:
                    st.dataframe(rounds_df[['round_id', 'name']], use_container_width=True)
                else:
                    st.info("No rounds found using this equipment.")
    else:
        st.info("No equipment types found.")

# Tab 2: Disciplines
with tab_disciplines:
    st.header("Archery Disciplines")
    st.write("Explore different archery disciplines and their descriptions")
    
    disciplines_df = get_all_disciplines()
    
    if not disciplines_df.empty:
        st.success(f"Found {len(disciplines_df)} discipline(s)")
        
        for idx, discipline in disciplines_df.iterrows():
            with st.expander(f"🏹 {discipline['name']} (ID: {discipline['discipline_id']})"):
                st.write(f"**Discipline Name:** {discipline['name']}")
                st.write(f"**Description:**")
                st.write(discipline.get('description', 'No description available'))
    else:
        st.info("No disciplines found.")

# Tab 3: Age Divisions
with tab_age:
    st.header("Age Divisions")
    st.write("View official age divisions for competitions")
    
    age_divisions_df = get_all_age_divisions()
    
    if not age_divisions_df.empty:
        st.success(f"Found {len(age_divisions_df)} age division(s)")
        
        # Display as a table
        display_df = age_divisions_df[['age_division_id', 'min_age', 'max_age']].copy()
        display_df['Age Range'] = display_df.apply(
            lambda row: f"{row['min_age']} - {row['max_age']} years", axis=1
        )
        
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No age divisions found.")

# Tab 4: Categories
with tab_categories:
    st.header("Competition Categories")
    st.write("Categories are combinations of discipline, age division, and equipment")
    
    categories_df = get_all_categories()
    
    if not categories_df.empty:
        st.success(f"Found {len(categories_df)} category/categories")
        
        # Display categories
        for idx, category in categories_df.iterrows():
            with st.expander(f"🏆 Category {category['category_id']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Discipline:**")
                    st.info(category.get('discipline_name', 'N/A'))
                
                with col2:
                    st.write("**Age Range:**")
                    st.info(category.get('age_range', 'N/A'))
                
                with col3:
                    st.write("**Equipment:**")
                    st.info(category.get('equipment_name', 'N/A'))
                
                st.write(f"**Category ID:** {category['category_id']}")
                st.write(f"**Discipline ID:** {category['discipline_id']}")
                st.write(f"**Age Division ID:** {category['age_division_id']}")
                st.write(f"**Equipment ID:** {category['equipment_id']}")
    else:
        st.info("No categories found.")

# Tab 5: Add Options (AAF Members only)
if is_aaf_member:
    with tab_add:
        st.header("Add New Options")
        st.write("Add new equipment, disciplines, age divisions, and more")
        st.warning("⚠️ These actions require AAF membership privileges")
        
        add_option = st.selectbox("What would you like to add?", [
            "",
            "Equipment",
            "Discipline",
            "Age Division",
            "Target Face",
            "Range",
            "Round"
        ])
        
        if add_option == "Equipment":
            with st.form("add_equipment_form"):
                st.subheader("➕ Add New Equipment")
                
                equipment_name = st.text_input("Equipment Name*", placeholder="e.g., Compound Bow")
                equipment_description = st.text_area("Description*", 
                    value="This is an equipment officially recognized by Australian Archery Federation",
                    help="Describe the equipment type")
                
                submit = st.form_submit_button("Add Equipment", type="primary")
                
                if submit:
                    if not equipment_name or not equipment_description:
                        st.error("Please fill in all fields!")
                    else:
                        result = add_equipment(equipment_name, equipment_description)
                        if result:
                            st.success(f"✅ Equipment added successfully! ID: {result['equipment_id']}")
                            st.balloons()
                        else:
                            st.error("Failed to add equipment.")
        
        elif add_option == "Discipline":
            with st.form("add_discipline_form"):
                st.subheader("➕ Add New Discipline")
                
                discipline_name = st.text_input("Discipline Name*", placeholder="e.g., Indoor Target Archery")
                discipline_description = st.text_area("Description*",
                    value="This is a discipline officially recognized by Australian Archery Federation",
                    help="Describe the discipline")
                
                submit = st.form_submit_button("Add Discipline", type="primary")
                
                if submit:
                    if not discipline_name or not discipline_description:
                        st.error("Please fill in all fields!")
                    else:
                        result = add_discipline(discipline_name, discipline_description)
                        if result:
                            st.success(f"✅ Discipline added successfully! ID: {result['discipline_id']}")
                            st.balloons()
                        else:
                            st.error("Failed to add discipline.")
        
        elif add_option == "Age Division":
            with st.form("add_age_division_form"):
                st.subheader("➕ Add New Age Division")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    min_age = st.number_input("Minimum Age*", min_value=0, max_value=150, value=18)
                
                with col2:
                    max_age = st.number_input("Maximum Age*", min_value=0, max_value=150, value=70)
                
                submit = st.form_submit_button("Add Age Division", type="primary")
                
                if submit:
                    if min_age >= max_age:
                        st.error("Minimum age must be less than maximum age!")
                    else:
                        result = add_age_division(min_age, max_age)
                        if result:
                            st.success(f"✅ Age division added successfully! ID: {result['age_division_id']}")
                            st.balloons()
                        else:
                            st.error("Failed to add age division.")
        
        elif add_option == "Target Face":
            with st.form("add_target_face_form"):
                st.subheader("➕ Add New Target Face")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    diameter = st.number_input("Diameter*", min_value=0.0, step=0.1, value=122.0)
                
                with col2:
                    unit_options = ["mm", "cm", "m", "km", "in", "ft", "yd", "mi", "pc"]
                    unit_of_length = st.selectbox("Unit of Length*", unit_options)
                
                submit = st.form_submit_button("Add Target Face", type="primary")
                
                if submit:
                    result = add_target_face(diameter, unit_of_length)
                    if result:
                        st.success(f"✅ Target face added successfully! ID: {result['target_face_id']}")
                        st.balloons()
                    else:
                        st.error("Failed to add target face.")
        
        elif add_option == "Range":
            with st.form("add_range_form"):
                st.subheader("➕ Add New Range")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    distance = st.number_input("Distance*", min_value=0.0, step=0.1, value=70.0)
                
                with col2:
                    unit_options = ["mm", "cm", "m", "km", "in", "ft", "yd", "mi", "pc"]
                    unit_of_length = st.selectbox("Unit of Length*", unit_options)
                
                with col3:
                    target_face_id = st.number_input("Target Face ID*", min_value=1, step=1, value=1)
                
                submit = st.form_submit_button("Add Range", type="primary")
                
                if submit:
                    result = add_range(distance, unit_of_length, target_face_id)
                    if result:
                        st.success(f"✅ Range added successfully! ID: {result['range_id']}")
                        st.balloons()
                    else:
                        st.error("Failed to add range.")
        
        elif add_option == "Round":
            with st.form("add_round_form"):
                st.subheader("➕ Add New Round")
                
                round_name = st.text_input("Round Name*", placeholder="e.g., Male U21 Longbow")
                category_id = st.number_input("Category ID*", min_value=1, step=1, value=1,
                    help="The category this round belongs to")
                
                submit = st.form_submit_button("Add Round", type="primary")
                
                if submit:
                    if not round_name:
                        st.error("Please enter a round name!")
                    else:
                        result = add_round(round_name, category_id)
                        if result:
                            st.success(f"✅ Round added successfully! ID: {result['round_id']}")
                            st.balloons()
                        else:
                            st.error("Failed to add round.")
        
        else:
            st.info("👆 Please select an option from the dropdown above.")
else:
    # Show info for non-AAF members
    st.info("ℹ️ Only Australian Archery Federation members can add new options. Contact the DB team to become an AAF member.")
