from utility_function.initilize_dbconnection import supabase
import pandas as pd
from datetime import datetime

def get_all_events(event_type="all", date_start=None, date_end=None, category_id=None, eligible_group_id=None):
    """Get filtered events (yearly championships or club competitions)"""
    try:
        if event_type == "yearly_club_championship":
            query = supabase.table("yearly_club_championship").select("*")
            
            if date_start:
                query = query.gte("year", date_start.year)
            if date_end:
                query = query.lte("year", date_end.year)
            if eligible_group_id:
                query = query.eq("eligible_group_of_club_id", eligible_group_id)
            if category_id:
                query = query.eq("category_id", category_id)
            
            response = query.execute()
            return pd.DataFrame(response.data) if response.data else pd.DataFrame()
            
        elif event_type == "club_competition":
            # Get only club competitions not part of any yearly championship
            query = supabase.table("club_competition").select("*")
            
            if date_start:
                query = query.gte("date_start", date_start.isoformat())
            if date_end:
                query = query.lte("date_end", date_end.isoformat())
            if eligible_group_id:
                query = query.eq("eligible_group_of_club_id", eligible_group_id)
            if category_id:
                query = query.eq("category_id", category_id)
            
            response = query.execute()
            if response.data:
                df = pd.DataFrame(response.data)
                
                # Filter out competitions that are part of yearly championships
                # Check event_context table to see which competitions are linked to championships
                event_contexts = supabase.table("event_context").select("club_competition_id, yearly_club_championship_id").execute()
                
                if event_contexts.data:
                    # Get competition IDs that are part of championships
                    linked_comp_ids = [ec['club_competition_id'] for ec in event_contexts.data if ec.get('yearly_club_championship_id')]
                    
                    # Filter out linked competitions
                    df = df[~df['club_competition_id'].isin(linked_comp_ids)]
                
                return df
            return pd.DataFrame()
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching events: {e}")
        return pd.DataFrame()

def get_event_hierarchy(event_id, event_type):
    """Get hierarchical data for an event (for icicle chart)"""
    try:
        if event_type == "yearly_club_championship":
            # Get all club competitions for this championship
            event_contexts = supabase.table("event_context").select("*").eq("yearly_club_championship_id", event_id).execute()
        else:
            # Get event contexts for this club competition
            event_contexts = supabase.table("event_context").select("*").eq("club_competition_id", event_id).execute()
        
        if not event_contexts.data:
            return []
        
        hierarchy_data = []
        for ctx in event_contexts.data:
            # Get round info
            round_info = supabase.table("round").select("*").eq("round_id", ctx['round_id']).execute()
            # Get range info
            range_info = supabase.table("range").select("*").eq("range_id", ctx['range_id']).execute()
            
            hierarchy_data.append({
                "event_context_id": ctx['event_context_id'],
                "club_competition_id": ctx['club_competition_id'],
                "round_id": ctx['round_id'],
                "range_id": ctx['range_id'],
                "end_order": ctx['end_order'],
                "round_name": round_info.data[0]['name'] if round_info.data else f"Round {ctx['round_id']}",
                "range_distance": range_info.data[0]['distance'] if range_info.data else "Unknown"
            })
        
        return hierarchy_data
    except Exception as e:
        print(f"Error fetching event hierarchy: {e}")
        return []

def get_eligible_clubs(eligible_group_id):
    """Get list of eligible clubs for an event"""
    try:
        if not eligible_group_id:
            return "All clubs are eligible"
        
        response = supabase.table("eligible_club_member").select("eligible_club_id").eq("eligible_group_of_club_id", eligible_group_id).execute()
        
        if response.data:
            club_ids = [row['eligible_club_id'] for row in response.data]
            clubs = supabase.table("club").select("name").in_("club_id", club_ids).execute()
            return [club['name'] for club in clubs.data] if clubs.data else []
        return []
    except Exception as e:
        print(f"Error fetching eligible clubs: {e}")
        return []

def get_request_forms(status_filter=None, type_filter=None, action_filter=None, user_id=None, is_creator=False):
    """Get competition request forms with filters"""
    try:
        query = supabase.table("request_competition_form").select("*")
        
        if status_filter and status_filter != "all":
            query = query.eq("status", status_filter)
        
        if type_filter and type_filter != "all":
            query = query.eq("type", type_filter)
        
        if action_filter and action_filter != "all":
            query = query.eq("action", action_filter)
        
        if user_id and not is_creator:
            # Show only user's own forms
            query = query.eq("applicant_id", user_id)
        
        response = query.execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching request forms: {e}")
        return pd.DataFrame()

def update_form_status(form_id, new_status):
    """Update status of a request form"""
    try:
        response = supabase.table("request_competition_form").update({"status": new_status}).eq("form_id", form_id).execute()
        return response.data is not None and len(response.data) > 0
    except Exception as e:
        print(f"Error updating form status: {e}")
        return False

def get_round_schedule(club_competition_id):
    """Get round schedule for a club competition"""
    try:
        response = supabase.table("round_schedule").select("*").eq("club_competition_id", club_competition_id).execute()
        
        if response.data:
            # Join with round table to get round names
            df = pd.DataFrame(response.data)
            for idx, row in df.iterrows():
                round_info = supabase.table("round").select("round_name").eq("round_id", row['round_id']).execute()
                if round_info.data:
                    df.at[idx, 'round_name'] = round_info.data[0]['round_name']
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching round schedule: {e}")
        return pd.DataFrame()

def create_yearly_championship(creator_id, year, championship_name, eligible_group_id=None):
    """Create a new yearly club championship"""
    try:
        response = supabase.table("yearly_club_championship").insert({
            "creator_id": creator_id,
            "year": year,
            "championship_name": championship_name,
            "eligible_group_of_club_id": eligible_group_id
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating yearly championship: {e}")
        return None

def create_club_competition(creator_id, competition_name, date_start, date_end, eligible_group_id=None, yearly_championship_id=None):
    """Create a new club competition"""
    try:
        response = supabase.table("club_competition").insert({
            "creator_id": creator_id,
            "competition_name": competition_name,
            "date_start": date_start,
            "date_end": date_end,
            "eligible_group_of_club_id": eligible_group_id
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating club competition: {e}")
        return None

def get_available_rounds():
    """Get all available rounds"""
    try:
        response = supabase.table("round").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching rounds: {e}")
        return pd.DataFrame()

def get_available_ranges():
    """Get all available ranges"""
    try:
        response = supabase.table("range").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching ranges: {e}")
        return pd.DataFrame()
