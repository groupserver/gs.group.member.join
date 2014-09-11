SET CLIENT_ENCODING = 'UTF8';
SET CLIENT_MIN_MESSAGES = WARNING;
-- The subscription confirmation information
CREATE TABLE confirmation (
    email            TEXT                      NOT NULL,
    confirmation_id  TEXT                      NOT NULL,
    user_id          TEXT                      NOT NULL,
    group_id         TEXT                      NOT NULL,
    site_id          TEXT                      NOT NULL,
    created_date     TIMESTAMP WITH TIME ZONE  NOT NULL DEFAULT now(),
    response_date    TIMESTAMP WITH TIME ZONE  DEFAULT NULL, 
    FOREIGN KEY (email, user_id) REFERENCES user_email (email, user_id),
    PRIMARY KEY (email, confirmation_id)
);
