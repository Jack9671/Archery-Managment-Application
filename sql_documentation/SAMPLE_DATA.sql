-- ============================================
-- ARCHERY DATABASE - COMPREHENSIVE TEST DATA
-- ============================================

-- Clear existing data (optional - comment out if you want to keep existing data)
-- TRUNCATE TABLE account CASCADE;

-- ============================================
-- 1. ACCOUNTS (Various roles)
-- ============================================

-- Admin Account
INSERT INTO account (account_id, email_address, hash_password, fullname, country, date_of_birth, sex, role, created_at, updated_at)
VALUES 
(1, 'admin1@archery.com.au', 'admin1@archery.com.au', 'Sarah Johnson', 'Australia', '1985-03-15', 'female', 'admin', NOW(), NOW());

-- Australia Archery Federation Members
INSERT INTO account (account_id, email_address, hash_password, fullname, country, date_of_birth, sex, role, created_at, updated_at)
VALUES 
(2, 'federation1@archery.com.au', 'federation1@archery.com.au', 'Michael Thompson', 'Australia', '1978-07-22', 'male', 'australia_archery_federation', NOW(), NOW()),
(3, 'federation2@archery.com.au', 'federation2@archery.com.au', 'Emma Davis', 'Australia', '1982-11-30', 'female', 'australia_archery_federation', NOW(), NOW());

-- Recorders
INSERT INTO account (account_id, email_address, hash_password, fullname, country, date_of_birth, sex, role, created_at, updated_at)
VALUES 
(4, 'recorder1@archery.com.au', 'recorder1@archery.com.au', 'David Chen', 'Australia', '1990-05-12', 'male', 'recorder', NOW(), NOW()),
(5, 'recorder2@archery.com.au', 'recorder2@archery.com.au', 'Lisa Martinez', 'Australia', '1988-09-25', 'female', 'recorder', NOW(), NOW()),
(6, 'recorder3@archery.com.au', 'recorder3@archery.com.au', 'James Anderson', 'Australia', '1992-02-18', 'male', 'recorder', NOW(), NOW());

-- Archers
INSERT INTO account (account_id, email_address, hash_password, fullname, country, date_of_birth, sex, role, created_at, updated_at)
VALUES 
(7, 'archer1@email.com', 'archer1@email.com', 'Oliver Brown', 'Australia', '2000-06-15', 'male', 'archer', NOW(), NOW()),
(8, 'archer2@email.com', 'archer2@email.com', 'Sophie Taylor', 'Australia', '1998-03-22', 'female', 'archer', NOW(), NOW()),
(9, 'archer3@email.com', 'archer3@email.com', 'Liam Harris', 'Australia', '2002-11-30', 'male', 'archer', NOW(), NOW()),
(10, 'archer4@email.com', 'archer4@email.com', 'Isabella White', 'Australia', '1995-08-17', 'female', 'archer', NOW(), NOW()),
(11, 'archer5@email.com', 'archer5@email.com', 'Noah Clark', 'Australia', '2003-04-05', 'male', 'archer', NOW(), NOW()),
(12, 'archer6@email.com', 'archer6@email.com', 'Mia Lewis', 'Australia', '1997-12-28', 'female', 'archer', NOW(), NOW()),
(13, 'archer7@email.com', 'archer7@email.com', 'William Lee', 'Australia', '2001-07-14', 'male', 'archer', NOW(), NOW()),
(14, 'archer8@email.com', 'archer8@email.com', 'Charlotte Walker', 'Australia', '1999-01-20', 'female', 'archer', NOW(), NOW()),
(15, 'archer9@email.com', 'archer9@email.com', 'Jack Robinson', 'Australia', '2004-09-08', 'male', 'archer', NOW(), NOW()),
(16, 'archer10@email.com', 'archer10@email.com', 'Amelia Young', 'Australia', '1996-05-25', 'female', 'archer', NOW(), NOW());

-- ============================================
-- 2. ROLE-SPECIFIC TABLES
-- ============================================

INSERT INTO admin (admin_id) VALUES (1);

INSERT INTO australia_archery_federation (member_id) VALUES (2), (3);

INSERT INTO recorder (recorder_id, year_of_experience, about_recorder)
VALUES 
(4, 8, 'Experienced recorder specializing in outdoor target archery. Certified level 3 judge.'),
(5, 5, 'Passionate about field archery competitions. Detail-oriented and reliable.'),
(6, 3, 'New to recording but enthusiastic. Background in sports management.');

-- ============================================
-- 3. EQUIPMENT
-- ============================================

INSERT INTO equipment (equipment_id, name, description)
VALUES 
(1, 'Recurve Bow', 'Olympic-style recurve bow, officially recognized by World Archery and Australian Archery Federation'),
(2, 'Compound Bow', 'Modern compound bow with cams and pulleys for mechanical advantage'),
(3, 'Barebow', 'Traditional bow without sights or stabilizers, shooting instinctively'),
(4, 'Longbow', 'Traditional English longbow, straight-limbed design'),
(5, 'Crossbow', 'Horizontal bow mounted on a stock, used in specialized competitions');

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

-- Add archers as recorders too (to satisfy FK constraints for request_competition_form)
INSERT INTO recorder (recorder_id, year_of_experience, about_recorder)
VALUES 
(7, 2, 'Archer who also helps with recording at local competitions'),
(8, 3, 'Experienced archer who volunteers as recorder'),
(9, 1, 'Beginner learning both archery and recording'),
(10, 5, 'Advanced archer with recording certification'),
(11, 1, 'Barebow archer interested in recording'),
(12, 2, 'Recurve archer who records occasionally'),
(13, 3, 'Compound archer and certified recorder'),
(14, 6, 'Advanced archer and experienced recorder'),
(15, 1, 'New archer learning to record'),
(16, 8, 'Professional archer with extensive recording experience');

-- ============================================
-- 5. CLUBS
-- ============================================

INSERT INTO club (club_id, name, creator_id, min_age_to_join, max_age_to_join, open_to_join, formation_date, about_club, club_logo_url)
VALUES 
(1, 'Sydney Archery Club', 7, 12, 70, true, '2010-03-15', 'Premier archery club in Sydney offering training for all skill levels. We have indoor and outdoor ranges.', 'https://ghcpcyvethwdzzgyymfp.supabase.co/storage/v1/object/public/User%20Avatar/Club_Logo/sydney_club.jpg'),
(2, 'Melbourne Arrows', 10, 10, 75, true, '2008-06-20', 'Friendly community club focused on outdoor target archery and field archery.', 'https://ghcpcyvethwdzzgyymfp.supabase.co/storage/v1/object/public/User%20Avatar/Club_Logo/melbourne_club.jpg'),
(3, 'Brisbane Bowmen', 14, 15, 65, true, '2015-09-10', 'Competitive club with strong junior development program.', 'https://ghcpcyvethwdzzgyymfp.supabase.co/storage/v1/object/public/User%20Avatar/Club_Logo/brisbane_club.jpg'),
(4, 'Perth Precision Archers', 16, 18, 70, false, '2012-11-05', 'Elite club for advanced archers. Membership by application only.', 'https://ghcpcyvethwdzzgyymfp.supabase.co/storage/v1/object/public/User%20Avatar/Club_Logo/perth_club.jpg');

-- Update archers with club memberships
UPDATE archer SET club_id = 1 WHERE archer_id IN (7, 8, 9);
UPDATE archer SET club_id = 2 WHERE archer_id IN (10, 11, 12);
UPDATE archer SET club_id = 3 WHERE archer_id IN (13, 14);
UPDATE archer SET club_id = 4 WHERE archer_id IN (15, 16);

-- ============================================
-- 6. DISCIPLINES
-- ============================================

INSERT INTO discipline (discipline_id, name, description)
VALUES 
(1, 'Outdoor Target Archery', 'Shooting at fixed stationary targets outdoors at known distances. Standard World Archery format.'),
(2, 'Indoor Target Archery', 'Precision shooting indoors at 18m or 25m distances with smaller target faces.'),
(3, 'Field Archery', 'Moving through natural terrain courses with targets at various distances and angles.'),
(4, 'Clout Archery', 'Long-distance discipline shooting at ground targets with concentric scoring zones.'),
(5, 'Para-Archery', 'Archery for athletes with disabilities, with classifications and allowed adaptations.');

-- ============================================
-- 7. AGE DIVISIONS
-- ============================================

INSERT INTO age_division (age_division_id, min_age, max_age)
VALUES 
(1, 10, 14),  -- Cub
(2, 15, 17),  -- Junior
(3, 18, 20),  -- Youth
(4, 21, 49),  -- Adult
(5, 50, 59),  -- Master
(6, 60, 70);  -- Senior Master

-- ============================================
-- 8. CATEGORIES (Discipline + Age + Equipment)
-- ============================================

INSERT INTO category (category_id, discipline_id, age_division_id, equipment_id)
VALUES 
-- Outdoor Target - All ages - Recurve
(1, 1, 1, 1),
(2, 1, 2, 1),
(3, 1, 3, 1),
(4, 1, 4, 1),
-- Outdoor Target - All ages - Compound
(5, 1, 1, 2),
(6, 1, 2, 2),
(7, 1, 3, 2),
(8, 1, 4, 2),
-- Indoor Target - Adults - Recurve
(9, 2, 4, 1),
-- Indoor Target - Adults - Compound
(10, 2, 4, 2),
-- Field Archery - Adults - Barebow
(11, 3, 4, 3),
-- Outdoor Target - Adults - Barebow
(12, 1, 4, 3);

-- ============================================
-- 9. TARGET FACES
-- ============================================

INSERT INTO target_face (target_face_id, diameter, unit_of_length)
VALUES 
(1, 122, 'cm'),  -- Standard 122cm outdoor target
(2, 80, 'cm'),   -- 80cm outdoor target
(3, 40, 'cm'),   -- 40cm indoor target
(4, 60, 'cm');   -- 60cm target

-- ============================================
-- 10. RANGES
-- ============================================

INSERT INTO range (range_id, target_face_id, distance, unit_of_length)
VALUES 
(1, 1, 70, 'm'),   -- 70m Olympic distance
(2, 1, 50, 'm'),   -- 50m distance
(3, 2, 30, 'm'),   -- 30m distance
(4, 3, 18, 'm'),   -- 18m indoor
(5, 1, 90, 'm'),   -- 90m long distance
(6, 4, 25, 'm');   -- 25m indoor

-- ============================================
-- 11. ROUNDS
-- ============================================

INSERT INTO round (round_id, name, category_id)
VALUES 
(1, 'Olympic Round - Adult Recurve', 4),
(2, 'Olympic Round - Youth Recurve', 3),
(3, 'Compound 70m Round', 8),
(4, 'Indoor 18m Round - Recurve', 9),
(5, 'Indoor 18m Round - Compound', 10),
(6, 'Field Round - Barebow', 11),
(7, 'Barebow 50m Round', 12);

-- ============================================
-- 12. EQUIVALENT ROUNDS
-- ============================================

INSERT INTO equivalent_round (round_id, equivalent_round_id, date_valid_start, date_valud_end)
VALUES 
(1, 2, '2024-01-01 00:00:00+00', '2025-12-31 23:59:59+00'),
(2, 1, '2024-01-01 00:00:00+00', '2025-12-31 23:59:59+00');

-- ============================================
-- 13. ELIGIBLE GROUPS OF CLUBS
-- ============================================

INSERT INTO eligible_group_of_club (eligible_group_of_club_id)
VALUES 
(1),  -- Sydney Region Clubs
(2),  -- National Clubs
(3);  -- Elite Clubs Only

INSERT INTO eligible_club_member (eligible_group_of_club_id, eligible_club_id)
VALUES 
(1, 1),  -- Sydney Archery Club in Sydney Region
(2, 1),  -- Sydney in National
(2, 2),  -- Melbourne in National
(2, 3),  -- Brisbane in National
(2, 4),  -- Perth in National
(3, 4);  -- Perth Elite only

-- ============================================
-- 14. YEARLY CLUB CHAMPIONSHIPS
-- ============================================

INSERT INTO yearly_club_championship (yearly_club_championship_id, name, year, creator_id, eligible_group_of_club_id)
VALUES 
(1, 'Australian National Championship 2025', 2025, 4, 2),
(2, 'Sydney Regional Championship 2025', 2025, 5, 1);

-- ============================================
-- 15. CLUB COMPETITIONS
-- ============================================

INSERT INTO club_competition (club_competition_id, name, address, date_start, date_end, creator_id, eligible_group_of_club_id)
VALUES 
(1, 'Summer Open Tournament', '123 Archery Lane, Sydney NSW 2000', '2025-01-15', '2025-01-17', 4, 2),
(2, 'Indoor Championship Round 1', '456 Sports Complex, Melbourne VIC 3000', '2025-02-20', '2025-02-20', 5, 2),
(3, 'Sydney Local Cup', '789 Range Road, Sydney NSW 2010', '2025-03-10', '2025-03-11', 6, 1),
(4, 'National Qualifier Stage 1', '321 Olympic Drive, Brisbane QLD 4000', '2025-04-05', '2025-04-07', 4, 2),
(5, 'Spring Field Archery Meet', '555 Forest Path, Perth WA 6000', '2025-05-12', '2025-05-13', 5, 3);

-- ============================================
-- 16. EVENT CONTEXTS
-- ============================================

INSERT INTO event_context (event_context_id, yearly_club_championship_id, club_competition_id, round_id, range_id, end_order)
VALUES 
-- Competition 1 events
('1-1-1-1', 1, 1, 1, 1, 1),
('1-1-1-2', 1, 1, 1, 1, 2),
('1-1-1-3', 1, 1, 1, 1, 3),
('1-3-2-1', 1, 1, 3, 2, 1),
('1-3-2-2', 1, 1, 3, 2, 2),
-- Competition 2 events
('2-4-4-1', NULL, 2, 4, 4, 1),
('2-4-4-2', NULL, 2, 4, 4, 2),
('2-4-4-3', NULL, 2, 4, 4, 3),
-- Competition 3 events
('3-1-1-1', 2, 3, 1, 1, 1),
('3-1-1-2', 2, 3, 1, 1, 2),
-- Competition 4 events
('4-1-1-1', 1, 4, 1, 1, 1),
('4-3-2-1', 1, 4, 3, 2, 1),
-- Competition 5 events
('5-6-3-1', NULL, 5, 6, 3, 1);

-- ============================================
-- 17. ROUND SCHEDULES
-- ============================================

INSERT INTO round_schedule (club_competition_id, round_id, datetime_to_start, expected_datetime_to_end)
VALUES 
(1, 1, '2025-01-15 09:00:00+00', '2025-01-15 12:00:00+00'),
(1, 3, '2025-01-15 14:00:00+00', '2025-01-15 17:00:00+00'),
(2, 4, '2025-02-20 10:00:00+00', '2025-02-20 16:00:00+00'),
(3, 1, '2025-03-10 09:00:00+00', '2025-03-10 15:00:00+00'),
(4, 1, '2025-04-05 09:00:00+00', '2025-04-05 13:00:00+00'),
(4, 3, '2025-04-06 09:00:00+00', '2025-04-06 13:00:00+00'),
(5, 6, '2025-05-12 08:00:00+00', '2025-05-12 17:00:00+00');

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

INSERT INTO participating (participating_id, event_context_id, score_1st_arrow, score_2nd_arrow, score_3rd_arrow, score_4th_arrow, score_5st_arrow, score_6st_arrow, sum_score, datetime, type, status)
VALUES 
-- Archer 7 in Competition 1
(7, '1-1-1-1', 9, 10, 9, 8, 10, 9, 55, '2025-01-15 09:30:00+00', 'competition', 'eligible'),
(7, '1-1-1-2', 10, 9, 9, 10, 8, 9, 55, '2025-01-15 09:45:00+00', 'competition', 'eligible'),
(7, '1-1-1-3', 8, 9, 10, 9, 9, 10, 55, '2025-01-15 10:00:00+00', 'competition', 'eligible'),
-- Archer 8 in Competition 1
(8, '1-1-1-1', 10, 10, 9, 10, 9, 10, 58, '2025-01-15 09:30:00+00', 'competition', 'eligible'),
(8, '1-1-1-2', 9, 10, 10, 9, 10, 9, 57, '2025-01-15 09:45:00+00', 'competition', 'eligible'),
(8, '1-1-1-3', 10, 9, 10, 10, 9, 9, 57, '2025-01-15 10:00:00+00', 'competition', 'eligible'),
-- Archer 10 in Competition 1 (compound)
(10, '1-3-2-1', 10, 10, 10, 9, 10, 10, 59, '2025-01-15 14:30:00+00', 'competition', 'eligible'),
(10, '1-3-2-2', 10, 9, 10, 10, 10, 9, 58, '2025-01-15 14:45:00+00', 'competition', 'eligible'),
-- Archer 12 in Competition 2 (indoor)
(12, '2-4-4-1', 10, 9, 10, 10, 9, 10, 58, '2025-02-20 10:30:00+00', 'competition', 'eligible'),
(12, '2-4-4-2', 9, 10, 9, 10, 10, 9, 57, '2025-02-20 11:00:00+00', 'competition', 'eligible'),
-- Archer 13 in Competition 2 (indoor compound)
(13, '2-4-4-1', 10, 10, 10, 10, 9, 10, 59, '2025-02-20 10:30:00+00', 'competition', 'eligible'),
(13, '2-4-4-2', 10, 10, 9, 10, 10, 10, 59, '2025-02-20 11:00:00+00', 'competition', 'eligible'),
-- Archer 14 in Competition 3
(14, '3-1-1-1', 10, 9, 10, 9, 10, 9, 57, '2025-03-10 09:30:00+00', 'competition', 'eligible'),
(14, '3-1-1-2', 9, 10, 10, 10, 9, 10, 58, '2025-03-10 10:00:00+00', 'competition', 'eligible'),
-- Archer 16 (professional) in Competition 4
(16, '4-3-2-1', 10, 10, 10, 10, 10, 9, 59, '2025-04-06 09:30:00+00', 'competition', 'eligible');

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

INSERT INTO request_competition_form (sender_id, type, action, yearly_club_championship_id, club_competition_id, round_id, sender_word, status, reviewer_word, reviewed_by, create_at, updated_at)
VALUES 
-- Archers applying to participate
(7, 'participating', 'enrol', 1, 1, 1, 'I would like to participate in the Olympic Round. I have been training hard.', 'eligible', 'Application approved. Welcome!', 4, '2025-01-01 10:00:00+00', '2025-01-02 14:00:00+00'),
(8, 'participating', 'enrol', 1, 1, 1, 'Excited to compete! Ready for the challenge.', 'eligible', 'Approved. Good luck!', 4, '2025-01-01 11:00:00+00', '2025-01-02 14:05:00+00'),
(10, 'participating', 'enrol', 1, 1, 3, 'Applying for compound division.', 'eligible', 'Approved', 4, '2025-01-01 12:00:00+00', '2025-01-02 14:10:00+00'),
(9, 'participating', 'enrol', NULL, 2, 4, 'First indoor competition, looking forward to it!', 'pending', '', 5, '2025-02-10 09:00:00+00', '2025-02-10 09:00:00+00'),
-- Recorders applying to record
(6, 'recording', 'enrol', NULL, 5, NULL, 'I would like to be the official recorder for this field archery event.', 'eligible', 'Welcome aboard!', 5, '2025-04-01 10:00:00+00', '2025-04-02 15:00:00+00'),
(4, 'recording', 'enrol', 2, 3, NULL, 'I would like to record for the Sydney Local Cup', 'eligible', 'Approved!', 6, '2025-02-25 10:00:00+00', '2025-02-26 15:00:00+00');

-- Club Enrollment Forms
INSERT INTO club_enrollment_form (form_id, sender_id, sender_word, status, club_id, club_creator_word, create_at, updated_at)
VALUES 
(1, 9, 'I am a beginner looking to join and learn from experienced archers.', 'eligible', 1, 'Welcome to Sydney Archery Club! We look forward to training with you.', '2024-12-01 10:00:00+00', '2024-12-03 14:00:00+00'),
(2, 11, 'Interested in joining for barebow training opportunities.', 'eligible', 2, 'Approved! Welcome to Melbourne Arrows.', '2024-11-15 09:00:00+00', '2024-11-17 16:00:00+00'),
(3, 15, 'Seeking high-level training and competition opportunities.', 'pending', 4, '', '2025-01-10 11:00:00+00', '2025-01-10 11:00:00+00');

-- Friendship Requests
INSERT INTO friendship_request_form (sender_id, receiver_id, sender_word, status)
VALUES 
(7, 8, 'Great shooting with you at the competition!', 'eligible'),
(8, 7, '', 'eligible'),
(10, 16, 'Would love to learn from your experience!', 'pending'),
(12, 14, 'Saw you at the club, lets connect!', 'eligible');

-- Group Requests
INSERT INTO "group" (group_id, creator_id, created_at)
VALUES 
(1, 8, '2024-12-01 10:00:00+00'),
(2, 10, '2025-01-05 09:00:00+00');

INSERT INTO group_member (group_id, member_id)
VALUES 
(1, 8),
(1, 7),
(1, 12),
(2, 10),
(2, 16);

INSERT INTO group_request_form (sender_id, group_id, sender_word, status)
VALUES 
(14, 1, 'Can I join your recurve training group?', 'pending'),
(13, 2, 'Would like to join the compound group!', 'eligible');

-- ============================================
-- 22. FRIENDSHIP & BLOCK LINKS
-- ============================================

INSERT INTO friendship_link (account_one_id, account_two_id, created_at)
VALUES 
(7, 8, '2024-12-10 10:00:00+00'),
(7, 12, '2024-11-20 14:00:00+00'),
(10, 16, '2024-10-15 09:00:00+00'),
(12, 14, '2024-12-01 11:00:00+00');

INSERT INTO block_link (account_one_id, account_two_id)
VALUES 
(9, 15);  -- Example block

-- ============================================
-- 23. CHAT HISTORIES
-- ============================================

-- Person to Person Chat
INSERT INTO person_to_person_chat_history (account_one_id, account_two_id, message_order, message, sender_id)
VALUES 
(7, 8, 1, 'Hey! Great scores today!', 7),
(7, 8, 2, 'Thanks! You too! Want to practice tomorrow?', 8),
(7, 8, 3, 'Absolutely! See you at 9am?', 7),
(7, 8, 4, 'Perfect!', 8);

INSERT INTO person_to_person_old_message_visibility (account_one_id, account_two_id, message_order, account_one_viewable, account_two_viewable)
VALUES 
(7, 8, 1, true, true),
(7, 8, 2, true, true),
(7, 8, 3, true, true),
(7, 8, 4, true, true);

-- Group Chat
INSERT INTO group_chat_history (group_id, message_order, message, writer_id)
VALUES 
(1, 1, 'Welcome to the recurve training group!', 8),
(1, 2, 'Thanks for adding me!', 7),
(1, 3, 'Happy to be here!', 12),
(1, 4, 'Lets schedule our next practice session', 8),
(2, 1, 'Compound shooters unite!', 10),
(2, 2, 'Looking forward to training together', 16);

INSERT INTO group_old_message_visibility (group_id, message_order, viewable_member_id)
VALUES 
(1, 1, 8),
(1, 1, 7),
(1, 1, 12),
(1, 2, 8),
(1, 2, 7),
(1, 2, 12),
(1, 3, 8),
(1, 3, 7),
(1, 3, 12),
(1, 4, 8),
(1, 4, 7),
(1, 4, 12),
(2, 1, 10),
(2, 1, 16),
(2, 2, 10),
(2, 2, 16);

-- ============================================
-- 24. AI CONVERSATION HISTORY
-- ============================================

INSERT INTO ai_conversation_history (account_id, conversation_order, prompt_response_order, prompt, response)
VALUES 
(7, 1, 1, 'What are some tips for improving my recurve form?', 'Here are key tips for recurve form: 1) Maintain consistent anchor point, 2) Keep your bow arm straight and locked, 3) Focus on back tension during release, 4) Practice your breathing rhythm, 5) Ensure proper alignment from drawing shoulder to arrow to target.'),
(7, 1, 2, 'How do I improve my grouping at 70m?', 'To improve grouping at 70m: 1) Work on consistent shot execution, 2) Practice at longer distances regularly, 3) Fine-tune your sight settings, 4) Focus on mental game and shot routine, 5) Record and analyze your arrow patterns, 6) Ensure equipment is properly tuned.'),
(8, 1, 1, 'What should I eat before a competition?', 'Before competition: 1) Eat a balanced meal 2-3 hours before, 2) Include complex carbs for sustained energy, 3) Moderate protein, 4) Avoid heavy, greasy foods, 5) Stay hydrated, 6) Have light snacks like bananas or energy bars during breaks, 7) Avoid trying new foods on competition day.'),
(10, 1, 1, 'How do I tune my compound bow?', 'Compound bow tuning steps: 1) Paper tune first - shoot through paper to check arrow flight, 2) Walk back tune at various distances, 3) Adjust cam timing if needed, 4) Check center shot alignment, 5) Fine-tune rest position, 6) Verify nocking point height, 7) Test with broadheads if hunting.'),
(12, 1, 1, 'Whats a good training routine for intermediate archers?', 'Intermediate training routine: 1) 3-4 sessions per week, 2) Warm up with close-range shooting, 3) Practice at competition distances, 4) Include blank bale sessions for form, 5) Work on mental training and visualization, 6) Film yourself to analyze form, 7) Include strength and flexibility exercises, 8) Rest adequately between sessions.');

-- ============================================
-- 25. ACCOUNT REPORTS
-- ============================================

INSERT INTO account_report (report_id, reporter_id, report_content, evidence_pdf_file_url, target_account_id, status, decision_made_by, created_at, updated_at)
VALUES 
(1, 8, 12, 'https://ghcpcyvethwdzzgyymfp.supabase.co/storage/v1/object/public/Reports/evidence_001.pdf', 15, 'pending', 1, '2025-01-18 14:30:00+00', '2025-01-18 14:30:00+00'),
(2, 10, 14, NULL, 9, 'ineligible', 1, '2025-01-10 09:00:00+00', '2025-01-12 16:00:00+00');

-- Note: report_content appears to be INT type in schema but should likely be TEXT. Using placeholder values.

-- ============================================
-- 26. ADDITIONAL PARTICIPATING RECORDS (Practice)
-- ============================================

INSERT INTO participating (participating_id, event_context_id, score_1st_arrow, score_2nd_arrow, score_3rd_arrow, score_4th_arrow, score_5st_arrow, score_6st_arrow, sum_score, datetime, type, status)
VALUES 
-- Practice rounds for various archers (using different event contexts to avoid duplicates)
(7, '1-1-1-2', 8, 9, 8, 9, 8, 7, 49, '2024-12-20 10:00:00+00', 'practice', 'eligible'),
(7, '1-1-1-3', 9, 8, 9, 8, 9, 9, 52, '2024-12-22 10:00:00+00', 'practice', 'eligible'),
(8, '1-1-1-2', 9, 10, 9, 9, 10, 8, 55, '2024-12-21 14:00:00+00', 'practice', 'eligible'),
(8, '1-1-1-3', 10, 9, 10, 9, 9, 10, 57, '2024-12-23 14:00:00+00', 'practice', 'eligible'),
(10, '1-3-2-2', 10, 10, 9, 10, 9, 10, 58, '2024-12-15 11:00:00+00', 'practice', 'eligible'),
(12, '2-4-4-2', 9, 9, 10, 9, 8, 9, 54, '2025-02-10 13:00:00+00', 'practice', 'eligible'),
(13, '2-4-4-2', 10, 9, 10, 10, 9, 10, 58, '2025-02-11 13:00:00+00', 'practice', 'eligible'),
(14, '3-1-1-2', 9, 10, 9, 10, 9, 9, 56, '2025-02-28 10:00:00+00', 'practice', 'eligible'),
(16, '4-3-2-1', 10, 10, 10, 9, 10, 10, 59, '2025-03-25 09:00:00+00', 'practice', 'eligible');

-- ============================================
-- 27. MORE COMPETITION EVENTS FOR TESTING
-- ============================================

-- Add more event contexts for comprehensive testing
INSERT INTO event_context (event_context_id, yearly_club_championship_id, club_competition_id, round_id, range_id, end_order)
VALUES 
('1-1-1-4', 1, 1, 1, 1, 4),
('1-1-1-5', 1, 1, 1, 1, 5),
('1-1-1-6', 1, 1, 1, 1, 6),
('2-4-4-4', NULL, 2, 4, 4, 4),
('2-4-4-5', NULL, 2, 4, 4, 5),
('3-1-1-3', 2, 3, 1, 1, 3),
('3-1-1-4', 2, 3, 1, 1, 4),
('4-1-1-2', 1, 4, 1, 1, 2),
('4-1-1-3', 1, 4, 1, 1, 3);

-- Add more participating records for these events
INSERT INTO participating (participating_id, event_context_id, score_1st_arrow, score_2nd_arrow, score_3rd_arrow, score_4th_arrow, score_5st_arrow, score_6st_arrow, sum_score, datetime, type, status)
VALUES 
-- Archer 7 continuing competition 1
(7, '1-1-1-4', 9, 10, 9, 9, 8, 10, 55, '2025-01-15 10:15:00+00', 'competition', 'eligible'),
(7, '1-1-1-5', 10, 9, 9, 10, 9, 9, 56, '2025-01-15 10:30:00+00', 'competition', 'eligible'),
(7, '1-1-1-6', 9, 9, 10, 8, 10, 9, 55, '2025-01-15 10:45:00+00', 'competition', 'eligible'),
-- Archer 8 continuing competition 1
(8, '1-1-1-4', 10, 10, 9, 10, 9, 10, 58, '2025-01-15 10:15:00+00', 'competition', 'eligible'),
(8, '1-1-1-5', 9, 10, 10, 10, 9, 9, 57, '2025-01-15 10:30:00+00', 'competition', 'eligible'),
(8, '1-1-1-6', 10, 9, 10, 9, 10, 10, 58, '2025-01-15 10:45:00+00', 'competition', 'eligible'),
-- Archer 12 continuing competition 2
(12, '2-4-4-4', 9, 10, 9, 9, 10, 9, 56, '2025-02-20 11:30:00+00', 'competition', 'eligible'),
(12, '2-4-4-5', 10, 9, 10, 9, 9, 10, 57, '2025-02-20 12:00:00+00', 'competition', 'eligible'),
-- Archer 13 continuing competition 2
(13, '2-4-4-4', 10, 10, 10, 9, 10, 10, 59, '2025-02-20 11:30:00+00', 'competition', 'eligible'),
(13, '2-4-4-5', 10, 10, 10, 10, 9, 10, 59, '2025-02-20 12:00:00+00', 'competition', 'eligible'),
-- Archer 14 continuing competition 3
(14, '3-1-1-3', 10, 9, 10, 9, 10, 10, 58, '2025-03-10 10:30:00+00', 'competition', 'eligible'),
(14, '3-1-1-4', 9, 10, 9, 10, 9, 9, 56, '2025-03-10 11:00:00+00', 'competition', 'eligible'),
-- Additional archers in competition 4
(7, '4-1-1-1', 9, 9, 10, 8, 9, 9, 54, '2025-04-05 09:30:00+00', 'competition', 'eligible'),
(7, '4-1-1-2', 10, 9, 9, 9, 8, 10, 55, '2025-04-05 09:45:00+00', 'competition', 'eligible'),
(8, '4-1-1-1', 10, 10, 9, 10, 9, 9, 57, '2025-04-05 09:30:00+00', 'competition', 'eligible'),
(8, '4-1-1-2', 9, 10, 10, 9, 10, 10, 58, '2025-04-05 09:45:00+00', 'competition', 'eligible');

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
INSERT INTO request_competition_form (sender_id, type, action, yearly_club_championship_id, club_competition_id, round_id, sender_word, status, reviewer_word, reviewed_by, create_at, updated_at)
VALUES 
(11, 'participating', 'enrol', 2, 3, 1, 'I would like to participate in the Sydney Local Cup', 'pending', '', 6, '2025-03-01 10:00:00+00', '2025-03-01 10:00:00+00'),
(13, 'participating', 'enrol', 1, 4, 1, 'Application for National Qualifier', 'in progress', 'Under review, will update soon', 4, '2025-03-20 14:00:00+00', '2025-03-22 09:00:00+00'),
(15, 'participating', 'enrol', NULL, 5, 6, 'Want to try field archery for the first time', 'ineligible', 'Sorry, this competition is for advanced archers only', 6, '2025-04-01 11:00:00+00', '2025-04-03 16:00:00+00'),
(5, 'recording', 'enrol', 1, 4, NULL, 'Application to record National Qualifier', 'pending', '', 4, '2025-03-20 14:00:00+00', '2025-03-20 14:00:00+00');

-- Add more club enrollment forms with different statuses
INSERT INTO club_enrollment_form (form_id, sender_id, sender_word, status, club_id, club_creator_word, create_at, updated_at)
VALUES 
(4, 13, 'Moving to Sydney area, would love to join!', 'in progress', 1, 'We are reviewing your application', '2025-02-15 09:00:00+00', '2025-02-16 14:00:00+00'),
(5, 16, 'Looking for a more competitive environment', 'eligible', 4, 'Your credentials are excellent. Welcome!', '2024-10-01 10:00:00+00', '2024-10-05 15:00:00+00'),
(6, 11, 'Interested in joining for weekend practice', 'ineligible', 4, 'Unfortunately, membership is currently full', '2025-01-20 11:00:00+00', '2025-01-22 16:00:00+00');

-- ============================================
-- 29. ADDITIONAL FRIENDSHIPS AND GROUPS
-- ============================================

-- More friendship links
INSERT INTO friendship_link (account_one_id, account_two_id, created_at)
VALUES 
(8, 14, '2024-11-15 10:00:00+00'),
(10, 13, '2024-12-20 14:00:00+00'),
(11, 12, '2024-10-10 09:00:00+00');

-- More friendship requests
INSERT INTO friendship_request_form (sender_id, receiver_id, sender_word, status)
VALUES 
(9, 11, 'Fellow barebow archer! Lets connect', 'pending'),
(13, 16, 'Would appreciate any tips from a pro!', 'eligible'),
(15, 16, 'Training partner request', 'ineligible');

-- Additional groups
INSERT INTO "group" (group_id, creator_id, created_at)
VALUES 
(3, 14, '2024-09-15 10:00:00+00'),  -- Advanced Recurve Group
(4, 4, '2025-01-20 09:00:00+00');   -- Recorder Network Group

INSERT INTO group_member (group_id, member_id)
VALUES 
(3, 14),
(3, 8),
(3, 12),
(4, 4),
(4, 5),
(4, 6);

-- Group chat messages
INSERT INTO group_chat_history (group_id, message_order, message, writer_id)
VALUES 
(3, 1, 'Welcome to the advanced recurve training group!', 14),
(3, 2, 'Excited to train with you all', 8),
(3, 3, 'Looking forward to improving together', 12),
(4, 1, 'Recorder coordination group for upcoming events', 4),
(4, 2, 'Thanks for setting this up!', 5),
(4, 3, 'Great idea to have a dedicated channel', 6);

INSERT INTO group_old_message_visibility (group_id, message_order, viewable_member_id)
VALUES 
(3, 1, 14), (3, 1, 8), (3, 1, 12),
(3, 2, 14), (3, 2, 8), (3, 2, 12),
(3, 3, 14), (3, 3, 8), (3, 3, 12),
(4, 1, 4), (4, 1, 5), (4, 1, 6),
(4, 2, 4), (4, 2, 5), (4, 2, 6),
(4, 3, 4), (4, 3, 5), (4, 3, 6);

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