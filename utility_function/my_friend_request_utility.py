from utility_function.initilize_dbconnection import supabase
from datetime import datetime


def get_received_friend_requests(user_id: int):
    res = supabase.table("friendship_request_form") \
        .select("*") \
        .eq("receiver_id", user_id) \
        .eq("status", "pending") \
        .order("created_at", desc=True) \
        .execute()
    return res.data or []


def accept_friend_request(sender_id: int, receiver_id: int, created_at: str):
    now = datetime.utcnow().isoformat()

    # ✅ Update request status
    supabase.table("friendship_request_form") \
        .update({"status": "accepted", "updated_at": now}) \
        .eq("sender_id", sender_id) \
        .eq("receiver_id", receiver_id) \
        .eq("created_at", created_at) \
        .execute()

    # ✅ Add friendship link
    supabase.table("friendship_link").insert({
        "account_one_id": sender_id,
        "account_two_id": receiver_id,
        "created_at": now
    }).execute()

    return True


def decline_friend_request(sender_id: int, receiver_id: int, created_at: str):
    supabase.table("friendship_request_form") \
        .update({"status": "declined"}) \
        .eq("sender_id", sender_id) \
        .eq("receiver_id", receiver_id) \
        .eq("created_at", created_at) \
        .execute()
    return True
