from utility_function.initilize_dbconnection import supabase
import pandas as pd

def get_round_rankings(round_id, competition_id):
    """Get rankings for a specific round in a competition"""
    try:
        # Get all participants for this round
        event_contexts = supabase.table("event_context").select("event_context_id").eq("round_id", round_id).eq("club_competition_id", competition_id).execute()
        
        if not event_contexts.data:
            return pd.DataFrame()
        
        event_context_ids = [ctx['event_context_id'] for ctx in event_contexts.data]
        
        # Get all participating records
        participants_data = []
        for ec_id in event_context_ids:
            response = supabase.table("participating").select("*").eq("event_context_id", ec_id).eq("type", "competition").execute()
            if response.data:
                participants_data.extend(response.data)
        
        if not participants_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(participants_data)
        
        # Calculate total score for each participant
        score_columns = ['score_1st_arrow', 'score_2nd_arrow', 'score_3rd_arrow', 
                        'score_4th_arrow', 'score_5th_arrow', 'score_6th_arrow']
        df['total_score'] = df[score_columns].sum(axis=1)
        
        # Group by participant and sum scores
        participant_scores = df.groupby('participating_id')['total_score'].sum().reset_index()
        participant_scores = participant_scores.sort_values('total_score', ascending=False)
        participant_scores['rank'] = range(1, len(participant_scores) + 1)
        
        return participant_scores
    except Exception as e:
        print(f"Error getting round rankings: {e}")
        return pd.DataFrame()

def get_category_percentile(archer_id, category_id):
    """Get percentile for an archer in a specific category"""
    try:
        response = supabase.table("category_rating_percentile").select("*").eq("archer_id", archer_id).eq("category_id", category_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error fetching category percentile: {e}")
        return None

def calculate_normalized_average_score(archer_id, round_id, yearly_championship_id):
    """Calculate normalized average score for an archer in a specific round across all competitions in a yearly championship"""
    try:
        # Get all club competitions for this yearly championship
        competitions = supabase.table("club_competition").select("club_competition_id").execute()
        
        if not competitions.data:
            return 0
        
        # Get event contexts for this round in these competitions
        event_contexts = supabase.table("event_context").select("*").eq("round_id", round_id).eq("yearly_club_championship_id", yearly_championship_id).execute()
        
        if not event_contexts.data:
            return 0
        
        total_normalized_score = 0
        count = 0
        
        for ctx in event_contexts.data:
            # Get participant's score
            participating = supabase.table("participating").select("*").eq("participating_id", archer_id).eq("event_context_id", ctx['event_context_id']).eq("type", "competition").execute()
            
            if participating.data:
                part_data = participating.data[0]
                actual_score = (part_data.get('score_1st_arrow', 0) + 
                              part_data.get('score_2nd_arrow', 0) + 
                              part_data.get('score_3rd_arrow', 0) + 
                              part_data.get('score_4th_arrow', 0) + 
                              part_data.get('score_5th_arrow', 0) + 
                              part_data.get('score_6th_arrow', 0))
                
                # Max score is 6 arrows * 10 points = 60 per end
                max_score = 60
                normalized_score = actual_score / max_score if max_score > 0 else 0
                
                total_normalized_score += normalized_score
                count += 1
        
        return total_normalized_score / count if count > 0 else 0
    except Exception as e:
        print(f"Error calculating normalized average score: {e}")
        return 0

def get_personal_performance(archer_id):
    """Get personal performance data for an archer"""
    try:
        response = supabase.table("participating").select("*").eq("participating_id", archer_id).eq("type", "competition").execute()
        
        if not response.data:
            return pd.DataFrame()
        
        df = pd.DataFrame(response.data)
        
        # Calculate total scores
        score_columns = ['score_1st_arrow', 'score_2nd_arrow', 'score_3rd_arrow', 
                        'score_4th_arrow', 'score_5th_arrow', 'score_6th_arrow']
        df['total_score'] = df[score_columns].sum(axis=1)
        
        return df
    except Exception as e:
        print(f"Error fetching personal performance: {e}")
        return pd.DataFrame()

def get_community_performance(round_id, competition_id):
    """Get community performance for a specific round in a competition"""
    try:
        # Get all event contexts for this round and competition
        event_contexts = supabase.table("event_context").select("event_context_id").eq("round_id", round_id).eq("club_competition_id", competition_id).execute()
        
        if not event_contexts.data:
            return pd.DataFrame()
        
        event_context_ids = [ctx['event_context_id'] for ctx in event_contexts.data]
        
        # Get all participants
        all_participants = []
        for ec_id in event_context_ids:
            response = supabase.table("participating").select("*").eq("event_context_id", ec_id).eq("type", "competition").execute()
            if response.data:
                all_participants.extend(response.data)
        
        if not all_participants:
            return pd.DataFrame()
        
        df = pd.DataFrame(all_participants)
        
        # Calculate total scores
        score_columns = ['score_1st_arrow', 'score_2nd_arrow', 'score_3rd_arrow', 
                        'score_4th_arrow', 'score_5th_arrow', 'score_6th_arrow']
        df['total_score'] = df[score_columns].sum(axis=1)
        
        # Group by participant
        participant_scores = df.groupby('participating_id')['total_score'].sum().reset_index()
        
        return participant_scores
    except Exception as e:
        print(f"Error fetching community performance: {e}")
        return pd.DataFrame()

def get_all_categories():
    """Get all available categories"""
    try:
        response = supabase.table("category").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return pd.DataFrame()
