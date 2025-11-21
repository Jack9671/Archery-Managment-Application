--Policy 1
CREATE POLICY "Allow anyone to upload to User Uploaded bucket"
ON storage.objects
FOR INSERT
WITH CHECK (bucket_id = 'User Uploaded');