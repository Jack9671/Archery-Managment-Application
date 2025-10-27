import streamlit as st
from utility_function.initilize_dbconnection import supabase
from typing import List, Dict
from datetime import datetime

st.set_page_config(layout="wide", page_title="My Connections")

# ---------- Helper functions (DB) ----------
from utility_function.my_connection_utility import search_accounts


def get_accounts_by_role(role: str, limit: int = 100) -> List[Dict]:
    try:
        q = supabase.table("account").select("account_id, fullname, email_address, avatar_url, role")
        if role and role.lower() != "all":
            q = q.eq("role", role)
        res = q.limit(limit).execute()
        return res.data or []
    except Exception as e:
        st.error(f"DB error: {e}")
        return []


def get_friends_of(user_id: int):
    try:
        res = supabase.table("friendship_link").select("*")\
            .or_(f"account_one_id.eq.{user_id},account_two_id.eq.{user_id}")\
            .execute()
        return res.data or []
    except Exception:
        return []


def are_friends(user1: int, user2: int) -> bool:
    res = get_friends_of(user1)
    for r in res:
        a = r["account_one_id"]
        b = r["account_two_id"]
        if (a == user1 and b == user2) or (a == user2 and b == user1):
            return True
    return False


def send_friend_request(sender_id: int, receiver_id: int, message: str):
    try:
        now = datetime.utcnow().isoformat()
        payload = {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "sender_word": message,
            "status": "pending",
            "created_at": now,
            "updated_at": now
        }
        supabase.table("friendship_request_form").insert(payload).execute()
        return True
    except Exception as e:
        st.error(f"Failed to send friend request: {e}")
        return False


def get_private_chat(user1: int, user2: int):
    try:
        res = supabase.table("person_to_person_old_message")\
            .select("*")\
            .order("message_order", desc=False).execute()
        messages = [m for m in res.data if m["writer_id"] in (user1, user2)]
        return messages
    except:
        return []


def append_private_message(sender_id: int, receiver_id: int, message: str):
    try:
        payload = {
            "message": message,
            "writer_id": sender_id,
            "created_at": datetime.utcnow().isoformat()
        }
        supabase.table("person_to_person_old_message").insert(payload).execute()
        return True
    except:
        return False


# ---------- UI ----------
def main():
    if "user_id" not in st.session_state:
        return

    user_id = st.session_state["user_id"]
    st.title("🤝 My Connections")

    tab1, tab2 = st.tabs(["👥 Connections & Requests", "💬 Chat Messages"])

    # TAB 1 -----------------------------------------------------------------
    with tab1:
        col_search, col_filter = st.columns([3, 1])
        with col_search:
            keyword = st.text_input("Search by name or email", key="search_main", placeholder="Enter keyword...")
        with col_filter:
            role = st.selectbox("Filter by role", ["All", "archer", "recorder", "australia_archery_federation", "admin"])

        if keyword:
            accounts = search_accounts(keyword, limit=100)
        else:
            accounts = get_accounts_by_role(role, limit=100)

        accounts = [a for a in accounts if a["account_id"] != user_id]

        st.markdown("### Results")
        if not accounts:
            st.info("No matching users found.")
        else:
            for acc in accounts:
                uid = acc["account_id"]
                left, mid, right = st.columns([1, 4, 2])
                left.write("🧑")
                mid.markdown(f"**{acc['fullname']}**\n\n*{acc['role']}*")

                if are_friends(user_id, uid):
                    if right.button("Message", key=f"msg_{uid}"):
                        st.session_state["chat_with"] = uid
                else:
                    intro = right.text_input("Message", value="Hi, let's connect!", key=f"intro_{uid}")
                    if right.button("Send Request", key=f"req_{uid}"):
                        send_friend_request(user_id, uid, intro)
                        st.success("Request sent ✔️")

        # Friend List
        st.markdown("---")
        st.markdown("### Your Friends")
        friends = get_friends_of(user_id)

        if not friends:
            st.caption("No friends yet.")
        else:
            for fr in friends:
                fid = fr["account_one_id"] if fr["account_one_id"] != user_id else fr["account_two_id"]
                fdata = supabase.table("account").select("*").eq("account_id", fid).single().execute().data
                row = st.columns([1, 4, 1])
                row[0].write("🧑")
                row[1].markdown(f"**{fdata['fullname']}**")
                if row[2].button("Chat", key=f"chat_{fid}"):
                    st.session_state["chat_with"] = fid

    # TAB 2 -----------------------------------------------------------------
    with tab2:
        st.markdown("### 💬 Chat")
        chat_partner = st.session_state.get("chat_with")

        if not chat_partner:
            st.info("Select a friend in Tab 1 to start chatting.")
            return

        partner = supabase.table("account").select("*").eq("account_id", chat_partner).single().execute().data
        st.markdown(f"**Chat with {partner['fullname']}**")

        messages = get_private_chat(user_id, chat_partner)
        for m in messages:
            align = "right" if m["writer_id"] == user_id else "left"
            bg = "#e1ffe7" if m["writer_id"] == user_id else "#f1f1f1"
            st.markdown(f"<div style='text-align:{align}; background:{bg}; padding:6px; border-radius:8px; margin:3px'>{m['message']}</div>", unsafe_allow_html=True)

        msg = st.text_input("Write a message...", key="msg_send_box")
        if st.button("Send", key="send_btn"):
            append_private_message(user_id, chat_partner, msg)
            st.experimental_rerun()


if __name__ == "__main__":
    main()
