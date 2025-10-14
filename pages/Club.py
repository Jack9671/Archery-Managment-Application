import streamlit as st
from datetime import datetime
from utility_function.initilize_dbconnection import supabase

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please log in to view club information.")
    st.info("Navigate to the 'Sign Up Log In' page to access your account.")
    st.stop()

# Page header
st.title("🏛️ Archery Clubs")
st.write(f"**Logged in as:** {st.session_state.get('fullname', 'N/A')}")
st.write("Browse archery clubs and manage your membership.")
st.divider()

# Check if user is an archer
user_id = st.session_state.get('user_id')
try:
    archer_data = supabase.table("archer").select("archer_id, club_id").eq("archer_id", user_id).execute()
    is_archer = bool(archer_data.data)
    current_club_id = archer_data.data[0]['club_id'] if archer_data.data and archer_data.data[0]['club_id'] else None
except:
    is_archer = False
    current_club_id = None

if not is_archer:
    st.error("🚫 Access Denied")
    st.warning("You must be an Archer to view and join clubs.")
    st.info("Please submit a form to become an archer first.")
    st.stop()

# Display current club membership
if current_club_id:
    try:
        current_club = supabase.table("club").select("*").eq("club_id", current_club_id).execute()
        if current_club.data:
            club = current_club.data[0]
            
            with st.container(border=True):
                st.success("✅ You are currently a member of:")
                st.subheader(f"🏛️ {club['name']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Club ID:** {club['club_id']}")
                    st.write(f"**Age Group:** {club['age_group']}")
                with col2:
                    st.write(f"**Formation Date:** {club['formation_date']}")
                
                st.divider()
                
                # Leave club button
                if st.button("🚪 Leave Club", type="secondary"):
                    try:
                        supabase.table("archer").update({"club_id": None}).eq("archer_id", user_id).execute()
                        st.success("✅ You have left the club.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error leaving club: {str(e)}")
    except Exception as e:
        st.error(f"Error loading current club: {str(e)}")
else:
    st.info("ℹ️ You are not currently a member of any club.")

st.divider()

# Browse all clubs
st.subheader("🔍 Browse All Clubs")

# Filter options
col1, col2 = st.columns(2)

with col1:
    age_group_filter = st.selectbox(
        "Filter by Age Group",
        ["All", "open", "50+", "60+", "70+", "under 21", "under 18", "under 16", "under 14"],
        help="Filter clubs by their focus age group"
    )

with col2:
    search_club = st.text_input(
        "🔍 Search Clubs",
        placeholder="Enter club name...",
        help="Search clubs by name"
    )

# Sort option
sort_by = st.selectbox(
    "Sort By",
    ["Name (A-Z)", "Name (Z-A)", "Formation Date (Newest)", "Formation Date (Oldest)", "Most Members"],
    help="Choose how to sort the clubs"
)

try:
    # Fetch all clubs
    clubs = supabase.table("club").select("*").execute()
    clubs_list = clubs.data if clubs.data else []
    
    # Apply filters
    filtered_clubs = []
    for club in clubs_list:
        # Age group filter
        if age_group_filter != "All" and club['age_group'] != age_group_filter:
            continue
        
        # Search filter
        if search_club and search_club.lower() not in club['name'].lower():
            continue
        
        # Get member count
        try:
            members = supabase.table("archer").select("archer_id").eq("club_id", club['club_id']).execute()
            club['member_count'] = len(members.data) if members.data else 0
        except:
            club['member_count'] = 0
        
        filtered_clubs.append(club)
    
    # Sort clubs
    if sort_by == "Name (A-Z)":
        filtered_clubs.sort(key=lambda x: x['name'])
    elif sort_by == "Name (Z-A)":
        filtered_clubs.sort(key=lambda x: x['name'], reverse=True)
    elif sort_by == "Formation Date (Newest)":
        filtered_clubs.sort(key=lambda x: x['formation_date'], reverse=True)
    elif sort_by == "Formation Date (Oldest)":
        filtered_clubs.sort(key=lambda x: x['formation_date'])
    elif sort_by == "Most Members":
        filtered_clubs.sort(key=lambda x: x['member_count'], reverse=True)
    
    if not filtered_clubs:
        st.warning("No clubs found matching your criteria.")
    else:
        st.info(f"📊 Found {len(filtered_clubs)} club(s)")
        
        for club in filtered_clubs:
            is_current_club = (club['club_id'] == current_club_id)
            
            with st.expander(
                f"{'✅ ' if is_current_club else ''}🏛️ {club['name']} - {club['age_group']} ({club['member_count']} members)",
                expanded=is_current_club
            ):
                if is_current_club:
                    st.success("⭐ **You are a member of this club**")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Club ID:** {club['club_id']}")
                    st.write(f"**Name:** {club['name']}")
                    st.write(f"**Age Group Focus:** {club['age_group']}")
                    st.write(f"**Formation Date:** {club['formation_date']}")
                    st.write(f"**Total Members:** {club['member_count']}")
                    
                    # Calculate club age
                    try:
                        formation_date = datetime.strptime(club['formation_date'], '%Y-%m-%d').date()
                        today = datetime.now().date()
                        years = today.year - formation_date.year
                        st.write(f"**Club Age:** {years} year(s)")
                    except:
                        pass
                
                with col2:
                    # Show top members if any
                    try:
                        members = supabase.table("archer").select(
                            "account:archer_id(fullname)"
                        ).eq("club_id", club['club_id']).execute()
                        
                        if members.data and len(members.data) > 0:
                            st.write("**Sample Members:**")
                            for i, member in enumerate(members.data[:5]):
                                if member.get('account'):
                                    st.caption(f"• {member['account']['fullname']}")
                            
                            if len(members.data) > 5:
                                st.caption(f"...and {len(members.data) - 5} more")
                    except:
                        pass
                
                st.divider()
                
                # Join/Leave button
                if is_current_club:
                    st.info("You are already a member of this club.")
                    if st.button("🚪 Leave This Club", key=f"leave_{club['club_id']}"):
                        try:
                            supabase.table("archer").update({"club_id": None}).eq("archer_id", user_id).execute()
                            st.success("✅ You have left the club.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error leaving club: {str(e)}")
                else:
                    if current_club_id:
                        st.warning("⚠️ You must leave your current club before joining another one.")
                        if st.button("🔄 Switch to This Club", key=f"switch_{club['club_id']}"):
                            try:
                                supabase.table("archer").update({"club_id": club['club_id']}).eq("archer_id", user_id).execute()
                                st.success(f"✅ You have joined {club['name']}!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error switching clubs: {str(e)}")
                    else:
                        if st.button("🎯 Join This Club", key=f"join_{club['club_id']}", type="primary"):
                            try:
                                supabase.table("archer").update({"club_id": club['club_id']}).eq("archer_id", user_id).execute()
                                st.success(f"✅ You have joined {club['name']}!")
                                st.balloons()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error joining club: {str(e)}")

except Exception as e:
    st.error(f"Error loading clubs: {str(e)}")

# ==================== SIDEBAR INFO ====================
with st.sidebar:
    st.subheader("ℹ️ Club Information")
    
    if current_club_id:
        try:
            current_club = supabase.table("club").select("*").eq("club_id", current_club_id).execute()
            if current_club.data:
                club = current_club.data[0]
                
                st.write("**Your Current Club:**")
                st.success(f"🏛️ {club['name']}")
                st.write(f"Age Group: {club['age_group']}")
                
                # Get fellow members
                try:
                    members = supabase.table("archer").select(
                        "archer_id, account:archer_id(fullname)"
                    ).eq("club_id", current_club_id).execute()
                    
                    if members.data:
                        st.write(f"**Club Members ({len(members.data)}):**")
                        
                        for member in members.data[:10]:
                            if member.get('account'):
                                if member['archer_id'] == user_id:
                                    st.caption(f"⭐ {member['account']['fullname']} (You)")
                                else:
                                    st.caption(f"• {member['account']['fullname']}")
                        
                        if len(members.data) > 10:
                            st.caption(f"...and {len(members.data) - 10} more")
                except:
                    pass
        except:
            pass
    else:
        st.info("You are not a member of any club yet.")
    
    st.divider()
    
    # Club statistics
    try:
        total_clubs = supabase.table("club").select("club_id").execute()
        
        st.write("**Club Statistics:**")
        st.metric("Total Clubs", len(total_clubs.data) if total_clubs.data else 0)
        
        # Get age group distribution
        if total_clubs.data:
            all_clubs = supabase.table("club").select("age_group").execute()
            age_groups = {}
            for club in (all_clubs.data or []):
                age_group = club['age_group']
                age_groups[age_group] = age_groups.get(age_group, 0) + 1
            
            st.write("**By Age Group:**")
            for age_group, count in sorted(age_groups.items(), key=lambda x: x[1], reverse=True):
                st.caption(f"• {age_group}: {count} club(s)")
    except:
        pass
    
    st.divider()
    
    st.write("**About Clubs:**")
    st.caption("Clubs are community organizations that bring archers together. Join a club to:")
    st.caption("• Connect with fellow archers")
    st.caption("• Participate in club events")
    st.caption("• Access club resources")
    st.caption("• Build your archery network")

# ==================== STATISTICS SECTION ====================
st.divider()
st.subheader("📊 Club Statistics")

try:
    # Get all clubs with member counts
    all_clubs = supabase.table("club").select("*").execute()
    
    if all_clubs.data:
        club_stats = []
        total_members = 0
        
        for club in all_clubs.data:
            members = supabase.table("archer").select("archer_id").eq("club_id", club['club_id']).execute()
            member_count = len(members.data) if members.data else 0
            total_members += member_count
            
            club_stats.append({
                'name': club['name'],
                'age_group': club['age_group'],
                'members': member_count,
                'formation_date': club['formation_date']
            })
        
        # Sort by member count
        club_stats.sort(key=lambda x: x['members'], reverse=True)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Clubs", len(all_clubs.data))
        col2.metric("Total Club Members", total_members)
        col3.metric("Average Members/Club", f"{total_members / len(all_clubs.data):.1f}" if all_clubs.data else "0")
        
        st.divider()
        
        # Top clubs
        st.write("### 🏆 Top Clubs by Membership")
        
        top_clubs = club_stats[:5]
        for i, club in enumerate(top_clubs):
            medal = ""
            if i == 0:
                medal = "🥇"
            elif i == 1:
                medal = "🥈"
            elif i == 2:
                medal = "🥉"
            
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"{medal} **{club['name']}**")
            col2.write(f"{club['age_group']}")
            col3.metric("Members", club['members'])

except Exception as e:
    st.error(f"Error loading club statistics: {str(e)}")
