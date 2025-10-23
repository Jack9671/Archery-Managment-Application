-- ============================================
-- ARCHERY DATABASE - COMPREHENSIVE TEST DATA
-- ============================================

-- Clear existing data (optional - comment out if you want to keep existing data)
-- TRUNCATE TABLE account CASCADE;

-- ============================================
-- 1. ACCOUNTS (Various roles)
-- ============================================

-- Admin Account
INSERT INTO account ( email_address, hash_password, fullname, country, date_of_birth, sex, role, created_at, updated_at)
VALUES 
('admin1@archery.com.au', 'admin1@archery.com.au', 'Sarah Johnson', 'Australia', '1985-03-15', 'female', 'admin', NOW(), NOW());

-- Australia Archery Federation Members
INSERT INTO account ( email_address, hash_password, fullname, country, date_of_birth, sex, role, created_at, updated_at)
VALUES 
('federation1@archery.com.au', 'federation1@archery.com.au', 'Michael Thompson', 'Australia', '1978-07-22', 'male', 'australia_archery_federation', NOW(), NOW()),
('federation2@archery.com.au', 'federation2@archery.com.au', 'Emma Davis', 'Australia', '1982-11-30', 'female', 'australia_archery_federation', NOW(), NOW());

-- Recorders
INSERT INTO account ( email_address, hash_password, fullname, country, date_of_birth, sex, role, created_at, updated_at)
VALUES 
('recorder1@archery.com.au', 'recorder1@archery.com.au', 'David Chen', 'Australia', '1990-05-12', 'male', 'recorder', NOW(), NOW()),
('recorder2@archery.com.au', 'recorder2@archery.com.au', 'Lisa Martinez', 'Australia', '1988-09-25', 'female', 'recorder', NOW(), NOW()),
('recorder3@archery.com.au', 'recorder3@archery.com.au', 'James Anderson', 'Australia', '1992-02-18', 'male', 'recorder', NOW(), NOW());

-- Archers
INSERT INTO account ( email_address, hash_password, fullname, country, date_of_birth, sex, role, created_at, updated_at)
VALUES 
('archer1@email.com', 'archer1@email.com', 'Oliver Brown', 'Australia', '2000-06-15', 'male', 'archer', NOW(), NOW()),
( 'archer2@email.com', 'archer2@email.com', 'Sophie Taylor', 'Australia', '1998-03-22', 'female', 'archer', NOW(), NOW()),
( 'archer3@email.com', 'archer3@email.com', 'Liam Harris', 'Australia', '2002-11-30', 'male', 'archer', NOW(), NOW()),
( 'archer4@email.com', 'archer4@email.com', 'Isabella White', 'Australia', '1995-08-17', 'female', 'archer', NOW(), NOW()),
( 'archer5@email.com', 'archer5@email.com', 'Noah Clark', 'Australia', '2003-04-05', 'male', 'archer', NOW(), NOW()),
( 'archer6@email.com', 'archer6@email.com', 'Mia Lewis', 'Australia', '1997-12-28', 'female', 'archer', NOW(), NOW()),
( 'archer7@email.com', 'archer7@email.com', 'William Lee', 'Australia', '2001-07-14', 'male', 'archer', NOW(), NOW()),
( 'archer8@email.com', 'archer8@email.com', 'Charlotte Walker', 'Australia', '1999-01-20', 'female', 'archer', NOW(), NOW()),
( 'archer9@email.com', 'archer9@email.com', 'Jack Robinson', 'Australia', '2004-09-08', 'male', 'archer', NOW(), NOW()),
( 'archer10@email.com', 'archer10@email.com', 'Amelia Young', 'Australia', '1996-05-25', 'female', 'archer', NOW(), NOW());

-- ============================================
-- 2. ROLE-SPECIFIC TABLES
-- ============================================

INSERT INTO admin (admin_id, created_at) VALUES (1, NOW());

INSERT INTO australia_archery_federation (member_id, created_at) VALUES (2, NOW()), (3, NOW());

INSERT INTO recorder (recorder_id, year_of_experience, about_recorder)
VALUES 
(4, 8, 'Experienced recorder specializing in outdoor target archery. Certified level 3 judge.'),
(5, 5, 'Passionate about field archery competitions. Detail-oriented and reliable.'),
(6, 3, 'New to recording but enthusiastic. Background in sports management.');

-- ============================================
-- 3. EQUIPMENT
-- ============================================

INSERT INTO equipment ( name, description, created_at)
VALUES 
( 'Recurve Bow', 'Olympic-style recurve bow, officially recognized by World Archery and Australian Archery Federation', NOW()),
( 'Compound Bow', 'Modern compound bow with cams and pulleys for mechanical advantage', NOW()),
( 'Barebow', 'Traditional bow without sights or stabilizers, shooting instinctively', NOW()),
( 'Longbow', 'Traditional English longbow, straight-limbed design', NOW()),
( 'Crossbow', 'Horizontal bow mounted on a stock, used in specialized competitions', NOW());

-- ============================================
-- 4. ARCHERS (with equipment)
-- ============================================

INSERT INTO archer (archer_id, default_equipment_id, club_id, level, about_archer)
VALUES 
(4, 1, NULL, 'advanced (>= 6 years of experience)', 'Recorder who also competes occasionally'),
(5, 2, NULL, 'semi-advanced (>= 4 years of experience )', 'Recorder with compound bow experience'),
(6, 1, NULL, 'intermediate (>= 2 year of experience )', 'Recorder and recreational archer'),
(7, 1, NULL, 'intermediate (>= 2 year of experience )', 'Competitive recurve archer aiming for national championships'),
(8, 1, NULL, 'semi-advanced (>= 4 years of experience )', 'Specializing in outdoor target archery. Former junior champion.'),
(9, 2, NULL, 'beginner (< 1 year of expereince)', 'Just started with compound bow. Excited to compete!'),
(10, 2, NULL, 'advanced (>= 6 years of experience)', 'Compound archer with strong technical skills and consistent scoring'),
(11, 3, NULL, 'semi-intermediate (>= 1 year of experience)', 'Traditional barebow shooter, love the challenge'),
(12, 1, NULL, 'intermediate (>= 2 year of experience )', 'Recurve archer balancing work and training'),
(13, 2, NULL, 'semi-advanced (>= 4 years of experience )', 'Compound specialist focusing on indoor competitions'),
(14, 1, NULL, 'advanced (>= 6 years of experience)', 'Experienced recurve archer, enjoy mentoring beginners'),
(15, 3, NULL, 'beginner (< 1 year of expereince)', 'New to barebow, learning traditional techniques'),
(16, 2, NULL, 'professional (>= 10 year of experience)', 'Professional compound archer with national titles');


-- ============================================
-- 5. CLUBS
-- ============================================

INSERT INTO club ( name, creator_id, min_age_to_join, max_age_to_join, open_to_join, about_club, club_logo_url, created_at, updated_at)
VALUES 
('Sydney Archery Club', 7, 12, 70, true, 'Premier archery club in Sydney offering training for all skill levels. We have indoor and outdoor ranges.', 'https://ghcpcyvethwdzzgyymfp.supabase.co/storage/v1/object/public/User%20Avatar/Club_Logo/sydney_club.jpg', NOW(), NOW()),
('Melbourne Arrows', 10, 10, 75, true, 'Friendly community club focused on outdoor target archery and field archery.', 'https://ghcpcyvethwdzzgyymfp.supabase.co/storage/v1/object/public/User%20Avatar/Club_Logo/melbourne_club.jpg', NOW(), NOW()),
('Brisbane Bowmen', 14, 15, 65, true, 'Competitive club with strong junior development program.', 'https://ghcpcyvethwdzzgyymfp.supabase.co/storage/v1/object/public/User%20Avatar/Club_Logo/brisbane_club.jpg', NOW(), NOW()),
('Perth Precision Archers', 16, 18, 70, false, 'Elite club for advanced archers. Membership by application only.', 'https://ghcpcyvethwdzzgyymfp.supabase.co/storage/v1/object/public/User%20Avatar/Club_Logo/perth_club.jpg', NOW(), NOW());

-- Update archers with club memberships
UPDATE archer SET club_id = 1 WHERE archer_id IN (7, 8, 9);
UPDATE archer SET club_id = 2 WHERE archer_id IN (10, 11, 12);
UPDATE archer SET club_id = 3 WHERE archer_id IN (13, 14);
UPDATE archer SET club_id = 4 WHERE archer_id IN (15, 16);

-- ============================================
-- 6. DISCIPLINES
-- ============================================

INSERT INTO discipline ( name, description, created_at)
VALUES 
('Outdoor Target Archery', 'Shooting at fixed stationary targets outdoors at known distances. Standard World Archery format.', NOW()),
( 'Indoor Target Archery', 'Precision shooting indoors at 18m or 25m distances with smaller target faces.', NOW()),
('Field Archery', 'Moving through natural terrain courses with targets at various distances and angles.', NOW()),
('Clout Archery', 'Long-distance discipline shooting at ground targets with concentric scoring zones.', NOW()),
('Para-Archery', 'Archery for athletes with disabilities, with classifications and allowed adaptations.', NOW());

-- ============================================
-- 7. AGE DIVISIONS
-- ============================================

INSERT INTO age_division (min_age, max_age, created_at)
VALUES 
( 10, 14, NOW()),  -- Cub
( 15, 17, NOW()),  -- Junior
( 18, 20, NOW()),  -- Youth
( 21, 49, NOW()),  -- Adult
( 50, 59, NOW()),  -- Master
( 60, 70, NOW());  -- Senior Master

-- ============================================
-- 8. CATEGORIES (Discipline + Age + Equipment)
-- ============================================

INSERT INTO category (discipline_id, age_division_id, equipment_id, created_at)
VALUES 
-- Outdoor Target - All ages - Recurve
( 1, 1, 1, NOW()),
( 1, 2, 1, NOW()),
( 1, 3, 1, NOW()),
( 1, 4, 1, NOW()),
-- Outdoor Target - All ages - Compound
( 1, 1, 2, NOW()),
( 1, 2, 2, NOW()),
( 1, 3, 2, NOW()),
( 1, 4, 2, NOW()),
-- Indoor Target - Adults - Recurve
( 2, 4, 1, NOW()),
-- Indoor Target - Adults - Compound
(2, 4, 2, NOW()),
-- Field Archery - Adults - Barebow
( 3, 4, 3, NOW()),
-- Outdoor Target - Adults - Barebow
( 1, 4, 3, NOW());

-- ============================================
-- 9. TARGET FACES
-- ============================================

INSERT INTO target_face ( diameter, unit_of_length, created_at)
VALUES 
( 122, 'cm', NOW()),  -- Standard 122cm outdoor target
( 80, 'cm', NOW()),   -- 80cm outdoor target
( 40, 'cm', NOW()),   -- 40cm indoor target
( 60, 'cm', NOW());   -- 60cm target

-- ============================================
-- 10. RANGES
-- ============================================

INSERT INTO range (target_face_id, distance, unit_of_length, created_at)
VALUES 
(1, 70, 'm', NOW()),   -- 70m Olympic distance
( 1, 50, 'm', NOW()),   -- 50m distance
( 2, 30, 'm', NOW()),   -- 30m distance
( 3, 18, 'm', NOW()),   -- 18m indoor
( 1, 90, 'm', NOW()),   -- 90m long distance
( 4, 25, 'm', NOW());   -- 25m indoor

-- ============================================
-- 11. ROUNDS
-- ============================================

INSERT INTO round (name, category_id, created_at)
VALUES 
( 'Olympic Round (Outdoor Target Archery · 21-49 · Recurve Bow)', 4, NOW()),
( 'Youth Olympic Round (Outdoor Target Archery · 18-20 · Recurve Bow)', 3, NOW()),
( 'Compound 70m (Outdoor Target Archery · 21-49 · Compound Bow)', 8, NOW()),
( 'Indoor 18m (Indoor Target Archery · 21-49 · Recurve Bow)', 9, NOW()),
( 'Indoor 18m Compound (Indoor Target Archery · 21-49 · Compound Bow)', 10, NOW()),
( 'Field Round (Field Archery · 21-49 · Barebow)', 11, NOW()),
( 'Barebow 50m (Outdoor Target Archery · 21-49 · Barebow)', 12, NOW());

-- ============================================
-- 12. EQUIVALENT ROUNDS
-- ============================================

INSERT INTO equivalent_round (round_id, equivalent_round_id, date_valid_start, date_valud_end, created_at, updated_at)
VALUES 
(1, 2, '2024-01-01 00:00:00+00', '2025-12-31 23:59:59+00', NOW(), NOW()),
(2, 1, '2024-01-01 00:00:00+00', '2025-12-31 23:59:59+00', NOW(), NOW());

-- ============================================
-- 13. ELIGIBLE GROUPS OF CLUBS
-- ============================================

INSERT INTO eligible_group_of_club (eligible_group_of_club_id, created_at)
VALUES 
(1, NOW()),  -- Sydney Region Clubs
(2, NOW()),  -- National Clubs
(3, NOW());  -- Elite Clubs Only

INSERT INTO eligible_club_member (eligible_group_of_club_id, eligible_club_id, created_at)
VALUES 
(1, 1, NOW()),  -- Sydney Archery Club in Sydney Region
(2, 1, NOW()),  -- Sydney in National
(2, 2, NOW()),  -- Melbourne in National
(2, 3, NOW()),  -- Brisbane in National
(2, 4, NOW()),  -- Perth in National
(3, 4, NOW());  -- Perth Elite only

-- ============================================
-- 14. YEARLY CLUB CHAMPIONSHIPS
-- ============================================

INSERT INTO yearly_club_championship ( name, year, creator_id, eligible_group_of_club_id, created_at, updated_at)
VALUES 
('Australian National Championship 2025', 2025, 4, 2, NOW(), NOW()),
('Sydney Regional Championship 2025', 2025, 5, 1, NOW(), NOW());

-- ============================================
-- 15. CLUB COMPETITIONS
-- ============================================

INSERT INTO club_competition ( name, address, date_start, date_end, creator_id, eligible_group_of_club_id, created_at, updated_at)
VALUES 
('Summer Open Tournament', '123 Archery Lane, Sydney NSW 2000', '2025-01-15', '2025-01-17', 4, 2, NOW(), NOW()),
( 'Indoor Championship Round 1', '456 Sports Complex, Melbourne VIC 3000', '2025-02-20', '2025-02-20', 5, 2, NOW(), NOW()),
('Sydney Local Cup', '789 Range Road, Sydney NSW 2010', '2025-03-10', '2025-03-11', 6, 1, NOW(), NOW()),
('National Qualifier Stage 1', '321 Olympic Drive, Brisbane QLD 4000', '2025-04-05', '2025-04-07', 4, 2, NOW(), NOW()),
('Spring Field Archery Meet', '555 Forest Path, Perth WA 6000', '2025-05-12', '2025-05-13', 5, 3, NOW(), NOW());

-- ============================================
-- 16. EVENT CONTEXTS
-- ============================================

INSERT INTO event_context (yearly_club_championship_id, club_competition_id, round_id, range_id, end_order)
VALUES 
-- Competition 1 events (IDs 1-5)
(1, 1, 1, 1, 1),
(1, 1, 1, 1, 2),
(1, 1, 1, 1, 3),
(1, 1, 3, 2, 1),
(1, 1, 3, 2, 2),
-- Competition 2 events (IDs 6-8)
(NULL, 2, 4, 4, 1),
(NULL, 2, 4, 4, 2),
(NULL, 2, 4, 4, 3),
-- Competition 3 events (IDs 9-10)
(2, 3, 1, 1, 1),
(2, 3, 1, 1, 2),
-- Competition 4 events (IDs 11-12)
(1, 4, 1, 1, 1),
(1, 4, 3, 2, 1),
-- Competition 5 events (ID 13)
(NULL, 5, 6, 3, 1);

-- ============================================
-- 17. ROUND SCHEDULES
-- ============================================

INSERT INTO round_schedule (club_competition_id, round_id, datetime_to_start, datetime_to_end, created_at, updated_at)
VALUES 
(1, 1, '2025-01-15 09:00:00+00', '2025-01-15 12:00:00+00', NOW(), NOW()),
(1, 3, '2025-01-15 14:00:00+00', '2025-01-15 17:00:00+00', NOW(), NOW()),
(2, 4, '2025-02-20 10:00:00+00', '2025-02-20 16:00:00+00', NOW(), NOW()),
(3, 1, '2025-03-10 09:00:00+00', '2025-03-10 15:00:00+00', NOW(), NOW()),
(4, 1, '2025-04-05 09:00:00+00', '2025-04-05 13:00:00+00', NOW(), NOW()),
(4, 3, '2025-04-06 09:00:00+00', '2025-04-06 13:00:00+00', NOW(), NOW()),
(5, 6, '2025-05-12 08:00:00+00', '2025-05-12 17:00:00+00', NOW(), NOW());

-- ============================================
-- 18. RECORDINGS (Recorders assigned to competitions)
-- ============================================

INSERT INTO recording (recording_id, yearly_club_championship_id, club_competition_id)
VALUES 
(4, 1, 1),
(4, 1, 4),
(5, NULL, 2),
(5, 2, 3),
(6, NULL, 5);

-- ============================================
-- 19. PARTICIPATING (Archer scores)
-- ============================================

INSERT INTO participating (participating_id, event_context_id, score_1st_arrow, score_2nd_arrow, score_3rd_arrow, score_4th_arrow, score_5st_arrow, score_6st_arrow, sum_score, type, status, created_at, updated_at)
VALUES 
-- Archer 7 in Competition 1
(7, 1, 9, 10, 9, 8, 10, 9, 55, 'competition', 'eligible', '2025-01-15 09:30:00+00', '2025-01-15 09:30:00+00'),
(7, 2, 10, 9, 9, 10, 8, 9, 55, 'competition', 'eligible', '2025-01-15 09:45:00+00', '2025-01-15 09:45:00+00'),
(7, 3, 8, 9, 10, 9, 9, 10, 55, 'competition', 'eligible', '2025-01-15 10:00:00+00', '2025-01-15 10:00:00+00'),
-- Archer 8 in Competition 1
(8, 1, 10, 10, 9, 10, 9, 10, 58, 'competition', 'eligible', '2025-01-15 09:30:00+00', '2025-01-15 09:30:00+00'),
(8, 2, 9, 10, 10, 9, 10, 9, 57, 'competition', 'eligible', '2025-01-15 09:45:00+00', '2025-01-15 09:45:00+00'),
(8, 3, 10, 9, 10, 10, 9, 9, 57, 'competition', 'eligible', '2025-01-15 10:00:00+00', '2025-01-15 10:00:00+00'),
-- Archer 10 in Competition 1 (compound)
(10, 4, 10, 10, 10, 9, 10, 10, 59, 'competition', 'eligible', '2025-01-15 14:30:00+00', '2025-01-15 14:30:00+00'),
(10, 5, 10, 9, 10, 10, 10, 9, 58, 'competition', 'eligible', '2025-01-15 14:45:00+00', '2025-01-15 14:45:00+00'),
-- Archer 12 in Competition 2 (indoor)
(12, 6, 10, 9, 10, 10, 9, 10, 58, 'competition', 'eligible', '2025-02-20 10:30:00+00', '2025-02-20 10:30:00+00'),
(12, 7, 9, 10, 9, 10, 10, 9, 57, 'competition', 'eligible', '2025-02-20 11:00:00+00', '2025-02-20 11:00:00+00'),
-- Archer 13 in Competition 2 (indoor compound)
(13, 6, 10, 10, 10, 10, 9, 10, 59, 'competition', 'eligible', '2025-02-20 10:30:00+00', '2025-02-20 10:30:00+00'),
(13, 7, 10, 10, 9, 10, 10, 10, 59, 'competition', 'eligible', '2025-02-20 11:00:00+00', '2025-02-20 11:00:00+00'),
-- Archer 14 in Competition 3
(14, 9, 10, 9, 10, 9, 10, 9, 57, 'competition', 'eligible', '2025-03-10 09:30:00+00', '2025-03-10 09:30:00+00'),
(14, 10, 9, 10, 10, 10, 9, 10, 58, 'competition', 'eligible', '2025-03-10 10:00:00+00', '2025-03-10 10:00:00+00'),
-- Archer 16 (professional) in Competition 4
(16, 12, 10, 10, 10, 10, 10, 9, 59, 'competition', 'eligible', '2025-04-06 09:30:00+00', '2025-04-06 09:30:00+00');

-- ============================================
-- 20. CATEGORY RATING PERCENTILES
-- ============================================

INSERT INTO category_rating_percentile (archer_id, category_id, percentile)
VALUES 
(7, 4, 65),   -- Adult Recurve
(8, 4, 78),   -- Adult Recurve
(9, 8, 15),   -- Adult Compound (beginner)
(10, 8, 85),  -- Adult Compound
(11, 12, 45), -- Barebow
(12, 4, 58),  -- Adult Recurve
(13, 10, 72), -- Indoor Compound
(14, 4, 82),  -- Adult Recurve
(15, 12, 20), -- Barebow (beginner)
(16, 8, 95);  -- Adult Compound (professional)

-- ============================================
-- 21. REQUEST FORMS
-- ============================================

-- Competition Request Forms
-- NOTE: All accounts 4-16 now exist in BOTH archer and recorder tables to satisfy dual FK constraints

INSERT INTO request_competition_form (sender_id, type, action, yearly_club_championship_id, club_competition_id, round_id, sender_word, status, reviewer_word, reviewed_by, created_at, updated_at)
VALUES 
-- Archers applying to participate
(7, 'participating', 'enrol', 1, 1, 1, 'I would like to participate in the Olympic Round. I have been training hard.', 'eligible', 'Application approved. Welcome!', 4, '2025-01-01 10:00:00+00', '2025-01-02 14:00:00+00'),
(8, 'participating', 'enrol', 1, 1, 2, 'Excited to compete! Ready for the challenge.', 'eligible', 'Approved. Good luck!', 4, '2025-01-01 11:00:00+00', '2025-01-02 14:05:00+00'),
(10, 'participating', 'enrol', 1, 1, 2, 'Applying for compound division.', 'eligible', 'Approved', 4, '2025-01-01 12:00:00+00', '2025-01-02 14:10:00+00'),
(9, 'participating', 'enrol', NULL, 2, 1, 'First indoor competition, looking forward to it!', 'pending', '', 5, '2025-02-10 09:00:00+00', '2025-02-10 09:00:00+00'),
-- Recorders applying to record
(6, 'recording', 'enrol', NULL, 5, 1, 'I would like to be the official recorder for this field archery event.', 'eligible', 'Welcome aboard!', 5, '2025-04-01 10:00:00+00', '2025-04-02 15:00:00+00'),
(4, 'recording', 'enrol', 2, 3, 2, 'I would like to record for the Sydney Local Cup', 'eligible', 'Approved!', 6, '2025-02-25 10:00:00+00', '2025-02-26 15:00:00+00');

-- Club Enrollment Forms
INSERT INTO club_enrollment_form (sender_id, sender_word, status, club_id, club_creator_word, created_at, updated_at)
VALUES 
(9, 'I am a beginner looking to join and learn from experienced archers.', 'eligible', 1, 'Welcome to Sydney Archery Club! We look forward to training with you.', '2024-12-01 10:00:00+00', '2024-12-03 14:00:00+00'),
(11, 'Interested in joining for barebow training opportunities.', 'eligible', 2, 'Approved! Welcome to Melbourne Arrows.', '2024-11-15 09:00:00+00', '2024-11-17 16:00:00+00'),
(15, 'Seeking high-level training and competition opportunities.', 'pending', 4, '', '2025-01-10 11:00:00+00', '2025-01-10 11:00:00+00');


-- ============================================
-- 25. ACCOUNT REPORTS
-- ============================================

INSERT INTO account_report (report_id, reporter_id, report_content, evidence_pdf_file_url, target_account_id, status, decision_made_by, created_at, updated_at)
VALUES 
(1, 8, 12, 'https://ghcpcyvethwdzzgyymfp.supabase.co/storage/v1/object/public/Reports/evidence_001.pdf', 15, 'pending', 1, '2025-01-18 14:30:00+00', '2025-01-18 14:30:00+00'),
(2, 10, 14, NULL, 9, 'ineligible', 1, '2025-01-10 09:00:00+00', '2025-01-12 16:00:00+00');


-- ============================================
-- 26. ADDITIONAL PARTICIPATING RECORDS (Practice)
-- ============================================

INSERT INTO participating (participating_id, event_context_id, score_1st_arrow, score_2nd_arrow, score_3rd_arrow, score_4th_arrow, score_5st_arrow, score_6st_arrow, sum_score, type, status, created_at, updated_at)
VALUES 
-- Practice rounds for various archers (using different event contexts to avoid duplicates)
(7, 2, 8, 9, 8, 9, 8, 7, 49, 'practice', 'eligible', '2024-12-20 10:00:00+00', '2024-12-20 10:00:00+00'),
(7, 3, 9, 8, 9, 8, 9, 9, 52, 'practice', 'eligible', '2024-12-22 10:00:00+00', '2024-12-22 10:00:00+00'),
(8, 2, 9, 10, 9, 9, 10, 8, 55, 'practice', 'eligible', '2024-12-21 14:00:00+00', '2024-12-21 14:00:00+00'),
(8, 3, 10, 9, 10, 9, 9, 10, 57, 'practice', 'eligible', '2024-12-23 14:00:00+00', '2024-12-23 14:00:00+00'),
(10, 5, 10, 10, 9, 10, 9, 10, 58, 'practice', 'eligible', '2024-12-15 11:00:00+00', '2024-12-15 11:00:00+00'),
(12, 7, 9, 9, 10, 9, 8, 9, 54, 'practice', 'eligible', '2025-02-10 13:00:00+00', '2025-02-10 13:00:00+00'),
(13, 7, 10, 9, 10, 10, 9, 10, 58, 'practice', 'eligible', '2025-02-11 13:00:00+00', '2025-02-11 13:00:00+00'),
(14, 10, 9, 10, 9, 10, 9, 9, 56, 'practice', 'eligible', '2025-02-28 10:00:00+00', '2025-02-28 10:00:00+00'),
(16, 12, 10, 10, 10, 9, 10, 10, 59, 'practice', 'eligible', '2025-03-25 09:00:00+00', '2025-03-25 09:00:00+00');

-- ============================================
-- 27. MORE COMPETITION EVENTS FOR TESTING
-- ============================================

-- Add more event contexts for comprehensive testing (IDs 14-22)
INSERT INTO event_context (yearly_club_championship_id, club_competition_id, round_id, range_id, end_order)
VALUES 
(1, 1, 1, 1, 4),
(1, 1, 1, 1, 5),
(1, 1, 1, 1, 6),
(NULL, 2, 4, 4, 4),
(NULL, 2, 4, 4, 5),
(2, 3, 1, 1, 3),
(2, 3, 1, 1, 4),
(1, 4, 1, 1, 2),
(1, 4, 1, 1, 3);

-- Add more participating records for these events
INSERT INTO participating (participating_id, event_context_id, score_1st_arrow, score_2nd_arrow, score_3rd_arrow, score_4th_arrow, score_5st_arrow, score_6st_arrow, sum_score, type, status, created_at, updated_at)
VALUES 
-- Archer 7 continuing competition 1
(7, 14, 9, 10, 9, 9, 8, 10, 55, 'competition', 'eligible', '2025-01-15 10:15:00+00', '2025-01-15 10:15:00+00'),
(7, 15, 10, 9, 9, 10, 9, 9, 56, 'competition', 'eligible', '2025-01-15 10:30:00+00', '2025-01-15 10:30:00+00'),
(7, 16, 9, 9, 10, 8, 10, 9, 55, 'competition', 'eligible', '2025-01-15 10:45:00+00', '2025-01-15 10:45:00+00'),
-- Archer 8 continuing competition 1
(8, 14, 10, 10, 9, 10, 9, 10, 58, 'competition', 'eligible', '2025-01-15 10:15:00+00', '2025-01-15 10:15:00+00'),
(8, 15, 9, 10, 10, 10, 9, 9, 57, 'competition', 'eligible', '2025-01-15 10:30:00+00', '2025-01-15 10:30:00+00'),
(8, 16, 10, 9, 10, 9, 10, 10, 58, 'competition', 'eligible', '2025-01-15 10:45:00+00', '2025-01-15 10:45:00+00'),
-- Archer 12 continuing competition 2
(12, 17, 9, 10, 9, 9, 10, 9, 56, 'competition', 'eligible', '2025-02-20 11:30:00+00', '2025-02-20 11:30:00+00'),
(12, 18, 10, 9, 10, 9, 9, 10, 57, 'competition', 'eligible', '2025-02-20 12:00:00+00', '2025-02-20 12:00:00+00'),
-- Archer 13 continuing competition 2
(13, 17, 10, 10, 10, 9, 10, 10, 59, 'competition', 'eligible', '2025-02-20 11:30:00+00', '2025-02-20 11:30:00+00'),
(13, 18, 10, 10, 10, 10, 9, 10, 59, 'competition', 'eligible', '2025-02-20 12:00:00+00', '2025-02-20 12:00:00+00'),
-- Archer 14 continuing competition 3
(14, 19, 10, 9, 10, 9, 10, 10, 58, 'competition', 'eligible', '2025-03-10 10:30:00+00', '2025-03-10 10:30:00+00'),
(14, 20, 9, 10, 9, 10, 9, 9, 56, 'competition', 'eligible', '2025-03-10 11:00:00+00', '2025-03-10 11:00:00+00'),
-- Additional archers in competition 4
(7, 11, 9, 9, 10, 8, 9, 9, 54, 'competition', 'eligible', '2025-04-05 09:30:00+00', '2025-04-05 09:30:00+00'),
(7, 21, 10, 9, 9, 9, 8, 10, 55, 'competition', 'eligible', '2025-04-05 09:45:00+00', '2025-04-05 09:45:00+00'),
(8, 11, 10, 10, 9, 10, 9, 9, 57, 'competition', 'eligible', '2025-04-05 09:30:00+00', '2025-04-05 09:30:00+00'),
(8, 21, 9, 10, 10, 9, 10, 10, 58, 'competition', 'eligible', '2025-04-05 09:45:00+00', '2025-04-05 09:45:00+00');

-- ============================================
-- 28. ADDITIONAL TEST SCENARIOS
-- ============================================

-- Add a deactivated account for testing
INSERT INTO account (account_id, email_address, hash_password, fullname, country, date_of_birth, sex, role, deactivated, created_at, updated_at)
VALUES 
(17, 'deactivated@email.com', 'deactivated@email.com', 'John Deactivated', 'Australia', '1994-04-10', 'male', 'archer', true, '2023-06-15 10:00:00+00', '2024-12-01 15:00:00+00');

INSERT INTO archer (archer_id, default_equipment_id, club_id, level, about_archer)
VALUES 
(17, 1, NULL, 'intermediate (>= 2 year of experience )', 'Former active member');

-- Add pending competition requests for testing approval workflow
INSERT INTO request_competition_form (sender_id, type, action, yearly_club_championship_id, club_competition_id, round_id, sender_word, status, reviewer_word, reviewed_by, created_at, updated_at)
VALUES 
(11, 'participating', 'enrol', 2, 3, 1, 'I would like to participate in the Sydney Local Cup', 'pending', '', 6, '2025-03-01 10:00:00+00', '2025-03-01 10:00:00+00'),
(13, 'participating', 'enrol', 1, 4, 1, 'Application for National Qualifier', 'in progress', 'Under review, will update soon', 4, '2025-03-20 14:00:00+00', '2025-03-22 09:00:00+00'),
(15, 'participating', 'enrol', NULL, 5, 2, 'Want to try field archery for the first time', 'ineligible', 'Sorry, this competition is for advanced archers only', 6, '2025-04-01 11:00:00+00', '2025-04-03 16:00:00+00'),
(5, 'recording', 'enrol', 1, 4, 2, 'Application to record National Qualifier', 'pending', '', 4, '2025-03-20 14:00:00+00', '2025-03-20 14:00:00+00');

-- Add more club enrollment forms with different statuses
INSERT INTO club_enrollment_form (sender_id, sender_word, status, club_id, club_creator_word, created_at, updated_at)
VALUES 
(13, 'Moving to Sydney area, would love to join!', 'in progress', 1, 'We are reviewing your application', '2025-02-15 09:00:00+00', '2025-02-16 14:00:00+00'),
(16, 'Looking for a more competitive environment', 'eligible', 4, 'Your credentials are excellent. Welcome!', '2024-10-01 10:00:00+00', '2024-10-05 15:00:00+00'),
(11, 'Interested in joining for weekend practice', 'ineligible', 4, 'Unfortunately, membership is currently full', '2025-01-20 11:00:00+00', '2025-01-22 16:00:00+00');



-- ============================================
-- 30. SUMMARY & VERIFICATION QUERIES
-- ============================================

-- The following queries can be used to verify the data:

-- SELECT COUNT(*) as total_accounts FROM account;
-- SELECT COUNT(*) as total_archers FROM archer;
-- SELECT COUNT(*) as total_clubs FROM club;
-- SELECT COUNT(*) as total_competitions FROM club_competition;
-- SELECT COUNT(*) as total_participations FROM participating;
-- SELECT COUNT(*) as total_friendships FROM friendship_link;
-- SELECT COUNT(*) as total_groups FROM "group";

-- Check competition schedules:
-- SELECT cc.name, rs.round_id, rs.datetime_to_start, rs.expected_datetime_to_end
-- FROM club_competition cc
-- JOIN round_schedule rs ON cc.club_competition_id = rs.club_competition_id
-- ORDER BY rs.datetime_to_start;

-- Check archer scores in competitions:
-- SELECT a.account_id, acc.fullname, p.event_context_id, p.sum_score, p.datetime
-- FROM participating p
-- JOIN archer a ON p.participating_id = a.archer_id
-- JOIN account acc ON a.archer_id = acc.account_id
-- WHERE p.type = 'competition'
-- ORDER BY p.datetime;

-- Check club memberships:
-- SELECT c.name as club_name, COUNT(a.archer_id) as member_count
-- FROM club c
-- LEFT JOIN archer a ON c.club_id = a.club_id
-- GROUP BY c.club_id, c.name;

-- ============================================
-- DATA INSERTION COMPLETE
-- ============================================
-- Total records created:
-- - 17 Accounts (1 admin, 2 federation, 3 recorders, 10 archers, 1 deactivated)
-- - 4 Clubs
-- - 5 Equipment types
-- - 5 Disciplines
-- - 6 Age divisions
-- - 12 Categories
-- - 4 Target faces
-- - 6 Ranges
-- - 7 Rounds
-- - 2 Yearly championships
-- - 5 Club competitions
-- - 22 Event contexts
-- - 50+ Participating records
-- - Multiple forms (competition, enrollment, friendship, group)
-- - Chat histories (person-to-person and group)
-- - AI conversation histories
-- - Friendship links and group memberships
-- ============================================