import streamlit as st
from datetime import datetime, timezone
from utility_function.initilize_dbconnection import supabase
from utility_function.my_friend_request_utility import (
    get_received_friend_requests,
    accept_friend_request,
    decline_friend_request
)

def main():
    if "user_id" not in st.session_state:
        st.error("Please log in first.")
        return

    user_id = st.session_state["user_id"]
    st.title("Friend Requests")

    # Lấy danh sách yêu cầu kết bạn đến người dùng hiện tại
    requests = get_received_friend_requests(user_id)

    if not requests:
        st.info("No pending friend requests.")
        return

    for req in requests:
        sender_id = req["sender_id"]
        created_at = req["created_at"]

        # Lấy thông tin người gửi
        sender = supabase.table("account").select("*") \
            .eq("account_id", sender_id).single().execute().data

        if not sender:
            continue

        # Chia layout thành 3 cột: Avatar - Thông tin - Hành động
        left, mid, right = st.columns([1, 4, 2])

        with left:
            avatar = sender.get("avatar_url") or "https://static.vecteezy.com/system/resources/previews/009/292/244/non_2x/default-avatar-profile-icon-of-social-media-user-vector.jpg"
            st.image(avatar, width=70)

        with mid:
            st.markdown(f"**{sender['fullname']}**")
            st.write(f"📧 {sender.get('email_address', 'No email')}")
            st.write(f"🎯 Role: *{sender.get('role', 'N/A')}*")
            st.caption(f"✉️ {req.get('sender_word', '')}")

            # Hiển thị thời gian gửi yêu cầu (tuỳ chọn)
            try:
                t = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                minutes_ago = int((datetime.now(timezone.utc) - t).total_seconds() // 60)
                st.caption(f"Sent {minutes_ago} minutes ago")
            except Exception:
                pass

        with right:
            accept_key = f"accept_{sender_id}_{created_at}"
            decline_key = f"decline_{sender_id}_{created_at}"

            if st.button("Accept", key=accept_key):
                accept_friend_request(sender_id, user_id, created_at)
                st.success(f"Accepted friend request from {sender['fullname']}")
                st.rerun()

            if st.button("Decline", key=decline_key):
                decline_friend_request(sender_id, user_id, created_at)
                st.warning(f"Declined friend request from {sender['fullname']}")
                st.rerun()

        st.divider()


if __name__ == "__main__":
    main()
