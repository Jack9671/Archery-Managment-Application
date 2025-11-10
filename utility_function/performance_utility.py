
from utility_function.initilize_dbconnection import supabase
import streamlit as st
import pandas as pd

# ========================
# Name → ID Maps
# ========================

def _safe_dict(lst, key_name, id_name):
    try:
        return {row.get(key_name): row.get(id_name) for row in lst if row.get(key_name) and row.get(id_name)}
    except Exception:
        return {}

def get_club_competitions():
    try:
        res = supabase.table("club_competition").select("club_competition_id,name").execute()
        return _safe_dict(res.data or [], "name", "club_competition_id")
    except Exception as e:
        st.warning(f"Could not load club competitions: {e}")
        return {}

def get_yearly_championships():
    try:
        res = supabase.table("yearly_club_championship").select("yearly_club_championship_id,name").execute()
        return _safe_dict(res.data or [], "name", "yearly_club_championship_id")
    except Exception as e:
        st.warning(f"Could not load yearly club championships: {e}")
        return {}

def get_rounds():
    try:
        res = supabase.table("round").select("round_id,name").execute()
        return _safe_dict(res.data or [], "name", "round_id")
    except Exception as e:
        st.warning(f"Could not load rounds: {e}")
        return {}

def get_categories():
    """
    Schema does not expose a category 'name', so we expose IDs as labels.
    You can replace this to join discipline/equipment/age_division for a richer label later.
    """
    try:
        res = supabase.table("category").select("category_id").execute()
        return _safe_dict(res.data or [], "category_id", "category_id")
    except Exception as e:
        st.warning(f"Could not load categories: {e}")
        return {}

def get_archers():
    """Return {fullname: account_id} for accounts with role 'archer'."""
    try:
        res = supabase.table("account").select("account_id,fullname,role").eq("role","archer").execute()
        data = res.data or []
        return {row["fullname"]: row["account_id"] for row in data if row.get("fullname") and row.get("account_id")}
    except Exception as e:
        st.warning(f"Could not load archers: {e}")
        return {}

# ========================
# Helper utilities
# ========================

def _compute_sum_score(row):
    keys = ["score_1st_arrow","score_2nd_arrow","score_3rd_arrow","score_4th_arrow","score_5th_arrow","score_6th_arrow"]
    if all(k in row for k in keys):
        return sum((row.get(k) or 0) for k in keys)
    return row.get("sum_score", 0)

def _participant_label(rec):
    """Return a display label for the archer: 'fullname (participating_id)'."""
    name = None
    archer = rec.get("archer")
    if isinstance(archer, dict):
        account = archer.get("account")
        if isinstance(account, dict):
            name = account.get("fullname")
    name = name or rec.get("fullname") or "Unknown"
    pid = rec.get("participating_id")
    return f"{name} ({pid})" if pid else name

# ========================
# Core fetcher
# ========================

def _fetch_participating_base(club_competition_id=None, round_id=None, archer_account_id=None, yearly_championship_id=None):
    """
    Base fetcher: participating + event_context + archer→account join.
    Joins are implicit based on FKs:
        participating.participating_id → archer.archer_id → account.account_id
    """
    try:
        select_cols = (
            "participating_id, sum_score, "
            "score_1st_arrow,score_2nd_arrow,score_3rd_arrow,"
            "score_4th_arrow,score_5th_arrow,score_6th_arrow, "
            "event_context!inner(event_context_id,yearly_club_championship_id,club_competition_id,round_id,range_id,end_order), "
            "archer!inner(account!inner(fullname))"
        )
        query = supabase.table("participating").select(select_cols).eq("type","competition")

        if club_competition_id:
            query = query.eq("event_context.club_competition_id", club_competition_id)
        if yearly_championship_id:
            query = query.eq("event_context.yearly_club_championship_id", yearly_championship_id)
        if round_id:
            query = query.eq("event_context.round_id", round_id)
        if archer_account_id:
            # nested filter through archer → account
            query = query.eq("archer.account.account_id", archer_account_id)

        res = query.execute()
        return res.data or []
    except Exception as e:
        st.warning(f"Error fetching participating data: {e}")
        return []

# ---------------------------
# View Sum Score - helpers
# ---------------------------
def fetch_scores_per_end(club_competition_id=None, round_id=None, archer_account_id=None):
    rows = _fetch_participating_base(club_competition_id, round_id, archer_account_id)
    if not rows: return pd.DataFrame()
    out = []
    for r in rows:
        out.append({
            "participant": _participant_label(r),
            "end_order": (r.get("event_context") or {}).get("end_order"),
            "sum_score": _compute_sum_score(r)
        })
    df = pd.DataFrame(out)
    return df.groupby(["participant","end_order"], as_index=False)["sum_score"].sum()

def fetch_scores_per_range(club_competition_id=None, round_id=None, archer_account_id=None):
    rows = _fetch_participating_base(club_competition_id, round_id, archer_account_id)
    if not rows: return pd.DataFrame()
    out = []
    for r in rows:
        out.append({
            "participant": _participant_label(r),
            "range_id": (r.get("event_context") or {}).get("range_id"),
            "sum_score": _compute_sum_score(r)
        })
    df = pd.DataFrame(out)
    return df.groupby(["participant","range_id"], as_index=False)["sum_score"].sum()

def fetch_scores_per_round(club_competition_id=None, round_id=None, archer_account_id=None):
    rows = _fetch_participating_base(club_competition_id, round_id, archer_account_id)
    if not rows: return pd.DataFrame()
    out = []
    for r in rows:
        out.append({
            "participant": _participant_label(r),
            "round_id": (r.get("event_context") or {}).get("round_id"),
            "sum_score": _compute_sum_score(r)
        })
    df = pd.DataFrame(out)
    return df.groupby(["participant","round_id"], as_index=False)["sum_score"].sum().sort_values("sum_score", ascending=False)

# ---------------------------
# Yearly normalized average
# ---------------------------
def _max_score_for_round(round_id):
    """
    Derive max score for a round via event_context ends: (#unique (range_id,end_order)) * 6 * 10.
    If your schema has a stored max per round, prefer that instead.
    """
    try:
        q = supabase.table("event_context").select("round_id, range_id, end_order").eq("round_id", round_id).execute()
        rows = q.data or []
        if not rows:
            return None
        ends = {(r.get("range_id"), r.get("end_order")) for r in rows if r.get("end_order") is not None}
        total_arrows = len(ends) * 6
        return total_arrows * 10 if total_arrows else None
    except Exception as e:
        st.info(f"Could not derive max score for round {round_id}: {e}")
        return None

def fetch_yearly_normalized_average(yc_id=None, round_id=None, archer_account_id=None):
    """
    Aggregate the same round across *all* club competitions inside a Yearly Club Championship,
    using the event_context.yearly_club_championship_id linkage from your schema.
    """
    if not yc_id or not round_id:
        st.info("Please select both a Yearly Club Championship and a Round.")
        return pd.DataFrame()

    # Fetch participating rows filtered by yearly and round directly via event_context
    rows = _fetch_participating_base(
        club_competition_id=None,
        round_id=round_id,
        archer_account_id=archer_account_id,
        yearly_championship_id=yc_id
    )
    if not rows:
        return pd.DataFrame()

    max_score = _max_score_for_round(round_id)
    if not max_score:
        st.info("Could not determine max score for the selected round — falling back to raw averages. # placeholder")
        max_score = None

    out = []
    for r in rows:
        s = _compute_sum_score(r)
        norm = (s / max_score) if max_score else None
        out.append({"participant": _participant_label(r), "sum_score": s, "normalized": norm})

    df = pd.DataFrame(out)
    if "normalized" in df.columns and df["normalized"].notna().any():
        agg = df.groupby("participant", as_index=False).agg(normalized_avg=("normalized","mean"))
        return agg.sort_values("normalized_avg", ascending=False)
    else:
        agg = df.groupby("participant", as_index=False).agg(raw_avg=("sum_score","mean"))
        return agg.sort_values("raw_avg", ascending=False)

# ---------------------------
# Rankings
# ---------------------------
def fetch_ranking_in_round(club_competition_id=None, round_id=None):
    rows = _fetch_participating_base(club_competition_id, round_id, None)
    if not rows: return pd.DataFrame()
    df = pd.DataFrame([
        {"participant": _participant_label(r), "sum_score": _compute_sum_score(r)}
        for r in rows
    ])
    return df.groupby("participant", as_index=False)["sum_score"].sum().sort_values("sum_score", ascending=False)

def fetch_ranking_yearly_same_round(yc_id=None, round_id=None):
    return fetch_yearly_normalized_average(yc_id, round_id, None)

# ---------------------------
# Category percentile
# ---------------------------
def fetch_category_percentile_distribution(archer_account_id=None, category_id=None):
    if not category_id:
        st.info("Please select a category.")
        return pd.DataFrame(), None
    try:
        # Schema: archer_id, category_id, percentile
        q = supabase.table("category_rating_percentile").select("archer_id, category_id, percentile").eq("category_id", category_id)
        res = q.execute()
        rows = res.data or []
    except Exception as e:
        st.warning(f"Could not load category rating distribution: {e}")
        return pd.DataFrame(), None

    if not rows:
        return pd.DataFrame(), None

    df = pd.DataFrame(rows).rename(columns={"archer_id":"archer_account_id","percentile":"c_score"})
    df = df[["archer_account_id","c_score"]].dropna()

    my_percentile = None
    if archer_account_id is not None and archer_account_id in set(df["archer_account_id"]):
        d_sorted = df.sort_values("c_score").reset_index(drop=True)
        idx_list = d_sorted.index[d_sorted["archer_account_id"] == archer_account_id].tolist()
        if idx_list:
            idx0 = idx_list[0]
            m = len(d_sorted)
            my_percentile = ((idx0 + 1) / m) * 100.0

    return df, my_percentile
