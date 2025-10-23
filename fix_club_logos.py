"""
Script to update all club logos to use the new storage structure
Run this once to fix existing clubs in the database
"""
from utility_function.initilize_dbconnection import supabase

def update_club_logos():
    """Update all clubs with old/missing logo URLs to use the new default"""
    
    new_default_url = "https://ghcpcyvethwdzzgyymfp.supabase.co/storage/v1/object/public/User%20Uploaded/Club_Logo/Default_Club_Logo.png"
    
    try:
        # Get all clubs
        response = supabase.table("club").select("club_id, club_logo_url").execute()
        clubs = response.data
        
        updated_count = 0
        
        for club in clubs:
            club_id = club['club_id']
            current_url = club.get('club_logo_url', '')
            
            # Update if URL is None, empty, or points to old User Avatar bucket
            should_update = (
                not current_url or 
                'User%20Avatar' in current_url or 
                'User Avatar' in current_url or
                'Default_Avatar' in current_url
            )
            
            if should_update:
                supabase.table("club").update({
                    "club_logo_url": new_default_url
                }).eq("club_id", club_id).execute()
                
                updated_count += 1
                print(f"Updated club {club_id}")
        
        print(f"\n✅ Successfully updated {updated_count} club(s)")
        return True
        
    except Exception as e:
        print(f"❌ Error updating club logos: {e}")
        return False

if __name__ == "__main__":
    print("Starting club logo update...")
    update_club_logos()
