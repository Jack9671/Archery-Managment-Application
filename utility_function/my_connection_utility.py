from utility_function.initilize_dbconnection import supabase


# 1. Search Accounts
def search_accounts(keyword="", role_filter=None, limit=50):
    # Cột đúng theo bảng 'account'
    query = supabase.table("account").select(
        "account_id, fullname, email_address, role, avatar_url"
    )

    # Tìm theo fullname hoặc email
    if keyword:
        query = query.or_(f"fullname.ilike.%{keyword}%,email_address.ilike.%{keyword}%")

    # Lọc theo vai trò (nếu có)
    if role_filter and role_filter != "All":
        query = query.eq("role", role_filter)

    response = query.limit(limit).execute()
    return response.data or []

# 2. Send Friend Request
def send_friend_request(sender_id, receiver_id, message):
    response = supabase.table("friend_requests").insert({
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "message": message,
        "status": "pending"
    }).execute()
    return response.data

# 3. Get Received Requests
def get_received_requests(user_id):
    response = supabase.table("friend_requests") \
        .select("id, sender_id, message, created_at, accounts!friend_requests_sender_id_fkey(name)") \
        .eq("receiver_id", user_id).eq("status", "pending") \
        .execute()
    return response.data

# 4. Get Sent Requests
def get_sent_requests(user_id):
    response = supabase.table("friend_requests") \
        .select("id, receiver_id, message, created_at, accounts!friend_requests_receiver_id_fkey(name)") \
        .eq("sender_id", user_id).eq("status", "pending") \
        .execute()
    return response.data

# 5. Accept Request
def accept_request(request_id):
    supabase.table("friend_requests").update({"status": "accepted"}).eq("id", request_id).execute()

# 6. Decline Request
def decline_request(request_id):
    supabase.table("friend_requests").update({"status": "declined"}).eq("id", request_id).execute()

# 7. Get My Friends List
def get_my_connections(user_id):
    response = supabase.rpc("get_user_connections", {"uid": user_id}).execute()
    return response.data

# 8. Remove Friend
def remove_friend(user_id, friend_id):
    supabase.rpc("remove_connection", {"uid": user_id, "fid": friend_id}).execute()