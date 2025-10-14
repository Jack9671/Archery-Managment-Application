-- =====================================================
-- SUPABASE STORAGE POLICIES FOR "User Avatar" BUCKET
-- =====================================================
-- These policies allow public upload and access to the User Avatar bucket
-- Apply these in your Supabase Dashboard: Storage > Policies

-- OPTION 1: PUBLIC ACCESS (Easiest - Anyone can upload and view)
-- Use this for development or if you want open avatar uploads
-- =====================================================

-- Allow public INSERT (upload)
CREATE POLICY "Public Upload Access"
ON storage.objects FOR INSERT
TO public
WITH CHECK (bucket_id = 'User Avatar');

-- Allow public SELECT (view/download)
CREATE POLICY "Public Read Access"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'User Avatar');

-- Allow public UPDATE (overwrite)
CREATE POLICY "Public Update Access"
ON storage.objects FOR UPDATE
TO public
USING (bucket_id = 'User Avatar')
WITH CHECK (bucket_id = 'User Avatar');

-- Allow public DELETE (remove files)
CREATE POLICY "Public Delete Access"
ON storage.objects FOR DELETE
TO public
USING (bucket_id = 'User Avatar');


-- =====================================================
-- OPTION 2: AUTHENTICATED USERS ONLY (More Secure)
-- Only logged-in users can upload their own avatars
-- =====================================================

-- Allow authenticated users to upload
CREATE POLICY "Authenticated Upload Access"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'User Avatar');

-- Allow everyone to view avatars
CREATE POLICY "Public View Access"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'User Avatar');

-- Allow authenticated users to update their own files
CREATE POLICY "Authenticated Update Own Files"
ON storage.objects FOR UPDATE
TO authenticated
USING (bucket_id = 'User Avatar')
WITH CHECK (bucket_id = 'User Avatar');


-- =====================================================
-- OPTION 3: USER-SPECIFIC ACCESS (Most Secure)
-- Users can only manage their own avatar files
-- Requires authentication and proper user context
-- =====================================================

-- Allow users to upload their own avatars
CREATE POLICY "Users Upload Own Avatar"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'User Avatar' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Allow everyone to view all avatars
CREATE POLICY "Public View All Avatars"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'User Avatar');

-- Allow users to update only their own avatars
CREATE POLICY "Users Update Own Avatar"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'User Avatar' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Allow users to delete only their own avatars
CREATE POLICY "Users Delete Own Avatar"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'User Avatar' AND
  (storage.foldername(name))[1] = auth.uid()::text
);


-- =====================================================
-- HOW TO APPLY THESE POLICIES
-- =====================================================
-- 
-- METHOD 1: Using Supabase Dashboard (Recommended)
-- 1. Go to https://supabase.com/dashboard
-- 2. Select your project
-- 3. Navigate to: Storage → Policies
-- 4. Click on "User Avatar" bucket
-- 5. Click "New Policy"
-- 6. Choose "Create a new policy from scratch"
-- 7. Copy and paste one of the policy sets above
-- 8. Click "Review" then "Save Policy"
--
-- METHOD 2: Using SQL Editor
-- 1. Go to SQL Editor in Supabase Dashboard
-- 2. Create a new query
-- 3. Copy and paste the desired OPTION (1, 2, or 3)
-- 4. Click "Run"
--
-- METHOD 3: Disable RLS (NOT RECOMMENDED for production)
-- 1. Go to Storage → Configuration
-- 2. Find "User Avatar" bucket
-- 3. Toggle OFF "RLS Enabled"
--
-- =====================================================
-- QUICK FIX FOR DEVELOPMENT
-- =====================================================
-- If you just want to get it working quickly for development:
-- Run this in SQL Editor to make the bucket fully public:

ALTER TABLE storage.objects DISABLE ROW LEVEL SECURITY;

-- WARNING: This disables security for ALL storage buckets!
-- Only use this temporarily for development.
-- 
-- To re-enable later:
-- ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;
--
-- =====================================================

-- =====================================================
-- VERIFY YOUR POLICIES
-- =====================================================
-- Run this to see all current policies on storage.objects:

SELECT 
  policyname,
  roles,
  cmd,
  qual,
  with_check
FROM pg_policies
WHERE tablename = 'objects' 
  AND schemaname = 'storage';

-- =====================================================
-- DROP POLICIES (if you need to remove them)
-- =====================================================
-- Replace "Policy_Name" with the actual policy name

-- DROP POLICY "Public Upload Access" ON storage.objects;
-- DROP POLICY "Public Read Access" ON storage.objects;
-- DROP POLICY "Public Update Access" ON storage.objects;
-- DROP POLICY "Public Delete Access" ON storage.objects;
