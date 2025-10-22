import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utility_function.initilize_dbconnection import supabase
from utility_function import performance_utility

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("Please log in to access this page.")
    st.stop()

st.title("📈 Performance Analytics")
st.write(f"Welcome, {st.session_state.get('fullname')}!")

user_role = st.session_state.get('role')
user_id = st.session_state.get('user_id')

# Create tabs
tabs = st.tabs(["👤 Personal Performance", "👥 Others' Performance", "🌍 Community Leaderboard", "🏆 Category Ratings"])
tab_personal, tab_others, tab_community, tab_category = tabs

# ========================================
# TAB 1: Personal Performance
# ========================================
with tab_personal:
    st.header("👤 My Performance Analytics")
    
    if user_role != 'archer':
        st.warning("Personal performance is only available for archers.")
    else:
        # Overall statistics
        st.subheader("📊 Overall Statistics")
        if st.button("🔄 Refresh Statistics", key="refresh_stats"):
            st.rerun()
        stats_type = st.selectbox("Score Type", ["competition", "practice"], key="stats_type")

        
        stats = performance_utility.get_personal_statistics(user_id, stats_type)
        
        if stats:
            cols = st.columns(3)
            cols[0].metric("Total Ends Recorded", stats['total_ends'])
            cols[1].metric("Verified Ends", stats['total_eligible_ends'])
            cols[2].metric("Average Score", f"{stats['average_score']:.2f}")
            
            cols = st.columns(3)
            cols[0].metric("Highest Score", stats['highest_score'])
            cols[1].metric("Lowest Score", stats['lowest_score'])
            cols[2].metric("Consistency (σ)", f"{stats['std_deviation']:.2f}")
        else:
            st.info("No performance data available yet. Start competing to track your performance!")
        
        st.divider()
        
        # Competition-specific performance
        st.subheader("🎯 Round Performance in Competition")
        st.write("View your total score, ranking, and percentile for a specific round in a competition")
        
        # Get archer's competition history
        comp_history = performance_utility.get_archer_competition_history(user_id)
        
        if not comp_history.empty:
            comp_map = {f"{row['name']} ({row['date_start']} to {row['date_end']})": idx 
                       for idx, row in comp_history.iterrows()}
            
            selected_comp_name = st.selectbox("Select Competition*", list(comp_map.keys()))
            comp_idx = comp_map[selected_comp_name]
            competition_id = comp_history.iloc[comp_idx].name
            
            # Get rounds in this competition
            rounds_map = performance_utility.get_rounds_in_competition(competition_id)
            
            if rounds_map:
                selected_round_name = st.selectbox("Select Round*", list(rounds_map.keys()))
                round_id = rounds_map[selected_round_name]
                
                if st.button("📊 Analyze Performance", type="primary", key="analyze_perf"):
                    performance = performance_utility.get_round_performance_for_competition(
                        user_id, competition_id, round_id
                    )
                    
                    if performance:
                        st.success("✅ Performance Analysis Complete!")
                        
                        cols = st.columns(4)
                        cols[0].metric("Total Score", performance['total_score'])
                        cols[1].metric("Ranking", f"#{performance['ranking']}")
                        cols[2].metric("Percentile", f"{performance['percentile']}%")
                        cols[3].metric("Total Participants", performance['total_participants'])
                        
                        # Visualization
                        fig = go.Figure(go.Indicator(
                            mode = "gauge+number+delta",
                            value = performance['percentile'],
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "Your Percentile"},
                            delta = {'reference': 50},
                            gauge = {
                                'axis': {'range': [None, 100]},
                                'bar': {'color': "darkblue"},
                                'steps': [
                                    {'range': [0, 25], 'color': "lightgray"},
                                    {'range': [25, 50], 'color': "gray"},
                                    {'range': [50, 75], 'color': "lightgreen"},
                                    {'range': [75, 100], 'color': "green"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 90
                                }
                            }
                        ))
                        
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Interpretation
                        if performance['percentile'] >= 90:
                            st.success("🌟 Outstanding! You're in the top 10% of performers!")
                        elif performance['percentile'] >= 75:
                            st.success("🎯 Excellent! You're performing better than 75% of participants!")
                        elif performance['percentile'] >= 50:
                            st.info("👍 Good! You're performing above average!")
                        else:
                            st.info("💪 Keep practicing! There's room for improvement!")
                    else:
                        st.warning("No performance data found for this round.")
            else:
                st.warning("No rounds found for this competition.")
        else:
            st.info("You haven't participated in any competitions yet.")
        
        st.divider()
        
        # Championship performance
        st.subheader("🏆 Championship Performance")
        st.write("View your normalized average score for a round across all competitions in a championship")
        
        championships_map = performance_utility.get_yearly_championships()
        
        if championships_map:
            selected_champ_name = st.selectbox("Select Championship*", list(championships_map.keys()))
            championship_id = championships_map[selected_champ_name]
            
            # Get rounds - need to fetch from championship competitions
            round_map = performance_utility.get_round_map()
            
            if round_map:
                selected_round_name = st.selectbox("Select Round*", list(round_map.keys()), key="champ_round")
                round_id = round_map[selected_round_name]
                
                if st.button("📈 Analyze Championship Performance", type="primary", key="analyze_champ"):
                    result = performance_utility.get_normalized_average_for_round_in_championship(
                        user_id, championship_id, round_id
                    )
                    
                    if result:
                        st.success("✅ Championship Analysis Complete!")
                        
                        cols = st.columns(3)
                        cols[0].metric("Normalized Average", f"{result['normalized_average']:.4f}")
                        cols[1].metric("Competitions Participated", result['competitions_participated'])
                        cols[2].metric("Total Competitions", result['total_competitions'])
                        
                        # Percentage bar
                        percentage = result['normalized_average'] * 100
                        
                        fig = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = percentage,
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "Score Efficiency (%)"},
                            gauge = {
                                'axis': {'range': [None, 100]},
                                'bar': {'color': "darkgreen"},
                                'steps': [
                                    {'range': [0, 50], 'color': "lightgray"},
                                    {'range': [50, 70], 'color': "yellow"},
                                    {'range': [70, 85], 'color': "orange"},
                                    {'range': [85, 100], 'color': "lightgreen"}
                                ]
                            }
                        ))
                        
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.info(f"💡 You scored an average of {percentage:.2f}% of the maximum possible score across {result['competitions_participated']} competition(s).")
                    else:
                        st.warning("No championship performance data found for this round.")
            else:
                st.warning("No rounds available.")
        else:
            st.info("No championships available yet.")

# ========================================
# TAB 2: Others' Performance
# ========================================
with tab_others:
    st.header("👥 View Others' Performance")
    st.write("Compare and learn from other archers' performance")
    
    archer_map = performance_utility.get_archer_map()
    
    if not archer_map:
        st.warning("No other archers found in the system.")
    else:
        selected_archer_name = st.selectbox("Select Archer*", list(archer_map.keys()))
        archer_id = archer_map[selected_archer_name]
        
        # Overall statistics
        st.subheader("📊 Overall Statistics")
        
        stats = performance_utility.get_personal_statistics(archer_id, 'competition')
        
        if stats:
            cols = st.columns(3)
            cols[0].metric("Total Ends", stats['total_ends'])
            cols[1].metric("Verified Ends", stats['total_eligible_ends'])
            cols[2].metric("Average Score", f"{stats['average_score']:.2f}")
            
            cols = st.columns(3)
            cols[0].metric("Highest Score", stats['highest_score'])
            cols[1].metric("Lowest Score", stats['lowest_score'])
            cols[2].metric("Consistency", f"{stats['std_deviation']:.2f}")
        else:
            st.info("This archer has no competition data yet.")
        
        st.divider()
        
        # Competition history
        st.subheader("🏆 Competition History")
        
        comp_history = performance_utility.get_archer_competition_history(archer_id)
        
        if not comp_history.empty:
            st.success(f"Found {len(comp_history)} competition(s)")
            st.dataframe(comp_history, use_container_width=True, hide_index=True)
        else:
            st.info("This archer hasn't participated in any competitions yet.")
        
        st.divider()
        
        # Round performance
        st.subheader("🎯 Round Performance Analysis")
        
        if not comp_history.empty:
            comp_map_others = {f"{row['name']} ({row['date_start']} to {row['date_end']})": idx 
                              for idx, row in comp_history.iterrows()}
            
            selected_comp_name_others = st.selectbox("Select Competition*", list(comp_map_others.keys()), key="others_comp")
            comp_idx_others = comp_map_others[selected_comp_name_others]
            competition_id_others = comp_history.iloc[comp_idx_others].name
            
            rounds_map_others = performance_utility.get_rounds_in_competition(competition_id_others)
            
            if rounds_map_others:
                selected_round_name_others = st.selectbox("Select Round*", list(rounds_map_others.keys()), key="others_round")
                round_id_others = rounds_map_others[selected_round_name_others]
                
                if st.button("📊 View Performance", type="primary", key="view_others"):
                    performance = performance_utility.get_round_performance_for_competition(
                        archer_id, competition_id_others, round_id_others
                    )
                    
                    if performance:
                        cols = st.columns(4)
                        cols[0].metric("Total Score", performance['total_score'])
                        cols[1].metric("Ranking", f"#{performance['ranking']}")
                        cols[2].metric("Percentile", f"{performance['percentile']}%")
                        cols[3].metric("Total Participants", performance['total_participants'])
                    else:
                        st.warning("No performance data found.")

# ========================================
# TAB 3: Community Leaderboard
# ========================================
with tab_community:
    st.header("🌍 Community Leaderboard")
    st.write("See the top performers for specific rounds in competitions")
    
    # Get all competitions
    try:
        comp_response = supabase.table("club_competition").select("club_competition_id, name, date_start, date_end").execute()
        
        if comp_response.data:
            comp_map_community = {f"{row['name']} ({row['date_start']} to {row['date_end']})": row['club_competition_id'] 
                                 for row in comp_response.data}
            
            selected_comp_community = st.selectbox("Select Competition*", list(comp_map_community.keys()), key="community_comp")
            competition_id_community = comp_map_community[selected_comp_community]
            
            # Get rounds in this competition
            rounds_map_community = performance_utility.get_rounds_in_competition(competition_id_community)
            
            if rounds_map_community:
                selected_round_community = st.selectbox("Select Round*", list(rounds_map_community.keys()), key="community_round")
                round_id_community = rounds_map_community[selected_round_community]
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    limit = st.slider("Number of top performers to display", min_value=5, max_value=50, value=10)
                with col2:
                    st.write("")
                    st.write("")
                    show_leaderboard = st.button("🏆 Show Leaderboard", type="primary", use_container_width=True)
                
                if show_leaderboard:
                    leaderboard_df = performance_utility.get_community_leaderboard(
                        round_id_community, competition_id_community, limit
                    )
                    
                    if not leaderboard_df.empty:
                        st.success(f"🎯 Top {len(leaderboard_df)} Performers")
                        
                        # Highlight top 3
                        def highlight_top3(row):
                            if row['Rank'] == 1:
                                return ['background-color: gold'] * len(row)
                            elif row['Rank'] == 2:
                                return ['background-color: silver'] * len(row)
                            elif row['Rank'] == 3:
                                return ['background-color: #CD7F32'] * len(row)
                            else:
                                return [''] * len(row)
                        
                        styled_df = leaderboard_df.style.apply(highlight_top3, axis=1)
                        st.dataframe(styled_df, use_container_width=True, hide_index=True)
                        
                        # Visualization horizontal bar chart
                        fig = px.bar(
                            leaderboard_df, 
                            x='Archer', 
                            y='Total Score',
                            color='Total Score',
                            color_continuous_scale='Viridis',
                            title=f'Top {len(leaderboard_df)} Performers',
                            labels={'Total Score': 'Total Score'},
                            text='Total Score',
                        
                        )
                        
                        fig.update_traces(texttemplate='%{text}', textposition='outside')
                        fig.update_layout(xaxis_tickangle=-45, height=500)
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show if current user is in leaderboard
                        if user_role == 'archer' and user_id in leaderboard_df['Archer ID'].values:
                            user_rank = leaderboard_df[leaderboard_df['Archer ID'] == user_id]['Rank'].values[0]
                            user_score = leaderboard_df[leaderboard_df['Archer ID'] == user_id]['Total Score'].values[0]
                            st.success(f"🎉 You're on the leaderboard! Rank #{user_rank} with {user_score} points!")
                    else:
                        st.info("No leaderboard data available for this round.")
            else:
                st.warning("No rounds found for this competition.")
        else:
            st.warning("No competitions available.")
    except Exception as e:
        st.error(f"Error loading leaderboard: {e}")

# ========================================
# TAB 4: Category Ratings
# ========================================
with tab_category:
    st.header("🏆 Category-Specific Ratings")
    st.write("View percentile rankings by category (discipline + age + equipment)")
    
    if user_role != 'archer':
        st.warning("Category ratings are only available for archers.")
        
        # Allow viewing other archers
        st.divider()
        st.subheader("View Other Archer's Ratings")
        
        archer_map_cat = performance_utility.get_archer_map()
        if archer_map_cat:
            selected_archer_cat = st.selectbox("Select Archer*", list(archer_map_cat.keys()), key="cat_archer")
            archer_id_cat = archer_map_cat[selected_archer_cat]
            view_archer_id = archer_id_cat
        else:
            st.stop()
    else:
        view_archer_id = user_id
    
    # Get category map
    category_map = performance_utility.get_category_map()
    
    if not category_map:
        st.warning("No categories available.")
    else:
        st.write("**Select a category to view your global percentile ranking:**")
        
        selected_category = st.selectbox("Select Category*", list(category_map.keys()))
        category_id = category_map[selected_category]
        
        if st.button("🔍 Check Rating", type="primary"):
            percentile = performance_utility.get_category_percentile(view_archer_id, category_id)
            
            if percentile is not None:
                st.success(f"✅ Category Percentile: **{percentile}%**")
                
                # Gauge chart
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = percentile,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': f"Global Percentile<br><span style='font-size:0.8em'>{selected_category}</span>"},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 25], 'color': "lightgray"},
                            {'range': [25, 50], 'color': "gray"},
                            {'range': [50, 75], 'color': "lightblue"},
                            {'range': [75, 90], 'color': "lightgreen"},
                            {'range': [90, 100], 'color': "gold"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 95
                        }
                    }
                ))
                
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Interpretation
                st.write("**What does this mean?**")
                if percentile >= 95:
                    st.success("🌟 **Elite Level!** You're performing better than 95% of all archers globally in this category!")
                elif percentile >= 90:
                    st.success("🏆 **Exceptional!** You're in the top 10% of archers in this category!")
                elif percentile >= 75:
                    st.info("🎯 **Advanced!** You're performing better than 75% of archers in this category!")
                elif percentile >= 50:
                    st.info("👍 **Above Average!** You're performing better than half of all archers!")
                else:
                    st.info("💪 **Developing!** Keep practicing to improve your global ranking!")
                
                st.info(f"💡 This percentile is calculated based on your verified competition scores in the {selected_category} category compared to all other archers globally.")
            else:
                st.warning("No rating data found for this category. Participate in competitions to earn a rating!")
        
        st.divider()
        
        # Show all available ratings
        st.subheader("📋 All Your Category Ratings")
        
        try:
            all_ratings_response = supabase.table("category_rating_percentile").select(
                """
                percentile,
                category(
                    discipline(name),
                    age_division(min_age, max_age),
                    equipment(name)
                )
                """
            ).eq("archer_id", view_archer_id).execute()
            
            if all_ratings_response.data:
                ratings_data = []
                for row in all_ratings_response.data:
                    cat = row['category']
                    ratings_data.append({
                        'Category': f"{cat['discipline']['name']} - {cat['equipment']['name']} (Ages {cat['age_division']['min_age']}-{cat['age_division']['max_age']})",
                        'Percentile': f"{row['percentile']}%"
                    })
                
                ratings_df = pd.DataFrame(ratings_data)
                st.dataframe(ratings_df, use_container_width=True, hide_index=True)
            else:
                st.info("No category ratings available yet. Compete to earn ratings!")
        except Exception as e:
            st.error(f"Error loading ratings: {e}")
