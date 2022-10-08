create table news(
    uuid text,
    full_text text NOT NULL,
    title text NOT NULL,
    post_dttm timestamp,
    url text NOT NULL UNIQUE,
    text_links text,
    processed_dttm timestamp,
    PRIMARY KEY (uuid)
);
CREATE INDEX ix_news_processed_dttm ON news (processed_dttm);


create table news_emb(
    uuid text,
    embedding_full_text real[] NOT NULL,
    embedding_title real[] NOT NULL,
    PRIMARY KEY (uuid)
);


create table news_roles_map(
    uuid text,
    role_id text,
    PRIMARY KEY (uuid, role_id)
);
CREATE INDEX ix_news_roles_map_role_id ON news_roles_map USING HASH (role_id);


create table roles(
    role_id text,
    role_desc text,
    role_embedding real[],
    PRIMARY KEY (role_id)
);
