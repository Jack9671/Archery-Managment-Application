import pandas as pd
import numpy as np
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

def get_round_performance_for_competition(archer_id, club_competition_id, round_id):
    """
    Get performance for a specific archer in a specific round within a competition.
    Returns: total_score, ranking, percentile
    """
    try:
        # Get all participants' scores for this round in this competition
        response = supabase.table("participating").select(
            """
            participating_id,
            sum_score,
            event_context!inner(
                club_competition_id,
                round_id
            )
            """
        ).eq("event_context.club_competition_id", club_competition_id).eq(
            "event_context.round_id", round_id
        ).eq("type", "competition").eq("status", "eligible").execute()
        
        if not response.data:
            return None
        
        # Calculate scores per archer
        archer_scores = {}
        for row in response.data:
            pid = row['participating_id']
            if pid not in archer_scores:
                archer_scores[pid] = 0
            archer_scores[pid] += row['sum_score']
        
        # Sort by score descending
        sorted_archers = sorted(archer_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Find archer's ranking
        archer_total_score = archer_scores.get(archer_id, 0)
        ranking = None
        for idx, (pid, score) in enumerate(sorted_archers):
            if pid == archer_id:
                ranking = idx + 1
                break
        
        # Calculate percentile
        total_archers = len(sorted_archers)
        if total_archers > 0 and ranking:
            percentile = ((total_archers - ranking) / total_archers) * 100
        else:
            percentile = 0
        
        return {
            "total_score": archer_total_score,
            "ranking": ranking,
            "percentile": round(percentile, 2),
            "total_participants": total_archers
        }
    except Exception as e:
        print(f"Error getting round performance: {e}")
        return None

def get_normalized_average_for_round_in_championship(archer_id, yearly_championship_id, round_id):
    """
    Get normalized average score for a round across all competitions in a championship.
    Formula: average of (actual_score / max_possible_score) for each competition
    """
    try:
        # Get all competitions in this championship
        comp_response = supabase.table("club_competition").select(
            "club_competition_id"
        ).eq("yearly_club_championship_id", yearly_championship_id).execute()
        
        if not comp_response.data:
            return None
        
        competition_ids = [comp['club_competition_id'] for comp in comp_response.data]
        
        normalized_scores = []
        
        for comp_id in competition_ids:
            # Get archer's score for this round in this competition
            score_response = supabase.table("participating").select(
                """
                sum_score,
                event_context!inner(
                    club_competition_id,
                    round_id,
                    end_order
                )
                """
            ).eq("participating_id", archer_id).eq(
                "event_context.club_competition_id", comp_id
            ).eq("event_context.round_id", round_id).eq("type", "competition").eq("status", "eligible").execute()
            
            if score_response.data:
                actual_score = sum(row['sum_score'] for row in score_response.data)
                
                # Get max possible score (number of ends * 6 arrows * 10 points)
                num_ends = len(score_response.data)
                max_score = num_ends * 6 * 10
                
                if max_score > 0:
                    normalized_scores.append(actual_score / max_score)
        
        if normalized_scores:
            avg_normalized = np.mean(normalized_scores)
            return {
                "normalized_average": round(avg_normalized, 4),
                "competitions_participated": len(normalized_scores),
                "total_competitions": len(competition_ids)
            }
        return None
    except Exception as e:
        print(f"Error getting normalized average: {e}")
        return None

def get_category_percentile(archer_id, category_id):
    """Get archer's percentile for a specific category"""
    try:
        response = supabase.table("category_rating_percentile").select(
            "percentile"
        ).eq("archer_id", archer_id).eq("category_id", category_id).execute()
        
        if response.data:
            return response.data[0]['percentile']
        return None
    except Exception as e:
        print(f"Error getting category percentile: {e}")
        return None

def get_archer_competition_history(archer_id):
    """Get all competitions an archer has participated in"""
    try:
        response = supabase.table("participating").select(
            """
            event_context!inner(
                club_competition_id,
                club_competition(name, date_start, date_end)
            )
            """
        ).eq("participating_id", archer_id).eq("type", "competition").eq("status", "eligible").execute()
        
        if response.data:
            competitions = {}
            for row in response.data:
                comp_id = row['event_context']['club_competition_id']
                if comp_id not in competitions:
                    competitions[comp_id] = row['event_context']['club_competition']
            
            return pd.DataFrame(list(competitions.values()))
        return pd.DataFrame()
    except Exception as e:
        print(f"Error getting competition history: {e}")
        return pd.DataFrame()

def get_rounds_in_competition(club_competition_id):
    """Get all rounds in a specific competition"""
    try:
        response = supabase.table("event_context").select(
            "round_id, round(name, category_id)"
        ).eq("club_competition_id", club_competition_id).execute()
        
        if response.data:
            rounds = {}
            for row in response.data:
                round_id = row['round_id']
                if round_id not in rounds:
                    rounds[round_id] = row['round']
            
            return {f"{r['name']} (ID: {rid})": rid for rid, r in rounds.items()}
        return {}
    except Exception as e:
        print(f"Error getting rounds: {e}")
        return {}

def get_yearly_championships():
    """Get all yearly championships"""
    try:
        response = supabase.table("yearly_club_championship").select(
            "yearly_club_championship_id, name, year"
        ).execute()
        
        if response.data:
            return {f"{row['name']} - {row['year']} (ID: {row['yearly_club_championship_id']})": 
                   row['yearly_club_championship_id'] for row in response.data}
        return {}
    except Exception as e:
        print(f"Error getting championships: {e}")
        return {}

def get_category_map():
    """Get mapping of category IDs to names"""
    try:
        response = supabase.table("category").select(
            """
            category_id,
            discipline(name),
            age_division(min_age, max_age),
            equipment(name)
            """
        ).execute()
        
        if response.data:
            category_map = {}
            for row in response.data:
                cat_name = f"{row['discipline']['name']} - {row['equipment']['name']} (Ages {row['age_division']['min_age']}-{row['age_division']['max_age']})"
                category_map[cat_name] = row['category_id']
            return category_map
        return {}
    except Exception as e:
        print(f"Error getting category map: {e}")
        return {}

def get_personal_statistics(archer_id, score_type='competition'):
    """Get overall statistics for an archer"""
    try:
        response = supabase.table("participating").select(
            "sum_score, status"
        ).eq("participating_id", archer_id).eq("type", score_type).execute()
        
        if response.data:
            scores = [row['sum_score'] for row in response.data]
            eligible_scores = [row['sum_score'] for row in response.data if row['status'] == 'eligible']
            
            return {
                "total_ends": len(scores),
                "total_eligible_ends": len(eligible_scores),
                "average_score": round(np.mean(scores), 2) if scores else 0,
                "highest_score": max(scores) if scores else 0,
                "lowest_score": min(scores) if scores else 0,
                "std_deviation": round(np.std(scores), 2) if scores else 0
            }
        return None
    except Exception as e:
        print(f"Error getting personal statistics: {e}")
        return None

def get_community_leaderboard(round_id, club_competition_id, limit=10):
    """Get top performers for a specific round in a competition"""
    try:
        response = supabase.table("participating").select(
            """
            participating_id,
            sum_score,
            archer(account(fullname)),
            event_context!inner(
                club_competition_id,
                round_id
            )
            """
        ).eq("event_context.club_competition_id", club_competition_id).eq(
            "event_context.round_id", round_id
        ).eq("type", "competition").eq("status", "eligible").execute()
        
        if not response.data:
            return pd.DataFrame()
        
        # Calculate total scores per archer
        archer_scores = {}
        archer_names = {}
        for row in response.data:
            pid = row['participating_id']
            if pid not in archer_scores:
                archer_scores[pid] = 0
                archer_names[pid] = row['archer']['account']['fullname']
            archer_scores[pid] += row['sum_score']
        
        # Create leaderboard
        leaderboard = [
            {"Rank": idx + 1, "Archer": archer_names[pid], "Archer ID": pid, "Total Score": score}
            for idx, (pid, score) in enumerate(sorted(archer_scores.items(), key=lambda x: x[1], reverse=True)[:limit])
        ]
        
        return pd.DataFrame(leaderboard)
    except Exception as e:
        print(f"Error getting leaderboard: {e}")
        return pd.DataFrame()
