CREATE TABLE IF NOT EXISTS placement_drive_topics (
    id SERIAL PRIMARY KEY,
    placement_drive_id INTEGER NOT NULL REFERENCES placement_drives(id),
    topic_id INTEGER NOT NULL REFERENCES topics(id),
    round_id INTEGER REFERENCES recruitment_rounds(id),
    category VARCHAR(100) NOT NULL,
    scope_key VARCHAR(150) NOT NULL,
    source_message_id INTEGER REFERENCES raw_messages(id),
    CONSTRAINT uq_placement_drive_topic_scope
        UNIQUE (placement_drive_id, topic_id, scope_key)
);
