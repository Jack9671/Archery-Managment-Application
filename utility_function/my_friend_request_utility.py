from utility_function.initilize_dbconnection import supabase
from datetime import datetime


# -----------------------------
# FRIEND REQUEST FUNCTIONS
# -----------------------------
def get_received_friend_requests(user_id: int):
    return (
        supabase.table("friendship_request_form")
        .select("*")
        .eq("receiver_id", user_id)
        .eq("status", "pending")
        .order("created_at", desc=True)
        .execute()
        .data or []
    )


def accept_friend_request(sender_id: int, receiver_id: int, created_at: str):
    now = datetime.utcnow().isoformat()

    check = (
        supabase.table("friendship_request_form")
        .select("*")
        .eq("sender_id", sender_id)
        .eq("receiver_id", receiver_id)
        .eq("created_at", created_at)
        .eq("status", "pending")
        .maybe_single()
        .execute()
    )

    if not check.data:
        return False

    supabase.table("friendship_request_form").update(
        {"status": "accepted", "updated_at": now}
    ).eq("sender_id", sender_id).eq("receiver_id", receiver_id).eq("created_at", created_at).execute()

    supabase.table("friendship_link").insert({
        "account_one_id": sender_id,
        "account_two_id": receiver_id,
        "created_at": now
    }).execute()

    return True


def decline_friend_request(sender_id: int, receiver_id: int, created_at: str):
    return (
        supabase.table("friendship_request_form")
        .update({"status": "rejected"})
        .eq("sender_id", sender_id)
        .eq("receiver_id", receiver_id)
        .eq("created_at", created_at)
        .execute()
    )


# -----------------------------
# FRIEND LIST FUNCTIONS
# -----------------------------
def get_friend_list(user_id: int):
    res = (
        supabase.table("friendship_link")
        .select("*")
        .or_(f"account_one_id.eq.{user_id},account_two_id.eq.{user_id}")
        .execute()
    )

    friends = []
    for row in res.data:
        fid = row["account_one_id"] if row["account_two_id"] == user_id else row["account_two_id"]
        friends.append(fid)

    return friends


def search_friend_in_list(name: str, friend_ids: list):
    """
    Tìm bạn bè trong friend_ids theo fullname.
    """
    if not friend_ids:
        return None

    res = (
        supabase.table("account")
        .select("account_id, fullname, email_address, role, avatar_url")
        .ilike("fullname", f"%{name}%")
        .in_("account_id", friend_ids)
        .execute()
    )

    if res.data:
        return res.data[0]

    return None



# -----------------------------
# BLOCK SYSTEM
# -----------------------------
def block_user(current_user_id: int, target_user_id: int):
    now = datetime.utcnow().isoformat()

    supabase.table("block_link").insert({
        "account_one_id": current_user_id,
        "account_two_id": target_user_id,
        "created_at": now
    }).execute()

    return True


def unblock_user(current_user_id: int, blocked_user_id: int):
    supabase.table("block_link").delete() \
        .eq("account_one_id", current_user_id) \
        .eq("account_two_id", blocked_user_id).execute()

    return True


def get_blocked_users(user_id: int):
    res = (
        supabase.table("block_link")
        .select("*, account_two_id")
        .eq("account_one_id", user_id)
        .execute()
    )

    return res.data or []


def is_blocked(user1: int, user2: int) -> bool:
    """Check if user1 blocked user2 or user2 blocked user1 → Disable chat."""
    res = (
        supabase.table("block_link")
        .select("*")
        .or_(
            f"and(account_one_id.eq.{user1},account_two_id.eq.{user2}),"
            f"and(account_one_id.eq.{user2},account_two_id.eq.{user1})"
        )
        .execute()
    )
    return len(res.data) > 0
