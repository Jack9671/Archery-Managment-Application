import streamlit as st
import time
from utility_function.initilize_dbconnection import supabase
from typing import List, Dict
from datetime import datetime
from utility_function.my_connection_utility import search_accounts

st.set_page_config(layout="wide", page_title="My Connections")

# =========================================================
# 🔹 Helper functions (DB)
# =========================================================

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


# =========================================================
# 🔹 CHAT FUNCTIONS — dùng bảng person_to_person_chat_history
# =========================================================

def get_private_chat(user1: int, user2: int):
    """Lấy toàn bộ tin nhắn giữa 2 user"""
    try:
        account_one_id = min(user1, user2)
        account_two_id = max(user1, user2)
        res = supabase.table("person_to_person_chat_history") \
            .select("*") \
            .eq("account_one_id", account_one_id) \
            .eq("account_two_id", account_two_id) \
            .order("message_order", desc=False) \
            .execute()
        return res.data or []
    except Exception as e:
        st.error(f"❌ Error loading chat: {e}")
        return []


def append_private_message(sender_id: int, receiver_id: int, message: str):
    """Thêm tin nhắn mới"""
    try:
        account_one_id = min(sender_id, receiver_id)
        account_two_id = max(sender_id, receiver_id)

        existing = supabase.table("person_to_person_chat_history") \
            .select("message_order") \
            .eq("account_one_id", account_one_id) \
            .eq("account_two_id", account_two_id) \
            .execute()

        next_order = (max([m["message_order"] for m in existing.data], default=0) + 1)

        payload = {
            "account_one_id": account_one_id,
            "account_two_id": account_two_id,
            "message_order": next_order,
            "message": message,
            "sender_id": sender_id,
            "created_at": datetime.utcnow().isoformat()
        }

        supabase.table("person_to_person_chat_history").insert(payload).execute()
        return True
    except Exception as e:
        st.error(f"❌ Error sending message: {e}")
        return False


# =========================================================
# 🔹 UI MAIN
# =========================================================
def main():
    if "user_id" not in st.session_state:
        st.warning("⚠️ Please log in first.")
        return

    user_id = st.session_state["user_id"]
    st.title("🤝 My Connections")

    tab1, tab2 = st.tabs(["👥 Connections & Requests", "💬 Chat Messages"])

    # ------------------------------------------------------------------
    # TAB 1: Connections
    # ------------------------------------------------------------------
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

        st.markdown("### Friends and Connections")
        if not accounts:
            st.info("No matching users found.")
        else:
            for i, acc in enumerate(accounts):
                uid = acc["account_id"]

                left, mid, right = st.columns([1, 4, 2])

                with left:
                    avatar = acc.get("avatar_url") or "https://static.vecteezy.com/system/resources/previews/009/292/244/non_2x/default-avatar-profile-icon-of-social-media-user-vector.jpg"
                    st.image(avatar, width=70)

                with mid:
                    st.markdown(f"**{acc['fullname']}**")
                    st.write(f"📧 {acc.get('email_address', 'No email')}")
                    st.write(f"🎯 Role: *{acc.get('role', 'N/A')}*")

                with right:
                    if are_friends(user_id, uid):
                        if st.button("Message", key=f"msg_{uid}_{i}"):
                            st.session_state["chat_with"] = uid
                    else:
                        intro = st.text_input("Message", value="Hi, let's connect!", key=f"intro_{uid}_{i}")
                        if st.button("Send Request", key=f"req_{uid}_{i}"):
                            send_friend_request(user_id, uid, intro)
                            st.success("Request sent ✔️")

                

        # Friend List
        st.markdown("---")
        st.markdown("### Your Friends")
        friends = get_friends_of(user_id)

        if not friends:
            st.caption("No friends yet.")
        else:
            seen = set()
            unique_friends = []
            for fr in friends:
                fid = fr["account_one_id"] if fr["account_one_id"] != user_id else fr["account_two_id"]
                if fid not in seen:
                    seen.add(fid)
                    unique_friends.append(fr)

            for i, fr in enumerate(unique_friends):
                fid = fr["account_one_id"] if fr["account_one_id"] != user_id else fr["account_two_id"]
                fdata = supabase.table("account").select("*").eq("account_id", fid).single().execute().data
                row = st.columns([1, 4, 1])

                with row[0]:
                    avatar = fdata.get("avatar_url") or "https://static.vecteezy.com/system/resources/previews/009/292/244/non_2x/default-avatar-profile-icon-of-social-media-user-vector.jpg"
                    st.image(avatar, width=70)

                with row[1]:
                    st.markdown(f"**{fdata['fullname']}**")

                with row[2]:
                    if st.button("Chat", key=f"chat_{fid}_{i}"):
                        st.session_state["chat_with"] = fid
                        st.session_state["active_tab"] = "chat"


    # ------------------------------------------------------------------
    # TAB 2: Chat
    # ------------------------------------------------------------------
    with tab2:
    
        # Tạo placeholder để chứa chat và dễ rerun
        placeholder = st.empty()

        while True:
            with placeholder.container():
                chat_partner = st.session_state.get("chat_with")

                if not chat_partner:
                    st.info("Select a friend in Tab 1 to start chatting.")
                    st.stop()

                # Lấy thông tin bạn chat
                partner = supabase.table("account").select("*").eq("account_id", chat_partner).single().execute().data
                st.subheader(f"💬 Chat with {partner['fullname']}")

                # Lấy tất cả tin nhắn giữa 2 người
                messages = get_private_chat(user_id, chat_partner)

                if not messages:
                    st.caption("No messages yet.")
                else:
                    for m in messages:
                        align = "right" if m["sender_id"] == user_id else "left"
                        bg = "#dcf8c6" if m["sender_id"] == user_id else "#f1f0f0"
                        st.markdown(
                            f"<div style='text-align:{align}; background:{bg}; padding:8px; border-radius:10px; margin:4px;'>{m['message']}</div>",
                            unsafe_allow_html=True
                        )

                # Input gửi tin nhắn
                msg = st.chat_input("Type a message...")
                if msg:
                    append_private_message(user_id, chat_partner, msg)
                    st.rerun()

            
            time.sleep(20) #auto refresh after 20 seconds for update messages
            st.rerun()


if __name__ == "__main__":
    main()
