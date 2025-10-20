from utility_function.initilize_dbconnection import supabase
import pandas as pd
from datetime import datetime

def get_total_accounts():
    """Get total number of accounts"""
    try:
        response = supabase.table("account").select("account_id", count="exact").execute()
        return response.count if response.count else 0
    except Exception as e:
        return 0

def get_deactivated_accounts_count():
    """Get total number of deactivated accounts"""
    try:
        response = supabase.table("account").select("account_id", count="exact").eq("deactivated", True).execute()
        return response.count if response.count else 0
    except Exception as e:
        return 0

def get_accounts_by_role(role):
    """Get count of accounts by role"""
    try:
        response = supabase.table("account").select("account_id", count="exact").eq("role", role).execute()
        return response.count if response.count else 0
    except Exception as e:
        return 0

def filter_accounts(email_filter=None, fullname_filter=None, min_age=None, max_age=None, 
                   role_filter=None, country_filter=None, deactivated_only=False, activated_only=False):
    """Filter accounts based on various criteria"""
    try:
        query = supabase.table("account").select("*")
        
        if email_filter:
            query = query.ilike("email_address", f"%{email_filter}%")
        
        if fullname_filter:
            query = query.ilike("fullname", f"%{fullname_filter}%")
        
        if role_filter and role_filter != "all":
            query = query.eq("role", role_filter)
        
        if country_filter and country_filter != "":
            query = query.eq("country", country_filter)
        
        if deactivated_only:
            query = query.eq("deactivated", True)
        elif activated_only:
            query = query.eq("deactivated", False)
        
        response = query.execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # Filter by age if specified
            if min_age is not None or max_age is not None:
                df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
                current_year = datetime.now().year
                df['age'] = current_year - df['date_of_birth'].dt.year
                
                if min_age is not None:
                    df = df[df['age'] >= min_age]
                if max_age is not None:
                    df = df[df['age'] <= max_age]
                
                df = df.drop('age', axis=1)
            
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Error filtering accounts: {e}")
        return pd.DataFrame()

def search_account_by_email_and_dob(email_address, date_of_birth):
    """Search for an account by email and date of birth"""
    try:
        response = supabase.table("account").select("*").eq("email_address", email_address).eq("date_of_birth", date_of_birth).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error searching account: {e}")
        return None

def update_account(account_id, updated_data):
    """Update account information"""
    try:
        response = supabase.table("account").update(updated_data).eq("account_id", account_id).execute()
        return response.data is not None and len(response.data) > 0
    except Exception as e:
        print(f"Error updating account: {e}")
        return False

def get_pending_reports():
    """Get all pending account reports"""
    try:
        response = supabase.table("account_report").select("*").eq("status", "pending").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching reports: {e}")
        return pd.DataFrame()

def update_report_status(report_id, status, account_id_to_deactivate=None):
    """Update report status and optionally deactivate account"""
    try:
        # Update report status
        response = supabase.table("account_report").update({"status": status}).eq("report_id", report_id).execute()
        
        if status == "eligible" and account_id_to_deactivate:
            # Deactivate the reported account
            supabase.table("account").update({"deactivated": True}).eq("account_id", account_id_to_deactivate).execute()
        
        return response.data is not None and len(response.data) > 0
    except Exception as e:
        print(f"Error updating report: {e}")
        return False

def delete_report(report_id):
    """Delete an account report"""
    try:
        response = supabase.table("account_report").delete().eq("report_id", report_id).execute()
        return response.data is not None
    except Exception as e:
        print(f"Error deleting report: {e}")
        return False
