import streamlit as st
from utility_function.initilize_dbconnection import supabase
import json

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please log in to access the chatbot assistant.")
    st.info("Navigate to the 'Sign Up Log In' page to access your account.")
    st.stop()

# Page header
st.title("🤖 Archery Assistant Chatbot")
st.write(f"**Logged in as:** {st.session_state.get('fullname', 'N/A')}")
st.write("Ask questions about competitions, scores, clubs, and more!")
st.divider()

# Determine user roles
user_id = st.session_state.get('user_id')

try:
    admin_check = supabase.table("admin").select("admin_id").eq("admin_id", user_id).execute()
    is_admin = bool(admin_check.data)
except:
    is_admin = False

try:
    recorder_check = supabase.table("recorder").select("recorder_id").eq("recorder_id", user_id).execute()
    is_recorder = bool(recorder_check.data)
except:
    is_recorder = False

try:
    archer_check = supabase.table("archer").select("archer_id").eq("archer_id", user_id).execute()
    is_archer = bool(archer_check.data)
except:
    is_archer = False

# Display user roles
roles = []
if is_admin:
    roles.append("Admin")
if is_recorder:
    roles.append("Recorder")
if is_archer:
    roles.append("Archer")
if not roles:
    roles.append("User")

st.info(f"**Your Roles:** {', '.join(roles)}")
st.caption("The assistant can access data based on your role permissions.")

st.divider()

# Initialize chat history
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
    # Add welcome message
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": f"Hello {st.session_state.get('fullname', 'there')}! 👋 I'm your Archery Assistant. I can help you with:\n\n" +
                   "• Competition information and schedules\n" +
                   "• Your scores and performance statistics\n" +
                   "• Club information and membership\n" +
                   "• Equipment and round compatibility\n" +
                   "• Event registration status\n\n" +
                   "What would you like to know?"
    })

# Display chat messages
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to get data based on query type
def get_database_response(query):
    query_lower = query.lower()
    response_parts = []
    
    try:
        # ==================== COMPETITIONS ====================
        if any(keyword in query_lower for keyword in ['competition', 'event', 'tournament', 'upcoming', 'schedule']):
            competitions = supabase.table("competition").select("*").order("date_start", desc=True).execute()
            if competitions.data:
                response_parts.append("📅 **Competitions:**\n")
                for comp in competitions.data[:5]:
                    response_parts.append(f"• **{comp['name']}** - {comp['date_start']} to {comp['date_end']}\n  📍 {comp['address']}\n")
        
        # ==================== MY SCORES ====================
        if any(keyword in query_lower for keyword in ['my score', 'my performance', 'my stats', 'my results']):
            if is_archer:
                scores = supabase.table("participant_score").select(
                    "sum_score, status, type, event_context:event_context_id(competition:competition_id(name))"
                ).eq("participant_id", user_id).eq("type", "competition").eq("status", "eligible").execute()
                
                if scores.data:
                    total = sum(s['sum_score'] for s in scores.data)
                    avg = total / len(scores.data)
                    response_parts.append(f"📊 **Your Performance:**\n")
                    response_parts.append(f"• Total Ends: {len(scores.data)}\n")
                    response_parts.append(f"• Average Score: {avg:.2f}/60\n")
                    response_parts.append(f"• Best Score: {max(s['sum_score'] for s in scores.data)}/60\n")
                else:
                    response_parts.append("You don't have any eligible competition scores yet.\n")
            else:
                response_parts.append("You need to be an archer to view your scores.\n")
        
        # ==================== CLUBS ====================
        if any(keyword in query_lower for keyword in ['club', 'membership', 'join', 'organization']):
            clubs = supabase.table("club").select("*").execute()
            if clubs.data:
                response_parts.append("🏛️ **Archery Clubs:**\n")
                for club in clubs.data[:5]:
                    # Get member count
                    members = supabase.table("archer").select("archer_id").eq("club_id", club['club_id']).execute()
                    member_count = len(members.data) if members.data else 0
                    response_parts.append(f"• **{club['name']}** ({club['age_group']}) - {member_count} members\n")
        
        # ==================== MY CLUB ====================
        if any(keyword in query_lower for keyword in ['my club', 'my membership']):
            if is_archer:
                archer_data = supabase.table("archer").select("club_id").eq("archer_id", user_id).execute()
                if archer_data.data and archer_data.data[0]['club_id']:
                    club_id = archer_data.data[0]['club_id']
                    club = supabase.table("club").select("*").eq("club_id", club_id).execute()
                    if club.data:
                        club_info = club.data[0]
                        response_parts.append(f"🏛️ **Your Club:**\n")
                        response_parts.append(f"• Name: {club_info['name']}\n")
                        response_parts.append(f"• Age Group: {club_info['age_group']}\n")
                        response_parts.append(f"• Formation Date: {club_info['formation_date']}\n")
                else:
                    response_parts.append("You are not currently a member of any club.\n")
        
        # ==================== EQUIPMENT ====================
        if any(keyword in query_lower for keyword in ['equipment', 'bow', 'gear', 'weapon']):
            equipment = supabase.table("equipment").select("*").execute()
            if equipment.data:
                response_parts.append("🏹 **Available Equipment:**\n")
                for eq in equipment.data[:5]:
                    response_parts.append(f"• **{eq['name']}**")
                    if eq.get('description'):
                        response_parts.append(f": {eq['description'][:100]}...\n")
                    else:
                        response_parts.append("\n")
        
        # ==================== ROUNDS ====================
        if any(keyword in query_lower for keyword in ['round', 'category', 'age group']):
            rounds = supabase.table("round").select("*").execute()
            if rounds.data:
                response_parts.append("🎯 **Available Rounds:**\n")
                for rnd in rounds.data[:5]:
                    response_parts.append(f"• **{rnd['name']}** - Age Group: {rnd['age_group']}\n")
        
        # ==================== RANKINGS ====================
        if any(keyword in query_lower for keyword in ['ranking', 'leaderboard', 'top', 'best']):
            scores = supabase.table("participant_score").select(
                "participant_id, sum_score, account:participant_id(fullname)"
            ).eq("type", "competition").eq("status", "eligible").execute()
            
            if scores.data:
                # Aggregate by participant
                participant_totals = {}
                for score in scores.data:
                    pid = score['participant_id']
                    if pid not in participant_totals:
                        participant_totals[pid] = {
                            'name': score['account']['fullname'] if score.get('account') else 'Unknown',
                            'total': 0
                        }
                    participant_totals[pid]['total'] += score['sum_score']
                
                # Sort by total
                sorted_participants = sorted(participant_totals.items(), key=lambda x: x[1]['total'], reverse=True)
                
                response_parts.append("🏆 **Top Archers:**\n")
                for i, (pid, data) in enumerate(sorted_participants[:5]):
                    medal = ["🥇", "🥈", "🥉"][i] if i < 3 else "•"
                    response_parts.append(f"{medal} **{data['name']}** - Total Score: {data['total']}\n")
        
        # ==================== REGISTRATION STATUS ====================
        if any(keyword in query_lower for keyword in ['registration', 'register', 'enroll', 'sign up', 'my request']):
            forms = supabase.table("request_form").select(
                "form_id, status, role, type, competition:competition_id(name), round:round_id(name)"
            ).eq("account_id", user_id).execute()
            
            if forms.data:
                response_parts.append("📋 **Your Registration Requests:**\n")
                for form in forms.data:
                    comp_name = form['competition']['name'] if form.get('competition') else 'Unknown'
                    round_name = form['round']['name'] if form.get('round') else 'Unknown'
                    status_emoji = {"pending": "⏳", "in progress": "🔄", "eligible": "✅", "ineligible": "❌"}.get(form['status'], "❓")
                    response_parts.append(f"{status_emoji} Form #{form['form_id']}: {form['type']} as {form['role']}\n")
                    response_parts.append(f"   Competition: {comp_name}, Round: {round_name}\n")
                    response_parts.append(f"   Status: {form['status']}\n")
            else:
                response_parts.append("You don't have any registration requests yet.\n")
        
        # ==================== ADMIN STATS ====================
        if is_admin and any(keyword in query_lower for keyword in ['admin', 'stats', 'statistics', 'total', 'count']):
            accounts = supabase.table("account").select("account_id").execute()
            admins = supabase.table("admin").select("admin_id").execute()
            recorders = supabase.table("recorder").select("recorder_id").execute()
            archers = supabase.table("archer").select("archer_id").execute()
            competitions = supabase.table("competition").select("competition_id").execute()
            
            response_parts.append("📊 **System Statistics (Admin View):**\n")
            response_parts.append(f"• Total Accounts: {len(accounts.data) if accounts.data else 0}\n")
            response_parts.append(f"• Admins: {len(admins.data) if admins.data else 0}\n")
            response_parts.append(f"• Recorders: {len(set([r['recorder_id'] for r in (recorders.data or [])])) if recorders.data else 0}\n")
            response_parts.append(f"• Archers: {len(archers.data) if archers.data else 0}\n")
            response_parts.append(f"• Competitions: {len(competitions.data) if competitions.data else 0}\n")
        
        # ==================== HELP ====================
        if any(keyword in query_lower for keyword in ['help', 'what can you do', 'how to', 'guide']):
            response_parts.append("ℹ️ **I can help you with:**\n\n")
            response_parts.append("**For Everyone:**\n")
            response_parts.append("• View competitions and events\n")
            response_parts.append("• Browse clubs and membership info\n")
            response_parts.append("• Check equipment and rounds\n\n")
            
            if is_archer:
                response_parts.append("**As an Archer:**\n")
                response_parts.append("• View your scores and performance\n")
                response_parts.append("• Check your registration status\n")
                response_parts.append("• See rankings and leaderboards\n\n")
            
            if is_recorder:
                response_parts.append("**As a Recorder:**\n")
                response_parts.append("• Manage event structures\n")
                response_parts.append("• Verify participant scores\n\n")
            
            if is_admin:
                response_parts.append("**As an Admin:**\n")
                response_parts.append("• View system statistics\n")
                response_parts.append("• Manage user accounts\n")
        
        # If no specific query matched, provide general help
        if not response_parts:
            response_parts.append("I'm not sure how to answer that specific question. Here are some things you can ask me:\n\n")
            response_parts.append("• 'Show me upcoming competitions'\n")
            response_parts.append("• 'What are my scores?'\n")
            response_parts.append("• 'Tell me about clubs'\n")
            response_parts.append("• 'What equipment is available?'\n")
            response_parts.append("• 'Show rankings'\n")
            response_parts.append("• 'What's my registration status?'\n")
        
        return "".join(response_parts)
    
    except Exception as e:
        return f"❌ I encountered an error while fetching data: {str(e)}\n\nPlease try rephrasing your question or contact support if the issue persists."

# Chat input
if prompt := st.chat_input("Ask me anything about archery events, scores, clubs..."):
    # Add user message to chat history
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_database_response(prompt)
        
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.chat_messages.append({"role": "assistant", "content": response})

# Sidebar with suggested questions
with st.sidebar:
    st.subheader("💡 Suggested Questions")
    
    st.write("**General:**")
    if st.button("Show upcoming competitions", key="q1"):
        st.session_state.chat_messages.append({"role": "user", "content": "Show me upcoming competitions"})
        st.rerun()
    
    if st.button("What clubs are available?", key="q2"):
        st.session_state.chat_messages.append({"role": "user", "content": "What clubs are available?"})
        st.rerun()
    
    if st.button("Show all equipment", key="q3"):
        st.session_state.chat_messages.append({"role": "user", "content": "Show me all equipment"})
        st.rerun()
    
    if is_archer:
        st.divider()
        st.write("**For Archers:**")
        
        if st.button("What are my scores?", key="q4"):
            st.session_state.chat_messages.append({"role": "user", "content": "What are my scores?"})
            st.rerun()
        
        if st.button("Show rankings", key="q5"):
            st.session_state.chat_messages.append({"role": "user", "content": "Show me the rankings"})
            st.rerun()
        
        if st.button("My registration status", key="q6"):
            st.session_state.chat_messages.append({"role": "user", "content": "What's my registration status?"})
            st.rerun()
        
        if st.button("What's my club?", key="q7"):
            st.session_state.chat_messages.append({"role": "user", "content": "Tell me about my club"})
            st.rerun()
    
    if is_admin:
        st.divider()
        st.write("**For Admins:**")
        
        if st.button("Show system statistics", key="q8"):
            st.session_state.chat_messages.append({"role": "user", "content": "Show me system statistics"})
            st.rerun()
    
    st.divider()
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_messages = []
        st.rerun()
    
    st.divider()
    
    st.caption("**Note:** This is a simple rule-based assistant. It retrieves data from the database based on keywords in your questions.")
    st.caption("For best results, use clear and specific questions.")

# Footer
st.divider()
st.caption("💬 Chatbot Assistant v1.0 | Powered by your archery database")
