import streamlit as st
from datetime import datetime
from utility_function.initilize_dbconnection import supabase
import pandas as pd

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please log in to view performance statistics.")
    st.info("Navigate to the 'Sign Up Log In' page to access your account.")
    st.stop()

# Page header
st.title("📈 Performance Analytics")
st.write(f"**Logged in as:** {st.session_state.get('fullname', 'N/A')}")
st.divider()

# Check if user is an archer
user_id = st.session_state.get('user_id')
try:
    archer_check = supabase.table("archer").select("archer_id").eq("archer_id", user_id).execute()
    is_archer = bool(archer_check.data)
except:
    is_archer = False

if not is_archer:
    st.error("🚫 Access Denied")
    st.warning("You must be an Archer to view performance statistics.")
    st.info("Please submit a form to become an archer.")
    st.stop()

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["📊 My Performance", "👥 Other Participants", "🌍 Community Rankings"])

# ==================== MY PERFORMANCE TAB ====================
with tab1:
    st.subheader("📊 My Personal Performance")
    
    # Type filter
    score_type_filter = st.radio(
        "Score Type",
        ["competition", "practice", "both"],
        horizontal=True,
        help="Filter by competition or practice scores"
    )
    
    try:
        # Get user's scores
        if score_type_filter == "both":
            my_scores = supabase.table("participant_score").select(
                "*, event_context:event_context_id(competition:competition_id(name), round:round_id(name, age_group))"
            ).eq("participant_id", user_id).execute()
        else:
            my_scores = supabase.table("participant_score").select(
                "*, event_context:event_context_id(competition:competition_id(name), round:round_id(name, age_group))"
            ).eq("participant_id", user_id).eq("type", score_type_filter).execute()
        
        scores_list = my_scores.data if my_scores.data else []
        
        if not scores_list:
            st.info(f"No {score_type_filter} scores found.")
        else:
            # Calculate statistics
            total_scores = len(scores_list)
            eligible_scores = len([s for s in scores_list if s['status'] == 'eligible'])
            
            # Only calculate from eligible scores for competition
            if score_type_filter == "competition":
                calc_scores = [s for s in scores_list if s['status'] == 'eligible']
            else:
                calc_scores = scores_list
            
            if calc_scores:
                sum_scores = [s['sum_score'] for s in calc_scores]
                avg_score = sum(sum_scores) / len(sum_scores)
                max_score = max(sum_scores)
                min_score = min(sum_scores)
                
                # Calculate accuracy (assuming 60 is perfect)
                accuracy_rate = (avg_score / 60) * 100
                
                # Count perfect arrows (score of 10)
                perfect_arrows = 0
                total_arrows = 0
                for s in calc_scores:
                    arrows = [s['score_1st_arrow'], s['score_2nd_arrow'], s['score_3rd_arrow'],
                             s['score_4th_arrow'], s['score_5st_arrow'], s['score_6st_arrow']]
                    perfect_arrows += arrows.count(10)
                    total_arrows += 6
                
                perfect_arrow_rate = (perfect_arrows / total_arrows * 100) if total_arrows > 0 else 0
                
                # Display statistics
                st.write("### 📈 Overall Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Ends", total_scores)
                col2.metric("Average Score", f"{avg_score:.2f}/60")
                col3.metric("Best Score", f"{max_score}/60")
                col4.metric("Accuracy Rate", f"{accuracy_rate:.1f}%")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Eligible Scores", eligible_scores)
                col2.metric("Lowest Score", f"{min_score}/60")
                col3.metric("Perfect Arrows", perfect_arrows)
                col4.metric("Perfect Arrow Rate", f"{perfect_arrow_rate:.1f}%")
                
                st.divider()
                
                # Score distribution
                st.write("### 📊 Score Distribution")
                
                # Create DataFrame for visualization
                df = pd.DataFrame(calc_scores)
                df['sum_score'] = df['sum_score'].astype(float)
                
                # Simple bar chart using Streamlit
                st.bar_chart(df['sum_score'])
                
                st.divider()
                
                # Performance by competition
                st.write("### 🏆 Performance by Competition")
                
                comp_stats = {}
                for score in calc_scores:
                    event_ctx = score.get('event_context', {})
                    comp_name = event_ctx.get('competition', {}).get('name', 'Unknown') if event_ctx else 'Unknown'
                    
                    if comp_name not in comp_stats:
                        comp_stats[comp_name] = {
                            'scores': [],
                            'count': 0
                        }
                    
                    comp_stats[comp_name]['scores'].append(score['sum_score'])
                    comp_stats[comp_name]['count'] += 1
                
                for comp_name, stats in comp_stats.items():
                    avg = sum(stats['scores']) / len(stats['scores'])
                    max_s = max(stats['scores'])
                    
                    with st.container(border=True):
                        st.write(f"**🏆 {comp_name}**")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Ends", stats['count'])
                        col2.metric("Average", f"{avg:.2f}/60")
                        col3.metric("Best", f"{max_s}/60")
                
                st.divider()
                
                # Performance by round
                st.write("### 🎯 Performance by Round")
                
                round_stats = {}
                for score in calc_scores:
                    event_ctx = score.get('event_context', {})
                    round_name = event_ctx.get('round', {}).get('name', 'Unknown') if event_ctx else 'Unknown'
                    
                    if round_name not in round_stats:
                        round_stats[round_name] = {
                            'scores': [],
                            'count': 0
                        }
                    
                    round_stats[round_name]['scores'].append(score['sum_score'])
                    round_stats[round_name]['count'] += 1
                
                for round_name, stats in round_stats.items():
                    avg = sum(stats['scores']) / len(stats['scores'])
                    max_s = max(stats['scores'])
                    
                    with st.container(border=True):
                        st.write(f"**🎯 {round_name}**")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Ends", stats['count'])
                        col2.metric("Average", f"{avg:.2f}/60")
                        col3.metric("Best", f"{max_s}/60")
                
                st.divider()
                
                # Recent scores
                st.write("### 📅 Recent Scores")
                
                # Sort by datetime
                recent_scores = sorted(calc_scores, key=lambda x: x['datetime'], reverse=True)[:10]
                
                for score in recent_scores:
                    event_ctx = score.get('event_context', {})
                    comp_name = event_ctx.get('competition', {}).get('name', 'Unknown') if event_ctx else 'Unknown'
                    round_name = event_ctx.get('round', {}).get('name', 'Unknown') if event_ctx else 'Unknown'
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    col1.write(f"{comp_name} - {round_name}")
                    col2.write(f"Score: {score['sum_score']}/60")
                    col3.write(f"{score['datetime'][:10]}")
            else:
                st.info("No eligible scores to calculate statistics.")
    
    except Exception as e:
        st.error(f"Error loading performance data: {str(e)}")

# ==================== OTHER PARTICIPANTS TAB ====================
with tab2:
    st.subheader("👥 Other Participants' Performance")
    st.info("View performance of other participants in competitions you're registered in.")
    
    try:
        # Get competitions where user is registered
        my_registrations = supabase.table("participant_score").select(
            "event_context_id, event_context:event_context_id(competition_id, round_id, competition:competition_id(name), round:round_id(name))"
        ).eq("participant_id", user_id).eq("type", "competition").execute()
        
        if not my_registrations.data:
            st.warning("You are not registered in any competitions yet.")
        else:
            # Get unique competition-round pairs
            comp_round_pairs = {}
            for reg in my_registrations.data:
                event_ctx = reg.get('event_context', {})
                comp_id = event_ctx.get('competition_id')
                round_id = event_ctx.get('round_id')
                comp_name = event_ctx.get('competition', {}).get('name', 'Unknown') if event_ctx.get('competition') else 'Unknown'
                round_name = event_ctx.get('round', {}).get('name', 'Unknown') if event_ctx.get('round') else 'Unknown'
                
                key = (comp_id, round_id)
                if key not in comp_round_pairs:
                    comp_round_pairs[key] = {
                        'comp_name': comp_name,
                        'round_name': round_name
                    }
            
            # Select competition and round
            options = [f"{v['comp_name']} - {v['round_name']}" for k, v in comp_round_pairs.items()]
            selected_option = st.selectbox("Select Competition & Round", options)
            
            # Find the selected competition and round IDs
            selected_index = options.index(selected_option)
            selected_key = list(comp_round_pairs.keys())[selected_index]
            selected_comp_id, selected_round_id = selected_key
            
            # Get all event contexts for this competition and round
            contexts = supabase.table("event_context").select("event_context_id").eq(
                "competition_id", selected_comp_id
            ).eq("round_id", selected_round_id).execute()
            
            context_ids = [ctx['event_context_id'] for ctx in (contexts.data or [])]
            
            if context_ids:
                # Get all participants' scores for these contexts
                all_scores = []
                for ctx_id in context_ids:
                    scores = supabase.table("participant_score").select(
                        "participant_id, sum_score, status, account:participant_id(fullname, country)"
                    ).eq("event_context_id", ctx_id).eq("type", "competition").eq("status", "eligible").execute()
                    
                    if scores.data:
                        all_scores.extend(scores.data)
                
                if all_scores:
                    # Aggregate scores by participant
                    participant_stats = {}
                    for score in all_scores:
                        pid = score['participant_id']
                        
                        # Skip current user
                        if pid == user_id:
                            continue
                        
                        if pid not in participant_stats:
                            participant_stats[pid] = {
                                'name': score['account']['fullname'] if score.get('account') else 'Unknown',
                                'country': score['account']['country'] if score.get('account') else 'Unknown',
                                'scores': [],
                                'total': 0
                            }
                        
                        participant_stats[pid]['scores'].append(score['sum_score'])
                        participant_stats[pid]['total'] += score['sum_score']
                    
                    if not participant_stats:
                        st.info("No other participants found in this competition/round.")
                    else:
                        st.write(f"### 📊 Rankings ({len(participant_stats)} participants)")
                        
                        # Sort by total score
                        sorted_participants = sorted(
                            participant_stats.items(),
                            key=lambda x: x[1]['total'],
                            reverse=True
                        )
                        
                        rank = 1
                        for pid, stats in sorted_participants:
                            avg_score = stats['total'] / len(stats['scores'])
                            max_score = max(stats['scores'])
                            
                            medal = ""
                            if rank == 1:
                                medal = "🥇"
                            elif rank == 2:
                                medal = "🥈"
                            elif rank == 3:
                                medal = "🥉"
                            
                            with st.container(border=True):
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.write(f"{medal} **#{rank} - {stats['name']}** ({stats['country']})")
                                    col_a, col_b, col_c = st.columns(3)
                                    col_a.metric("Total Score", stats['total'])
                                    col_b.metric("Average", f"{avg_score:.2f}/60")
                                    col_c.metric("Best", f"{max_score}/60")
                                
                                with col2:
                                    st.metric("Ends", len(stats['scores']))
                            
                            rank += 1
                else:
                    st.info("No scores found for this competition/round yet.")
            else:
                st.info("No event contexts found for this competition/round.")
    
    except Exception as e:
        st.error(f"Error loading participant data: {str(e)}")

# ==================== COMMUNITY RANKINGS TAB ====================
with tab3:
    st.subheader("🌍 Community Rankings")
    st.info("View overall rankings across all competitions (only eligible competition scores).")
    
    try:
        # Get all eligible competition scores
        all_scores = supabase.table("participant_score").select(
            "participant_id, sum_score, event_context:event_context_id(competition:competition_id(name), round:round_id(name)), account:participant_id(fullname, country)"
        ).eq("type", "competition").eq("status", "eligible").execute()
        
        scores_list = all_scores.data if all_scores.data else []
        
        if not scores_list:
            st.info("No eligible competition scores found in the community yet.")
        else:
            # Aggregate by participant
            participant_stats = {}
            for score in scores_list:
                pid = score['participant_id']
                
                if pid not in participant_stats:
                    participant_stats[pid] = {
                        'name': score['account']['fullname'] if score.get('account') else 'Unknown',
                        'country': score['account']['country'] if score.get('account') else 'Unknown',
                        'scores': [],
                        'total': 0,
                        'competitions': set()
                    }
                
                participant_stats[pid]['scores'].append(score['sum_score'])
                participant_stats[pid]['total'] += score['sum_score']
                
                # Track competitions participated
                event_ctx = score.get('event_context', {})
                if event_ctx and event_ctx.get('competition'):
                    comp_name = event_ctx['competition'].get('name', 'Unknown')
                    participant_stats[pid]['competitions'].add(comp_name)
            
            # Sort by total score
            sorted_community = sorted(
                participant_stats.items(),
                key=lambda x: x[1]['total'],
                reverse=True
            )
            
            st.write(f"### 🏆 Top Archers ({len(sorted_community)} total)")
            
            # Display top 20
            display_count = min(20, len(sorted_community))
            
            for i in range(display_count):
                pid, stats = sorted_community[i]
                rank = i + 1
                
                avg_score = stats['total'] / len(stats['scores'])
                max_score = max(stats['scores'])
                accuracy = (avg_score / 60) * 100
                
                # Medal for top 3
                medal = ""
                if rank == 1:
                    medal = "🥇"
                elif rank == 2:
                    medal = "🥈"
                elif rank == 3:
                    medal = "🥉"
                
                # Highlight current user
                is_current_user = (pid == user_id)
                container_type = "border" if not is_current_user else "border"
                
                with st.container(border=True):
                    if is_current_user:
                        st.success("⭐ **This is you!**")
                    
                    st.write(f"{medal} **#{rank} - {stats['name']}** 🌍 {stats['country']}")
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("Total Score", stats['total'])
                    col2.metric("Average", f"{avg_score:.2f}/60")
                    col3.metric("Best", f"{max_score}/60")
                    col4.metric("Accuracy", f"{accuracy:.1f}%")
                    col5.metric("Competitions", len(stats['competitions']))
                    
                    if len(stats['competitions']) > 0:
                        st.caption(f"Participated in: {', '.join(list(stats['competitions'])[:3])}{'...' if len(stats['competitions']) > 3 else ''}")
            
            # Find and highlight current user if not in top 20
            user_rank = None
            for i, (pid, stats) in enumerate(sorted_community):
                if pid == user_id:
                    user_rank = i + 1
                    break
            
            if user_rank and user_rank > display_count:
                st.divider()
                st.write(f"### Your Rank: #{user_rank}")
                
                user_stats = participant_stats[user_id]
                avg_score = user_stats['total'] / len(user_stats['scores'])
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Score", user_stats['total'])
                col2.metric("Average", f"{avg_score:.2f}/60")
                col3.metric("Best", f"{max(user_stats['scores'])}/60")
                col4.metric("Competitions", len(user_stats['competitions']))
    
    except Exception as e:
        st.error(f"Error loading community rankings: {str(e)}")
