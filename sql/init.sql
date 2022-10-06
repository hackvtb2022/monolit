create table news(
    uuid text,
    full_text text NOT NULL,
    title text NOT NULL,
    post_dttm timestamp,
    url text NOT NULL UNIQUE,
    role_ids text[] NOT NULL,
    embedding_full_text real[] NOT NULL,
    embedding_title real[] NOT NULL,
    processed_dttm timestamp,
    PRIMARY KEY (uuid)
);

create table news_score(
    uuid text,
    role_id text,
    score real,
    processed_dttm timestamp,
    PRIMARY KEY (uuid, role_id, processed_dttm)
);
CREATE INDEX ix_news_score_uuid ON news_score USING HASH (uuid);
CREATE INDEX ix_news_score_uuid_role_id ON news_score (uuid, role_id);
CREATE INDEX ix_news_dttm ON news_score (processed_dttm);

-- todo нужна ли?
create table news_roles_map(
    uuid text,
    role_id text,
    PRIMARY KEY (uuid, role_id)
);

-- todo нужна ли?
create table roles(
    role_id text,
    role_desc text,
    role_embedding real[],
    PRIMARY KEY (role_id)
);
