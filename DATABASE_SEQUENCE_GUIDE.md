# Database Sequence Management Guide

## What is a Database Sequence?

A sequence is a database object that automatically generates unique numbers for primary key columns (like `form_id`, `club_id`, etc.). When you insert a new record without specifying the ID, PostgreSQL uses the sequence to generate the next available number.

## The Problem

The error `duplicate key value violates unique constraint` occurs when the sequence counter is **out of sync** with the actual data in the table. For example:
- The table has records with IDs: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
- But the sequence is at: 5
- Next insert tries to use ID 5, which already exists → ERROR!

## How This Happens

1. **Manual data insertion with explicit IDs** - Inserting data with specific `form_id` values bypasses the sequence
2. **Manual deletion and re-insertion** - Deleting records and inserting new ones can cause gaps
3. **Database restore from backup** - Restoring old data without updating sequences
4. **Testing/debugging** - Running SQL scripts that insert data with specific IDs

## Prevention (Code Best Practices)

### ✅ DO: Let the database auto-generate IDs

```python
# CORRECT - No form_id specified
insert_data = {
    "sender_id": user_id,
    "sender_word": message,
    "status": "pending"
}
supabase.table("request_competition_form").insert(insert_data).execute()
```

### ❌ DON'T: Specify explicit IDs

```python
# WRONG - Don't do this!
insert_data = {
    "form_id": 5,  # BAD! Let database handle this
    "sender_id": user_id,
    "status": "pending"
}
```

## Current Code Status

All insert operations in the Streamlit application are correctly implemented:
- ✅ `pages/Event.py` - No form_id in insert
- ✅ `pages/Club.py` - Uses utility function
- ✅ `utility_function/club_utility.py` - No form_id in insert
- ✅ All other utility functions - Correct implementation

## How to Fix Sequence Issues

### Step 1: Identify the Problem

Run the diagnostic script:
```bash
python fix_sequence.py
```

This will show:
- Current maximum ID in the table
- The SQL command needed to fix the sequence

### Step 2: Run the Fix SQL

The script will output something like:
```sql
SELECT setval('request_competition_form_form_id_seq', 10, true);
```

**Where to run it:**
1. Go to Supabase Dashboard
2. Click on "SQL Editor"
3. Paste the SQL command
4. Click "Run" (or press Ctrl+Enter)

### Step 3: Verify the Fix

Try inserting a new record through the Streamlit app. It should work now.

## Table Sequences to Monitor

- `request_competition_form_form_id_seq`
- `club_enrollment_form_form_id_seq`
- `club_club_id_seq`
- `account_account_id_seq`
- Other auto-increment primary keys

## Error Handling

The application now includes improved error handling:

**Event.py:**
```python
except Exception as e:
    error_msg = str(e)
    if "duplicate key value violates unique constraint" in error_msg and "form_id" in error_msg:
        st.error("⚠️ Database sequence error detected. Please contact an administrator to reset the sequence.")
        st.info("Technical details: The auto-increment sequence is out of sync with the database.")
    else:
        st.error(f"Error submitting request: {error_msg}")
```

This provides clear user feedback when sequence errors occur.

## Best Practices Summary

1. **Never manually specify primary key IDs in insert operations**
2. **Use the `fix_sequence.py` script to diagnose issues**
3. **After bulk data operations, check and reset sequences if needed**
4. **Monitor error logs for sequence-related errors**
5. **Keep backups before making schema changes**

## Quick Reference: Fix All Sequences

If you need to fix all sequences at once, run this SQL:

```sql
-- Fix request_competition_form sequence
SELECT setval('request_competition_form_form_id_seq', 
    COALESCE((SELECT MAX(form_id) FROM request_competition_form), 0) + 1, false);

-- Fix club_enrollment_form sequence  
SELECT setval('club_enrollment_form_form_id_seq',
    COALESCE((SELECT MAX(form_id) FROM club_enrollment_form), 0) + 1, false);

-- Fix club sequence
SELECT setval('club_club_id_seq',
    COALESCE((SELECT MAX(club_id) FROM club), 0) + 1, false);

-- Fix account sequence
SELECT setval('account_account_id_seq',
    COALESCE((SELECT MAX(account_id) FROM account), 0) + 1, false);
```

## Schema Issue Note

⚠️ **Schema Design Flaw:** The `request_competition_form` table has `reviewer_word` and `reviewed_by` marked as `NOT NULL`, but these should be nullable for pending forms. This is a design issue that should be addressed:

```sql
-- Recommended schema fix (run in Supabase SQL Editor):
ALTER TABLE request_competition_form 
ALTER COLUMN reviewer_word DROP NOT NULL,
ALTER COLUMN reviewed_by DROP NOT NULL;
```

Until this is fixed, the code uses placeholder values:
- `reviewer_word`: "Pending review"
- `reviewed_by`: 0 (may cause foreign key issues)
