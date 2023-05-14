import random
import sqlite3
import sys

from math import log

import models


def create_connection(db_file: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_file)
    return conn


def get_cursor(conn: sqlite3.Connection) -> sqlite3.Cursor:
    return conn.cursor()


def init_database(conn: sqlite3.Connection) -> None:
    c = get_cursor(conn)
    with open("../01_lab/db_init.sql") as f:
        c.executescript(f.read())

    conn.commit()


class State:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.users: list[models.User] = []
        self.posts: list[models.Post] = []
        self.follow_requests: list[models.FollowRequest] = []
        self.hashtags: list[models.Hashtag] = []

        init_database(self.conn)

        self.role_types = models.RoleTypes()

        inserts = self.role_types.generate_inserts()

        c = get_cursor(self.conn)

        for q in inserts:
            self.execute(q, c)
            role_id = c.lastrowid

            if not role_id:
                raise ValueError("No roletype id")

            self.role_types.set_id(q.values[0], role_id)

    def execute(self, query: models.Query, cursor: sqlite3.Cursor):
        cursor.execute(
            query.query,
            query.values,
        )

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def get_new_hashtag(self, c: sqlite3.Cursor) -> models.Hashtag:
        h = models.Hashtag()
        q = h.generate_insert()
        try:
            self.execute(q, c)
        except sqlite3.IntegrityError:
            return self.get_hashtag(c)

        hashtag_id = c.lastrowid
        if hashtag_id is None:
            raise ValueError("No hashtag id")
        h.set_id(hashtag_id)
        return h

    def get_new_attachment(
        self, c: sqlite3.Cursor, owner: models.User
    ) -> models.Attachment:
        a = models.Attachment(owner=owner)
        q = a.generate_insert()
        self.execute(q, c)

        attachment_id = c.lastrowid
        if attachment_id is None:
            raise ValueError("No attachment id")
        a.set_id(attachment_id)
        return a

    def get_hashtag(self, c: sqlite3.Cursor) -> models.Hashtag:
        if random.random() < 0.6 and len(self.hashtags) > 0:
            return random.choice(self.hashtags)
        else:
            new_hashtag = self.get_new_hashtag(c)
            self.hashtags.append(new_hashtag)
            return new_hashtag

    def iteration(self, n: int) -> None:
        # single iteration is:
        # 1. create user
        # 2. assign role to user
        # 2. create random number of posts
        # 3. choose random subset of posts and upvote them
        # 4. choose random subset users and subscribe to them
        # 5. choose random subset of users and ban them
        # 6. wont fill the notification really, should be some kind of trigger

        c = get_cursor(self.conn)
        for _ in range(n):
            user = models.User()
            q = user.generate_insert()
            try:
                self.execute(q, c)
            except sqlite3.IntegrityError:
                continue
            user_id = c.lastrowid

            if not user_id:
                raise ValueError("No user id")

            user.set_id(user_id)
            self.users.append(user)

            role = models.Role(user=user, role_types=self.role_types)
            q = role.generate_insert()
            self.execute(q, c)

            for _ in range(abs(int(random.normalvariate(30, 30)))):
                hashtags = [
                    self.get_hashtag(c)
                    for _ in range(
                        random.choices(
                            [0, 1, 2, 3, 4], [0.5, 0.3, 0.1, 0.05, 0.05], k=1
                        )[0]
                    )
                ]

                if random.random() < 0.3:
                    attachment = self.get_new_attachment(c, user)
                else:
                    attachment = None

                post = models.Post(owner=user, hashtags=hashtags, attachment=attachment)
                q = post.generate_insert()
                self.execute(q, c)
                post_id = c.lastrowid

                if not post_id:
                    raise ValueError("No post id")

                post.set_id(post_id)
                self.posts.append(post)

            for _ in range(abs(int(random.normalvariate(3, 3)))):
                hashtags = [
                    self.get_hashtag(c)
                    for _ in range(
                        random.choices(
                            [0, 1, 2, 3, 4], [0.7, 0.1, 0.1, 0.05, 0.05], k=1
                        )[0]
                    )
                ]

                comment = models.Post(
                    owner=user,
                    comment_for=random.choice(self.posts),
                    hashtags=hashtags,
                )

                q = comment.generate_insert()
                self.execute(q, c)
                comment_id = c.lastrowid
                if not comment_id:
                    raise ValueError("No comment id")

                comment.set_id(comment_id)
                self.posts.append(comment)

            for _ in range(abs(int(random.normalvariate(3, 3)))):
                hashtags = [
                    self.get_hashtag(c)
                    for _ in range(
                        random.choices(
                            [0, 1, 2, 3, 4], [0.8, 0.1, 0.04, 0.03, 0.03], k=1
                        )[0]
                    )
                ]

                repost = models.Post(
                    owner=user,
                    repost_of=random.choice(self.posts),
                    hashtags=hashtags,
                )

                q = repost.generate_insert()
                self.execute(q, c)

                repost_id = c.lastrowid
                if not repost_id:
                    raise ValueError("No repost id")

                repost.set_id(repost_id)
                self.posts.append(repost)

            to_like = random.sample(
                self.posts,
                int(min(len(self.posts) / 3, int(abs(random.normalvariate(5, 10))))),
            )

            for post in to_like:
                upvote = post.upvote(user)
                q = upvote.generate_insert()
                try:
                    # trying to upvote twice is not allowed
                    self.execute(q, c)
                except sqlite3.IntegrityError:
                    pass

            to_subscribe = random.sample(
                self.users,
                int(min(len(self.users) / 3, int(abs(random.normalvariate(5, 5))))),
            )

            for user_to_subscribe in to_subscribe:
                subscription = user.subscribe(user_to_subscribe)
                q = subscription.generate_insert()
                if isinstance(subscription, models.FollowRequest):
                    self.follow_requests.append(subscription)

                try:
                    # trying to subscribe twice is not allowed
                    self.execute(q, c)
                except sqlite3.IntegrityError:
                    pass

            to_ban = random.sample(
                self.users,
                int(min(len(self.users) / 100, int(abs(random.normalvariate(2, 2))))),
            )

            for user_to_ban in to_ban:
                ban = user.ban(user_to_ban)
                q = ban.generate_insert()
                try:
                    # trying to ban twice is not allowed
                    self.execute(q, c)
                except sqlite3.IntegrityError:
                    pass

            self.commit()

        # accept requests
        to_accept = random.sample(
            self.follow_requests,
            int(
                min(
                    len(self.follow_requests) / 2,
                    int(abs(random.normalvariate(30, 70))),
                )
            ),
        )

        for request in to_accept:
            delete_query, subscription = request.accept()
            self.execute(delete_query, c)
            q = subscription.generate_insert()
            try:
                # trying to subscribe twice is not allowed
                self.execute(q, c)
            except sqlite3.IntegrityError:
                pass

        # platform bans
        to_platform_ban = random.sample(
            self.users, abs(int(random.normalvariate(n // 100, log(n) // 100)))
        )

        for user_to_ban in to_platform_ban:
            pban = models.PlatformBan(user=user_to_ban)
            q = pban.generate_insert()
            try:
                # trying to ban twice is not allowed
                self.execute(q, c)
            except sqlite3.IntegrityError:
                pass

        self.commit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generator.py <number of iterations>")
        sys.exit(1)

    iterations = int(sys.argv[1])

    conn = create_connection("tw2tter.db")
    state = State(conn)
    state.iteration(iterations)
    state.close()
