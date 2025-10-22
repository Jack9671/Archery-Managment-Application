from utility_function.initilize_dbconnection import supabase
import streamlit as st
import pandas as pd

def get_club_competitions():
    """Get all club competitions"""
    try:
        response = supabase.table("club_competition").select("club_competition_id, name").execute()
        return {comp['name']: comp['club_competition_id'] for comp in response.data} if response.data else {}
    except Exception as e:
        st.error(f"Error fetching club competitions: {str(e)}")
        return {}

def get_rounds():
    """Get all rounds"""
    try:
        response = supabase.table("round").select("round_id, name").execute()
        return {round['name']: round['round_id'] for round in response.data} if response.data else {}
    except Exception as e:
        st.error(f"Error fetching rounds: {str(e)}")
        return {}

def get_archers():
    """Get all archers with their account names"""
    try:
        response = supabase.table("archer").select(
            "archer_id, account!inner(fullname)"
        ).execute()
        return {archer['account']['fullname']: archer['archer_id'] for archer in response.data} if response.data else {}
    except Exception as e:
        st.error(f"Error fetching archers: {str(e)}")
        return {}

def get_archer_scores(participating_id, club_competition_id, round_id):
    """
    Get participating records for a specific archer in a specific competition and round
    
    Args:
        participating_id: The archer's ID
        club_competition_id: The club competition ID
        round_id: The round ID
    
    Returns:
        List of participating records
    """
    try:
        # Query participating table with joins to get event context details
        response = supabase.table("participating").select(
            "*, event_context!inner(club_competition_id, round_id, end_order, range_id)"
        ).eq(
            "participating_id", participating_id
        ).eq(
            "event_context.club_competition_id", club_competition_id
        ).eq(
            "event_context.round_id", round_id
        ).eq(
            "type", "competition"
        ).execute()
        
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching archer scores: {str(e)}")
        return []

def get_recorder_scores(club_competition_id, round_id=None, participating_id=None):
    """
    Get participating records for a recorder with optional filters
    
    Args:
        club_competition_id: The club competition ID
        round_id: Optional round ID filter
        participating_id: Optional archer ID filter
    
    Returns:
        List of participating records
    """
    try:
        # Build query with joins
        query = supabase.table("participating").select(
            "*, event_context!inner(club_competition_id, round_id, end_order, range_id), archer!inner(account!inner(fullname))"
        ).eq(
            "event_context.club_competition_id", club_competition_id
        ).eq(
            "type", "competition"
        )
        
        # Add optional filters
        if round_id:
            query = query.eq("event_context.round_id", round_id)
        if participating_id:
            query = query.eq("participating_id", participating_id)
        
        response = query.execute()
        
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching recorder scores: {str(e)}")
        return []

def update_participating_scores(updates):
    """
    Update participating scores in the database
    
    Args:
        updates: List of dictionaries with updated participating records
    
    Returns:
        Boolean indicating success
    """
    try:
        for update in updates:
            # Calculate sum_score
            sum_score = (
                update.get('score_1st_arrow', 0) +
                update.get('score_2nd_arrow', 0) +
                update.get('score_3rd_arrow', 0) +
                update.get('score_4th_arrow', 0) +
                update.get('score_5st_arrow', 0) +
                update.get('score_6st_arrow', 0)
            )
            
            # Prepare update data
            update_data = {
                'score_1st_arrow': update.get('score_1st_arrow'),
                'score_2nd_arrow': update.get('score_2nd_arrow'),
                'score_3rd_arrow': update.get('score_3rd_arrow'),
                'score_4th_arrow': update.get('score_4th_arrow'),
                'score_5st_arrow': update.get('score_5st_arrow'),
                'score_6st_arrow': update.get('score_6st_arrow'),
                'sum_score': sum_score,
                'updated_at': 'now()'
            }
            
            # Add status if it's a recorder update
            if 'status' in update:
                update_data['status'] = update['status']
            
            # Update the record
            supabase.table("participating").update(
                update_data
            ).eq(
                "participating_id", update['participating_id']
            ).eq(
                "event_context_id", update['event_context_id']
            ).eq(
                "type", update['type']
            ).execute()
        
        return True
    except Exception as e:
        st.error(f"Error updating scores: {str(e)}")
        return False

def format_participating_data_for_display(records, include_archer_name=False):
    """
    Format participating records for display in st.data_editor
    
    Args:
        records: List of participating records
        include_archer_name: Whether to include archer name (for recorder view)
    
    Returns:
        DataFrame formatted for display
    """
    if not records:
        return pd.DataFrame()
    
    # Sort records by end_order
    records_sorted = sorted(records, key=lambda x: x['event_context']['end_order'])
    
    display_data = []
    for record in records_sorted:
        row = {
            'End Order': record['event_context']['end_order'],
            'Arrow 1': record['score_1st_arrow'],
            'Arrow 2': record['score_2nd_arrow'],
            'Arrow 3': record['score_3rd_arrow'],
            'Arrow 4': record['score_4th_arrow'],
            'Arrow 5': record['score_5st_arrow'],
            'Arrow 6': record['score_6st_arrow'],
            'Total': record['sum_score'],
            'Status': record['status'],
            # Hidden fields for update
            '_participating_id': record['participating_id'],
            '_event_context_id': record['event_context_id'],
            '_type': record['type']
        }
        
        if include_archer_name:
            row['Archer'] = record['archer']['account']['fullname']
            # Move Archer to front
            row = {'Archer': row['Archer'], **{k: v for k, v in row.items() if k != 'Archer'}}
        
        display_data.append(row)
    
    return pd.DataFrame(display_data)
