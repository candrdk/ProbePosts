CREATE VIEW rate_view AS
	SELECT user_id, post_id, rating FROM ratings;

CREATE OR REPLACE FUNCTION rate() 
RETURNS trigger AS $rate$
	DECLARE
    	existing_rating BOOL;
	BEGIN
    	-- If the user has already rated this post, we want to either update or delete the rating.
    	IF EXISTS (SELECT 1 FROM ratings WHERE post_id = NEW.post_id AND user_id = NEW.user_id) THEN
            SELECT rating INTO existing_rating FROM ratings WHERE post_id = NEW.post_id AND user_id = NEW.user_id;
            
            -- If same rating is passed, delete the rating
        	IF existing_rating = NEW.rating THEN
            	DELETE FROM ratings 
                WHERE post_id = NEW.post_id AND user_id = NEW.user_id;
            ELSE
            -- If a new rating is passed, update the rating
            	UPDATE ratings 
                SET rating = NEW.rating 
                WHERE post_id = NEW.post_id AND user_id = NEW.user_id;
			END IF;
		ELSE
        -- If the user has not rated this post, simply insert
        	INSERT INTO ratings (user_id, post_id, rating) 
            VALUES (NEW.user_id, NEW.post_id, NEW.rating);
        END IF;
        
        RETURN NULL;
    END;
$rate$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER rate 
	INSTEAD OF INSERT ON rate_view
    FOR EACH ROW EXECUTE FUNCTION rate();
