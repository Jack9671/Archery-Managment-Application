from utility_function.initilize_dbconnection import supabase
import pandas as pd

def get_archer_scores(archer_id, score_type="competition"):
    """Get scores for an archer (competition or practice)"""
    try:
        response = supabase.table("participating").select("*").eq("participating_id", archer_id).eq("type", score_type).execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching archer scores: {e}")
        return pd.DataFrame()

def get_event_participants(event_context_id):
    """Get all participants for a specific event context"""
    try:
        response = supabase.table("participating").select("*").eq("event_context_id", event_context_id).execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching participants: {e}")
        return pd.DataFrame()

def update_score(participating_id, event_context_id, score_type, arrow_scores):
    """Update arrow scores for a participant"""
    try:
        update_data = {
            "score_1st_arrow": arrow_scores.get('arrow_1', 0),
            "score_2nd_arrow": arrow_scores.get('arrow_2', 0),
            "score_3rd_arrow": arrow_scores.get('arrow_3', 0),
            "score_4th_arrow": arrow_scores.get('arrow_4', 0),
            "score_5th_arrow": arrow_scores.get('arrow_5', 0),
            "score_6th_arrow": arrow_scores.get('arrow_6', 0),
        }
        
        response = supabase.table("participating").update(update_data).eq("participating_id", participating_id).eq("event_context_id", event_context_id).eq("type", score_type).execute()
        return response.data is not None and len(response.data) > 0
    except Exception as e:
        print(f"Error updating score: {e}")
        return False

def verify_score(participating_id, event_context_id, score_type, status):
    """Verify a participant's score (set status to eligible)"""
    try:
        response = supabase.table("participating").update({"status": status}).eq("participating_id", participating_id).eq("event_context_id", event_context_id).eq("type", score_type).execute()
        return response.data is not None and len(response.data) > 0
    except Exception as e:
        print(f"Error verifying score: {e}")
        return False

def get_event_context_info(event_context_id):
    """Get detailed information about an event context"""
    try:
        response = supabase.table("event_context").select("*").eq("event_context_id", event_context_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error fetching event context: {e}")
        return None

def check_recorder_permission(recorder_id, competition_id):
    """Check if recorder has permission to modify scores for this competition"""
    try:
        # Check if recorder is in recording table for this competition
        response = supabase.table("recording").select("*").eq("recorder_id", recorder_id).eq("club_competition_id", competition_id).execute()
        
        if response.data:
            return True
        
        # Check if recorder is the creator
        comp_response = supabase.table("club_competition").select("creator_id").eq("club_competition_id", competition_id).execute()
        if comp_response.data and comp_response.data[0]['creator_id'] == recorder_id:
            return True
        
        return False
    except Exception as e:
        print(f"Error checking recorder permission: {e}")
        return False
