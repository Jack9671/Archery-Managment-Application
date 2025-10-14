-- Those are rules, Web team does not need to call them as they are automatically applied to DB

    --RULE1: score is only betweeen 0 and 10, and sum score is between 0 and 60 inclusively

  ALTER TABLE participant_score
ADD CONSTRAINT check_all_scores_range
CHECK (
  score_1st_arrow BETWEEN 0 AND 10 AND
  score_2nd_arrow BETWEEN 0 AND 10 AND
  score_3rd_arrow BETWEEN 0 AND 10 AND
  score_4th_arrow BETWEEN 0 AND 10 AND
  score_5st_arrow BETWEEN 0 AND 10 AND
  score_6st_arrow BETWEEN 0 AND 10 AND
  sum_score       BETWEEN 0 AND 60
);


  -- RULE1: When year of a yearly_club_championship row is updated, all competition.date_start and competition.date_end for competitions that are linked to that championship (via event_context) will have their year part changed to the new year, preserving month/day when possible. (If the original date was Feb 29 and the new year is not a leap year, it will become Feb 28.)

-- ===== propagate championship YEAR changes to linked competitions =====
-- Helper: Adjust a date to a new year, preserving month/day (if invalid day e.g. Feb 29 -> last day of Feb).
CREATE OR REPLACE FUNCTION adjust_date_year(orig_date date, new_year int)
RETURNS date AS $$
DECLARE
  m int := EXTRACT(MONTH FROM orig_date)::int;
  d int := EXTRACT(DAY FROM orig_date)::int;
  last_d int;
BEGIN
  SELECT EXTRACT(DAY FROM (make_date(new_year, m, 1) + INTERVAL '1 month' - INTERVAL '1 day'))::int INTO last_d;
  IF d > last_d THEN
    d := last_d;
  END IF;
  RETURN make_date(new_year, m, d);
END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- Trigger function: After year changed on yearly_club_championship, update linked competitions'' dates
CREATE OR REPLACE FUNCTION trg_yearly_cc_year_update()
RETURNS trigger AS $$
BEGIN
  -- only do work if year actually changed
  IF NEW.year IS NULL OR NEW.year = OLD.year THEN
    RETURN NEW;
  END IF;

  UPDATE competition c
  SET
    date_start = adjust_date_year(c.date_start, NEW.year),
    date_end   = adjust_date_year(c.date_end,   NEW.year)
  WHERE c.competition_id IN (
    SELECT DISTINCT ec.competition_id
    FROM event_context ec
    WHERE ec.yearly_club_championship_id = NEW.yearly_club_championship_id
  );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger (fires AFTER UPDATE OF year)
DROP TRIGGER IF EXISTS yearly_cc_year_update_trg ON yearly_club_championship;
CREATE TRIGGER yearly_cc_year_update_trg
AFTER UPDATE OF year ON yearly_club_championship
FOR EACH ROW
EXECUTE FUNCTION trg_yearly_cc_year_update();

  --RULE2: If a competition is already linked to a non-NULL yearly_club_championship (via any event_context row), then you cannot insert or update competition.date_start or competition.date_end to a date with a year different from the parent championship year. Attempting to do so will raise an error.
  
  -- ===== block competition date changes that would mismatch parent''s year =====
CREATE OR REPLACE FUNCTION trg_competition_check_dates()
RETURNS trigger AS $$
DECLARE
  parent_year int;
  comp_id int := COALESCE(NEW.competition_id, OLD.competition_id);
BEGIN
  -- find parent year if competition is linked to any non-null yearly_club_championship
  SELECT yc.year
  INTO parent_year
  FROM event_context ec
  JOIN yearly_club_championship yc
    ON yc.yearly_club_championship_id = ec.yearly_club_championship_id
  WHERE ec.competition_id = comp_id
    AND ec.yearly_club_championship_id IS NOT NULL
  LIMIT 1;

  IF parent_year IS NULL THEN
    RETURN NEW; -- no parent -> rule does not apply
  END IF;

  -- ensure NEW.date_start and NEW.date_end have parent''s year
  IF EXTRACT(YEAR FROM NEW.date_start)::int <> parent_year
     OR EXTRACT(YEAR FROM NEW.date_end)::int <> parent_year THEN
    RAISE EXCEPTION 'Competition %: date_start/date_end year must be % (parent championship).',
      comp_id, parent_year;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS competition_check_dates_trg ON competition;
CREATE TRIGGER competition_check_dates_trg
BEFORE INSERT OR UPDATE ON competition
FOR EACH ROW
EXECUTE FUNCTION trg_competition_check_dates();

  --RULE3:Any competition that has a parent (i.e. is referenced by an event_context row whose yearly_club_championship_id is NOT NULL) must have both date_start and date_end with year equal to that parent''s year. When linking (inserting/updating) an event_context to attach a competition to a parent, we check this and reject if mismatch.

-- ===== prevent linking a competition to a parent if competition dates'' years do not match parent''s year =====
CREATE OR REPLACE FUNCTION trg_event_context_enforce_parent_year()
RETURNS trigger AS $$
DECLARE
  parent_year int;
  comp_start_year int;
  comp_end_year int;
BEGIN
  -- if this event_context row has no parent, this rule doesn''t apply
  IF NEW.yearly_club_championship_id IS NULL THEN
    RETURN NEW;
  END IF;

  -- fetch parent year
  SELECT year INTO parent_year
  FROM yearly_club_championship
  WHERE yearly_club_championship_id = NEW.yearly_club_championship_id;

  IF parent_year IS NULL THEN
    RAISE EXCEPTION 'yearly_club_championship % not found', NEW.yearly_club_championship_id;
  END IF;

  -- fetch competition''s date years
  SELECT EXTRACT(YEAR FROM date_start)::int, EXTRACT(YEAR FROM date_end)::int
    INTO comp_start_year, comp_end_year
  FROM competition
  WHERE competition_id = NEW.competition_id;

  IF comp_start_year IS NULL OR comp_end_year IS NULL THEN
    RAISE EXCEPTION 'competition % not found', NEW.competition_id;
  END IF;

  IF comp_start_year <> parent_year OR comp_end_year <> parent_year THEN
    RAISE EXCEPTION 'Cannot link competition % to yearly_club_championship %: competition date years (% / %) must equal parent year (%).',
      NEW.competition_id, NEW.yearly_club_championship_id, comp_start_year, comp_end_year, parent_year;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS event_context_enforce_parent_year_trg ON event_context;
CREATE TRIGGER event_context_enforce_parent_year_trg
BEFORE INSERT OR UPDATE ON event_context
FOR EACH ROW
EXECUTE FUNCTION trg_event_context_enforce_parent_year();


   --RULE1: YYYY in date_start == YYYY in date_end of same competition.

ALTER TABLE competition
ADD CONSTRAINT chk_competition_same_year
CHECK (EXTRACT(YEAR FROM date_start) = EXTRACT(YEAR FROM date_end));



    /*RULE1: when status of a form has been set to "eligible", there are 2 cases.
    Case 1: If type is "enrol", then insert.
    Case 2: If type is "withdraw", then delete. 
    The tables that will be affected together are archer table, recorder table, and participant_score table. 
    Particularly, Case 1: automatically insert a new row in participant_score table or recorder table depending on role attribute. If role is recorder, then add new row of recorder with given competition_id and round_id. If role is participant, then automatically generate N new rows in participant_score. N is the total number of rows sharing same given competition_id and round_id.
                  Case 2: automatically delete N rows in participant_score table or recorder table depending on role attribute. If role is recorder, then delete new row of recorder with given competition_id and round_id. If role is participant, then automatically delete N existing rows in participant_score. N is the total number of rows sharing same given competition_id and round_id.
    */
-- Trigger function for Rule 1: when request_form.status becomes ''eligible''
CREATE OR REPLACE FUNCTION trg_request_form_status_to_eligible()
RETURNS trigger AS $$
BEGIN
  -- Only act when status transitions to ''eligible'' from something else
  IF NEW.status = 'eligible' AND (OLD.status IS DISTINCT FROM 'eligible') THEN

    -- CASE: ENROL
    IF NEW.type = 'enrol' THEN

      -- Subcase: recorder role -> insert a recorder row (avoid duplicates)
      IF NEW.role = 'recorder' THEN
        INSERT INTO recorder (recorder_id, competition_id, round_id)
        VALUES (NEW.account_id, NEW.competition_id, NEW.round_id)
        ON CONFLICT DO NOTHING;
      END IF;

      -- Subcase: participant role -> insert participant row AND create N participant_score rows
      IF NEW.role = 'participant' THEN

        INSERT INTO participant_score (
          participant_id,
          event_context_id,
          score_1st_arrow,
          score_2nd_arrow,
          score_3rd_arrow,
          score_4th_arrow,
          score_5st_arrow,
          score_6st_arrow,
          sum_score,
          datetime,
          type,
          status
        )
        SELECT
          NEW.account_id AS participant_id,
          ec.event_context_id,
          0, 0, 0, 0, 0, 0,         -- six arrow scores
          0 AS sum_score,
          now() AT TIME ZONE 'UTC' AS datetime,
          'competition'::type_participant_score_enum AS type,
          'pending'::status_enum AS status
        FROM event_context ec
        WHERE ec.competition_id = NEW.competition_id
          AND ec.round_id = NEW.round_id
        ON CONFLICT (participant_id, event_context_id) DO NOTHING;
      END IF;

    ELSIF NEW.type = 'withdraw' THEN
      -- CASE: WITHDRAW

      -- Subcase: recorder role -> delete recorder row(s) matching
      IF NEW.role = 'recorder' THEN
        DELETE FROM recorder
        WHERE recorder_id = NEW.account_id
          AND competition_id = NEW.competition_id
          AND round_id = NEW.round_id;
      END IF;

      -- Subcase: participant role -> delete participant_score rows for matching event_contexts
      IF NEW.role = 'participant' THEN
        DELETE FROM participant_score ps
        WHERE ps.participant_id = NEW.account_id
          AND ps.event_context_id IN (
            SELECT ec.event_context_id
            FROM event_context ec
            WHERE ec.competition_id = NEW.competition_id
              AND ec.round_id = NEW.round_id
          );
      END IF;

    END IF; -- NEW.type

  END IF; -- status changed to eligible

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger: fires AFTER UPDATE OF status on request_form
DROP TRIGGER IF EXISTS request_form_status_to_eligible_trg ON request_form;
CREATE TRIGGER request_form_status_to_eligible_trg
AFTER UPDATE OF status ON request_form
FOR EACH ROW
EXECUTE FUNCTION trg_request_form_status_to_eligible();