import sqlite3
from tabulate import tabulate  # type: ignore
from typing import Any


class Query:
    def __init__(self, query: str, name: str):
        self.query = query
        self.name = name

    def execute(self, conn: sqlite3.Connection) -> Any:
        c = conn.cursor()
        c.execute(self.query)
        return [(d[0] for d in c.description)] + c.fetchall()


query_average_number_of_upvotes_for_top_posters = Query(
    query="""SELECT u.username, COUNT(p.id) AS num_posts, AVG(COALESCE(upvote_count, 0)) AS avg_upvotes
FROM user u
LEFT JOIN post p ON u.id = p.owner
LEFT JOIN (
  SELECT post_id, COUNT(*) AS upvote_count
  FROM upvote
  GROUP BY post_id
) uv ON p.id = uv.post_id
GROUP BY u.id
ORDER BY num_posts DESC
LIMIT 10;
    """,
    name="Среднее количество лайков у пользователей с наибольшим количеством постов",
)


query_second_level_subscribers = Query(
    query="""WITH RECURSIVE second_handshake_subscribers(user_id, subscriber_id, level) AS (
  SELECT s.followee, s.follower, 1
  FROM subscription s
  WHERE s.followee IN (SELECT id FROM user) -- optional optimization
  UNION ALL
  SELECT ss.user_id, s.follower, ss.level + 1
  FROM second_handshake_subscribers ss
  INNER JOIN subscription s ON ss.subscriber_id = s.followee
  WHERE ss.level < 2 -- limit to second-handshake subscribers
)
SELECT shs.user_id, COUNT(DISTINCT shs.subscriber_id) AS num_second_handshake_subscribers
FROM second_handshake_subscribers shs
GROUP BY shs.user_id ORDER BY num_second_handshake_subscribers DESC LIMIT 10;
    """,
    name="Количество подписчиков первого и второго уровня - непосредственные подписчкики + подписчики подписчиков",
)

query_most_common_language_for_private_users = Query(
    query="""SELECT 
    primary_language,
    COUNT(*) OVER (PARTITION BY primary_language) AS lang_count
FROM user
WHERE is_private = TRUE
ORDER BY lang_count DESC
LIMIT 1;
""",
    name="Самый популярный язык среди приватных пользователей",
)

query_posts_with_usernames_emails = Query(
    query="""SELECT post.id, substr(post.text, 1, 20), user.username, user.email
FROM post
INNER JOIN user ON post.owner = user.id
LIMIT 10;
""",
    name="Посты с соответствующими юзернеймами и емейлами",
)

query_upvoted_by_user = Query(
    query="""SELECT post.id, substr(post.text, 1, 20), upvote.user_id
FROM post
INNER JOIN upvote ON post.id = upvote.post_id
WHERE upvote.user_id = 78;
""",
    name="Посты, которые лайкнул пользователь с id 78",
)

query_posts_with_attachments = Query(
    query="""SELECT post.id, substr(post.text, 1, 20), attachment.name, attachment.mime
FROM post
LEFT JOIN attachment ON post.attachment = attachment.id LIMIT 10;
""",
    name="Посты с прикрепленными файлами",
)

query_most_recent_posts_per_user = Query(
    query="""SELECT user.username, user.email, post.text
FROM user
LEFT JOIN (
    SELECT owner, text
    FROM post
    WHERE id IN (
        SELECT MAX(id)
        FROM post
        GROUP BY owner
    )
) AS post ON user.id = post.owner LIMIT 10;""",
    name="Последние посты каждого пользователя",
)


query_total_number_of_posts_votes = Query(
    query="""SELECT u.id, u.username, u.email, COUNT(p.id) AS total_posts, COUNT(up.post_id) AS total_upvotes
FROM user u
LEFT JOIN post p ON p.owner = u.id
LEFT JOIN upvote up ON up.post_id = p.id
GROUP BY u.id, u.username, u.email
ORDER BY total_upvotes DESC LIMIT 10;""",
    name="Сборная статистика по пользователям",
)


if __name__ == "__main__":
    queries = [
        query_average_number_of_upvotes_for_top_posters,
        query_second_level_subscribers,
        query_most_common_language_for_private_users,
        query_posts_with_usernames_emails,
        query_upvoted_by_user,
        query_posts_with_attachments,
        query_most_recent_posts_per_user,
        query_total_number_of_posts_votes,
    ]

    query_dict = {q.name: q for q in queries}

    conn = sqlite3.connect("tw2tter.db")

    for q in queries:
        print(f"### {q.name}")
        print()
        print(f"Запрос:\n```\n{q.query.strip()}\n```")
        print()
        print("```")
        print(tabulate(q.execute(conn)))
        print("```")
