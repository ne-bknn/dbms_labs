import psycopg2
from tabulate import tabulate  # type: ignore
from typing import Any


class Query:
    def __init__(self, query: str, name: str):
        self.query = query
        self.name = name

    def execute(self, conn) -> Any:
        c = conn.cursor()
        c.execute(self.query)
        return [(d[0] for d in c.description)] + c.fetchall()


query_search_by_username = Query(
    query="SELECT username FROM users WHERE username LIKE '%Cat%' LIMIT 10;",
    name="Поиск пользователя по имени",
)

query_amount_of_english_users = Query(
    query="SELECT COUNT(*) FROM users WHERE primary_language = 'en';",
    name="Количество англоязычных пользователей",
)

query_users_by_language = Query(
    query="SELECT primary_language, COUNT(*) FROM users GROUP BY primary_language LIMIT 10;",
    name="Количество пользователей по языкам",
)

query_posts_by_user = Query(
    query="SELECT COUNT(*) FROM post WHERE owner = (SELECT id FROM users WHERE username = 'Death_Louce');",
    name="Количество постов пользователя Death_Louce",
)

query_top_users_by_amount_of_posts = Query(
    query="SELECT username, COUNT(*) as n_posts FROM post JOIN users ON post.owner = users.id group by username order by n_posts desc LIMIT 10;",
    name="Топ пользователей по количеству постов",
)

query_top_posts_by_amount_of_comments = Query(
    query="SELECT comment_for, COUNT(*) AS n_comments FROM post WHERE comment_for IS NOT NULL GROUP BY comment_for ORDER BY n_comments DESC LIMIT 10;",
    name="Топ постов по количеству комментариев",
)

query_total_cdn_usage = Query(
    query="SELECT (SUM(size) / 1024 / 1024) AS total_size FROM attachment;",
    name="Общее использование CDN, в MB",
)

query_cdn_usage_by_user = Query(
    query="SELECT username, (SUM(size) / 1024 / 1024) as storage_used FROM attachment JOIN users ON attachment.owner_id = users.id GROUP BY username LIMIT 10;",
    name="Использование CDN по пользователям",
)

query_average_subscribers_per_privacy_status = Query(
    query="SELECT is_private, AVG(n_subscribers) as subscribers_average FROM (SELECT followee, users.is_private, COUNT(*) AS n_subscribers FROM subscription JOIN users ON followee = users.id  GROUP BY followee, users.is_private  ORDER BY n_subscribers DESC) AS foo GROUP BY is_private;",
    name="Среднее количество подписок для приватных/публичных пользователей",
)

query_average_number_of_upvotes_for_top_posters = Query(
    query="""SELECT u.username, COUNT(p.id) AS num_posts, AVG(COALESCE(upvote_count, 0)) AS avg_upvotes
FROM users u
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
  WHERE s.followee IN (SELECT id FROM users) -- optional optimization
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
FROM users
WHERE is_private = TRUE
ORDER BY lang_count DESC
LIMIT 1;
""",
    name="Самый популярный язык среди приватных пользователей",
)

query_posts_with_usernames_emails = Query(
    query="""SELECT post.id, substr(post.text, 1, 20), users.username, users.email
FROM post
INNER JOIN users ON post.owner = users.id
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
    query="""SELECT users.username, users.email, post.text
FROM users
LEFT JOIN (
    SELECT owner, text
    FROM post
    WHERE id IN (
        SELECT MAX(id)
        FROM post
        GROUP BY owner
    )
) AS post ON users.id = post.owner LIMIT 10;""",
    name="Последние посты каждого пользователя",
)


query_total_number_of_posts_votes = Query(
    query="""SELECT u.id, u.username, u.email, COUNT(p.id) AS total_posts, COUNT(up.post_id) AS total_upvotes
FROM users u
LEFT JOIN post p ON p.owner = u.id
LEFT JOIN upvote up ON up.post_id = p.id
GROUP BY u.id, u.username, u.email
ORDER BY total_upvotes DESC LIMIT 10;""",
    name="Сборная статистика по пользователям",
)


if __name__ == "__main__":
    queries = [
        query_search_by_username,
        query_amount_of_english_users,
        query_users_by_language,
        query_posts_by_user,
        query_top_users_by_amount_of_posts,
        query_top_posts_by_amount_of_comments,
        query_total_cdn_usage,
        query_cdn_usage_by_user,
        query_average_subscribers_per_privacy_status,
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

    conn = psycopg2.connect("postgresql://postgres:aboba@localhost/main")

    for q in queries:
        print(f"### {q.name}")
        print()
        print(f"Запрос:\n```\n{q.query.strip()}\n```")
        print()
        print("```")
        print(tabulate(q.execute(conn)))
        print("```")
