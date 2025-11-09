
import streamlit as st
import pandas as pd
import plotly.express as px
from utility_function.initilize_dbconnection import supabase
from utility_function import performance_utility as perf

if not st.session_state.get('logged_in', False):
    st.warning("Please log in to access this page.")
    st.stop()

st.title("📈 Performance")
st.caption("Browse personal, others’, and community performance — per End/Range/Round, rankings, and category percentiles.")

def _show_df(df: pd.DataFrame, use_index=False, height=380):
    if df is None or df.empty:
        st.info("No data to display.")
        return
    st.dataframe(df, use_container_width=True, height=height, hide_index=not use_index)

tab1, tab2 = st.tabs(["🔢 View Sum Score", "🏅 Ranking"])

# =====================================
# TAB 1: View Sum Score
# =====================================
with tab1:
    st.subheader("🔢 View Sum Score")
    mode = st.radio(
        "View:",
        ["per end", "per range", "per round", "average for round in a yearly club championship"],
        horizontal=True
    )

    club_map = perf.get_club_competitions()
    round_map = perf.get_rounds()
    yc_map = perf.get_yearly_championships()
    archer_map = perf.get_archers()

    if mode in ["per end", "per range", "per round"]:
        colA, colB, colC = st.columns([1.2, 1, 1])
        with colA:
            club_name = st.selectbox("Club Competition", [""] + list(club_map.keys()), key="tab1_club")
        with colB:
            round_name = st.selectbox("Round (optional)", [""] + list(round_map.keys()), key="tab1_round")
        with colC:
            archer_name = st.selectbox("Participant (optional)", [""] + list(archer_map.keys()), key="tab1_archer")

        if st.button("Apply score configuration", type="primary"):
            club_id = club_map.get(club_name) if club_name else None
            rnd_id = round_map.get(round_name) if round_name else None
            archer_account_id = archer_map.get(archer_name) if archer_name else None

            if mode == "per end":
                df = perf.fetch_scores_per_end(club_competition_id=club_id, round_id=rnd_id, archer_account_id=archer_account_id)
            elif mode == "per range":
                df = perf.fetch_scores_per_range(club_competition_id=club_id, round_id=rnd_id, archer_account_id=archer_account_id)
            else:
                df = perf.fetch_scores_per_round(club_competition_id=club_id, round_id=rnd_id, archer_account_id=archer_account_id)

            _show_df(df)

            if mode == "per round" and df is not None and not df.empty:
                try:
                    fig = px.bar(
                        df.sort_values("sum_score", ascending=False),
                        x="sum_score",
                        y="participant",
                        orientation="h",
                        title="Total Score per Round (sorted)"
                    )
                    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not render bar chart: {e}")

    else:
        colA, colB = st.columns([1.2, 1.2])
        with colA:
            yc_name = st.selectbox("Yearly Club Championship", [""] + list(yc_map.keys()), key="tab1_yc")
        with colB:
            round_name = st.selectbox("Round", [""] + list(round_map.keys()), key="tab1_round_yc")

        archer_name = st.selectbox("Participant (optional)", [""] + list(archer_map.keys()), key="tab1_archer_yc")

        if st.button("Apply score configuration", type="primary"):
            yc_id = yc_map.get(yc_name) if yc_name else None
            rnd_id = round_map.get(round_name) if round_name else None
            archer_account_id = archer_map.get(archer_name) if archer_name else None

            df = perf.fetch_yearly_normalized_average(yc_id=yc_id, round_id=rnd_id, archer_account_id=archer_account_id)
            _show_df(df)

            if df is not None and not df.empty:
                try:
                    fig = px.bar(
                        df.sort_values("normalized_avg", ascending=False),
                        x="normalized_avg",
                        y="participant",
                        orientation="h",
                        title="Normalized Average Score (Yearly Championship)"
                    )
                    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not render bar chart: {e}")

# =====================================
# TAB 2: Ranking
# =====================================
with tab2:
    st.subheader("🏅 Ranking")
    opt = st.radio(
        "Choose:",
        [
            "view ranking in a round in a club competition",
            "view ranking in the same rounds played by multiple club competitions in a yearly club championship",
            "view global rating percentile per category",
        ],
    )

    if opt == "view ranking in a round in a club competition":
        club_map = perf.get_club_competitions()
        round_map = perf.get_rounds()
        colA, colB = st.columns([1.2, 1.2])
        with colA:
            club_name = st.selectbox("Club Competition", [""] + list(club_map.keys()), key="tab2_club")
        with colB:
            round_name = st.selectbox("Round", [""] + list(round_map.keys()), key="tab2_round")

        if st.button("Show Ranking", type="primary"):
            club_id = club_map.get(club_name) if club_name else None
            rnd_id = round_map.get(round_name) if round_name else None

            df = perf.fetch_ranking_in_round(club_competition_id=club_id, round_id=rnd_id)
            _show_df(df)

            if df is not None and not df.empty:
                try:
                    fig = px.bar(
                        df.sort_values("sum_score", ascending=False),
                        x="sum_score",
                        y="participant",
                        orientation="h",
                        title="Ranking — Round in Club Competition",
                    )
                    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not render bar chart: {e}")

    elif opt == "view ranking in the same rounds played by multiple club competitions in a yearly club championship":
        yc_map = perf.get_yearly_championships()
        round_map = perf.get_rounds()
        colA, colB = st.columns([1.2, 1.2])
        with colA:
            yc_name = st.selectbox("Yearly Club Championship", [""] + list(yc_map.keys()), key="tab2_yc")
        with colB:
            round_name = st.selectbox("Round", [""] + list(round_map.keys()), key="tab2_round_yc")

        if st.button("Show Yearly Ranking", type="primary"):
            yc_id = yc_map.get(yc_name) if yc_name else None
            rnd_id = round_map.get(round_name) if round_name else None

            df = perf.fetch_ranking_yearly_same_round(yc_id=yc_id, round_id=rnd_id)
            _show_df(df)

            if df is not None and not df.empty:
                try:
                    fig = px.bar(
                        df.sort_values("normalized_avg", ascending=False),
                        x="normalized_avg",
                        y="participant",
                        orientation="h",
                        title="Yearly Ranking — Same Round across Competitions (Normalized Avg)",
                    )
                    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not render bar chart: {e}")

    else:
        # =====================================
        # UPDATED GLOBAL PERCENTILE VIEW
        # =====================================
        st.subheader("📈 View Global Rating Percentile per Category")

        archer_map = perf.get_archers()
        category_map = perf.get_categories()

        colA, colB = st.columns([1.2, 1.2])
        with colA:
            selected_archer = st.selectbox("Select Archer", [""] + list(archer_map.keys()), key="tab2_archer_new")
        with colB:
            selected_category = st.selectbox("Select Category", [""] + list(category_map.keys()), key="tab2_category_new")

        if st.button("Show Percentile", type="primary", key="show_percentile_new"):
            archer_account_id = archer_map.get(selected_archer)
            category_id = category_map.get(selected_category)

            df, my_percentile = perf.fetch_category_percentile_distribution(
                archer_account_id=archer_account_id, category_id=category_id
            )

            if df.empty:
                st.warning("No data found for the selected category.")
            else:
                reverse_map = {v: k for k, v in archer_map.items()}
                df["archer_account_id"] = df["archer_account_id"].map(reverse_map)
                df = df.rename(columns={"archer_account_id": "Archer Name", "c_score": "Category Score"})
                df = df.sort_values("Category Score", ascending=False).reset_index(drop=True)
                st.dataframe(df, use_container_width=True)

                # Compute proper percentile ranks (0–100)
                df_plot = df.sort_values("Category Score", ascending=True).reset_index(drop=True)
                if len(df_plot) > 1:
                    df_plot["Percentile Rank"] = (df_plot.index / (len(df_plot) - 1)) * 100.0
                else:
                    df_plot["Percentile Rank"] = 100.0

                # Plot line chart
                fig = px.line(
                    df_plot,
                    x="Percentile Rank",
                    y="Category Score",
                    title=f"Distribution of Archers for Category {selected_category}",
                    markers=True,
                    hover_data=["Archer Name", "Category Score"],
                )
                fig.update_layout(
                    xaxis=dict(
                        range=[0, 100],
                        tickmode="array",
                        tickvals=[0, 25, 50, 75, 100],
                        title="Percentile Rank (0 = lowest, 100 = highest)",
                    )
                )

                selected_percentile = None
                # Highlight selected archer
                selected_row = df_plot[df_plot["Archer Name"] == selected_archer]
                if not selected_row.empty:
                    selected_score = selected_row.iloc[0]["Category Score"]
                    selected_percentile = selected_row.iloc[0]["Percentile Rank"]
                    fig.add_scatter(
                        x=[selected_percentile],
                        y=[selected_score],
                        mode="markers+text",
                        marker=dict(size=12, color="red"),
                        text=[selected_archer],
                        textposition="top center",
                        name="Selected Archer",
                    )

                st.plotly_chart(fig, use_container_width=True)

                # Insight text
                if selected_percentile is not None:
                    percentile_str = f"{selected_percentile:.2f}"
                    top_pct = 100 - selected_percentile
                    st.success(
                        f"🏹 **{selected_archer}** has an estimated percentile of **{percentile_str}**, "
                        f"placing them above approximately **{percentile_str}%** of archers in **Category {selected_category}**."
                    )
                    if selected_percentile >= 90:
                        st.info(f"🌟 Excellent performance! {selected_archer} ranks in the top 10% of this category.")
                    elif selected_percentile >= 75:
                        st.info(f"💪 Great job! {selected_archer} ranks in the top {top_pct:.0f}% — strong competitive level.")
                    elif selected_percentile >= 55:
                        st.info(f"👍 {selected_archer} is performing **above average** for Category {selected_category}.")
                    elif selected_percentile >= 45:
                        st.info(f"👌 {selected_archer} is performing **around the average range** for Category {selected_category}.")
                    else:
                        st.info(f"📉 {selected_archer} is performing **below average** for Category {selected_category}. Keep practicing!")
                else:
                    st.warning("Unable to estimate percentile for the selected archer.")
