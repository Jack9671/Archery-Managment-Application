import streamlit as st
from datetime import date, datetime
from utility_function.initilize_dbconnection import supabase
import hashlib

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please log in to access the admin page.")
    st.info("Navigate to the 'Sign Up Log In' page to access your account.")
    st.stop()

# Check if user is Admin
user_id = st.session_state.get('user_id')
try:
    admin_check = supabase.table("admin").select("admin_id").eq("admin_id", user_id).execute()
    is_admin = bool(admin_check.data)
except:
    is_admin = False

if not is_admin:
    st.error("🚫 Access Denied")
    st.warning("You must be an Admin to access this page.")
    st.info("Please contact an administrator if you believe you should have access.")
    st.stop()

# Page header
st.title("👤 Admin Account Management")
st.write(f"**Logged in as:** {st.session_state.get('fullname', 'N/A')}")
st.divider()

# Tabs for different admin functions
tab1, tab2, tab3, tab4 = st.tabs(["📋 View Accounts", "➕ Add Account", "✏️ Modify Account", "🗑️ Delete Account"])

# ==================== VIEW ACCOUNTS TAB ====================
with tab1:
    st.subheader("📋 All Accounts")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        role_filter = st.selectbox(
            "Filter by Role",
            ["All", "Admin", "Recorder", "Archer", "Regular User"],
            help="Filter accounts by their role"
        )
    
    with col2:
        sex_filter = st.selectbox(
            "Filter by Sex",
            ["All", "male", "female"],
            help="Filter accounts by sex"
        )
    
    with col3:
        country_filter = st.text_input(
            "Filter by Country",
            placeholder="e.g., USA, Vietnam",
            help="Enter country name to filter"
        )
    
    # Search by name or email
    search_query = st.text_input(
        "🔍 Search by Name or Email",
        placeholder="Enter name or email...",
        help="Search accounts by fullname or email address"
    )
    
    try:
        # Fetch all accounts
        query = supabase.table("account").select(
            "account_id, email_address, fullname, country, date_of_birth, sex, avatar_url, created_at"
        )
        
        accounts_response = query.order("account_id").execute()
        accounts = accounts_response.data if accounts_response.data else []
        
        # Get role information
        admins = supabase.table("admin").select("admin_id").execute()
        admin_ids = [a['admin_id'] for a in (admins.data if admins.data else [])]
        
        recorders = supabase.table("recorder").select("recorder_id").execute()
        recorder_ids = list(set([r['recorder_id'] for r in (recorders.data if recorders.data else [])]))
        
        archers = supabase.table("archer").select("archer_id").execute()
        archer_ids = [a['archer_id'] for a in (archers.data if archers.data else [])]
        
        # Apply filters
        filtered_accounts = []
        for account in accounts:
            # Role filter
            account_roles = []
            if account['account_id'] in admin_ids:
                account_roles.append("Admin")
            if account['account_id'] in recorder_ids:
                account_roles.append("Recorder")
            if account['account_id'] in archer_ids:
                account_roles.append("Archer")
            if not account_roles:
                account_roles.append("Regular User")
            
            if role_filter != "All" and role_filter not in account_roles:
                continue
            
            # Sex filter
            if sex_filter != "All" and account['sex'] != sex_filter:
                continue
            
            # Country filter
            if country_filter and country_filter.lower() not in account['country'].lower():
                continue
            
            # Search filter
            if search_query:
                if (search_query.lower() not in account['fullname'].lower() and 
                    search_query.lower() not in account['email_address'].lower()):
                    continue
            
            account['roles'] = ", ".join(account_roles)
            filtered_accounts.append(account)
        
        st.info(f"📊 Showing {len(filtered_accounts)} of {len(accounts)} accounts")
        
        # Display accounts
        for account in filtered_accounts:
            with st.expander(f"👤 {account['fullname']} ({account['email_address']}) - {account['roles']}"):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.image(account['avatar_url'], width=120)
                
                with col2:
                    st.write(f"**Account ID:** {account['account_id']}")
                    st.write(f"**Full Name:** {account['fullname']}")
                    st.write(f"**Email:** {account['email_address']}")
                    st.write(f"**Country:** {account['country']}")
                    st.write(f"**Date of Birth:** {account['date_of_birth']}")
                    st.write(f"**Sex:** {account['sex']}")
                    st.write(f"**Roles:** {account['roles']}")
                    st.write(f"**Created At:** {account['created_at']}")
        
    except Exception as e:
        st.error(f"Error loading accounts: {str(e)}")

# ==================== ADD ACCOUNT TAB ====================
with tab2:
    st.subheader("➕ Create New Account")
    
    with st.form("add_account_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_email = st.text_input("Email Address*", help="Required - used for login")
            new_password = st.text_input("Password*", type="password", help="Minimum 6 characters")
            new_fullname = st.text_input("Full Name*", help="Required")
            new_country = st.text_input("Country*", help="Required")
        
        with col2:
            new_dob = st.date_input(
                "Date of Birth*",
                value=date(2000, 1, 1),
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                help="Required"
            )
            new_sex = st.selectbox("Sex*", ["male", "female"], help="Required")
            
            # Role assignment
            st.write("**Assign Roles (Optional):**")
            assign_admin = st.checkbox("Make Admin")
            assign_archer = st.checkbox("Make Archer")
        
        # Default equipment for archer
        default_equipment = None
        if assign_archer:
            try:
                equipment_response = supabase.table("equipment").select("equipment_id, name").execute()
                equipment_list = equipment_response.data if equipment_response.data else []
                if equipment_list:
                    equipment_options = {f"{eq['equipment_id']} - {eq['name']}": eq['equipment_id'] for eq in equipment_list}
                    selected_equipment = st.selectbox("Default Equipment*", list(equipment_options.keys()))
                    default_equipment = equipment_options[selected_equipment]
            except Exception as e:
                st.warning(f"Could not load equipment: {str(e)}")
        
        submit_add = st.form_submit_button("Create Account", type="primary")
        
        if submit_add:
            # Validate
            if not all([new_email, new_password, new_fullname, new_country, new_dob, new_sex]):
                st.error("Please fill in all required fields!")
                st.stop()
            
            if len(new_password) < 6:
                st.error("Password must be at least 6 characters!")
                st.stop()
            
            if assign_archer and not default_equipment:
                st.error("Please select default equipment for archer!")
                st.stop()
            
            try:
                # Check if email exists
                existing = supabase.table("account").select("email_address").eq("email_address", new_email).execute()
                if existing.data:
                    st.error("Email already exists!")
                    st.stop()
                
                # Hash password
                hash_password = hashlib.sha256(new_password.encode()).hexdigest()
                
                # Insert account
                account_response = supabase.table("account").insert({
                    "email_address": new_email,
                    "hash_password": hash_password,
                    "fullname": new_fullname,
                    "country": new_country,
                    "date_of_birth": new_dob.isoformat(),
                    "sex": new_sex,
                    "avatar_url": "https://ghcpcyvethwdzzgyymfp.supabase.co/storage/v1/object/public/User%20Avatar/Default_Avatar.jpg"
                }).execute()
                
                if account_response.data:
                    new_account_id = account_response.data[0]['account_id']
                    st.success(f"✅ Account created successfully! Account ID: {new_account_id}")
                    
                    # Assign roles
                    if assign_admin:
                        try:
                            supabase.table("admin").insert({"admin_id": new_account_id}).execute()
                            st.success("✅ Admin role assigned!")
                        except Exception as e:
                            st.warning(f"Could not assign admin role: {str(e)}")
                    
                    if assign_archer:
                        try:
                            supabase.table("archer").insert({
                                "archer_id": new_account_id,
                                "default_equipment_id": default_equipment
                            }).execute()
                            st.success("✅ Archer role assigned!")
                        except Exception as e:
                            st.warning(f"Could not assign archer role: {str(e)}")
                    
                    st.balloons()
                
            except Exception as e:
                st.error(f"Error creating account: {str(e)}")

# ==================== MODIFY ACCOUNT TAB ====================
with tab3:
    st.subheader("✏️ Modify Existing Account")
    
    # Select account to modify
    try:
        accounts_response = supabase.table("account").select("account_id, email_address, fullname").order("account_id").execute()
        accounts = accounts_response.data if accounts_response.data else []
        
        if not accounts:
            st.info("No accounts found.")
        else:
            account_options = {f"{acc['account_id']} - {acc['fullname']} ({acc['email_address']})": acc['account_id'] for acc in accounts}
            selected_account = st.selectbox("Select Account to Modify", list(account_options.keys()))
            modify_account_id = account_options[selected_account]
            
            # Fetch account details
            account_data = supabase.table("account").select("*").eq("account_id", modify_account_id).execute()
            if account_data.data:
                current_account = account_data.data[0]
                
                # Check current roles
                is_admin_now = bool(supabase.table("admin").select("admin_id").eq("admin_id", modify_account_id).execute().data)
                is_archer_now = bool(supabase.table("archer").select("archer_id").eq("archer_id", modify_account_id).execute().data)
                
                with st.form("modify_account_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        mod_email = st.text_input("Email Address", value=current_account['email_address'])
                        mod_fullname = st.text_input("Full Name", value=current_account['fullname'])
                        mod_country = st.text_input("Country", value=current_account['country'])
                        mod_sex = st.selectbox("Sex", ["male", "female"], index=0 if current_account['sex'] == 'male' else 1)
                    
                    with col2:
                        mod_dob = st.date_input(
                            "Date of Birth",
                            value=datetime.strptime(current_account['date_of_birth'], '%Y-%m-%d').date()
                        )
                        
                        st.write("**Update Password (Optional):**")
                        mod_password = st.text_input("New Password", type="password", help="Leave blank to keep current password")
                        
                        st.write("**Manage Roles:**")
                        mod_admin = st.checkbox("Admin Role", value=is_admin_now)
                        mod_archer = st.checkbox("Archer Role", value=is_archer_now)
                    
                    submit_modify = st.form_submit_button("Update Account", type="primary")
                    
                    if submit_modify:
                        try:
                            # Update account
                            update_data = {
                                "email_address": mod_email,
                                "fullname": mod_fullname,
                                "country": mod_country,
                                "date_of_birth": mod_dob.isoformat(),
                                "sex": mod_sex
                            }
                            
                            # Update password if provided
                            if mod_password:
                                if len(mod_password) >= 6:
                                    update_data["hash_password"] = hashlib.sha256(mod_password.encode()).hexdigest()
                                else:
                                    st.error("Password must be at least 6 characters!")
                                    st.stop()
                            
                            supabase.table("account").update(update_data).eq("account_id", modify_account_id).execute()
                            st.success("✅ Account updated successfully!")
                            
                            # Update roles
                            # Admin role
                            if mod_admin and not is_admin_now:
                                supabase.table("admin").insert({"admin_id": modify_account_id}).execute()
                                st.success("✅ Admin role added!")
                            elif not mod_admin and is_admin_now:
                                supabase.table("admin").delete().eq("admin_id", modify_account_id).execute()
                                st.success("✅ Admin role removed!")
                            
                            # Archer role
                            if mod_archer and not is_archer_now:
                                # Need to select equipment
                                equipment_response = supabase.table("equipment").select("equipment_id").execute()
                                if equipment_response.data:
                                    default_eq = equipment_response.data[0]['equipment_id']
                                    supabase.table("archer").insert({
                                        "archer_id": modify_account_id,
                                        "default_equipment_id": default_eq
                                    }).execute()
                                    st.success("✅ Archer role added!")
                            elif not mod_archer and is_archer_now:
                                supabase.table("archer").delete().eq("archer_id", modify_account_id).execute()
                                st.success("✅ Archer role removed!")
                            
                            st.balloons()
                            
                        except Exception as e:
                            st.error(f"Error updating account: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading accounts: {str(e)}")

# ==================== DELETE ACCOUNT TAB ====================
with tab4:
    st.subheader("🗑️ Delete Account")
    st.warning("⚠️ Warning: Deleting an account will remove all associated data. This action cannot be undone!")
    
    try:
        accounts_response = supabase.table("account").select("account_id, email_address, fullname").order("account_id").execute()
        accounts = accounts_response.data if accounts_response.data else []
        
        if not accounts:
            st.info("No accounts found.")
        else:
            account_options = {f"{acc['account_id']} - {acc['fullname']} ({acc['email_address']})": acc['account_id'] for acc in accounts}
            selected_delete = st.selectbox("Select Account to Delete", list(account_options.keys()), key="delete_select")
            delete_account_id = account_options[selected_delete]
            
            # Show account details
            account_data = supabase.table("account").select("*").eq("account_id", delete_account_id).execute()
            if account_data.data:
                acc = account_data.data[0]
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(acc['avatar_url'], width=120)
                with col2:
                    st.write(f"**Account ID:** {acc['account_id']}")
                    st.write(f"**Name:** {acc['fullname']}")
                    st.write(f"**Email:** {acc['email_address']}")
                    st.write(f"**Country:** {acc['country']}")
                
                # Confirmation
                confirm_text = st.text_input(
                    f"Type 'DELETE {delete_account_id}' to confirm deletion",
                    help="Confirmation required"
                )
                
                if st.button("🗑️ Delete Account", type="primary", disabled=(confirm_text != f"DELETE {delete_account_id}")):
                    try:
                        # Delete account (cascading deletes will handle related tables)
                        supabase.table("account").delete().eq("account_id", delete_account_id).execute()
                        st.success(f"✅ Account {delete_account_id} deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting account: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading accounts: {str(e)}")
