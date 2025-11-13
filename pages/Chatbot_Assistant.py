import os
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from utility_function.initilize_dbconnection import supabase

# --- Load API key ---
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)

# --- Khởi tạo model Gemini ---
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

# --- Lấy thông tin người dùng hiện tại ---
if "user_id" not in st.session_state:
    st.error("⚠️ Please log in first.")
    st.stop()

user_id = st.session_state["user_id"]

# --- Sidebar: Chat sessions ---
st.sidebar.header("💬 Chat Sessions")

# Lấy danh sách hội thoại từ DB
conversations = supabase.table("ai_conversation_history") \
    .select("conversation_order") \
    .eq("account_id", user_id) \
    .execute()

# Trích xuất danh sách chat unique
chat_ids = sorted(list({c["conversation_order"] for c in conversations.data})) if conversations.data else []

# Session state giữ chat hiện tại
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

# --- Tạo chat mới ---
if st.sidebar.button("➕ New Chat"):
    new_order = (max(chat_ids) + 1) if chat_ids else 1
    st.session_state.current_chat = new_order
    st.success(f"🆕 New chat #{new_order} created!")
    st.rerun()

# --- Danh sách chat trong sidebar ---
for cid in chat_ids:
    col1, col2 = st.sidebar.columns([4, 1])
    if col1.button(f"Chat {cid}", key=f"select_{cid}"):
        st.session_state.current_chat = cid
        st.rerun()

    if col2.button("🗑", key=f"delete_{cid}"):
        # Xóa toàn bộ conversation khỏi DB
        supabase.table("ai_conversation_history") \
            .delete() \
            .eq("account_id", user_id) \
            .eq("conversation_order", cid) \
            .execute()

        # Xóa khỏi session state
        st.session_state.conversations = [
            c for c in st.session_state.get("conversations", []) if c.get("id") != cid
        ]
        if st.session_state.current_chat == cid:
            st.session_state.current_chat = None

        st.warning(f"Chat {cid} deleted permanently.")
        st.rerun()

# --- Hiển thị khung chat ---
if st.session_state.current_chat:
    chat_id = st.session_state.current_chat
    st.subheader(f"💭 Chat {chat_id}")

    # Lấy lịch sử hội thoại trong DB
    messages = supabase.table("ai_conversation_history") \
        .select("*") \
        .eq("account_id", user_id) \
        .eq("conversation_order", chat_id) \
        .order("prompt_response_order", desc=False) \
        .execute().data or []

    # Hiển thị tin nhắn cũ
    for msg in messages:
        with st.chat_message("user"):
            st.markdown(msg["prompt"])
        with st.chat_message("assistant"):
            st.markdown(msg["response"])

    # Nhập câu hỏi mới
    user_input = st.chat_input("Nhập câu hỏi của bạn về bắn cung...")
    if user_input:
        st.chat_message("user").markdown(user_input)

        # Gọi model Gemini
        response = model.generate_content(user_input)
        bot_reply = response.text.strip()

        # Hiển thị phản hồi chatbot
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

        # Xác định thứ tự tin nhắn tiếp theo
        next_order = (max([m["prompt_response_order"] for m in messages], default=0)) + 1
        now = datetime.utcnow().isoformat()

        # Ghi vào DB
        supabase.table("ai_conversation_history").insert({
            "account_id": user_id,
            "conversation_order": chat_id,
            "prompt_response_order": next_order,
            "prompt": user_input,
            "response": bot_reply,
            "created_at": now
        }).execute()

        st.rerun()

else:
    st.write("👉 Tạo hoặc chọn một đoạn hội thoại ở bên trái để bắt đầu.")
