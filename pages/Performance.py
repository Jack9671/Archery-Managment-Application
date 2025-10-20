import streamlit as st
import pandas as pd
import plotly.express as px
from utility_function.initilize_dbconnection import supabase
from utility_function.performance_utility import (
    get_round_rankings, get_category_percentile, calculate_normalized_average_score,
    get_personal_performance, get_community_performance, get_all_categories
)

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("Please log in to access this page.")
    st.stop()

st.title("📊 Performance Tracking")
st.write(f"Welcome, {st.session_state.get('fullname')}!")

# Create tabs
tab1, tab2, tab3 = st.tabs(["🎯 Round Performance", "👤 Personal Performance", "🏆 Category Rankings"])

# Tab 1: Round Performance
with tab1:
    st.header("Round Performance")
    st.write("View rankings and scores for specific rounds in competitions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        round_id = st.text_input("Round ID", placeholder="Enter round ID")
    
    with col2:
        competition_id = st.text_input("Competition ID", placeholder="Enter competition ID")
    
    if st.button("📊 View Rankings", type="primary"):
        if round_id and competition_id:
            rankings_df = get_round_rankings(round_id, competition_id)
            
            if not rankings_df.empty:
                st.success(f"Found {len(rankings_df)} participant(s)")
                
                # Display rankings table
                st.subheader("Rankings")
                st.dataframe(rankings_df, use_container_width=True)
                
                # Visualization
                if len(rankings_df) > 0:
                    fig = px.bar(
                        rankings_df,
                        x='participating_id',
                        y='total_score',
                        title=f'Scores for Round {round_id} in Competition {competition_id}',
                        labels={'participating_id': 'Participant ID', 'total_score': 'Total Score'},
                        color='total_score',
                        color_continuous_scale='Viridis'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No rankings found for this round and competition.")
        else:
            st.error("Please enter both Round ID and Competition ID.")
    
    # Normalized Average Score for Yearly Championship
    st.divider()
    st.subheader("📈 Normalized Average Score (Yearly Championship)")
    st.write("Calculate how well an archer performs on a specific round during a yearly championship")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        archer_id_norm = st.text_input("Archer ID", placeholder="Enter archer ID", key="archer_norm")
    
    with col2:
        round_id_norm = st.text_input("Round ID ", placeholder="Enter round ID", key="round_norm")
    
    with col3:
        championship_id = st.text_input("Championship ID", placeholder="Enter championship ID")
    
    if st.button("🧮 Calculate Normalized Score", type="primary"):
        if archer_id_norm and round_id_norm and championship_id:
            normalized_score = calculate_normalized_average_score(
                archer_id_norm, round_id_norm, championship_id
            )
            
            st.metric("Normalized Average Score", f"{normalized_score:.2%}")
            
            if normalized_score > 0:
                st.success(f"Archer {archer_id_norm} has a normalized average score of {normalized_score:.2%} for Round {round_id_norm}")
            else:
                st.info("No data available for this combination.")
        else:
            st.error("Please fill in all fields.")

# Tab 2: Personal Performance
with tab2:
    st.header("Personal Performance")
    
    performance_type = st.radio("View Performance For", ["Myself", "Another Archer"])
    
    if performance_type == "Myself":
        archer_id_personal = st.session_state.user_id
        st.info(f"Viewing performance for: {st.session_state.fullname} (ID: {archer_id_personal})")
    else:
        archer_id_personal = st.text_input("Enter Archer ID", placeholder="Archer ID")
    
    if st.button("📊 Load Performance Data", type="primary"):
        if archer_id_personal:
            performance_df = get_personal_performance(archer_id_personal)
            
            if not performance_df.empty:
                st.success(f"Found {len(performance_df)} competition record(s)")
                
                # Display performance data
                st.dataframe(performance_df, use_container_width=True)
                
                # Statistics
                st.divider()
                st.subheader("📈 Performance Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Competitions", len(performance_df))
                
                with col2:
                    avg_score = performance_df['total_score'].mean()
                    st.metric("Average Score", f"{avg_score:.2f}")
                
                with col3:
                    max_score = performance_df['total_score'].max()
                    st.metric("Best Score", f"{max_score:.0f}")
                
                with col4:
                    min_score = performance_df['total_score'].min()
                    st.metric("Lowest Score", f"{min_score:.0f}")
                
                # Score trend visualization
                if len(performance_df) > 1:
                    st.divider()
                    st.subheader("📉 Score Trend")
                    
                    # Sort by event context id (chronological)
                    performance_df_sorted = performance_df.sort_values('event_context_id')
                    
                    fig = px.line(
                        performance_df_sorted,
                        x=performance_df_sorted.index,
                        y='total_score',
                        title='Score Progression Over Competitions',
                        labels={'index': 'Competition Number', 'total_score': 'Total Score'},
                        markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No competition performance data found for this archer.")
        else:
            st.error("Please enter an Archer ID.")

# Tab 3: Category Rankings
with tab3:
    st.header("Category Rankings & Percentiles")
    st.write("View percentile rankings for different categories")
    
    # Get all categories
    categories_df = get_all_categories()
    
    if not categories_df.empty:
        st.subheader("📋 Available Categories")
        st.dataframe(categories_df[['category_id']], use_container_width=True)
    
    st.divider()
    st.subheader("🔍 Check Archer Percentile")
    
    col1, col2 = st.columns(2)
    
    with col1:
        archer_id_percentile = st.text_input("Archer ID", placeholder="Enter archer ID", key="archer_percentile")
    
    with col2:
        category_id_percentile = st.text_input("Category ID", placeholder="Enter category ID", key="category_percentile")
    
    if st.button("🏅 Get Percentile", type="primary"):
        if archer_id_percentile and category_id_percentile:
            percentile_data = get_category_percentile(archer_id_percentile, category_id_percentile)
            
            if percentile_data:
                percentile_value = percentile_data.get('percentile', 0)
                
                st.success(f"Percentile found for Archer {archer_id_percentile} in Category {category_id_percentile}")
                
                # Display percentile with visual indicator
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col2:
                    st.metric("Percentile Ranking", f"{percentile_value:.1f}%")
                    
                    # Create a progress bar visualization
                    st.progress(percentile_value / 100)
                    
                    # Interpretation
                    if percentile_value >= 90:
                        st.success("🏆 Excellent! Top 10% performer")
                    elif percentile_value >= 75:
                        st.info("🥈 Great! Top 25% performer")
                    elif percentile_value >= 50:
                        st.info("📊 Good! Above average performer")
                    else:
                        st.info("📈 Keep practicing to improve your ranking!")
                
                st.divider()
                st.write("**What does this mean?**")
                st.write(f"This archer performs better than {percentile_value:.1f}% of all archers in this category.")
            else:
                st.warning("No percentile data found for this archer in this category.")
        else:
            st.error("Please enter both Archer ID and Category ID.")
    
    # Community performance comparison
    st.divider()
    st.subheader("🌐 Community Performance")
    st.write("Compare performance across all participants in a specific round")
    
    col1, col2 = st.columns(2)
    
    with col1:
        community_round_id = st.text_input("Round ID", placeholder="Enter round ID", key="community_round")
    
    with col2:
        community_comp_id = st.text_input("Competition ID", placeholder="Enter competition ID", key="community_comp")
    
    if st.button("👥 View Community Performance", type="primary"):
        if community_round_id and community_comp_id:
            community_df = get_community_performance(community_round_id, community_comp_id)
            
            if not community_df.empty:
                st.success(f"Found {len(community_df)} participant(s)")
                
                # Display data
                st.dataframe(community_df, use_container_width=True)
                
                # Statistics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_community_score = community_df['total_score'].mean()
                    st.metric("Community Average", f"{avg_community_score:.2f}")
                
                with col2:
                    highest_score = community_df['total_score'].max()
                    st.metric("Highest Score", f"{highest_score:.0f}")
                
                with col3:
                    lowest_score = community_df['total_score'].min()
                    st.metric("Lowest Score", f"{lowest_score:.0f}")
                
                # Distribution visualization
                fig = px.histogram(
                    community_df,
                    x='total_score',
                    nbins=20,
                    title='Score Distribution',
                    labels={'total_score': 'Total Score', 'count': 'Number of Participants'},
                    color_discrete_sequence=['#636EFA']
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No community performance data found.")
        else:
            st.error("Please enter both Round ID and Competition ID.")
