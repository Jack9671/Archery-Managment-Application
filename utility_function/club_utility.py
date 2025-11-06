from utility_function.initilize_dbconnection import supabase
import pandas as pd

def get_all_clubs(search_query=None):
    """Get all clubs, optionally filtered by search query"""
    try:
        query = supabase.table("club").select("*")
        
        if search_query:
            query = query.ilike("name", f"%{search_query}%")
        
        response = query.execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching clubs: {e}")
        return pd.DataFrame()

def get_club_by_id(club_id):
    """Get club information by ID"""
    try:
        response = supabase.table("club").select("*").eq("club_id", club_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error fetching club: {e}")
        return None

def get_archer_club(archer_id):
    """Get the club that an archer belongs to or created"""
    try:
        # Check if archer is a member of any club
        response = supabase.table("archer").select("club_id").eq("archer_id", archer_id).execute()
        
        if response.data and response.data[0].get('club_id'):
            club_id = response.data[0]['club_id']
            return get_club_by_id(club_id)
        
        return None
    except Exception as e:
        print(f"Error fetching archer club: {e}")
        return None

def create_club(creator_id, club_name, club_description, formation_date, club_logo_url=None, min_age=10, max_age=70, open_to_join=True):
    """Create a new club"""
    try:
        response = supabase.table("club").insert({
            "creator_id": creator_id,
            "name": club_name,
            "about_club": club_description,
            "formation_date": formation_date,
            "club_logo_url": club_logo_url or "https://ghcpcyvethwdzzgyymfp.supabase.co/storage/v1/object/public/User%20Uploaded/Club_Logo/Default_Club_Logo.png",
            "min_age_to_join": min_age,
            "max_age_to_join": max_age,
            "open_to_join": open_to_join
        }).execute()
        
        if response.data:
            club_id = response.data[0]['club_id']
            # Update archer's club_id
            supabase.table("archer").update({"club_id": club_id}).eq("archer_id", creator_id).execute()
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error creating club: {e}")
        return None

def join_club(archer_id, club_id, sender_word="I would like to join this club."):
    """Request to join a club (submit enrollment form)"""
    try:
        # Get club age restrictions
        club_response = supabase.table("club").select("min_age_to_join, max_age_to_join, open_to_join").eq("club_id", club_id).execute()
        
        if not club_response.data:
            print(f"Club {club_id} not found")
            return None
        
        club = club_response.data[0]
        
        # Check if club is open to join
        if not club.get('open_to_join', True):
            print(f"Club {club_id} is not open to join")
            return None
        
        # Get archer's date of birth to calculate age
        archer_response = supabase.table("archer").select("date_of_birth").eq("archer_id", archer_id).execute()
        
        if not archer_response.data:
            print(f"Archer {archer_id} not found")
            return None
        
        date_of_birth = archer_response.data[0].get('date_of_birth')
        
        if date_of_birth:
            from datetime import datetime
            dob = datetime.fromisoformat(date_of_birth.replace('Z', '+00:00'))
            today = datetime.now()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            # Check age restrictions
            min_age = club.get('min_age_to_join', 10)
            max_age = club.get('max_age_to_join', 70)
            
            if age < min_age or age > max_age:
                print(f"Archer {archer_id} (age {age}) does not meet age requirement ({min_age}-{max_age})")
                return "age_restriction"
        
        # Check if there's already a pending request
        existing = supabase.table("club_enrollment_form").select("*").eq("sender_id", archer_id).eq("club_id", club_id).eq("status", "pending").execute()
        
        if existing.data:
            print(f"Archer {archer_id} already has a pending request for club {club_id}")
            return None
        
        response = supabase.table("club_enrollment_form").insert({
            "sender_id": archer_id,
            "sender_word": sender_word,
            "club_id": club_id,
            "status": "pending",
            "club_creator_word": ""
        }).execute()
        
        if response.data:
            print(f"Successfully created enrollment form: {response.data[0]}")
        
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error joining club: {e}")
        return None

def get_club_members(club_id):
    """Get all members of a club"""
    try:
        response = supabase.table("archer").select("archer_id, level, about_archer").eq("club_id", club_id).execute()
        
        if not response.data:
            return pd.DataFrame()
        
        # Get account information for each member
        members_data = []
        for member in response.data:
            account_info = supabase.table("account").select("fullname, avatar_url, email_address").eq("account_id", member['archer_id']).execute()
            if account_info.data:
                member_data = {**member, **account_info.data[0]}
                members_data.append(member_data)
        
        return pd.DataFrame(members_data) if members_data else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching club members: {e}")
        return pd.DataFrame()

def get_pending_enrollment_forms(club_id):
    """Get pending enrollment forms for a club"""
    try:
        print(f"Fetching pending forms for club_id: {club_id}")
        response = supabase.table("club_enrollment_form").select("*").eq("club_id", club_id).eq("status", "pending").execute()
        print(f"Found {len(response.data) if response.data else 0} pending forms")
        if response.data:
            print(f"Forms data: {response.data}")
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching enrollment forms: {e}")
        return pd.DataFrame()

def update_enrollment_status(form_id, status, club_id=None, sender_id=None):
    """Update enrollment form status and update archer's club if accepted, then delete the form"""
    try:
        if status == "eligible" and club_id and sender_id:
            # Accept: Update archer's club_id
            supabase.table("archer").update({"club_id": club_id}).eq("archer_id", sender_id).execute()
            print(f"Added archer {sender_id} to club {club_id}")
        
        # Delete the form after processing (whether eligible or ineligible)
        if status in ["eligible", "ineligible"]:
            response = supabase.table("club_enrollment_form").delete().eq("form_id", form_id).execute()
            print(f"Deleted form {form_id} with status {status}")
            return response.data is not None
        else:
            # For other statuses (like "in progress"), just update the form
            update_data = {"status": status}
            response = supabase.table("club_enrollment_form").update(update_data).eq("form_id", form_id).execute()
            print(f"Updated form {form_id} to status {status}")
            return response.data is not None and len(response.data) > 0
            
    except Exception as e:
        print(f"Error updating enrollment status: {e}")
        return False

def remove_club_member(archer_id):
    """Remove a member from a club"""
    try:
        response = supabase.table("archer").update({"club_id": None}).eq("archer_id", archer_id).execute()
        return response.data is not None and len(response.data) > 0
    except Exception as e:
        print(f"Error removing club member: {e}")
        return False

def check_club_creator(archer_id, club_id):
    """Check if an archer is the creator of a club"""
    try:
        response = supabase.table("club").select("creator_id").eq("club_id", club_id).execute()
        if response.data:
            return response.data[0]['creator_id'] == archer_id
        return False
    except Exception as e:
        print(f"Error checking club creator: {e}")
        return False
