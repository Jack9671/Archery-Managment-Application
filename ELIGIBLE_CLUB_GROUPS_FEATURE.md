# Eligible Club Groups Feature

## Overview
This feature allows recorders to create and manage groups of clubs that will be eligible to participate in specific events (Yearly Club Championships or Club Competitions).

## What Was Implemented

### 1. **New Utility Functions** (`utility_function/event_utility.py`)

#### `get_all_clubs()`
- Fetches all clubs from the database
- Returns list of clubs with their IDs and names

#### `create_eligible_group_with_clubs(club_ids)`
- Creates a new eligible group in the `eligible_group_of_club` table
- Adds specified clubs to the group via `eligible_club_member` table
- Returns the newly created `eligible_group_id`
- Includes rollback on failure

#### `get_eligible_group_details(eligible_group_id)`
- Retrieves details of a specific eligible group
- Returns group ID and list of member clubs with their details

#### `get_all_eligible_groups()`
- Fetches all eligible groups from the database
- Includes member club details for each group
- Returns list of groups with their clubs

### 2. **New Tab for Recorders** (Pages/Event.py)

Added a new **"🏢 Club Groups"** tab with two sub-tabs:

#### **Create Club Group Tab**
- Lists all available clubs in the database
- Multi-select interface to choose clubs
- Preview of selected clubs before creation
- Creates the eligible group with one click
- Displays the new group ID for use in event creation

#### **View Existing Groups Tab**
- Displays all existing eligible club groups
- Shows group ID and member count
- Expandable sections for each group showing:
  - Group ID
  - Number of member clubs
  - Table of all member clubs
  - Usage instructions
- Refresh button to reload groups

### 3. **Enhanced Event Creation Wizard**

Updated the event creation wizard (Step 2: Basic Information) for both event types:

#### **Previous Implementation**
- Simple text input for "Eligible Group ID"
- User had to manually type the group ID
- No preview of which clubs are in the group

#### **New Implementation**
- Dropdown selector with all available eligible groups
- Option to select "All Clubs (No Restriction)"
- Shows descriptive labels: "Group {ID} ({X} clubs)"
- Preview panel that expands to show all member clubs
- Automatic handling when no groups exist

### 4. **Updated Imports**
Added necessary imports to Event.py:
```python
from utility_function.event_utility import (
    ...,
    get_all_clubs,
    create_eligible_group_with_clubs,
    get_eligible_group_details,
    get_all_eligible_groups
)
```

## Database Schema Used

### Tables
1. **`eligible_group_of_club`**
   - `eligible_group_of_club_id` (Primary Key, Auto-increment)

2. **`eligible_club_member`**
   - `eligible_group_of_club_id` (Foreign Key)
   - `eligible_club_id` (Foreign Key to `club.club_id`)
   - Composite Primary Key: (eligible_group_of_club_id, eligible_club_id)

3. **`club`**
   - `club_id` (Primary Key)
   - `name`
   - Other club fields...

4. **`yearly_club_championship`**
   - `eligible_group_of_club_id` (Foreign Key, nullable)
   - If NULL, all clubs can participate

5. **`club_competition`**
   - `eligible_group_of_club_id` (Foreign Key, nullable)
   - If NULL, all clubs can participate

## User Flow

### Creating an Eligible Club Group
1. Recorder navigates to **Event Management** page
2. Clicks on **"🏢 Club Groups"** tab
3. Selects **"➕ Create Club Group"** sub-tab
4. Uses multi-select to choose clubs
5. Reviews selected clubs in preview
6. Clicks **"✅ Create Eligible Group"**
7. Receives confirmation with new Group ID

### Using an Eligible Group in Event Creation
1. Recorder starts event creation wizard
2. In Step 2 (Basic Information), finds **"Club Eligibility"** section
3. Selects desired eligible group from dropdown
   - Or selects "All Clubs (No Restriction)"
4. Reviews member clubs in preview panel
5. Continues with event creation

### Viewing Existing Groups
1. Recorder navigates to **"🏢 Club Groups"** tab
2. Selects **"📋 View Existing Groups"** sub-tab
3. Sees list of all eligible groups
4. Expands any group to see details
5. Can refresh to see updated data

## Benefits

1. **Better User Experience**
   - Visual selection instead of manual ID entry
   - Preview of clubs before committing
   - Clear labels and descriptions

2. **Error Prevention**
   - Dropdown prevents invalid group IDs
   - Shows what clubs are included before selection
   - Validates club selections before creation

3. **Flexibility**
   - Easy to restrict events to specific clubs
   - Simple to allow all clubs (no restriction)
   - Can create multiple groups for different purposes

4. **Transparency**
   - View all existing groups and their members
   - See exactly which clubs can participate
   - Clear usage instructions

## Future Enhancements (Optional)

1. **Edit Existing Groups**
   - Add/remove clubs from existing groups
   - Rename or describe groups

2. **Group Templates**
   - Save common club combinations
   - Quick selection of frequently used groups

3. **Group Analytics**
   - Show which events use each group
   - Track participation by group

4. **Bulk Operations**
   - Create multiple groups at once
   - Clone existing groups

5. **Search and Filter**
   - Search groups by member clubs
   - Filter by number of members
