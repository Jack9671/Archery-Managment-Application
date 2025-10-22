import pandas as pd
from utility_function.initilize_dbconnection import supabase

def get_archer_map():
    """Get mapping of archer names to archer IDs"""
    try:
        response = supabase.table("archer").select("archer_id, account(fullname)").execute()
        if response.data:
            return {f"{row['account']['fullname']} (ID: {row['archer_id']})": row['archer_id'] 
                   for row in response.data}
        return {}
    except Exception as e:
        print(f"Error getting archer map: {e}")
        return {}

def get_competition_map():
    """Get mapping of competition names to competition IDs"""
    try:
        response = supabase.table("club_competition").select("club_competition_id, name").execute()
        if response.data:
            return {f"{row['name']} (ID: {row['club_competition_id']})": row['club_competition_id'] 
                   for row in response.data}
        return {}
    except Exception as e:
        print(f"Error getting competition map: {e}")
        return {}

def get_round_map():
    """Get mapping of round names to round IDs"""
    try:
        response = supabase.table("round").select("round_id, name").execute()
        if response.data:
            return {f"{row['name']} (ID: {row['round_id']})": row['round_id'] 
                   for row in response.data}
        return {}
    except Exception as e:
        print(f"Error getting round map: {e}")
        return {}

def get_event_contexts_for_competition(club_competition_id):
    """Get all event contexts for a specific competition"""
    try:
        response = supabase.table("event_context").select(
            "event_context_id, round_id, range_id, end_order, round(name), range(distance, unit_of_length)"
        ).eq("club_competition_id", club_competition_id).order("round_id").order("range_id").order("end_order").execute()
        
        if response.data:
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    except Exception as e:
        print(f"Error getting event contexts: {e}")
        return pd.DataFrame()

def get_participant_scores(archer_id, club_competition_id=None, round_id=None, score_type=None):
    """Get scores for a specific archer with optional filters"""
    try:
        query = supabase.table("participating").select(
            """
            participating_id,
            event_context_id,
            score_1st_arrow,
            score_2nd_arrow,
            score_3rd_arrow,
            score_4th_arrow,
            score_5st_arrow,
            score_6st_arrow,
            sum_score,
            datetime,
            type,
            status,
            event_context(
                club_competition_id,
                round_id,
                range_id,
                end_order,
                round(name),
                range(distance, unit_of_length),
                club_competition(name)
            )
            """
        ).eq("participating_id", archer_id)
        
        if score_type:
            query = query.eq("type", score_type)
        
        response = query.order("datetime", desc=True).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            # Flatten nested structures
            if not df.empty and 'event_context' in df.columns:
                event_context = pd.json_normalize(df['event_context'])
                df = df.drop('event_context', axis=1)
                df = pd.concat([df, event_context], axis=1)
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"Error getting participant scores: {e}")
        return pd.DataFrame()

def add_score(archer_id, event_context_id, scores, score_type='practice'):
    """Add a new score entry"""
    try:
        sum_score = sum(scores)
        response = supabase.table("participating").insert({
            "participating_id": archer_id,
            "event_context_id": event_context_id,
            "score_1st_arrow": scores[0],
            "score_2nd_arrow": scores[1],
            "score_3rd_arrow": scores[2],
            "score_4th_arrow": scores[3],
            "score_5st_arrow": scores[4],
            "score_6st_arrow": scores[5],
            "sum_score": sum_score,
            "type": score_type,
            "status": "pending"
        }).execute()
        
        return {"success": True, "message": "Score added successfully!"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_score(archer_id, event_context_id, score_type, scores):
    """Update an existing score entry"""
    try:
        sum_score = sum(scores)
        response = supabase.table("participating").update({
            "score_1st_arrow": scores[0],
            "score_2nd_arrow": scores[1],
            "score_3rd_arrow": scores[2],
            "score_4th_arrow": scores[3],
            "score_5st_arrow": scores[4],
            "score_6st_arrow": scores[5],
            "sum_score": sum_score
        }).eq("participating_id", archer_id).eq("event_context_id", event_context_id).eq("type", score_type).execute()
        
        return {"success": True, "message": "Score updated successfully!"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_score(archer_id, event_context_id, score_type):
    """Delete a score entry"""
    try:
        response = supabase.table("participating").delete().eq(
            "participating_id", archer_id
        ).eq("event_context_id", event_context_id).eq("type", score_type).execute()
        
        return {"success": True, "message": "Score deleted successfully!"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def verify_scores_by_recorder(recorder_id, archer_ids, event_context_ids):
    """Recorder verifies multiple scores as eligible"""
    try:
        # Check if recorder has permission for these competitions
        for event_context_id in event_context_ids:
            # Get competition_id from event_context
            ec_response = supabase.table("event_context").select("club_competition_id").eq("event_context_id", event_context_id).execute()
            if ec_response.data:
                competition_id = ec_response.data[0]['club_competition_id']
                # Check if recorder is assigned to this competition
                rec_response = supabase.table("recording").select("*").eq("recording_id", recorder_id).eq("club_competition_id", competition_id).execute()
                if not rec_response.data:
                    return {"success": False, "error": f"Recorder not authorized for competition {competition_id}"}
        
        # Update status to eligible
        for archer_id in archer_ids:
            for event_context_id in event_context_ids:
                supabase.table("participating").update({
                    "status": "eligible"
                }).eq("participating_id", archer_id).eq("event_context_id", event_context_id).eq("type", "competition").execute()
        
        return {"success": True, "message": f"Verified {len(archer_ids)} archer(s) scores successfully!"}
    except Exception as e:
        return {"success": False, "error": str(e)}
