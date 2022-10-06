create table news(
    uuid UUID,
    full_text text NOT NULL,
    title text NOT NULL,
    post_dttm timestamp,
    url text NOT NULL UNIQUE,
    role_ids integer[] NOT NULL,
    embedding_full_text integer[] NOT NULL,
    embedding_title integer[] NOT NULL,
    processed_dttm timestamp,
    PRIMARY KEY (uuid)
);

-- todo нужна ли?
create table news_roles_map(
    uuid UUID REFERENCES news,
    role_id int,
    PRIMARY KEY (uuid, role_id)
);

-- todo нужна ли?
create table roles(
    role_id int,
    role_desc text,
    role_embedding integer[]
    PRIMARY KEY (role_id)
);
