from utility_function.initilize_dbconnection import supabase
import pandas as pd
import datetime
def get_all_equipment():
    """Get all equipment types"""
    try:
        response = supabase.table("equipment").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching equipment: {e}")
        return pd.DataFrame()

def get_all_disciplines():
    """Get all disciplines"""
    try:
        response = supabase.table("discipline").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching disciplines: {e}")
        return pd.DataFrame()

def get_all_age_divisions():
    """Get all age divisions"""
    try:
        response = supabase.table("age_division").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching age divisions: {e}")
        return pd.DataFrame()

def get_all_categories():
    """Get all categories with related information"""
    try:
        response = supabase.table("category").select("*").execute()
        
        if not response.data:
            return pd.DataFrame()
        
        df = pd.DataFrame(response.data)
        
        # Enrich with related information
        for idx, row in df.iterrows():
            # Get discipline name
            discipline = supabase.table("discipline").select("name").eq("discipline_id", row['discipline_id']).execute()
            if discipline.data:
                df.at[idx, 'discipline_name'] = discipline.data[0]['name']
            
            # Get age division
            age_div = supabase.table("age_division").select("min_age, max_age").eq("age_division_id", row['age_division_id']).execute()
            if age_div.data:
                df.at[idx, 'age_range'] = f"{age_div.data[0]['min_age']}-{age_div.data[0]['max_age']}"
            
            # Get equipment name
            equipment = supabase.table("equipment").select("name").eq("equipment_id", row['equipment_id']).execute()
            if equipment.data:
                df.at[idx, 'equipment_name'] = equipment.data[0]['name']
        
        return df
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return pd.DataFrame()

def get_rounds_by_equipment(equipment_id):
    """Get all rounds that use a specific equipment"""
    try:
        # Get categories with this equipment
        categories = supabase.table("category").select("category_id").eq("equipment_id", equipment_id).execute()
        
        if not categories.data:
            return pd.DataFrame()
        
        category_ids = [cat['category_id'] for cat in categories.data]
        
        # Get rounds with these categories
        response = supabase.table("round").select("*").in_("category_id", category_ids).execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching rounds by equipment: {e}")
        return pd.DataFrame()

def add_equipment(equipment_name, description, photo_url=None):
    """Add new equipment (AAF members only)"""
    try:
        response = supabase.table("equipment").insert({
            "name": equipment_name,
            "description": description,
            "photo_url": photo_url or "https://ghcpcyvethwdzzgyymfp.supabase.co/storage/v1/object/public/User%20Uploaded/Equipment_Photo/Default_Equipment_Photo.png",
            "created_at": datetime.now().isoformat()
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error adding equipment: {e}")
        return None

def add_discipline(discipline_name, description):
    """Add new discipline (AAF members only)"""
    try:
        response = supabase.table("discipline").insert({
            "name": discipline_name,
            "description": description,
            "created_at": datetime.now().isoformat()
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error adding discipline: {e}")
        return None

def add_age_division(min_age, max_age):
    """Add new age division (AAF members only)"""
    try:
        response = supabase.table("age_division").insert({
            "min_age": min_age,
            "max_age": max_age,
            "created_at": datetime.now().isoformat()
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error adding age division: {e}")
        return None

def add_target_face(diameter, unit_of_length):
    """Add new target face (AAF members only)"""
    try:
        response = supabase.table("target_face").insert({
            "diameter": diameter,
            "unit_of_length": unit_of_length,
            "created_at": datetime.now().isoformat()
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error adding target face: {e}")
        return None

def add_range(distance, unit_of_length, target_face_id):
    """Add new range (AAF members only)"""
    try:
        from datetime import datetime
        response = supabase.table("range").insert({
            "distance": distance,
            "unit_of_length": unit_of_length,
            "target_face_id": target_face_id,
            "created_at": datetime.now().isoformat()
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error adding range: {e}")
        import traceback
        traceback.print_exc()
        return None

def add_round(round_name, category_id):
    """Add new round (AAF members only)"""
    try:
        response = supabase.table("round").insert({
            "name": round_name,
            "category_id": category_id,
            "created_at": datetime.now().isoformat()
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error adding round: {e}")
        return None
