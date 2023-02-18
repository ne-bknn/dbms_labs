CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    primary_language TEXT NOT NULL,
    is_private BOOLEAN NOT NULL,
    password TEXT NOT NULL
);
CREATE TABLE subscription (
    follower INTEGER NOT NULL,
    followee INTEGER NOT NULL,
    PRIMARY KEY (follower, followee),
    FOREIGN KEY(follower) REFERENCES user(id),
    FOREIGN KEY(followee) REFERENCES user(id)
);
CREATE TABLE post (
    id INTEGER AUTOINCREMENT NOT NULL UNIQUE,
    owner INTEGER NOT NULL,
    attachment INTEGER,
    text TEXT NOT NULL,
    comment_for INTEGER,
    repost_of INTEGER,
    PRIMARY KEY (id, owner),
    FOREIGN KEY(owner) REFERENCES user(id),
    FOREIGN KEY(attachment) REFERENCES attachment(id),
    FOREIGN KEY(comment_for) REFERENCES post(id),
    FOREIGN KEY(repost_of) REFERENCES post(id)
);
CREATE TABLE attachment (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    mime TEXT NOT NULL,
    size INTEGER NOT NULL,
    storage_url TEXT NOT NULL UNIQUE,
    owner_id INTEGER NOT NULL,
    FOREIGN KEY(owner_id) REFERENCES user(id)
);
CREATE TABLE hashtag (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE
);
CREATE TABLE posttaglink (
    post_id INTEGER NOT NULL UNIQUE,
    hastag_id INTEGER NOT NULL UNIQUE,
    PRIMARY KEY (post_id, hastag_id),
    FOREIGN KEY(post_id) REFERENCES post(id),
    FOREIGN KEY(hastag_id) REFERENCES hashtag(id)
);
CREATE TABLE follow_requests (
    from_user INTEGER NOT NULL,
    to_user INTEGER NOT NULL,
    PRIMARY KEY (from_user, to_user),
    FOREIGN KEY(from_user) REFERENCES user(id),
    FOREIGN KEY(to_user) REFERENCES user(id)
);
CREATE TABLE user_ban (
    user INTEGER NOT NULL,
    by_user INTEGER NOT NULL,
    PRIMARY KEY (user, by_user),
    FOREIGN KEY(user) REFERENCES user(id),
    FOREIGN KEY(by_user) REFERENCES user(id)
);
CREATE TABLE notification (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    post_id INTEGER NOT NULL,
    notifiable_id INTEGER NOT NULL,
    FOREIGN KEY(post_id) REFERENCES post(id),
    FOREIGN KEY(notifiable_id) REFERENCES user(id)
);
CREATE TABLE like (
    post_id INTEGER NOT NULL,
    user_id INTEGER PRIMARY KEY NOT NULL,
    FOREIGN KEY(post_id) REFERENCES post(id),
    FOREIGN KEY(user_id) REFERENCES user(id)
);
CREATE TABLE role_types (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE role (
    role_type_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (role_type_id, user_id),
    FOREIGN KEY(role_type_id) REFERENCES role_types(id),
    FOREIGN KEY(user_id) REFERENCES user(id)
);
CREATE TABLE platform_ban (
    id INTEGER PRIMARY KEY NOT NULL,
    user_id INTEGER NOT NULL,
    until INTEGER NOT NULL,
    reason TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES user(id)
);