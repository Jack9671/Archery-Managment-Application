from utility_function.initilize_dbconnection import supabase

# Get current max form_id
result = supabase.table('request_competition_form').select('form_id').order('form_id', desc=True).limit(1).execute()

if result.data:
    max_id = result.data[0]['form_id']
    print(f"Current max form_id in table: {max_id}")
    next_id = max_id + 1
    print(f"Next form_id should be: {next_id}")
    
    # Execute SQL to reset the sequence
    sql = f"SELECT setval('request_competition_form_form_id_seq', {max_id}, true);"
    print(f"\nSQL to fix sequence: {sql}")
    print("\nPlease run this SQL in your Supabase SQL Editor:")
    print(sql)
else:
    print("No records found in request_competition_form table")
    print("\nSQL to reset sequence:")
    print("SELECT setval('request_competition_form_form_id_seq', 1, false);")
