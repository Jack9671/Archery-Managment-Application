import streamlit as st
import pandas as pd
from utility_function.initilize_dbconnection import supabase
from utility_function.admin_utility import (
    get_total_accounts, get_deactivated_accounts_count, get_accounts_by_role,
    filter_accounts, search_account_by_email_and_dob, update_account,
    get_pending_reports, update_report_status, delete_report
)
from utility_function.sign_up_log_in_utility import get_countries
from datetime import date

# Check if user is logged in and is an admin
if not st.session_state.get('logged_in', False):
    st.warning("Please log in to access this page.")
    st.stop()

if st.session_state.get('role') != 'admin':
    st.error("Access denied. This page is only accessible to administrators.")
    st.stop()

st.title("Admin Dashboard")
st.write(f"Welcome, {st.session_state.get('fullname')}!")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔍 Browse Accounts", "✏️ Update Account", "📝 Account Reports"])

with tab1:
    st.header("Dashboard Overview")
    st.write("System statistics and metrics")
    
    # Fetch metrics
    total_accounts = get_total_accounts()
    deactivated_accounts = get_deactivated_accounts_count()
    admin_count = get_accounts_by_role("admin")
    aaf_count = get_accounts_by_role("australia_archery_federation")
    recorder_count = get_accounts_by_role("recorder")
    archer_count = get_accounts_by_role("archer")
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Accounts", total_accounts)
        st.metric("Deactivated Accounts", deactivated_accounts)
    
    with col2:
        st.metric("Admin Accounts", admin_count)
        st.metric("AAF Members", aaf_count)
    
    with col3:
        st.metric("Recorders", recorder_count)
        st.metric("Archers", archer_count)
    
    # Additional statistics
    st.divider()
    st.subheader("Account Activity")
    active_accounts = total_accounts - deactivated_accounts
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Accounts", active_accounts)
        if total_accounts > 0:
            active_percentage = (active_accounts / total_accounts) * 100
            st.metric("Active Percentage", f"{active_percentage:.1f}%")
    
    with col2:
        st.metric("Inactive Accounts", deactivated_accounts)
        if total_accounts > 0:
            inactive_percentage = (deactivated_accounts / total_accounts) * 100
            st.metric("Inactive Percentage", f"{inactive_percentage:.1f}%")

with tab2:
    st.header("Browse Accounts")
    st.write("Filter and view accounts in the system")
    
    # Filter section
    with st.expander("🔧 Configure Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            email_filter = st.text_input("Email Address", placeholder="Search by email...")
            fullname_filter = st.text_input("Full Name", placeholder="Search by name...")
        
        with col2:
            min_age = st.number_input("Minimum Age", min_value=0, max_value=150, value=0, step=1)
            max_age = st.number_input("Maximum Age", min_value=0, max_value=150, value=150, step=1)
        
        with col3:
            role_filter = st.selectbox("Role", ["all", "admin", "australia_archery_federation", "recorder", "archer"])
            countries = get_countries()
            country_filter = st.selectbox("Country", [""] + countries)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            account_status = st.radio("Account Status", ["All", "Active Only", "Deactivated Only"])
        
        run_filter = st.button("🔍 Apply Filters", type="primary", use_container_width=True)
    
    # Apply filters
    if run_filter or 'accounts_df' not in st.session_state:
        deactivated_only = account_status == "Deactivated Only"
        activated_only = account_status == "Active Only"
        
        accounts_df = filter_accounts(
            email_filter=email_filter if email_filter else None,
            fullname_filter=fullname_filter if fullname_filter else None,
            min_age=min_age if min_age > 0 else None,
            max_age=max_age if max_age < 150 else None,
            role_filter=role_filter,
            country_filter=country_filter if country_filter else None,
            deactivated_only=deactivated_only,
            activated_only=activated_only
        )
        
        st.session_state.accounts_df = accounts_df
    
    # Display results
    if 'accounts_df' in st.session_state and not st.session_state.accounts_df.empty:
        st.success(f"Found {len(st.session_state.accounts_df)} account(s)")
        
        # Display dataframe
        st.dataframe(
            st.session_state.accounts_df,
            use_container_width=True,
            height=400
        )
    else:
        st.info("No accounts found with the current filters. Try adjusting your search criteria.")

with tab3:
    st.header("Update Account")
    st.write("Search for an account and update its information")
    
    # Search section
    with st.form("search_account_form"):
        st.subheader("Search Account")
        col1, col2 = st.columns(2)
        
        with col1:
            search_email = st.text_input("Email Address*")
        
        with col2:
            search_dob = st.date_input(
                "Date of Birth*",
                value=date(2000, 1, 1),
                min_value=date(1900, 1, 1),
                max_value=date.today()
            )
        
        search_button = st.form_submit_button("🔍 Search Account", type="primary")
        
        if search_button:
            if not search_email:
                st.error("Please enter an email address")
            else:
                account = search_account_by_email_and_dob(search_email, search_dob.isoformat())
                
                if account:
                    st.session_state.selected_account = account
                    st.success("Account found!")
                else:
                    st.error("No account found with the provided email and date of birth")
                    if 'selected_account' in st.session_state:
                        del st.session_state.selected_account
    
    # Update section
    if 'selected_account' in st.session_state:
        st.divider()
        st.subheader("Update Account Information")
        
        account = st.session_state.selected_account
        
        with st.form("update_account_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                updated_fullname = st.text_input("Full Name", value=account.get('fullname', ''))
                updated_email = st.text_input("Email Address", value=account.get('email_address', ''))
                updated_country = st.selectbox("Country", get_countries(), index=get_countries().index(account.get('country', 'Australia')) if account.get('country') in get_countries() else 0)
            
            with col2:
                updated_sex = st.selectbox("Sex", ["male", "female"], index=0 if account.get('sex') == 'male' else 1)
                updated_role = st.selectbox("Role", ["admin", "australia_archery_federation", "recorder", "archer"], 
                                          index=["admin", "australia_archery_federation", "recorder", "archer"].index(account.get('role', 'archer')))
                updated_deactivated = st.checkbox("Deactivated", value=account.get('deactivated', False))
            
            update_button = st.form_submit_button("💾 Update Account", type="primary")
            
            if update_button:
                updated_data = {
                    "fullname": updated_fullname,
                    "email_address": updated_email,
                    "country": updated_country,
                    "sex": updated_sex,
                    "role": updated_role,
                    "deactivated": updated_deactivated
                }
                
                success = update_account(account['account_id'], updated_data)
                
                if success:
                    st.success("Account updated successfully!")
                    st.balloons()
                    # Refresh the account data
                    updated_account = search_account_by_email_and_dob(updated_email, account['date_of_birth'])
                    if updated_account:
                        st.session_state.selected_account = updated_account
                    st.rerun()
                else:
                    st.error("Failed to update account. Please try again.")

with tab4:
    st.header("Account Report Review")
    st.write("Review and manage pending account reports")
    
    # Fetch pending reports
    reports_df = get_pending_reports()
    
    if not reports_df.empty:
        st.info(f"There are {len(reports_df)} pending report(s) to review")
        
        for idx, report in reports_df.iterrows():
            with st.expander(f"📋 Report #{report['report_id']} - Reported by Account #{report['reporter_id']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Report ID:** {report['report_id']}")
                    st.write(f"**Reporter ID:** {report['reporter_id']}")
                    st.write(f"**Reported Account ID:** {report['target_account_id']}")
                    st.write(f"**Report Content:**")
                    st.text_area("", value=str(report.get('report_content', 'No content provided')), disabled=True, key=f"reason_{report['report_id']}")
                    
                    if report.get('evidence_pdf_file_url'):
                        st.write(f"**Evidence:** [View PDF]({report['evidence_pdf_file_url']})")
                
                with col2:
                    st.write("**Actions:**")
                    
                    col_accept, col_reject = st.columns(2)
                    
                    with col_accept:
                        if st.button("✅ Accept", key=f"accept_{report['report_id']}", type="primary"):
                            success = update_report_status(report['report_id'], "eligible", report['target_account_id'])
                            if success:
                                # Delete report after accepting
                                delete_report(report['report_id'])
                                st.success("Report accepted. Account has been deactivated.")
                                st.rerun()
                            else:
                                st.error("Failed to process report")
                    
                    with col_reject:
                        if st.button("❌ Reject", key=f"reject_{report['report_id']}"):
                            success = update_report_status(report['report_id'], "ineligible")
                            if success:
                                # Delete report after rejecting
                                delete_report(report['report_id'])
                                st.success("Report rejected.")
                                st.rerun()
                            else:
                                st.error("Failed to process report")
    else:
        st.success("✅ No pending reports to review!")
