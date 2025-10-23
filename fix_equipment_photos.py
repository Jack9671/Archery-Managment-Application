"""
Script to update all equipment photos to use the new storage structure
Run this once to fix existing equipment in the database
"""
from utility_function.initilize_dbconnection import supabase

def update_equipment_photos():
    """Update all equipment with old/missing photo URLs to use the new default"""
    
    new_default_url = "https://ghcpcyvethwdzzgyymfp.supabase.co/storage/v1/object/public/User%20Uploaded/Equipment_Photo/Default_Equipment_Photo.png"
    
    try:
        # Get all equipment
        response = supabase.table("equipment").select("equipment_id, photo_url, name").execute()
        equipment_list = response.data
        
        updated_count = 0
        
        for equipment in equipment_list:
            equipment_id = equipment['equipment_id']
            equipment_name = equipment.get('name', 'Unknown')
            current_url = equipment.get('photo_url', '')
            
            # Update if URL is None, empty, or points to old paths
            should_update = (
                not current_url or 
                current_url is None or
                'User%20Avatar' in str(current_url) or 
                'User Avatar' in str(current_url) or
                str(current_url).strip() == '' or
                str(current_url).upper() == 'NULL'
            )
            
            if should_update:
                supabase.table("equipment").update({
                    "photo_url": new_default_url
                }).eq("equipment_id", equipment_id).execute()
                
                updated_count += 1
                print(f"Updated equipment {equipment_id}: {equipment_name}")
            else:
                print(f"Skipped equipment {equipment_id}: {equipment_name} (already has valid photo_url)")
        
        print(f"\n✅ Successfully updated {updated_count} equipment item(s)")
        print(f"📊 Total equipment checked: {len(equipment_list)}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating equipment photos: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting equipment photo update...")
    print("=" * 50)
    update_equipment_photos()
