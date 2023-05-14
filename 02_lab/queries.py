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


query_search_by_username = Query(
    query="SELECT username FROM user WHERE username LIKE '%Cat%' LIMIT 10;",
    name="Поиск пользователя по имени",
)

query_amount_of_english_users = Query(
    query="SELECT COUNT(*) FROM user WHERE primary_language = 'en';",
    name="Количество англоязычных пользователей",
)

query_users_by_language = Query(
    query="SELECT primary_language, COUNT(*) FROM user GROUP BY primary_language LIMIT 10;",
    name="Количество пользователей по языкам",
)

query_posts_by_user = Query(
    query="SELECT COUNT(*) FROM post WHERE owner = (SELECT id FROM user WHERE username = 'Death_Louce');",
    name="Количество постов пользователя 78",
)

query_top_users_by_amount_of_posts = Query(
    query="SELECT username, COUNT(*) as n_posts FROM post JOIN user ON post.owner = user.id group by username order by n_posts desc LIMIT 10;",
    name="Топ пользователей по количеству постов",
)

query_top_posts_by_amount_of_comments = Query(
    query="SELECT comment_for AS parent, COUNT(*) AS n_comments FROM post WHERE parent IS NOT NULL GROUP BY parent ORDER BY n_comments DESC LIMIT 10;",
    name="Топ постов по количеству комментариев",
)

query_total_cdn_usage = Query(
    query="SELECT (SUM(size) / 1024 / 1024) AS total_size FROM attachment;",
    name="Общее использование CDN, в MB",
)

query_cdn_usage_by_user = Query(
    query="SELECT username, (SUM(size) / 1024 / 1024) as storage_used FROM attachment JOIN user ON attachment.owner_id = user.id GROUP BY username LIMIT 10;",
    name="Использование CDN по пользователям",
)

query_average_subscribers_per_privacy_status = Query(
    query="SELECT is_private, AVG(n_subscribers) as subscribers_average FROM (SELECT followee, user.is_private, COUNT(*) AS n_subscribers FROM subscription JOIN user ON followee = user.id  GROUP BY followee  ORDER BY n_subscribers DESC) GROUP BY is_private;",
    name="Среднее количество подписок для приватных/публичных пользователей",
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
    ]

    query_dict = {q.name: q for q in queries}

    conn = sqlite3.connect("tw2tter.db")

    for q in queries:
        print(f"### {q.name}")
        print()
        print(f"Запрос: `{q.query}`")
        print()
        print("```")
        print(tabulate(q.execute(conn)))
        print("```")
        print("\n\n")
