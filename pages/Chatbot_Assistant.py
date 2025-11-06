import os
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)
model = genai.GenerativeModel(
    "gemini-2.0-flash-lite",
    system_instruction="""You are a chatbot assistant for an archery management system.

Your goals:
1. Automatically detect the user's language (English or Vietnamese).
2. Respond in the same language as the user.
3. Restrict your knowledge and conversation scope strictly to topics related to archery — 
   including techniques, equipment, rules, training, event organization, and system management.
4. If the user asks a question unrelated to archery, respond:
   - English: "Sorry, I only assist with archery-related topics."
   - Vietnamese: "Xin lỗi, tôi chỉ hỗ trợ các vấn đề liên quan đến bắn cung."""
)
# --- Cấu hình giao diện ---
st.set_page_config(page_title="Archery Chatbot", page_icon="🏹")
st.title("🏹 Archery Management Chatbot")

# --- Khởi tạo danh sách hội thoại ---
if "conversations" not in st.session_state:
    st.session_state.conversations = []  # danh sách các hội thoại
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None  # hội thoại hiện tại

# ---  Quản lý hội thoại ---
with st.expander("💬 Chat Sessions", expanded=True):
    # Nút tạo hội thoại mới
    if st.button("➕ New Chat", use_container_width=True):
        new_chat = {
            "id": len(st.session_state.conversations) + 1,
            "messages": []
        }
        st.session_state.conversations.append(new_chat)
        st.session_state.current_chat = new_chat["id"]
        st.rerun()

    # Hiển thị danh sách hội thoại
    for chat in st.session_state.conversations:
        col1, col2 = st.columns([4, 1])
        if col1.button(f"Chat {chat['id']}", key=f"select_{chat['id']}", use_container_width=True):
            st.session_state.current_chat = chat["id"]
            st.rerun()
        if col2.button("🗑", key=f"delete_{chat['id']}"):
            st.session_state.conversations = [
                c for c in st.session_state.conversations if c["id"] != chat["id"]
            ]
            if st.session_state.current_chat == chat["id"]:
                st.session_state.current_chat = None
            st.rerun()

# --- HIỂN THỊ NỘI DUNG CHAT ĐANG CHỌN ---
if st.session_state.current_chat:
    chat = next(
        (c for c in st.session_state.conversations if c["id"] == st.session_state.current_chat),
        None
    )

    if chat:
        st.subheader(f"💭 Chat {chat['id']}")

        # Hiển thị tin nhắn cũ
        for msg in chat["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Nhập câu hỏi mới
        user_input = st.chat_input("Ask a question about Archery...")
        if user_input:
            # Hiển thị tin nhắn người dùng
            st.chat_message("user").markdown(user_input)
            chat["messages"].append({"role": "user", "content": user_input})

            # Gọi API Gemini
            response = model.generate_content(user_input)
            bot_reply = response.text

            # Hiển thị phản hồi chatbot
            with st.chat_message("assistant"):
                st.markdown(bot_reply)

            # Lưu tin nhắn bot
            chat["messages"].append({"role": "assistant", "content": bot_reply})
            st.rerun()

else:
    st.write("👉 Tạo hoặc chọn một đoạn hội thoại ở bên trái để bắt đầu.")