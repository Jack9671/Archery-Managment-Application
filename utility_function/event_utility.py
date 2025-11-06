from utility_function.initilize_dbconnection import supabase
import pandas as pd
from datetime import datetime
import streamlit as st
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
            query = query.eq("sender_id", user_id)
        
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
        # Convert to integer if it's a string
        if isinstance(club_competition_id, str):
            club_competition_id = int(club_competition_id)
        
        response = supabase.table("round_schedule").select("*").eq("club_competition_id", club_competition_id).execute()
        
        if response.data:
            # Join with round table to get round names
            df = pd.DataFrame(response.data)
            for idx, row in df.iterrows():
                # Query for 'name' column, not 'round_name'
                round_info = supabase.table("round").select("name").eq("round_id", row['round_id']).execute()
                if round_info.data:
                    df.at[idx, 'round_name'] = round_info.data[0]['name']
                else:
                    df.at[idx, 'round_name'] = f"Round {row['round_id']}"
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

def _create_round_schedules(club_competition_id, round_ids, round_schedules):
    """
    Create round_schedule entries for a competition
    
    Args:
        club_competition_id: ID of the club competition
        round_ids: List of round IDs
        round_schedules: Dict mapping round_id to schedule info {start_date, start_time, end_date, end_time}
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from datetime import datetime
        
        for round_id in round_ids:
            schedule_info = round_schedules.get(round_id)
            if not schedule_info:
                print(f"Warning: No schedule info for round {round_id}, skipping")
                continue
            
            # Combine date and time into datetime
            start_datetime = datetime.combine(schedule_info['start_date'], schedule_info['start_time'])
            end_datetime = datetime.combine(schedule_info['end_date'], schedule_info['end_time'])
            
            # Insert round_schedule
            response = supabase.table("round_schedule").insert({
                "club_competition_id": club_competition_id,
                "round_id": round_id,
                "datetime_to_start": start_datetime.isoformat(),
                "datetime_to_end": end_datetime.isoformat(),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }).execute()
            
            if not response.data:
                print(f"Failed to create schedule for round {round_id}")
                return False
        
        return True
    except Exception as e:
        print(f"Error creating round schedules: {e}")
        import traceback
        traceback.print_exc()
        return False

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
                "eligible_group_of_club_id": event_data.get('eligible_group_id'),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
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
                    "eligible_group_of_club_id": event_data.get('eligible_group_id'),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
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
                
                # Create round_schedule entries for this competition
                schedule_success = _create_round_schedules(comp_id, event_data['rounds'], 
                                                          event_data.get('round_schedules', {}))
                if not schedule_success:
                    return {"success": False, "error": f"Failed to create round schedules for competition: {comp['name']}"}
        
        else:  # Club Competition
            # Create standalone club competition
            comp_response = supabase.table("club_competition").insert({
                "creator_id": creator_id,
                "name": event_data['name'],
                "address": event_data['address'],
                "date_start": event_data['date_start'].isoformat() if hasattr(event_data['date_start'], 'isoformat') else str(event_data['date_start']),
                "date_end": event_data['date_end'].isoformat() if hasattr(event_data['date_end'], 'isoformat') else str(event_data['date_end']),
                "eligible_group_of_club_id": event_data.get('eligible_group_id'),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
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
            
            # Create round_schedule entries for this competition
            schedule_success = _create_round_schedules(comp_id, event_data['rounds'], 
                                                      event_data.get('round_schedules', {}))
            if not schedule_success:
                return {"success": False, "error": "Failed to create round schedules"}
        
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
                    # Don't manually set event_context_id - let it auto-increment
                    context_response = supabase.table("event_context").insert({
                        "yearly_club_championship_id": championship_id,
                        "club_competition_id": competition_id,
                        "round_id": round_id,
                        "range_id": range_id,
                        "end_order": end_order
                    }).execute()
                    
                    if not context_response.data:
                        print(f"Failed to create event_context for round {round_id}, range {range_id}, end {end_order}")
                        return None
                    
                    # Get the auto-generated event_context_id
                    created_context_ids.append(context_response.data[0]['event_context_id'])
        
        return created_context_ids
    
    except Exception as e:
        print(f"Error creating event contexts: {e}")
        import traceback
        traceback.print_exc()
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

def get_club_competition_map():
    data = supabase.table("club_competition").select("club_competition_id, name").execute().data
    return {c["name"] : c["club_competition_id"] for c in data}
def get_yearly_club_championship_map():
    data = supabase.table("yearly_club_championship").select("yearly_club_championship_id, name").execute().data
    return {c["name"]: c["yearly_club_championship_id"] for c in data}
def get_round_map():
    data = supabase.table("round").select("round_id, name").execute().data
    return {c["name"] : c["round_id"] for c in data}

def get_range_map():
    data = supabase.table("range").select("range_id, distance").execute().data
    return { c["distance"] : c["range_id"] for c in data}

def get_discipline_map():
    data = supabase.table("discipline").select("discipline_id, name").execute().data
    return { c["name"] : c["discipline_id"] for c in data}

def get_discipline_id_to_name_map():
    """Get mapping from discipline_id to discipline name"""
    data = supabase.table("discipline").select("discipline_id, name").execute().data
    return { c["discipline_id"] : c["name"] for c in data}

def get_equipment_map():
    data = supabase.table("equipment").select("equipment_id, name").execute().data
    return { c["name"] : c["equipment_id"] for c in data}

def get_equipment_id_to_name_map():
    """Get mapping from equipment_id to equipment name"""
    data = supabase.table("equipment").select("equipment_id, name").execute().data
    return { c["equipment_id"] : c["name"] for c in data}

def get_age_division_map():
    # age_division table does not have name, just min_age and max_age, so we need to create a name like "18-25"
    data = supabase.table("age_division").select("age_division_id, min_age, max_age").execute().data
    return {f"{c['min_age']}-{c['max_age']}": c["age_division_id"] for c in data}

def get_age_division_id_to_name_map():
    """Get mapping from age_division_id to age range string"""
    data = supabase.table("age_division").select("age_division_id, min_age, max_age").execute().data
    return {c["age_division_id"]: f"{c['min_age']}-{c['max_age']}" for c in data}

def get_category_map():
    #category table does not have name, just discipline_id, age_division_id, equipment_id, so we need to create a name like "Outdoor Target Archery · 18-25 · Longbow"
    discipline_id_to_name = get_discipline_id_to_name_map()
    age_division_id_to_name = get_age_division_id_to_name_map()
    equipment_id_to_name = get_equipment_id_to_name_map()

    category_map = {}
    for c in supabase.table("category").select("category_id, discipline_id, age_division_id, equipment_id").execute().data:
        discipline_name = discipline_id_to_name.get(c['discipline_id'], 'Unknown Discipline')
        age_division_name = age_division_id_to_name.get(c['age_division_id'], 'Unknown Age Division')
        equipment_name = equipment_id_to_name.get(c['equipment_id'], 'Unknown Equipment')
        name = f"{discipline_name} · {age_division_name} · {equipment_name}"
        category_map[name] = c["category_id"]
    return category_map

def get_club_map():
    data = supabase.table("club").select("club_id, name").execute().data
    return {c["name"]: c["club_id"] for c in data}

def get_list_of_eligible_group_id_from_a_set_of_club_id(club_ids:set) -> list:
    """Given a set of club IDs, find an eligible group id that contain these clubs as subset"""
    try:
        response = supabase.table("eligible_club_member").select("eligible_group_of_club_id, eligible_club_id").in_("eligible_club_id", club_ids).execute() 
        if not response.data:
            return []
        #response.data is a list of dicts with eligible_group_of_club_id and eligible_club_id where eligible_club_id is in club_ids
        group_to_clubs = {}
        for row in response.data:
            group_id = row["eligible_group_of_club_id"]
            club_id = row["eligible_club_id"]
            if group_id not in group_to_clubs:
                group_to_clubs[group_id] = set()
            group_to_clubs[group_id].add(club_id)
        matching_group_ids = []
        for group_id, member_clubs in group_to_clubs.items():
            if club_ids.issubset(member_clubs):
                matching_group_ids.append(group_id)
        return matching_group_ids
    except Exception as e:
        print(f"Error fetching eligible groups: {e}")
        return []   

def get_list_of_member_club_name_from_eligible_group_of_club_id(eligible_group_of_club_id):
    """Given an eligible_group_of_club_id, return the list of member club names"""
    try:
        response = supabase.table("eligible_club_member").select("eligible_club_id").eq("eligible_group_of_club_id", eligible_group_of_club_id).execute() 
        if not response.data:
            return []
        club_ids = [row["eligible_club_id"] for row in response.data]
        clubs_response = supabase.table("club").select("name").in_("club_id", club_ids).execute()
        if not clubs_response.data:
            return []
        club_names = [row["name"] for row in clubs_response.data]
        return club_names
    except Exception as e:
        print(f"Error fetching member clubs: {e}")
        return []

def get_event_hierarchy_for_icicle(event_type, event_id):
    """
    Get hierarchical data for icicle chart visualization
    Handles two cases:
    Case 1: Yearly Championship → Club Competition → Round → Range → End
    Case 2: Club Competition → Round → Range → End
    
    Args:
        event_type: 'yearly_club_championship' or 'club_competition'
        event_id: the ID of the event
        
    Returns: DataFrame with columns: labels, parents, ids, values, level, hover_info
    """
    try:
        hierarchy_rows = []
        
        if event_type == 'yearly club championship':
            # Case 1: Yearly Championship hierarchy
            # Get championship info
            championship_response = supabase.table("yearly_club_championship").select("*").eq("yearly_club_championship_id", event_id).execute()
            if not championship_response.data:
                return pd.DataFrame()
            
            championship = championship_response.data[0]
            championship_name = championship['name']
            
            # Build detailed hover info for championship
            champ_hover = f"<b>Yearly Club Championship</b><br>"
            champ_hover += f"ID: {championship.get('yearly_club_championship_id', 'N/A')}<br>"
            champ_hover += f"Year: {championship.get('year', 'N/A')}<br>"
            champ_hover += f"Creator ID: {championship.get('creator_id', 'N/A')}<br>"
            champ_hover += f"Eligible Group ID: {championship.get('eligible_group_of_club_id', 'All Clubs')}<br>"
            champ_hover += f"Created: {championship.get('created_at', 'N/A')[:10] if championship.get('created_at') else 'N/A'}"
            
            # Root: Yearly Championship
            root_id = f'championship_{event_id}'
            hierarchy_rows.append({
                'labels': championship_name,
                'parents': '',
                'ids': root_id,
                'values': 1,
                'level': 0,
                'hover_info': champ_hover
            })
            
            # Get all club competitions under this championship
            event_contexts = supabase.table("event_context").select("*").eq("yearly_club_championship_id", event_id).not_.is_("club_competition_id", "null").execute()
            
            if not event_contexts.data:
                return pd.DataFrame(hierarchy_rows)
            
            # Get unique club competition IDs
            comp_ids = list(set([ec['club_competition_id'] for ec in event_contexts.data if ec.get('club_competition_id')]))
            
            # Get competition details
            competitions = supabase.table("club_competition").select("*").in_("club_competition_id", comp_ids).execute()
            
            for competition in competitions.data:
                comp_id = competition['club_competition_id']
                comp_name = competition['name']
                comp_node_id = f'competition_{comp_id}'
                
                # Build detailed hover info for competition
                comp_hover = f"<b>Club Competition</b><br>"
                comp_hover += f"ID: {comp_id}<br>"
                comp_hover += f"Address: {competition.get('address', 'N/A')}<br>"
                comp_hover += f"Start Date: {competition.get('date_start', 'N/A')}<br>"
                comp_hover += f"End Date: {competition.get('date_end', 'N/A')}<br>"
                comp_hover += f"Creator ID: {competition.get('creator_id', 'N/A')}<br>"
                comp_hover += f"Eligible Group ID: {competition.get('eligible_group_of_club_id', 'All Clubs')}"
                
                hierarchy_rows.append({
                    'labels': comp_name,
                    'parents': root_id,
                    'ids': comp_node_id,
                    'values': 1,
                    'level': 1,
                    'hover_info': comp_hover
                })
                
                # Get rounds for this competition
                comp_contexts = [ec for ec in event_contexts.data if ec.get('club_competition_id') == comp_id]
                round_ids = list(set([ec['round_id'] for ec in comp_contexts if ec.get('round_id')]))
                
                if round_ids:
                    rounds = supabase.table("round").select("*, category(discipline_id, age_division_id, equipment_id)").in_("round_id", round_ids).execute()
                    
                    for round_data in rounds.data:
                        round_id = round_data['round_id']
                        round_name = round_data['name']
                        round_node_id = f'round_{comp_id}_{round_id}'
                        
                        # Build detailed hover info for round
                        round_hover = f"<b>Round</b><br>"
                        round_hover += f"ID: {round_id}<br>"
                        round_hover += f"Name: {round_name}<br>"
                        round_hover += f"Category ID: {round_data.get('category_id', 'N/A')}<br>"
                        if round_data.get('category'):
                            cat = round_data['category']
                            round_hover += f"Discipline ID: {cat.get('discipline_id', 'N/A')}<br>"
                            round_hover += f"Age Division ID: {cat.get('age_division_id', 'N/A')}<br>"
                            round_hover += f"Equipment ID: {cat.get('equipment_id', 'N/A')}<br>"
                        round_hover += f"Created: {round_data.get('created_at', 'N/A')[:10] if round_data.get('created_at') else 'N/A'}"
                        
                        hierarchy_rows.append({
                            'labels': round_name,
                            'parents': comp_node_id,
                            'ids': round_node_id,
                            'values': 1,
                            'level': 2,
                            'hover_info': round_hover
                        })
                        
                        # Get ranges and ends for this round
                        _add_ranges_and_ends_for_icicle(hierarchy_rows, comp_contexts, round_id, round_node_id, level_offset=3)
        
        else:
            # Case 2: Club Competition hierarchy (standalone)
            # Get competition info
            competition_response = supabase.table("club_competition").select("*").eq("club_competition_id", event_id).execute()
            if not competition_response.data:
                return pd.DataFrame()
            
            competition = competition_response.data[0]
            comp_name = competition['name']
            
            # Build detailed hover info for competition
            comp_hover = f"<b>Club Competition</b><br>"
            comp_hover += f"ID: {event_id}<br>"
            comp_hover += f"Address: {competition.get('address', 'N/A')}<br>"
            comp_hover += f"Start Date: {competition.get('date_start', 'N/A')}<br>"
            comp_hover += f"End Date: {competition.get('date_end', 'N/A')}<br>"
            comp_hover += f"Creator ID: {competition.get('creator_id', 'N/A')}<br>"
            comp_hover += f"Eligible Group ID: {competition.get('eligible_group_of_club_id', 'All Clubs')}<br>"
            comp_hover += f"Created: {competition.get('created_at', 'N/A')[:10] if competition.get('created_at') else 'N/A'}"
            
            # Root: Club Competition
            root_id = f'competition_{event_id}'
            hierarchy_rows.append({
                'labels': comp_name,
                'parents': '',
                'ids': root_id,
                'values': 1,
                'level': 0,
                'hover_info': comp_hover
            })
            
            # Get all rounds for this competition
            event_contexts = supabase.table("event_context").select("*").eq("club_competition_id", event_id).execute()
            
            if not event_contexts.data:
                return pd.DataFrame(hierarchy_rows)
            
            round_ids = list(set([ec['round_id'] for ec in event_contexts.data if ec.get('round_id')]))
            
            if round_ids:
                rounds = supabase.table("round").select("*, category(discipline_id, age_division_id, equipment_id)").in_("round_id", round_ids).execute()
                
                for round_data in rounds.data:
                    round_id = round_data['round_id']
                    round_name = round_data['name']
                    round_node_id = f'round_{round_id}'
                    
                    # Build detailed hover info for round
                    round_hover = f"<b>Round</b><br>"
                    round_hover += f"ID: {round_id}<br>"
                    round_hover += f"Name: {round_name}<br>"
                    round_hover += f"Category ID: {round_data.get('category_id', 'N/A')}<br>"
                    if round_data.get('category'):
                        cat = round_data['category']
                        round_hover += f"Discipline ID: {cat.get('discipline_id', 'N/A')}<br>"
                        round_hover += f"Age Division ID: {cat.get('age_division_id', 'N/A')}<br>"
                        round_hover += f"Equipment ID: {cat.get('equipment_id', 'N/A')}<br>"
                    round_hover += f"Created: {round_data.get('created_at', 'N/A')[:10] if round_data.get('created_at') else 'N/A'}"
                    
                    hierarchy_rows.append({
                        'labels': round_name,
                        'parents': root_id,
                        'ids': round_node_id,
                        'values': 1,
                        'level': 1,
                        'hover_info': round_hover
                    })
                    
                    # Get ranges and ends for this round
                    _add_ranges_and_ends_for_icicle(hierarchy_rows, event_contexts.data, round_id, round_node_id, level_offset=2)
        
        return pd.DataFrame(hierarchy_rows)
    
    except Exception as e:
        print(f"Error getting event hierarchy for icicle: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def _add_ranges_and_ends_for_icicle(hierarchy_rows, event_contexts, round_id, parent_node_id, level_offset):
    """
    Helper function to add ranges and ends to the hierarchy for icicle chart
    
    Args:
        hierarchy_rows: list to append hierarchy data to
        event_contexts: list of event context records
        round_id: the round ID to get contexts for
        parent_node_id: the parent node ID (round node)
        level_offset: the level offset for range nodes
    """
    # Get contexts for this specific round
    round_contexts = [ec for ec in event_contexts if ec.get('round_id') == round_id]
    
    # Group by range
    range_ids = list(set([ec['range_id'] for ec in round_contexts if ec.get('range_id')]))
    
    if range_ids:
        ranges = supabase.table("range").select("*, target_face(*)").in_("range_id", range_ids).execute()
        
        for range_data in ranges.data:
            range_id = range_data['range_id']
            range_distance = range_data.get('distance', 'N/A')
            range_unit = range_data.get('unit_of_length', 'm')
            range_name = f"{range_distance}{range_unit}" if range_distance != 'N/A' else f"Range {range_id}"
            range_node_id = f'range_{range_id}_{parent_node_id}'
            
            # Build detailed hover info for range
            range_hover = f"<b>Range</b><br>"
            range_hover += f"ID: {range_id}<br>"
            range_hover += f"Distance: {range_distance} {range_unit}<br>"
            range_hover += f"Target Face ID: {range_data.get('target_face_id', 'N/A')}<br>"
            if range_data.get('target_face'):
                tf = range_data['target_face']
                range_hover += f"Target Diameter: {tf.get('diameter', 'N/A')} {tf.get('unit_of_length', 'cm')}<br>"
            range_hover += f"Created: {range_data.get('created_at', 'N/A')[:10] if range_data.get('created_at') else 'N/A'}"
            
            hierarchy_rows.append({
                'labels': range_name,
                'parents': parent_node_id,
                'ids': range_node_id,
                'values': 1,
                'level': level_offset,
                'hover_info': range_hover
            })
            
            # Get ends for this range in this round
            # Count unique end_order values for this range and round
            range_round_contexts = [ec for ec in round_contexts if ec.get('range_id') == range_id]
            
            if range_round_contexts:
                # Get unique end orders
                end_orders = sorted(set([ec.get('end_order') for ec in range_round_contexts if ec.get('end_order')]))
                
                # Add each end
                for end_order in end_orders:
                    end_id = f'end_{range_id}_{parent_node_id}_{end_order}'
                    
                    # Find the event context for this specific end
                    end_context = next((ec for ec in range_round_contexts if ec.get('end_order') == end_order), None)
                    
                    # Build detailed hover info for end
                    end_hover = f"<b>End</b><br>"
                    end_hover += f"End Order: {end_order}<br>"
                    if end_context:
                        end_hover += f"Event Context ID: {end_context.get('event_context_id', 'N/A')}<br>"
                        end_hover += f"Round ID: {end_context.get('round_id', 'N/A')}<br>"
                        end_hover += f"Range ID: {end_context.get('range_id', 'N/A')}"
                    
                    hierarchy_rows.append({
                        'labels': f'End {end_order}',
                        'parents': range_node_id,
                        'ids': end_id,
                        'values': 1,
                        'level': level_offset + 1,
                        'hover_info': end_hover
                    })

def get_user_joined_events(user_id, time_filter="all"):
    """Get events that a user has joined (approved enrollment)
    
    Args:
        user_id: The user's account ID
        time_filter: "all", "history" (past events), or "upcoming" (future events)
    
    Returns:
        dict with 'championships' and 'competitions' DataFrames
    """
    try:
        # Get approved enrollment requests for this user
        requests_response = supabase.table("request_competition_form")\
            .select("*, yearly_club_championship_id, club_competition_id")\
            .eq("sender_id", user_id)\
            .eq("status", "eligible")\
            .eq("action", "enrol")\
            .execute()
        
        if not requests_response.data:
            return {
                'championships': pd.DataFrame(),
                'competitions': pd.DataFrame()
            }
        
        requests_df = pd.DataFrame(requests_response.data)
        
        # Separate championship and competition requests
        championship_requests = requests_df[requests_df['yearly_club_championship_id'].notna()]
        competition_requests = requests_df[requests_df['club_competition_id'].notna()]
        
        # Get championship details
        championships_df = pd.DataFrame()
        if not championship_requests.empty:
            championship_ids = championship_requests['yearly_club_championship_id'].unique().tolist()
            champ_response = supabase.table("yearly_club_championship")\
                .select("*")\
                .in_("yearly_club_championship_id", championship_ids)\
                .execute()
            
            if champ_response.data:
                championships_df = pd.DataFrame(champ_response.data)
                
                # Apply time filter based on year
                current_year = datetime.now().year
                if time_filter == "history":
                    championships_df = championships_df[championships_df['year'] < current_year]
                elif time_filter == "upcoming":
                    championships_df = championships_df[championships_df['year'] >= current_year]
        
        # Get competition details
        competitions_df = pd.DataFrame()
        if not competition_requests.empty:
            competition_ids = competition_requests['club_competition_id'].unique().tolist()
            comp_response = supabase.table("club_competition")\
                .select("*")\
                .in_("club_competition_id", competition_ids)\
                .execute()
            
            if comp_response.data:
                competitions_df = pd.DataFrame(comp_response.data)
                
                # Apply time filter based on end_date
                current_date = datetime.now().date()
                if time_filter == "history":
                    competitions_df = competitions_df[pd.to_datetime(competitions_df['end_date']).dt.date < current_date]
                elif time_filter == "upcoming":
                    competitions_df = competitions_df[pd.to_datetime(competitions_df['end_date']).dt.date >= current_date]
        
        return {
            'championships': championships_df,
            'competitions': competitions_df
        }
    
    except Exception as e:
        print(f"Error fetching user joined events: {e}")
        return {
            'championships': pd.DataFrame(),
            'competitions': pd.DataFrame()
        }

def add_participant_to_participating_table(user_id: str, event_type: str, event_id: str, round_id: str) -> None:
    if event_type == 'club competition':
        #step 1: get all rows from event_context table where club_competition_id = event_id and round_id = round_id transform to a dataframe
        event_context_response = supabase.table("event_context").select("*").eq("club_competition_id", event_id).eq("round_id", round_id).execute()
        event_context_df = pd.DataFrame(event_context_response.data) 
        #for each row in event_context_df, insert a row into participating table with user_id and event_context_id with type = "competition". Does the same with type "practice"
        for _, row in event_context_df.iterrows():
            supabase.table("participating").insert({
                "participating_id": user_id,
                "event_context_id": row["event_context_id"],
                "type": "competition",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }).execute()
        for _, row in event_context_df.iterrows():
            supabase.table("participating").insert({
                "participating_id": user_id,
                "event_context_id": row["event_context_id"],
                "type": "practice",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }).execute()
    elif event_type == 'yearly club championship':
        #step 1: get all rows from event_context table where yearly_club_championship_id = event_id and round_id = round_id transform to a dataframe
        event_context_response = supabase.table("event_context").select("*").eq("yearly_club_championship_id", event_id).eq("round_id", round_id).execute()
        event_context_df = pd.DataFrame(event_context_response.data) 
        #for each row in event_context_df, insert a row into participating table with user_id and event_context_id with type = "championship". Does the same with type "practice"
        for _, row in event_context_df.iterrows():
            supabase.table("participating").insert({
                "participating_id": user_id,
                "event_context_id": row["event_context_id"],
                "type": "championship",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }).execute()
        for _, row in event_context_df.iterrows():
            supabase.table("participating").insert({
                "participating_id": user_id,
                "event_context_id": row["event_context_id"],
                "type": "practice",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }).execute()

def add_recorder_to_recording_table(user_id: str, event_type: str, event_id:str) -> None:
    if event_type == 'club competition':
        #insert a row into recording table with user_id and club_competition_id = event_id
        supabase.table("recording").insert({
            "recording_id": user_id,
            "club_competition_id": event_id
        }).execute()
    elif event_type == 'yearly club championship':
        #get all club_competition_id from event_context table where yearly_club_championship_id = event_id
        event_context_response = supabase.table("event_context").select("club_competition_id")\
            .eq("yearly_club_championship_id", event_id)\
            .execute()
        #then for each club_competition_id, insert a row into recording table with given user_id, yearly_club_championship_id = event_id and club_competition_id
        for row in event_context_response.data:
            supabase.table("recording").insert({
                "recording_id": user_id,
                "yearly_club_championship_id": event_id,
                "club_competition_id": row["club_competition_id"],
                "created_at": datetime.now().isoformat()
            }).execute()

def get_all_yearly_championship_ids_of_a_recorder(user_id: str) -> list:
    '''there are two tables to collect yearly club championship ids of a recorder: yearly_club_championship and recording
    for yearly_club_championship table, we need to get all yearly club championships where creator_id = user_id.
    for recording table, we need to get all yearly club championships where recording_id = user_id.
    finally, we need to combine the two lists and remove duplicates before returning the final list of yearly club championships.
    '''
    try:
        championship_ids = set()
        
        # Get yearly championships where user is the creator
        creator_response = supabase.table("yearly_club_championship")\
            .select("yearly_club_championship_id")\
            .eq("creator_id", user_id)\
            .execute()
        
        if creator_response.data:
            championship_ids.update([row['yearly_club_championship_id'] for row in creator_response.data])
        
        # Get yearly championships where user is a recorder
        recorder_response = supabase.table("recording")\
            .select("yearly_club_championship_id")\
            .eq("recording_id", user_id)\
            .not_.is_("yearly_club_championship_id", "null")\
            .execute()
        
        if recorder_response.data:
            championship_ids.update([row['yearly_club_championship_id'] for row in recorder_response.data if row.get('yearly_club_championship_id')])
        
        return list(championship_ids)
    
    except Exception as e:
        print(f"Error fetching yearly championship IDs for recorder: {e}")
        return []

def get_all_club_competition_ids_of_a_recorder(user_id: str) -> list:
    '''there are two tables to collect club competition ids of a recorder: club_competition and recording
    for club_competition table, we need to get all club competitions where creator_id = user_id.
    for recording table, we need to get all club competitions where recording_id = user_id.
    finally, we need to combine the two lists and remove duplicates before returning the final list of club competitions.
    '''
    try:
        competition_ids = set()
        
        # Get club competitions where user is the creator
        creator_response = supabase.table("club_competition")\
            .select("club_competition_id")\
            .eq("creator_id", user_id)\
            .execute()
        
        if creator_response.data:
            competition_ids.update([row['club_competition_id'] for row in creator_response.data])
        
        # Get club competitions where user is a recorder
        recorder_response = supabase.table("recording")\
            .select("club_competition_id")\
            .eq("recording_id", user_id)\
            .not_.is_("club_competition_id", "null")\
            .execute()
        
        if recorder_response.data:
            competition_ids.update([row['club_competition_id'] for row in recorder_response.data if row.get('club_competition_id')])
        
        return list(competition_ids)
    
    except Exception as e:
        print(f"Error fetching club competition IDs for recorder: {e}")
        return []

def get_yearly_club_championship_map_of_a_recorder(user_id: str) -> dict:
    '''Get mapping of yearly club championship names to IDs for a recorder'''
    championship_ids = get_all_yearly_championship_ids_of_a_recorder(user_id)
    if not championship_ids:
        return {}
    response = supabase.table("yearly_club_championship").select("yearly_club_championship_id, name")\
        .in_("yearly_club_championship_id", championship_ids)\
        .execute()
    if not response.data:
        return {}
    return {row['name']: row['yearly_club_championship_id'] for row in response.data}
def get_club_competition_map_of_a_recorder(user_id: str) -> dict:
    '''Get mapping of club competition names to IDs for a recorder'''
    competition_ids = get_all_club_competition_ids_of_a_recorder(user_id)
    if not competition_ids:
        return {}
    response = supabase.table("club_competition").select("club_competition_id, name")\
        .in_("club_competition_id", competition_ids)\
        .execute()
    if not response.data:
        return {}
    return {row['name']: row['club_competition_id'] for row in response.data}


def get_all_rounds_in_a_club_competititon(club_competition_id: str) -> list:
    """Get all round IDs in a given club competition"""
    try:
        response = supabase.table("event_context").select("round_id")\
            .eq("club_competition_id", club_competition_id)\
            .execute()
        
        if not response.data:
            return []
        
        round_ids = list(set([row['round_id'] for row in response.data if row.get('round_id')]))
        return round_ids
    
    except Exception as e:
        print(f"Error fetching rounds in club competition: {e}")
        return []

def get_all_rounds_in_a_yearly_championship(yearly_championship_id: str) -> list:
    """Get all round IDs in a given yearly club championship"""
    try:
        response = supabase.table("event_context").select("round_id")\
            .eq("yearly_club_championship_id", yearly_championship_id)\
            .execute()
        
        if not response.data:
            return []
        
        round_ids = list(set([row['round_id'] for row in response.data if row.get('round_id')]))
        #turn to set and make unique, then back to list
        round_ids = list(set(round_ids))
        return round_ids
    except Exception as e:
        print(f"Error fetching rounds in yearly championship: {e}")
        return []

def get_round_map_of_an_event(event_type: str, event_id: str) -> dict:
    """Get mapping of round names to IDs for a given event (club competition or yearly championship)"""
    try:
        if event_type == 'club competition':
            round_ids = get_all_rounds_in_a_club_competititon(event_id)
        elif event_type == 'yearly club championship':
            round_ids = get_all_rounds_in_a_yearly_championship(event_id)
        else:
            return {}
        
        if not round_ids:
            return {}
        
        response = supabase.table("round").select("round_id, name")\
            .in_("round_id", round_ids)\
            .execute()
        
        if not response.data:
            return {}
        
        return {row['name']: row['round_id'] for row in response.data}
    
    except Exception as e:
        print(f"Error fetching round map of an event: {e}")
        return {}
    
def get_all_club_competition_by_a_yearly_championship(yearly_championship_id: str) -> list:
    """Get all club competition IDs under a given yearly club championship"""
    try:
        response = supabase.table("event_context").select("club_competition_id")\
            .eq("yearly_club_championship_id", yearly_championship_id)\
            .execute()
        
        if not response.data:
            return []
        
        competition_ids = list(set([row['club_competition_id'] for row in response.data if row.get('club_competition_id')]))
        return competition_ids
    
    except Exception as e:
        print(f"Error fetching club competitions under yearly championship: {e}")
        return []

def get_club_competition_map_of_a_yearly_championship(yearly_championship_id: str) -> dict:
    """Get mapping of club competition names to IDs under a given yearly club championship"""
    competition_ids = get_all_club_competition_by_a_yearly_championship(yearly_championship_id)
    if not competition_ids:
        return {}
    response = supabase.table("club_competition").select("club_competition_id, name")\
        .in_("club_competition_id", competition_ids)\
        .execute()

    if not response.data:
        return {}

    return {row['name']: row['club_competition_id'] for row in response.data}

def get_all_club_competition_ids_of_no_yearly_club_championship() -> list:
    '''Get all club competition IDs that where yearly club championship_id is NULL in event_context table'''
    try:
        response = supabase.table("event_context").select("club_competition_id")\
            .is_("yearly_club_championship_id", "null")\
            .not_.is_("club_competition_id", "null")\
            .execute()
        
        if not response.data:
            return []
        
        competition_ids = list(set([row['club_competition_id'] for row in response.data if row.get('club_competition_id')]))
        return competition_ids
    
    except Exception as e:
        print(f"Error fetching club competition IDs of no yearly championship: {e}")
        return []
def get_club_competition_map_of_no_yearly_club_championship() -> dict:
    '''Get mapping of club competition names to IDs for competitions not part of any yearly championship'''
    competition_ids = get_all_club_competition_ids_of_no_yearly_club_championship()
    if not competition_ids:
        return {}
    response = supabase.table("club_competition").select("club_competition_id, name")\
        .in_("club_competition_id", competition_ids).execute()
    return {row['name']: row['club_competition_id'] for row in response.data}
