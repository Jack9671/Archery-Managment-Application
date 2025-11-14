import streamlit as st
from datetime import datetime, timezone
from utility_function.initilize_dbconnection import supabase

from utility_function.my_friend_request_utility import (
    get_received_friend_requests,
    accept_friend_request,
    decline_friend_request,
    get_friend_list,
    search_friend_in_list,
    block_user,
    unblock_user,
    get_blocked_users,
)


def main():
    if "user_id" not in st.session_state:
        st.error("Please log in first.")
        return

    user_id = st.session_state["user_id"]

    st.title("Friend Request & Block Management")

    tab1, tab2, tab3 = st.tabs(["Friend Requests", "Block User", "Unblock"])

    # ----------------------------------------------------------------------
    # TAB 1 — FRIEND REQUESTS
    # ----------------------------------------------------------------------
    with tab1:
        requests = get_received_friend_requests(user_id)

        if not requests:
            st.info("No pending friend requests.")
        else:
            for req in requests:
                sender_id = req["sender_id"]
                created_at = req["created_at"]

                sender = (
                    supabase.table("account")
                    .select("*")
                    .eq("account_id", sender_id)
                    .single()
                    .execute()
                    .data
                )

                if not sender:
                    continue

                left, mid, right = st.columns([1, 4, 2])

                with left:
                    avatar = sender.get("avatar_url") or "https://static.vecteezy.com/system/resources/previews/009/292/244/non_2x/default-avatar-profile-icon-of-social-media-user-vector.jpg"
                    st.image(avatar, width=70)

                with mid:
                    st.markdown(f"**{sender['fullname']}**")
                    st.write(f"📧 {sender.get('email_address', '')}")
                    st.caption(f"✉️ {req.get('sender_word', '')}")

                    try:
                        t = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        minutes_ago = int((datetime.now(timezone.utc) - t).total_seconds() // 60)
                        st.caption(f"Sent {minutes_ago} minutes ago")
                    except Exception:
                        pass

                with right:
                    if st.button("Accept", key=f"accept_{sender_id}_{created_at}"):
                        accept_friend_request(sender_id, user_id, created_at)
                        st.success("Friend request accepted.")
                        st.rerun()

                    if st.button("Reject", key=f"reject_{sender_id}_{created_at}"):
                        decline_friend_request(sender_id, user_id, created_at)
                        st.warning("Friend request rejected.")
                        st.rerun()

                st.divider()

    # ----------------------------------------------------------------------
    # TAB 2 — BLOCK USER
    # ----------------------------------------------------------------------
    with tab2:
        st.subheader("Block a Friend")

        friend_ids = get_friend_list(user_id)
        search = st.text_input("Search friend name to block")

        if search:
            result = search_friend_in_list(search, friend_ids)

            if not result:
                st.error("Not found this user in your friend list")
            else:
                st.success(f"Found friend: {result['fullname']}")

                if st.button("Block this user"):
                    block_user(user_id, result["account_id"])
                    st.success(f"You blocked {result['fullname']}")
                    st.rerun()

    # ----------------------------------------------------------------------
    # TAB 3 — UNBLOCK USER
    # ----------------------------------------------------------------------
    with tab3:
        st.subheader("Unblock Users")

        blocked_list = get_blocked_users(user_id)

        if not blocked_list:
            st.info("You have not blocked anyone.")
        else:
            for row in blocked_list:
                blocked_id = row["account_two_id"]

                user = (
                    supabase.table("account")
                    .select("fullname, account_id")
                    .eq("account_id", blocked_id)
                    .single()
                    .execute()
                    .data
                )

                if not user:
                    continue

                left, mid = st.columns([3, 1])

                with left:
                    st.write(f"🚫 {user['fullname']}")

                with mid:
                    if st.button("Unblock", key=f"unblock_{blocked_id}"):
                        unblock_user(user_id, blocked_id)
                        st.success(f"Unblocked {user['fullname']}")
                        st.rerun()


if __name__ == "__main__":
    main()
