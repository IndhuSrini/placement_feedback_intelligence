ALTER TABLE placement_drives
    ADD COLUMN IF NOT EXISTS batch VARCHAR(50);

ALTER TABLE placement_drives
    ADD COLUMN IF NOT EXISTS package VARCHAR(50);

ALTER TABLE raw_messages
    ADD COLUMN IF NOT EXISTS source_chat_id VARCHAR(100);

ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS preparation_category VARCHAR(100);

CREATE TABLE IF NOT EXISTS eligibility_source_messages (
    eligibility_id INTEGER NOT NULL REFERENCES eligibility_criteria(id),
    raw_message_id INTEGER NOT NULL REFERENCES raw_messages(id),
    PRIMARY KEY (eligibility_id, raw_message_id)
);

CREATE TABLE IF NOT EXISTS recruitment_round_source_messages (
    round_id INTEGER NOT NULL REFERENCES recruitment_rounds(id),
    raw_message_id INTEGER NOT NULL REFERENCES raw_messages(id),
    PRIMARY KEY (round_id, raw_message_id)
);

CREATE TABLE IF NOT EXISTS placement_drive_topic_source_messages (
    id SERIAL PRIMARY KEY,
    placement_drive_topic_id INTEGER NOT NULL
        REFERENCES placement_drive_topics(id),
    raw_message_id INTEGER NOT NULL REFERENCES raw_messages(id),
    CONSTRAINT uq_drive_topic_source_message
        UNIQUE (placement_drive_topic_id, raw_message_id)
);
