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
            "name": championship_name,
            "eligible_group_of_club_id": eligible_group_id
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating yearly championship: {e}")
        return None

def create_club_competition(creator_id, competition_name, date_start, date_end, address="TBA", eligible_group_id=None, yearly_championship_id=None):
    """Create a new club competition"""
    try:
        response = supabase.table("club_competition").insert({
            "creator_id": creator_id,
            "name": competition_name,
            "address": address,
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

def create_complete_event(creator_id, event_data):
    """
    Create a complete event with all components atomically
    
    Args:
        creator_id: ID of the user creating the event
        event_data: Dictionary containing:
            - event_type: "Yearly Club Championship" or "Club Competition"
            - name: Event name
            - year: Year (for championship)
            - address: Address (for competition)
            - date_start: Start date (for competition)
            - date_end: End date (for competition)
            - eligible_group_id: Optional eligible group ID
            - competitions: List of competitions (for championship)
            - rounds: List of round IDs
            - ranges_config: Dict mapping round_id to list of {range_id, num_ends}
    
    Returns:
        Dict with success status and created IDs, or error message
    """
    try:
        created_ids = {
            'championship_id': None,
            'competition_ids': [],
            'event_context_ids': []
        }
        
        event_type = event_data.get('event_type')
        
        # STEP 1: Create Championship or Competition
        if event_type == "Yearly Club Championship":
            # Create yearly championship
            championship_response = supabase.table("yearly_club_championship").insert({
                "creator_id": creator_id,
                "year": event_data['year'],
                "name": event_data['name'],
                "eligible_group_of_club_id": event_data.get('eligible_group_id')
            }).execute()
            
            if not championship_response.data:
                return {"success": False, "error": "Failed to create championship"}
            
            championship_id = championship_response.data[0]['yearly_club_championship_id']
            created_ids['championship_id'] = championship_id
            
            # Create all competitions for this championship
            competitions_to_create = event_data.get('competitions', [])
            
            for comp in competitions_to_create:
                comp_response = supabase.table("club_competition").insert({
                    "creator_id": creator_id,
                    "name": comp['name'],
                    "address": comp['address'],
                    "date_start": comp['date_start'].isoformat() if hasattr(comp['date_start'], 'isoformat') else str(comp['date_start']),
                    "date_end": comp['date_end'].isoformat() if hasattr(comp['date_end'], 'isoformat') else str(comp['date_end']),
                    "eligible_group_of_club_id": event_data.get('eligible_group_id')
                }).execute()
                
                if not comp_response.data:
                    return {"success": False, "error": f"Failed to create competition: {comp['name']}"}
                
                comp_id = comp_response.data[0]['club_competition_id']
                created_ids['competition_ids'].append(comp_id)
                
                # Create event_context records for this competition
                context_ids = _create_event_contexts(championship_id, comp_id, 
                                                     event_data['rounds'], 
                                                     event_data['ranges_config'])
                
                if context_ids is None:
                    return {"success": False, "error": f"Failed to create event contexts for competition: {comp['name']}"}
                
                created_ids['event_context_ids'].extend(context_ids)
        
        else:  # Club Competition
            # Create standalone club competition
            comp_response = supabase.table("club_competition").insert({
                "creator_id": creator_id,
                "name": event_data['name'],
                "address": event_data['address'],
                "date_start": event_data['date_start'].isoformat() if hasattr(event_data['date_start'], 'isoformat') else str(event_data['date_start']),
                "date_end": event_data['date_end'].isoformat() if hasattr(event_data['date_end'], 'isoformat') else str(event_data['date_end']),
                "eligible_group_of_club_id": event_data.get('eligible_group_id')
            }).execute()
            
            if not comp_response.data:
                return {"success": False, "error": "Failed to create competition"}
            
            comp_id = comp_response.data[0]['club_competition_id']
            created_ids['competition_ids'].append(comp_id)
            
            # Create event_context records for this competition
            context_ids = _create_event_contexts(None, comp_id, 
                                                 event_data['rounds'], 
                                                 event_data['ranges_config'])
            
            if context_ids is None:
                return {"success": False, "error": "Failed to create event contexts"}
            
            created_ids['event_context_ids'].extend(context_ids)
        
        return {
            "success": True,
            "message": f"Successfully created {event_type}",
            "created_ids": created_ids
        }
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error creating complete event: {e}")
        print(f"Full traceback: {error_details}")
        
        # Extract more meaningful error message from Supabase errors
        error_msg = str(e)
        if hasattr(e, 'message'):
            error_msg = e.message
        elif isinstance(e, dict) and 'message' in e:
            error_msg = e['message']
            
        return {"success": False, "error": error_msg}

def _create_event_contexts(championship_id, competition_id, round_ids, ranges_config):
    """
    Helper function to create event_context records
    
    Args:
        championship_id: ID of championship (or None for standalone competition)
        competition_id: ID of competition
        round_ids: List of round IDs
        ranges_config: Dict mapping round_id to list of {range_id, num_ends}
    
    Returns:
        List of created event_context_ids, or None on failure
    """
    try:
        created_context_ids = []
        
        for round_id in round_ids:
            range_configs = ranges_config.get(round_id, [])
            
            for range_config in range_configs:
                range_id = range_config['range_id']
                num_ends = range_config['num_ends']
                
                # Create event_context records for each end
                for end_order in range(1, num_ends + 1):
                    # Generate event_context_id in format: {comp_id}-{round_id}-{range_id}-{end_order}
                    event_context_id = f"{competition_id}-{round_id}-{range_id}-{end_order}"
                    
                    context_response = supabase.table("event_context").insert({
                        "event_context_id": event_context_id,
                        "yearly_club_championship_id": championship_id,
                        "club_competition_id": competition_id,
                        "round_id": round_id,
                        "range_id": range_id,
                        "end_order": end_order
                    }).execute()
                    
                    if not context_response.data:
                        print(f"Failed to create event_context: {event_context_id}")
                        return None
                    
                    created_context_ids.append(event_context_id)
        
        return created_context_ids
    
    except Exception as e:
        print(f"Error creating event contexts: {e}")
        return None

def get_available_ranges():
    """Get all available ranges"""
    try:
        response = supabase.table("range").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching ranges: {e}")
        return pd.DataFrame()

def get_all_clubs():
    """Get all clubs from database"""
    try:
        response = supabase.table("club").select("club_id, name").execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error fetching clubs: {e}")
        return []

def create_eligible_group_with_clubs(club_ids):
    """
    Create a new eligible group and add clubs to it
    
    Args:
        club_ids: List of club IDs to add to the group
    
    Returns:
        eligible_group_id or None on failure
    """
    try:
        # Create the eligible group
        group_response = supabase.table("eligible_group_of_club").insert({}).execute()
        
        if not group_response.data:
            return None
        
        eligible_group_id = group_response.data[0]['eligible_group_of_club_id']
        
        # Add clubs to the group
        if club_ids:
            members_to_insert = [
                {"eligible_group_of_club_id": eligible_group_id, "eligible_club_id": club_id}
                for club_id in club_ids
            ]
            
            members_response = supabase.table("eligible_club_member").insert(members_to_insert).execute()
            
            if not members_response.data:
                # Rollback: delete the group if we can't add members
                supabase.table("eligible_group_of_club").delete().eq("eligible_group_of_club_id", eligible_group_id).execute()
                return None
        
        return eligible_group_id
    
    except Exception as e:
        print(f"Error creating eligible group: {e}")
        return None

def get_eligible_group_details(eligible_group_id):
    """
    Get details of an eligible group including all member clubs
    
    Args:
        eligible_group_id: ID of the eligible group
    
    Returns:
        Dict with group info and list of clubs, or None
    """
    try:
        # Get club members
        members_response = supabase.table("eligible_club_member").select("eligible_club_id").eq("eligible_group_of_club_id", eligible_group_id).execute()
        
        if not members_response.data:
            return {"eligible_group_id": eligible_group_id, "clubs": []}
        
        club_ids = [m['eligible_club_id'] for m in members_response.data]
        
        # Get club details
        clubs_response = supabase.table("club").select("club_id, name").in_("club_id", club_ids).execute()
        
        clubs = clubs_response.data if clubs_response.data else []
        
        return {
            "eligible_group_id": eligible_group_id,
            "clubs": clubs
        }
    
    except Exception as e:
        print(f"Error fetching eligible group details: {e}")
        return None

def get_all_eligible_groups():
    """
    Get all eligible groups with their member clubs
    
    Returns:
        List of dicts with group info and clubs
    """
    try:
        groups_response = supabase.table("eligible_group_of_club").select("eligible_group_of_club_id").execute()
        
        if not groups_response.data:
            return []
        
        groups_with_clubs = []
        for group in groups_response.data:
            group_id = group['eligible_group_of_club_id']
            group_details = get_eligible_group_details(group_id)
            if group_details:
                groups_with_clubs.append(group_details)
        
        return groups_with_clubs
    
    except Exception as e:
        print(f"Error fetching eligible groups: {e}")
        return []
