-- ============================================
-- ARCHERY DATABASE - COMPREHENSIVE TEST DATA
-- ============================================

-- Clear existing data (optional - comment out if you want to keep existing data)
-- TRUNCATE TABLE account CASCADE;

START TRANSACTION;
-- ============================================
-- 1. ACCOUNTS (Various roles)
-- ============================================

-- Admin Account
INSERT INTO account ( email_address, hash_password, fullname, country, date_of_birth, sex, role, deactivated, created_at, updated_at)
VALUES 
('admin1@archery.com.au', 'admin1@archery.com.au', 'Sarah Johnson', 'Australia', '1985-03-15', 'female', 'admin', false, NOW(), NOW());

-- Australia Archery Federation Members
INSERT INTO account ( email_address, hash_password, fullname, country, date_of_birth, sex, role, deactivated, created_at, updated_at)
VALUES 
('federation1@archery.com.au', 'federation1@archery.com.au', 'Michael Thompson', 'Australia', '1978-07-22', 'male', 'australia_archery_federation', false, NOW(), NOW()),
('federation2@archery.com.au', 'federation2@archery.com.au', 'Emma Davis', 'Australia', '1982-11-30', 'female', 'australia_archery_federation', false, NOW(), NOW());

-- Recorders
INSERT INTO account ( email_address, hash_password, fullname, country, date_of_birth, sex, role, deactivated, created_at, updated_at)
VALUES 
('recorder1@archery.com.au', 'recorder1@archery.com.au', 'David Chen', 'Australia', '1990-05-12', 'male', 'recorder', false, NOW(), NOW()),
('recorder2@archery.com.au', 'recorder2@archery.com.au', 'Lisa Martinez', 'Australia', '1988-09-25', 'female', 'recorder', false, NOW(), NOW()),
('recorder3@archery.com.au', 'recorder3@archery.com.au', 'James Anderson', 'Australia', '1992-02-18', 'male', 'recorder', false, NOW(), NOW());

-- Archers
INSERT INTO account ( email_address, hash_password, fullname, country, date_of_birth, sex, role, deactivated, created_at, updated_at)
VALUES 
('archer1@email.com', 'archer1@email.com', 'Oliver Brown', 'Australia', '2000-06-15', 'male', 'archer', false, NOW(), NOW()),
( 'archer2@email.com', 'archer2@email.com', 'Sophie Taylor', 'Australia', '1998-03-22', 'female', 'archer', false, NOW(), NOW()),
( 'archer3@email.com', 'archer3@email.com', 'Liam Harris', 'Australia', '2002-11-30', 'male', 'archer', false, NOW(), NOW()),
( 'archer4@email.com', 'archer4@email.com', 'Isabella White', 'Australia', '1995-08-17', 'female', 'archer', false, NOW(), NOW()),
( 'archer5@email.com', 'archer5@email.com', 'Noah Clark', 'Australia', '2003-04-05', 'male', 'archer', false, NOW(), NOW()),
( 'archer6@email.com', 'archer6@email.com', 'Mia Lewis', 'Australia', '1997-12-28', 'female', 'archer', false, NOW(), NOW()),
( 'archer7@email.com', 'archer7@email.com', 'William Lee', 'Australia', '2001-07-14', 'male', 'archer', false, NOW(), NOW()),
( 'archer8@email.com', 'archer8@email.com', 'Charlotte Walker', 'Australia', '1999-01-20', 'female', 'archer', false, NOW(), NOW()),
( 'archer9@email.com', 'archer9@email.com', 'Jack Robinson', 'Australia', '2004-09-08', 'male', 'archer', false, NOW(), NOW()),
( 'archer10@email.com', 'archer10@email.com', 'Amelia Young', 'Australia', '1996-05-25', 'female', 'archer', false, NOW(), NOW()),
( 'deactivated@email.com', 'deactivated@email.com', 'John Deactivated', 'Australia', '1994-04-10', 'male', 'archer', true, '2023-06-15 10:00:00+00', '2026-12-01 15:00:00+00');


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
(16, 2, NULL, 'professional (>= 10 year of experience)', 'Professional compound archer with national titles'),
(17, 1, NULL, 'intermediate (>= 2 year of experience )', 'Former active member');

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
-- 12. ELIGIBLE GROUPS OF CLUBS
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
-- 13. YEARLY CLUB CHAMPIONSHIPS
-- ============================================

INSERT INTO yearly_club_championship ( name, year, creator_id, eligible_group_of_club_id, created_at, updated_at)
VALUES 
('Australian National Championship 2026', 2026, 4, 2, NOW(), NOW()),
('Sydney Regional Championship 2026', 2026, 5, 1, NOW(), NOW());

-- ============================================
-- 14. CLUB COMPETITIONS
-- ============================================

INSERT INTO club_competition ( name, address, date_start, date_end, creator_id, eligible_group_of_club_id, created_at, updated_at)
VALUES 
('Summer Open Tournament', '123 Archery Lane, Sydney NSW 2000', '2026-01-15', '2026-01-17', 4, 2, NOW(), NOW()),
( 'Indoor Championship Round 1', '456 Sports Complex, Melbourne VIC 3000', '2026-02-20', '2026-02-20', 5, 2, NOW(), NOW()),
('Sydney Local Cup', '789 Range Road, Sydney NSW 2010', '2026-03-10', '2026-03-11', 6, 1, NOW(), NOW()),
('National Qualifier Stage 1', '321 Olympic Drive, Brisbane QLD 4000', '2026-04-05', '2026-04-07', 4, 2, NOW(), NOW()),
('Spring Field Archery Meet', '555 Forest Path, Perth WA 6000', '2026-05-12', '2026-05-13', 5, 3, NOW(), NOW());

-- ============================================
-- 15. EVENT CONTEXTS
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
(NULL, 5, 6, 3, 1),
-- Additional event contexts to satisfy event structure
(1, 1, 1, 1, 4),
(1, 1, 1, 1, 5),
(1, 1, 1, 1, 6),
(NULL, 2, 4, 4, 4),
(NULL, 2, 4, 4, 5),
(2, 3, 1, 1, 3),
(2, 3, 1, 1, 4),
(1, 4, 1, 1, 2),
(1, 4, 1, 1, 3);

-- ============================================
-- 16. ROUND SCHEDULES
-- ============================================

INSERT INTO round_schedule (club_competition_id, round_id, datetime_to_start, datetime_to_end, created_at, updated_at)
VALUES 
(1, 1, '2026-01-15 09:00:00+00', '2026-01-15 12:00:00+00', NOW(), NOW()),
(1, 3, '2026-01-15 14:00:00+00', '2026-01-15 17:00:00+00', NOW(), NOW()),
(2, 4, '2026-02-20 10:00:00+00', '2026-02-20 16:00:00+00', NOW(), NOW()),
(3, 1, '2026-03-10 09:00:00+00', '2026-03-10 15:00:00+00', NOW(), NOW()),
(4, 1, '2026-04-05 09:00:00+00', '2026-04-05 13:00:00+00', NOW(), NOW()),
(4, 3, '2026-04-06 09:00:00+00', '2026-04-06 13:00:00+00', NOW(), NOW()),
(5, 6, '2026-05-12 08:00:00+00', '2026-05-12 17:00:00+00', NOW(), NOW());

-- ============================================
-- 17. RECORDINGS (Recorders assigned to competitions)
-- ============================================
-- RULE: If a recorder records for a yearly_club_championship, they must record for ALL club competitions within that championship

INSERT INTO recording (recording_id, yearly_club_championship_id, club_competition_id, created_at)
VALUES 
-- Recorder 4 records for Yearly Championship 1, which includes competitions 1 and 4
(4, 1, 1, NOW()),
(4, 1, 4, NOW()),
-- Recorder 5 records for standalone competition 2 (not part of any championship)
(5, NULL, 2, NOW()),
-- Recorder 5 also records for Yearly Championship 2, which includes competition 3
(5, 2, 3, NOW()),
-- Recorder 6 records for standalone competition 5 (not part of any championship)
(6, NULL, 5, NOW());

-- ============================================
-- 18. PARTICIPATING (Archer scores)
-- ============================================
-- RULE: If an archer participates in a yearly_club_championship round, they participate in that round across ALL competitions in the championship
-- Event Context Mapping:
--   Championship 1 -> Competitions 1 & 4
--     - Competition 1: event_context 1-5 (Round 1: contexts 1-3, Round 3: contexts 4-5)
--     - Competition 4: event_context 11-12, 21-22 (Round 1: contexts 11, 21-22, Round 3: context 12)
--   Championship 2 -> Competition 3
--     - Competition 3: event_context 9-10, 19-20 (Round 1 only)
--   Standalone Competition 2: event_context 6-8, 17-18 (Round 4)
--   Standalone Competition 5: event_context 13 (Round 6)

INSERT INTO participating (participating_id, event_context_id, score_1st_arrow, score_2nd_arrow, score_3rd_arrow, score_4th_arrow, score_5th_arrow, score_6th_arrow, sum_score, type, status, created_at, updated_at)
VALUES 
-- Archer 7 in Championship 1, Round 1 (must appear in both competitions 1 and 4)
-- Competition 1, Round 1 (contexts 1, 2, 3)
(7, 1, 9, 10, 9, 8, 10, 9, 55, 'competition', 'eligible', '2026-01-15 09:30:00+00', '2026-01-15 09:30:00+00'),
(7, 2, 10, 9, 9, 10, 8, 9, 55, 'competition', 'eligible', '2026-01-15 09:45:00+00', '2026-01-15 09:45:00+00'),
(7, 3, 8, 9, 10, 9, 9, 10, 55, 'competition', 'eligible', '2026-01-15 10:00:00+00', '2026-01-15 10:00:00+00'),

-- Archer 8 in Championship 1, Round 1 (must appear in both competitions 1 and 4)
-- Competition 1, Round 1 (contexts 1, 2, 3)
(8, 1, 10, 10, 9, 10, 9, 10, 58, 'competition', 'eligible', '2026-01-15 09:30:00+00', '2026-01-15 09:30:00+00'),
(8, 2, 9, 10, 10, 9, 10, 9, 57, 'competition', 'eligible', '2026-01-15 09:45:00+00', '2026-01-15 09:45:00+00'),
(8, 3, 10, 9, 10, 10, 9, 9, 57, 'competition', 'eligible', '2026-01-15 10:00:00+00', '2026-01-15 10:00:00+00'),

-- Archer 10 in Championship 1, Round 3 (compound - must appear in both competitions 1 and 4)
-- Competition 1, Round 3 (contexts 4, 5)
(10, 4, 10, 10, 10, 9, 10, 10, 59, 'competition', 'eligible', '2026-01-15 14:30:00+00', '2026-01-15 14:30:00+00'),
(10, 5, 10, 9, 10, 10, 10, 9, 58, 'competition', 'eligible', '2026-01-15 14:45:00+00', '2026-01-15 14:45:00+00'),

-- Archer 12 in standalone Competition 2 (indoor) - Round 4
(12, 6, 10, 9, 10, 10, 9, 10, 58, 'competition', 'eligible', '2026-02-20 10:30:00+00', '2026-02-20 10:30:00+00'),
(12, 7, 9, 10, 9, 10, 10, 9, 57, 'competition', 'eligible', '2026-02-20 11:00:00+00', '2026-02-20 11:00:00+00'),

-- Archer 13 in standalone Competition 2 (indoor compound) - Round 4
(13, 6, 10, 10, 10, 10, 9, 10, 59, 'competition', 'eligible', '2026-02-20 10:30:00+00', '2026-02-20 10:30:00+00'),
(13, 7, 10, 10, 9, 10, 10, 10, 59, 'competition', 'eligible', '2026-02-20 11:00:00+00', '2026-02-20 11:00:00+00'),

-- Archer 14 in Championship 2, Round 1 (Competition 3 only)
(14, 9, 10, 9, 10, 9, 10, 9, 57, 'competition', 'eligible', '2026-03-10 09:30:00+00', '2026-03-10 09:30:00+00'),
(14, 10, 9, 10, 10, 10, 9, 10, 58, 'competition', 'eligible', '2026-03-10 10:00:00+00', '2026-03-10 10:00:00+00'),

-- Archer 16 (professional) in Championship 1, Round 3 (Competition 4)
(16, 12, 10, 10, 10, 10, 10, 9, 59, 'competition', 'eligible', '2026-04-06 09:30:00+00', '2026-04-06 09:30:00+00'),
-- Archer 7 continuing in Competition 1, Round 1 (Championship 1)
(7, 14, 9, 10, 9, 9, 8, 10, 55, 'competition', 'eligible', '2026-01-15 10:15:00+00', '2026-01-15 10:15:00+00'),
(7, 15, 10, 9, 9, 10, 9, 9, 56, 'competition', 'eligible', '2026-01-15 10:30:00+00', '2026-01-15 10:30:00+00'),
(7, 16, 9, 9, 10, 8, 10, 9, 55, 'competition', 'eligible', '2026-01-15 10:45:00+00', '2026-01-15 10:45:00+00'),

-- Archer 8 continuing in Competition 1, Round 1 (Championship 1)
(8, 14, 10, 10, 9, 10, 9, 10, 58, 'competition', 'eligible', '2026-01-15 10:15:00+00', '2026-01-15 10:15:00+00'),
(8, 15, 9, 10, 10, 10, 9, 9, 57, 'competition', 'eligible', '2026-01-15 10:30:00+00', '2026-01-15 10:30:00+00'),
(8, 16, 10, 9, 10, 9, 10, 10, 58, 'competition', 'eligible', '2026-01-15 10:45:00+00', '2026-01-15 10:45:00+00'),

-- Archer 12 continuing in standalone Competition 2, Round 4
(12, 17, 9, 10, 9, 9, 10, 9, 56, 'competition', 'eligible', '2026-02-20 11:30:00+00', '2026-02-20 11:30:00+00'),
(12, 18, 10, 9, 10, 9, 9, 10, 57, 'competition', 'eligible', '2026-02-20 12:00:00+00', '2026-02-20 12:00:00+00'),

-- Archer 13 continuing in standalone Competition 2, Round 4
(13, 17, 10, 10, 10, 9, 10, 10, 59, 'competition', 'eligible', '2026-02-20 11:30:00+00', '2026-02-20 11:30:00+00'),
(13, 18, 10, 10, 10, 10, 9, 10, 59, 'competition', 'eligible', '2026-02-20 12:00:00+00', '2026-02-20 12:00:00+00'),

-- Archer 14 continuing in Championship 2, Competition 3, Round 1
(14, 19, 10, 9, 10, 9, 10, 10, 58, 'competition', 'eligible', '2026-03-10 10:30:00+00', '2026-03-10 10:30:00+00'),
(14, 20, 9, 10, 9, 10, 9, 9, 56, 'competition', 'eligible', '2026-03-10 11:00:00+00', '2026-03-10 11:00:00+00'),

-- Archer 7 and 8 MUST also appear in Competition 4, Round 1 (they're in Championship 1)
(7, 11, 9, 9, 10, 8, 9, 9, 54, 'competition', 'eligible', '2026-04-05 09:30:00+00', '2026-04-05 09:30:00+00'),
(7, 21, 10, 9, 9, 9, 8, 10, 55, 'competition', 'eligible', '2026-04-05 09:45:00+00', '2026-04-05 09:45:00+00'),
(7, 22, 9, 10, 9, 9, 10, 9, 56, 'competition', 'eligible', '2026-04-05 10:00:00+00', '2026-04-05 10:00:00+00'),
(8, 11, 10, 10, 9, 10, 9, 9, 57, 'competition', 'eligible', '2026-04-05 09:30:00+00', '2026-04-05 09:30:00+00'),
(8, 21, 9, 10, 10, 9, 10, 10, 58, 'competition', 'eligible', '2026-04-05 09:45:00+00', '2026-04-05 09:45:00+00'),
(8, 22, 10, 9, 10, 10, 9, 9, 57, 'competition', 'eligible', '2026-04-05 10:00:00+00', '2026-04-05 10:00:00+00'),

-- Archer 10 MUST also appear in Competition 4, Round 3 (compound, Championship 1)
(10, 12, 10, 10, 9, 10, 10, 9, 58, 'competition', 'eligible', '2026-04-06 09:30:00+00', '2026-04-06 09:30:00+00'),

-- Practice rounds for various archers (using different event contexts to avoid duplicates)
(7, 2, 8, 9, 8, 9, 8, 7, 49, 'practice', 'eligible', '2026-12-20 10:00:00+00', '2026-12-20 10:00:00+00'),
(7, 3, 9, 8, 9, 8, 9, 9, 52, 'practice', 'eligible', '2026-12-22 10:00:00+00', '2026-12-22 10:00:00+00'),
(8, 2, 9, 10, 9, 9, 10, 8, 55, 'practice', 'eligible', '2026-12-21 14:00:00+00', '2026-12-21 14:00:00+00'),
(8, 3, 10, 9, 10, 9, 9, 10, 57, 'practice', 'eligible', '2026-12-23 14:00:00+00', '2026-12-23 14:00:00+00'),
(10, 5, 10, 10, 9, 10, 9, 10, 58, 'practice', 'eligible', '2026-12-15 11:00:00+00', '2026-12-15 11:00:00+00'),
(12, 7, 9, 9, 10, 9, 8, 9, 54, 'practice', 'eligible', '2026-02-10 13:00:00+00', '2026-02-10 13:00:00+00'),
(13, 7, 10, 9, 10, 10, 9, 10, 58, 'practice', 'eligible', '2026-02-11 13:00:00+00', '2026-02-11 13:00:00+00'),
(14, 10, 9, 10, 9, 10, 9, 9, 56, 'practice', 'eligible', '2026-02-28 10:00:00+00', '2026-02-28 10:00:00+00'),
(16, 12, 10, 10, 10, 9, 10, 10, 59, 'practice', 'eligible', '2026-03-25 09:00:00+00', '2026-03-25 09:00:00+00');


-- ============================================
-- 19. CATEGORY RATING PERCENTILES
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
-- 20. REQUEST FORMS
-- ============================================
-- RULE: When requesting to participate in a yearly_club_championship round, the archer participates in that round across ALL linked competitions
-- RULE: When requesting to record for a yearly_club_championship, the recorder records for ALL linked competitions

-- Competition Request Forms
-- NOTE: All accounts 4-16 now exist in BOTH archer and recorder tables to satisfy dual FK constraints

INSERT INTO request_competition_form (sender_id, type, action, yearly_club_championship_id, club_competition_id, round_id, sender_word, status, reviewer_word, reviewed_by, created_at, updated_at)
VALUES 
-- Archers applying to participate in Championship 1, Round 1 (will participate in BOTH competitions 1 and 4)
(7, 'participating', 'enrol', 1, NULL, 1, 'I would like to participate in Round 1 of Australian National Championship 2026. I have been training hard.', 'eligible', 'Application approved. You will compete in all competitions for this round. Welcome!', 4, '2026-01-01 10:00:00+00', '2026-01-02 14:00:00+00'),
(8, 'participating', 'enrol', 1, NULL, 1, 'Excited to compete in the National Championship Round 1! Ready for the challenge.', 'eligible', 'Approved. You will participate in all linked competitions. Good luck!', 4, '2026-01-01 11:00:00+00', '2026-01-02 14:05:00+00'),

-- Archer applying to participate in Championship 1, Round 3 (compound - will participate in BOTH competitions 1 and 4)
(10, 'participating', 'enrol', 1, NULL, 3, 'Applying for Round 3 compound division in the National Championship.', 'eligible', 'Approved for all competitions in Round 3', 4, '2026-01-01 12:00:00+00', '2026-01-02 14:10:00+00'),

-- Archer applying for standalone Competition 2 (not part of any championship)
(9, 'participating', 'enrol', NULL, 2, 4, 'First indoor competition, looking forward to it!', 'pending', '', 5, '2026-02-10 09:00:00+00', '2026-02-10 09:00:00+00'),

-- Recorder applying to record for standalone Competition 5
(6, 'recording', 'enrol', NULL, 5, NULL, 'I would like to be the official recorder for this field archery event.', 'eligible', 'Welcome aboard!', 5, '2026-04-01 10:00:00+00', '2026-04-02 15:00:00+00'),

-- Recorder applying to record for Championship 2 (will record for ALL competitions in this championship, which is just competition 3)
(5, 'recording', 'enrol', 2, NULL, NULL, 'I would like to record for the Sydney Regional Championship 2026', 'eligible', 'Approved! You will record for all competitions in this championship.', 6, '2026-02-25 10:00:00+00', '2026-02-26 15:00:00+00'),

-- Archer applying for Championship 2 (will participate in competition 3)
(11, 'participating', 'enrol', 2, NULL, 1, 'I would like to participate in the Sydney Regional Championship', 'pending', '', 6, '2026-03-01 10:00:00+00', '2026-03-01 10:00:00+00'),
-- Archer applying for Championship 1, Round 1 (will participate in competitions 1 and 4)
(13, 'participating', 'enrol', 1, NULL, 1, 'Application for National Championship Round 1', 'in progress', 'Under review, will update soon', 4, '2026-03-20 14:00:00+00', '2026-03-22 09:00:00+00'),
-- Archer applying for standalone competition 5
(15, 'participating', 'enrol', NULL, 5, 6, 'Want to try field archery for the first time', 'ineligible', 'Sorry, this competition is for advanced archers only', 6, '2026-04-01 11:00:00+00', '2026-04-03 16:00:00+00'),
-- Recorder applying to record for Championship 1 (will record for ALL competitions 1 and 4)
(5, 'recording', 'enrol', 1, NULL, NULL, 'Application to record for Australian National Championship 2026', 'pending', '', 4, '2026-03-20 14:00:00+00', '2026-03-20 14:00:00+00');
 
-- Club Enrollment Forms
INSERT INTO club_enrollment_form (sender_id, sender_word, status, club_id, club_creator_word, created_at, updated_at)
VALUES 
(9, 'I am a beginner looking to join and learn from experienced archers.', 'eligible', 1, 'Welcome to Sydney Archery Club! We look forward to training with you.', '2026-12-01 10:00:00+00', '2026-12-03 14:00:00+00'),
(11, 'Interested in joining for barebow training opportunities.', 'eligible', 2, 'Approved! Welcome to Melbourne Arrows.', '2026-11-15 09:00:00+00', '2026-11-17 16:00:00+00'),
(15, 'Seeking high-level training and competition opportunities.', 'pending', 4, '', '2026-01-10 11:00:00+00', '2026-01-10 11:00:00+00'),
(13, 'Moving to Sydney area, would love to join!', 'in progress', 1, 'We are reviewing your application', '2026-02-15 09:00:00+00', '2026-02-16 14:00:00+00'),
(16, 'Looking for a more competitive environment', 'eligible', 4, 'Your credentials are excellent. Welcome!', '2026-10-01 10:00:00+00', '2026-10-05 15:00:00+00'),
(11, 'Interested in joining for weekend practice', 'ineligible', 4, 'Unfortunately, membership is currently full', '2026-01-20 11:00:00+00', '2026-01-22 16:00:00+00');


-- ============================================
-- 21. ACCOUNT REPORTS
-- ============================================

INSERT INTO account_report (report_id, reporter_id, report_content, evidence_pdf_file_url, target_account_id, status, decision_made_by, created_at, updated_at)
VALUES 
(1, 8, 12, 'https://ghcpcyvethwdzzgyymfp.supabase.co/storage/v1/object/public/Reports/evidence_001.pdf', 15, 'pending', 1, '2026-01-18 14:30:00+00', '2026-01-18 14:30:00+00'),
(2, 10, 14, NULL, 9, 'ineligible', 1, '2026-01-10 09:00:00+00', '2026-01-12 16:00:00+00');



-- ============================================
-- 22. FRIENDSHIP LINKS
-- ============================================
-- Note: account_one_id must be < account_two_id to avoid duplicates

INSERT INTO friendship_link (account_one_id, account_two_id, created_at)
VALUES 
-- Archers in the same club (Sydney Archery Club: 7, 8, 9)
(7, 8, '2025-06-15 10:00:00+00'),
(7, 9, '2025-07-20 14:30:00+00'),
(8, 9, '2025-06-20 11:15:00+00'),
-- Archers in Melbourne Arrows (10, 11, 12)
(10, 11, '2025-05-10 09:00:00+00'),
(10, 12, '2025-05-12 16:45:00+00'),
(11, 12, '2025-05-15 13:20:00+00'),
-- Cross-club friendships
(7, 10, '2025-08-01 10:30:00+00'),  -- Sydney to Melbourne
(8, 13, '2025-09-05 15:00:00+00'),  -- Sydney to Brisbane
(9, 14, '2025-10-12 11:00:00+00'),  -- Sydney to Brisbane
-- Recorder friendships
(4, 5, '2024-03-15 09:00:00+00'),
(4, 6, '2024-04-20 14:00:00+00'),
-- Archers and recorders
(7, 4, '2025-07-01 10:00:00+00'),
(10, 5, '2025-08-15 13:30:00+00'),
-- Professional connections
(14, 16, '2025-11-01 16:00:00+00');  -- Brisbane elite archers

-- ============================================
-- 23. BLOCK LINKS
-- ============================================
-- Note: account_one_id must be < account_two_id to avoid duplicates

INSERT INTO block_link (account_one_id, account_two_id, created_at)
VALUES 
-- Some blocked relationships (due to conflicts or disagreements)
(9, 15, '2026-01-25 14:00:00+00'),   -- Beginner conflict
(11, 16, '2026-02-10 09:30:00+00'),  -- Club rivalry
(13, 17, '2026-03-05 11:00:00+00');  -- Issue with deactivated account

-- ============================================
-- 24. FRIENDSHIP REQUEST FORMS
-- ============================================

INSERT INTO friendship_request_form (sender_id, receiver_id, sender_word, status, created_at, updated_at)
VALUES 
-- Pending requests
(12, 14, 'Hi! I saw your great scores at the competition. Would love to connect and share tips!', 'pending', '2026-11-15 10:00:00+00', '2026-11-15 10:00:00+00'),
(15, 7, 'New to archery and looking to learn from experienced archers. Hope we can be friends!', 'pending', '2026-11-18 14:30:00+00', '2026-11-18 14:30:00+00'),
(6, 10, 'I record many competitions and would like to connect with more archers', 'pending', '2026-11-19 09:00:00+00', '2026-11-19 09:00:00+00'),
-- Approved requests (these led to friendship_link entries above)
(7, 8, 'Hey! Let us connect as club mates', 'accepted', '2025-06-14 09:00:00+00', '2025-06-15 10:00:00+00'),
(9, 7, 'Would love to train together!', 'accepted', '2025-07-19 10:00:00+00', '2025-07-20 14:30:00+00'),
(10, 11, 'Fellow Melbourne archer here. Let us be friends!', 'accepted', '2025-05-09 14:00:00+00', '2025-05-10 09:00:00+00'),
(7, 10, 'Met you at the nationals. Great shooting! Let us stay in touch.', 'accepted', '2025-07-31 16:00:00+00', '2025-08-01 10:30:00+00'),
-- Rejected requests
(16, 11, 'Looking to expand my network', 'rejected', '2026-02-08 10:00:00+00', '2026-02-09 15:00:00+00'),
(17, 8, 'Want to connect', 'rejected', '2026-01-10 11:00:00+00', '2026-01-12 09:00:00+00'),
-- pending requests
(13, 14, 'We should connect as Brisbane club members!', 'pending', '2026-11-10 13:00:00+00', '2026-11-12 10:00:00+00');

-- ============================================
-- 25. PERSON-TO-PERSON CHAT HISTORY
-- ============================================
-- Note: account_one_id must be < account_two_id to avoid duplicates

INSERT INTO person_to_person_chat_history (account_one_id, account_two_id, message_order, message, sender_id, created_at)
VALUES 
-- Conversation between archers 7 and 8 (same club)
(7, 8, 1, 'Hey! Ready for practice this weekend?', 7, '2026-11-15 18:00:00+00'),
(7, 8, 2, 'Absolutely! What time are you thinking?', 8, '2026-11-15 18:05:00+00'),
(7, 8, 3, 'How about 9 AM Saturday?', 7, '2026-11-15 18:07:00+00'),
(7, 8, 4, 'Perfect! See you then.', 8, '2026-11-15 18:10:00+00'),
(7, 8, 5, 'Don''t forget to bring extra arrows!', 7, '2026-11-15 18:12:00+00'),

-- Conversation between archers 10 and 11 (Melbourne club)
(10, 11, 1, 'Did you see the new competition announcement?', 10, '2026-11-16 10:00:00+00'),
(10, 11, 2, 'Yes! Are you planning to participate?', 11, '2026-11-16 10:15:00+00'),
(10, 11, 3, 'Definitely. It''s going to be a great opportunity.', 10, '2026-11-16 10:20:00+00'),
(10, 11, 4, 'Let''s train together next week to prepare', 11, '2026-11-16 10:25:00+00'),

-- Cross-club conversation between archers 7 and 10
(7, 10, 1, 'Great scores at the national championship!', 7, '2026-04-08 20:00:00+00'),
(7, 10, 2, 'Thanks! You did amazing too. That last end was incredible.', 10, '2026-04-08 20:15:00+00'),
(7, 10, 3, 'Appreciate it! Want to share some training tips sometime?', 7, '2026-04-08 20:30:00+00'),
(7, 10, 4, 'Sure! I''ll send you my practice routine.', 10, '2026-04-08 20:45:00+00'),

-- Conversation between archer and recorder (7 and 4)
(4, 7, 1, 'I''ll be recording your competition next month', 4, '2026-03-15 14:00:00+00'),
(4, 7, 2, 'Great! Looking forward to it.', 7, '2026-03-15 14:10:00+00'),
(4, 7, 3, 'Let me know if you need any specific score breakdowns', 4, '2026-03-15 14:15:00+00'),

-- Conversation between recorders 4 and 5
(4, 5, 1, 'How was the recording session yesterday?', 4, '2026-02-21 09:00:00+00'),
(4, 5, 2, 'Smooth! All scores recorded accurately. Had 50+ participants.', 5, '2026-02-21 09:30:00+00'),
(4, 5, 3, 'That''s impressive. Any issues with the new scoring system?', 4, '2026-02-21 10:00:00+00'),
(4, 5, 4, 'None at all. It''s working perfectly.', 5, '2026-02-21 10:15:00+00'),

-- Conversation between archers 8 and 9 (club mates)
(8, 9, 1, 'Welcome to the club! How are you finding it?', 8, '2026-12-04 16:00:00+00'),
(8, 9, 2, 'Thanks! Everyone has been really welcoming. Still learning the basics.', 9, '2026-12-04 16:10:00+00'),
(8, 9, 3, 'If you need any help with your form, just ask!', 8, '2026-12-04 16:15:00+00'),
(8, 9, 4, 'That would be awesome! Maybe we can practice together?', 9, '2026-12-04 16:20:00+00'),

-- Conversation between archers 14 and 16 (elite level)
(14, 16, 1, 'Congratulations on your latest title!', 14, '2026-11-02 19:00:00+00'),
(14, 16, 2, 'Thank you! The competition was tough this year.', 16, '2026-11-02 19:30:00+00'),
(14, 16, 3, 'Your technique in the finals was flawless', 14, '2026-11-02 20:00:00+00'),
(14, 16, 4, 'Years of practice! Keep up your great work too.', 16, '2026-11-02 20:30:00+00');

-- ============================================
-- 26. PERSON-TO-PERSON OLD MESSAGE VISIBILITY
-- ============================================
-- This table tracks message deletions from a certain point BACKWARDS
-- When a user clicks "delete conversation" at message X, they delete from message 1 to X
-- Future messages (> X) remain visible
-- The message_order represents the LAST message deleted (all messages <= this number are deleted)

INSERT INTO person_to_person_old_message_visibility (account_one_id, account_two_id, message_order, account_one_viewable, account_two_viewable)
VALUES 
-- Conversation 7-8 (5 messages total): archer 7 deleted conversation when message 3 was latest (deleted 1,2,3; kept 4,5)
(7, 8, 1, false, true),
(7, 8, 2, false, true),
(7, 8, 3, false, true),
-- Messages 4 and 5 are still visible to archer 7 (no entries = default visible)

-- Conversation 10-11 (4 messages total): archer 11 deleted when message 2 was latest (deleted 1,2; kept 3,4)
(10, 11, 1, true, false),
(10, 11, 2, true, false),
-- Messages 3 and 4 are still visible to archer 11

-- Conversation 7-10 (4 messages total): archer 10 deleted when message 3 was latest (deleted 1,2,3; only message 4 remains)
(7, 10, 1, true, false),
(7, 10, 2, true, false),
(7, 10, 3, true, false),
-- Message 4 is still visible to archer 10

-- Conversation 4-5 (4 messages total): recorder 5 deleted when message 1 was latest (deleted only message 1; kept 2,3,4)
(4, 5, 1, true, false),
-- Messages 2, 3, 4 are still visible to recorder 5

-- Conversation 8-9 (4 messages total): archer 8 deleted entire conversation when message 4 was latest (deleted all 1,2,3,4)
(8, 9, 1, false, true),
(8, 9, 2, false, true),
(8, 9, 3, false, true),
(8, 9, 4, false, true),

-- Conversation 14-16 (4 messages total): both users deleted when message 2 was latest (both deleted 1,2; both can see 3,4)
(14, 16, 1, false, false),
(14, 16, 2, false, false);
-- Messages 3 and 4 are visible to both

-- Note: Messages not in this table default to visible for both parties
-- Conversation 4-7 (3 messages) has no deletions, so no entries needed
-- If new messages arrive after deletion, they will be visible (their message_order > deleted threshold)

COMMIT;

-- ============================================
-- 27. SUMMARY & VERIFICATION QUERIES
-- ============================================

-- The following queries can be used to verify the data:

-- SELECT COUNT(*) as total_accounts FROM account;
-- SELECT COUNT(*) as total_archers FROM archer;
-- SELECT COUNT(*) as total_clubs FROM club;
-- SELECT COUNT(*) as total_competitions FROM club_competition;
-- SELECT COUNT(*) as total_participations FROM participating;
-- SELECT COUNT(*) as total_friendships FROM friendship_link;
-- SELECT COUNT(*) as total_friend_requests FROM friendship_request_form;
-- SELECT COUNT(*) as total_chat_messages FROM person_to_person_chat_history;
-- SELECT COUNT(*) as total_blocks FROM block_link;
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

-- Check friendship connections:
-- SELECT acc1.fullname as person_1, acc2.fullname as person_2, fl.created_at
-- FROM friendship_link fl
-- JOIN account acc1 ON fl.account_one_id = acc1.account_id
-- JOIN account acc2 ON fl.account_two_id = acc2.account_id
-- ORDER BY fl.created_at DESC;

-- Check chat messages between friends:
-- SELECT acc1.fullname as sender, acc2.fullname as receiver, pch.message, pch.created_at
-- FROM person_to_person_chat_history pch
-- JOIN account acc1 ON pch.sender_id = acc1.account_id
-- JOIN account acc2 ON (pch.account_one_id = acc2.account_id OR pch.account_two_id = acc2.account_id) AND acc2.account_id != acc1.account_id
-- ORDER BY pch.created_at;

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
-- - 43 Participating records
-- - 15 Friendship links
-- - 3 Block links
-- - 10 Friendship request forms
-- - 30 Person-to-person chat messages
-- - 17 Message visibility records (demonstrating backward deletion pattern)
-- - 2 Account reports
-- - 6 club enrollment forms
--
-- ============================================
-- MESSAGE DELETION PATTERN:
-- ============================================
-- The person_to_person_old_message_visibility table demonstrates
-- backward deletion (deleting history up to a point):
-- - When a user deletes at message X, messages 1 through X are deleted
-- - Future messages (> X) remain visible
-- - New messages sent after deletion are always visible
-- 
-- Examples in sample data:
-- - Archer 7 deleted conversation with 8 up to message 3 (messages 4,5 still visible)
-- - Archer 11 deleted conversation with 10 up to message 2 (messages 3,4 still visible)
-- - Archer 8 deleted entire conversation with 9 up to message 4 (all deleted)
-- - Both archers 14 and 16 deleted up to message 2 (messages 3,4 visible to both)
--
-- ============================================
-- CONSISTENCY RULES ENFORCED:
-- ============================================
-- 1. YEARLY CHAMPIONSHIP STRUCTURE:
--    - Championship 1 (Australian National 2026) includes:
--      * Competition 1 (Summer Open Tournament)
--      * Competition 4 (National Qualifier Stage 1)
--    - Championship 2 (Sydney Regional 2026) includes:
--      * Competition 3 (Sydney Local Cup)
--
-- 2. PARTICIPATING TABLE CONSISTENCY:
--    - Archers who participate in a yearly_club_championship round
--      MUST have participating records in that round across ALL
--      competitions linked to that championship
--    - Example: Archer 7 in Championship 1, Round 1
--      → Has records in Competition 1, Round 1 (contexts 1,2,3,14,15,16)
--      → Has records in Competition 4, Round 1 (contexts 11,21,22)
--
-- 3. RECORDING TABLE CONSISTENCY:
--    - Recorders who record for a yearly_club_championship
--      MUST have recording records for ALL competitions
--      linked to that championship
--    - Example: Recorder 4 for Championship 1
--      → Has recording record for Competition 1
--      → Has recording record for Competition 4
--
-- 4. REQUEST FORMS CONSISTENCY:
--    - Participation requests with yearly_club_championship_id
--      have NULL club_competition_id (applies to all competitions)
--    - Recording requests with yearly_club_championship_id
--      have NULL club_competition_id (records all competitions)
--    - Standalone competition requests have NULL yearly_club_championship_id
-- ============================================
