# НИЯУ МИФИ. ИИКС. Лабораторная работа №4. Мищенко Тимофей, Б20-505. 2023.  

## Запуск PostgreSQL

Тривиально и делано многократно:

```bash
docker run -ti -p5432:5432 -e POSTGRES_PASSWORD=aboba postgres
```

## Миграция на PostgreSQL

Из-за архитектурных ошибок (ловления sqlite-исключений в коде) использование generator.py как способ генерации данных в Postgres оказался неудобным. Поэтому я вспользовался инструментом `pgloader` для миграции данных из sqlite в postgresql. Лог работы:

```
❯ pgloader sqlite:///$(pwd)/tw2tter.db pgsql://postgres:aboba@localhost/postgres
2023-05-14T23:56:57.010000+03:00 LOG pgloader version "3.6.0c0ea23"
2023-05-14T23:56:57.010000+03:00 LOG Data errors in '/tmp/pgloader/'
2023-05-14T23:56:57.053334+03:00 LOG Migrating from #<SQLITE-CONNECTION sqlite:///home/ne_bknn/Projects/dbms_labs/03_lab/tw2tter.db {1005BF9C83}>
2023-05-14T23:56:57.053334+03:00 LOG Migrating into #<PGSQL-CONNECTION pgsql://postgres@localhost:5432/postgres {1005D6F1C3}>
2023-05-14T23:56:58.330023+03:00 ERROR PostgreSQL Database error 42P17: functions in index expression must be marked IMMUTABLE
QUERY: CREATE UNIQUE INDEX idx_16425_user_ban_pkey ON user_ban (user, by_user);
2023-05-14T23:56:58.550027+03:00 ERROR PostgreSQL Database error 42704: index "idx_16425_user_ban_pkey" does not exist
QUERY: ALTER TABLE user_ban ADD PRIMARY KEY USING INDEX idx_16425_user_ban_pkey;
2023-05-14T23:56:58.610028+03:00 ERROR PostgreSQL Database error 42601: syntax error at or near "user"
QUERY: ALTER TABLE user_ban ADD FOREIGN KEY(user) REFERENCES "user"(id) ON UPDATE NO ACTION ON DELETE NO ACTION
2023-05-14T23:56:58.633361+03:00 LOG report summary reset
             table name     errors       rows      bytes      total time
-----------------------  ---------  ---------  ---------  --------------
                  fetch          0          0                     0.000s
        fetch meta data          0         53                     0.027s
         Create Schemas          0          0                     0.003s
       Create SQL Types          0          0                     0.003s
          Create tables          0         26                     0.123s
         Set Table OIDs          0         13                     0.007s
-----------------------  ---------  ---------  ---------  --------------
                 "user"          0        981    51.9 kB          0.090s
           subscription          0       1494    11.0 kB          0.073s
                   post          0      39937    10.7 MB          0.873s
             attachment          0      10281     1.0 MB          0.223s
            posttaglink          0          0                     0.093s
               user_ban          0       1495    11.3 kB          0.323s
                 upvote          0       8273    74.0 kB          0.323s
                   role          0        981     5.6 kB          0.723s
                hashtag          0      12669   192.7 kB          0.263s
         follow_request          0       3643    27.0 kB          0.577s
           notification          0          0                     0.303s
             role_types          0          6     0.1 kB          0.587s
           platform_ban          0         10     0.3 kB          0.683s
-----------------------  ---------  ---------  ---------  --------------
COPY Threads Completion          0          4                     0.903s
         Create Indexes          1         19                     1.077s
 Index Build Completion          0         20                     0.180s
        Reset Sequences          0          6                     0.053s
           Primary Keys          1         12                     0.020s
    Create Foreign Keys          1         19                     0.073s
        Create Triggers          0          0                     0.000s
       Install Comments          0          0                     0.000s
-----------------------  ---------  ---------  ---------  --------------
      Total import time          ✓      79770    12.1 MB          2.307s
```

Запускаем 02_lab/queries.py и 03_lab/queries.py, подменив движок с sqlite на psycopg2. Объединенный список запросов в 04_lab/queries.py.

На этом этапе произошла первая проблема: после загрузки данных таблица `user` почти пуста - в ней только одна строчка с одной колонкой, в которой написано `postgres`. Изначально я подумал, что таблица user в базе данных `postgres` в СУБД `postgres` - зарезервирована. Создал БД `main`, запустил `pgloader` снова на новую БД.

```bash
❯ psql -h localhost -U postgres
Password for user postgres:
psql (15.2, server 15.3 (Debian 15.3-1.pgdg110+1))
Type "help" for help.

postgres=# create database main;
CREATE DATABASE
postgres=#
\q
```

Однако ничего не изменилось; оказалось, `USER` - зарезервированное слово `postgres`[[1]](https://www.postgresql.org/docs/current/sql-keywords-appendix.html). 

Переименуем таблицу в `users` в `tw2tter.db`:

```bash
❯ sqlite3 ../03_lab/tw2tter.db
SQLite version 3.41.2 2023-03-22 11:56:21
Enter ".help" for usage hints.
sqlite> alter table user rename to users;
sqlite> select * from users limit 1;
1|Pink_Mammoth|P.Mammoth@gmail.com|fr|1|7fj0j1huny
sqlite>
```

Дропнем БД `main` и создадим обратно в `postgres`:

```
❯ psql -h localhost -U postgres
zsh: correct 'psql' to 'psl' [nyae]? n
Password for user postgres: 
psql (15.2, server 15.3 (Debian 15.3-1.pgdg110+1))
Type "help" for help.

postgres=# drop database main;
ERROR:  database "main" is being accessed by other users
DETAIL:  There is 1 other session using the database.
postgres=# drop database main;
DROP DATABASE
postgres=# create database main;
CREATE DATABASE
postgres=#
```

Снова запустим `pgloader`, проверим что все получилось:

```
❯ psql -h localhost -U postgres
Password for user postgres: 
psql (15.2, server 15.3 (Debian 15.3-1.pgdg110+1))
Type "help" for help.

postgres=# \c main
psql (15.2, server 15.3 (Debian 15.3-1.pgdg110+1))
You are now connected to database "main" as user "postgres".
main=# select * from users limit 1;
 id |   username   |        email        | primary_language | is_private |  password  
----+--------------+---------------------+------------------+------------+------------
  1 | Pink_Mammoth | P.Mammoth@gmail.com | fr               | t          | 7fj0j1huny
(1 row)

main=# 
\q
```

Переименуем `user` в `users` в `queries.py`. Запустим.

Postgres находит багу в моих запросах в sqlite:

```
SELECT COUNT(*) FROM post WHERE owner = 'Death_Louce';
```

```
psycopg2.errors.InvalidTextRepresentation: invalid input syntax for type bigint: "Death_Louce"
LINE 1: SELECT COUNT(*) FROM post WHERE owner = 'Death_Louce';
```

По какой-то неведомой причине для Sqlite этот запрос приемлем. Перепишем его:

```sql
    SELECT COUNT(*) FROM post WHERE owner = (SELECT id FROM users WHERE username = 'Death_Louce');
```

Следующая ошибка в следующем запросе:

```sql
    SELECT comment_for AS parent, COUNT(*) AS n_comments FROM post WHERE parent IS NOT NULL GROUP BY parent ORDER BY n_comments DESC LIMIT 10;",
```

```
psycopg2.errors.UndefinedColumn: column "parent" does not exist
LINE 1: ...AS parent, COUNT(*) AS n_comments FROM post WHERE parent IS ...
```

Postgres не нравится алиас, давате без него:

```sql
    SELECT comment_for, COUNT(*) AS n_comments FROM post WHERE comment_for IS NOT NULL GROUP BY comment_for ORDER BY n_comments DESC LIMIT 10;",
```

Следующая ошибка:

```sql
SELECT is_private, AVG(n_subscribers) as subscribers_average FROM (SELECT followee, users.is_private, COUNT(*) AS n_subscribers FROM subscription JOIN users ON followee = users.id  GROUP BY followee  ORDER BY n_subscribers DESC) GROUP BY is_private;
```

```
psycopg2.errors.SyntaxError: subquery in FROM must have an alias
LINE 1: ...e, AVG(n_subscribers) as subscribers_average FROM (SELECT fo...
                                                             ^
HINT:  For example, FROM (SELECT ...) [AS] foo.
```

Алиас так алиас:

```sql
SELECT is_private, AVG(n_subscribers) as subscribers_average FROM (SELECT followee, users.is_private, COUNT(*) AS n_subscribers FROM subscription JOIN users ON followee = users.id  GROUP BY followee  ORDER BY n_subscribers DESC) AS foo GROUP BY is_private;
```

Там же:

```
psycopg2.errors.GroupingError: column "users.is_private" must appear in the GROUP BY clause or be used in an aggregate function
LINE 1: ...rs) as subscribers_average FROM (SELECT followee, users.is_p...
```

Исправим:

```sql
SELECT is_private, AVG(n_subscribers) as subscribers_average FROM (SELECT followee, users.is_private, COUNT(*) AS n_subscribers FROM subscription JOIN users ON followee = users.id  GROUP BY followee, users.is_private  ORDER BY n_subscribers DESC) AS foo GROUP BY is_private;
```


После чего все работает.

## Результаты запросов

### Поиск пользователя по имени

Запрос:
```
SELECT username FROM users WHERE username LIKE '%Cat%' LIMIT 10;
```

```
------------
username
Punching_Cat
Nuclear_Cat
------------
```
### Количество англоязычных пользователей

Запрос:
```sql
SELECT COUNT(*) FROM users WHERE primary_language = 'en';
```

```
-----
count
112
-----
```
### Количество пользователей по языкам

Запрос:
```sql
SELECT primary_language, COUNT(*) FROM users GROUP BY primary_language LIMIT 10;
```

```
----------------  -----
primary_language  count
de                112
pl                122
fr                117
cn                106
en                112
it                140
es                138
ru                134
----------------  -----
```
### Количество постов пользователя Death_Louce

Запрос:
```sql
SELECT COUNT(*) FROM post WHERE owner = (SELECT id FROM users WHERE username = 'Death_Louce');
```

```
-----
count
0
-----
```
### Топ пользователей по количеству постов

Запрос:
```sql
SELECT username, COUNT(*) as n_posts FROM post JOIN users ON post.owner = users.id group by username order by n_posts desc LIMIT 10;
```

```
--------------  -------
username        n_posts
Spying_Kerotan  159
Dire_Chick      125
Midnight_Crow   119
Sly_Firefly     119
Ghost_Ape       116
Western_Boa     113
Vile_Komodo     111
Bloody_Ape      111
Assassin_Yoshi  109
Rampant_Hawk    109
--------------  -------
```
### Топ постов по количеству комментариев

Запрос:
```sql
SELECT comment_for, COUNT(*) AS n_comments FROM post WHERE comment_for IS NOT NULL GROUP BY comment_for ORDER BY n_comments DESC LIMIT 10;
```

```
-----------  ----------
comment_for  n_comments
272          4
6            4
15           3
2695         3
7553         3
10045        3
188          3
12415        3
283          3
4193         3
-----------  ----------
```
### Общее использование CDN, в MB

Запрос:
```sql
SELECT (SUM(size) / 1024 / 1024) AS total_size FROM attachment;
```

```
---------------------
total_size
4913.2104234695434570
---------------------
```
### Использование CDN по пользователям

Запрос:
```sql
SELECT username, (SUM(size) / 1024 / 1024) as storage_used FROM attachment JOIN users ON attachment.owner_id = users.id GROUP BY username LIMIT 10;
```

```
---------------  -------------------
username         storage_used
Charging_Little  8.7187232971191406
Revolver_Hornet  7.6303224563598633
Peace_Orca       3.4662027359008789
Technical_Deer   10.1868820190429688
Biting_Ray       2.1454820632934570
Seething_Heron   3.8384866714477539
Death_Deer       1.3714122772216797
Dirty_Dragon     10.8136863708496094
Bronze_Boss      4.4404506683349609
King_Eel         1.8070259094238281
---------------  -------------------
```
### Среднее количество подписок для приватных/публичных пользователей

Запрос:
```sql
SELECT is_private, AVG(n_subscribers) as subscribers_average FROM (SELECT followee, users.is_private, COUNT(*) AS n_subscribers FROM subscription JOIN users ON followee = users.id  GROUP BY followee, users.is_private  ORDER BY n_subscribers DESC) AS foo GROUP BY is_private;
```

```
----------  ----------------------
is_private  subscribers_average
False       5.9024390243902439
True        1.00000000000000000000
----------  ----------------------
```
### Среднее количество лайков у пользователей с наибольшим количеством постов

Запрос:
```sql
SELECT u.username, COUNT(p.id) AS num_posts, AVG(COALESCE(upvote_count, 0)) AS avg_upvotes
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
```

```
--------------  ---------  ----------------------
username        num_posts  avg_upvotes
Spying_Kerotan  159        0.49685534591194968553
Dire_Chick      125        0E-20
Midnight_Crow   119        0.11764705882352941176
Sly_Firefly     119        0.32773109243697478992
Ghost_Ape       116        0.03448275862068965517
Western_Boa     113        0.06194690265486725664
Vile_Komodo     111        0.09009009009009009009
Bloody_Ape      111        0.05405405405405405405
Assassin_Yoshi  109        0.05504587155963302752
Rampant_Hawk    109        0.10091743119266055046
--------------  ---------  ----------------------
```
### Количество подписчиков первого и второго уровня - непосредственные подписчкики + подписчики подписчиков

Запрос:
```sql
WITH RECURSIVE second_handshake_subscribers(user_id, subscriber_id, level) AS (
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
```

```
-------  --------------------------------
user_id  num_second_handshake_subscribers
563      54
488      51
976      46
687      45
770      44
266      42
388      41
551      40
149      40
664      39
-------  --------------------------------
```
### Самый популярный язык среди приватных пользователей

Запрос:
```sql
SELECT 
    primary_language,
    COUNT(*) OVER (PARTITION BY primary_language) AS lang_count
FROM users
WHERE is_private = TRUE
ORDER BY lang_count DESC
LIMIT 1;
```

```
----------------  ----------
primary_language  lang_count
it                107
----------------  ----------
```
### Посты с соответствующими юзернеймами и емейлами

Запрос:
```sql
SELECT post.id, substr(post.text, 1, 20), users.username, users.email
FROM post
INNER JOIN users ON post.owner = users.id
LIMIT 10;
```

```
--  --------------------  ------------  -------------------
id  substr                username      email
1   Modi modi non non do  Pink_Mammoth  P.Mammoth@gmail.com
2   Numquam voluptatem e  Pink_Mammoth  P.Mammoth@gmail.com
3   Labore sed dolor dol  Pink_Mammoth  P.Mammoth@gmail.com
4   Amet tempora eius vo  Pink_Mammoth  P.Mammoth@gmail.com
5   Quisquam neque quaer  Pink_Mammoth  P.Mammoth@gmail.com
6   Adipisci dolor conse  Pink_Mammoth  P.Mammoth@gmail.com
7   Magnam adipisci labo  Pink_Mammoth  P.Mammoth@gmail.com
8   Dolore numquam porro  Pink_Mammoth  P.Mammoth@gmail.com
9   Ut labore quaerat ut  Pink_Mammoth  P.Mammoth@gmail.com
10  Etincidunt consectet  Pink_Mammoth  P.Mammoth@gmail.com
--  --------------------  ------------  -------------------
```
### Посты, которые лайкнул пользователь с id 78

Запрос:
```sql
SELECT post.id, substr(post.text, 1, 20), upvote.user_id
FROM post
INNER JOIN upvote ON post.id = upvote.post_id
WHERE upvote.user_id = 78;
```

```
----  --------------------  -------
id    substr                user_id
1959  Velit adipisci dolor  78
95    Consectetur quaerat   78
1527  Consectetur eius vel  78
----  --------------------  -------
```
### Посты с прикрепленными файлами

Запрос:
```sql
SELECT post.id, substr(post.text, 1, 20), attachment.name, attachment.mime
FROM post
LEFT JOIN attachment ON post.attachment = attachment.id LIMIT 10;
```

```
--  --------------------  -----------------------  ----------
id  substr                name                     mime
1   Modi modi non non do
2   Numquam voluptatem e
3   Labore sed dolor dol
4   Amet tempora eius vo  cat_78188589.jpeg        image/jpeg
5   Quisquam neque quaer  caecilian_07486670.jpeg  image/jpeg
6   Adipisci dolor conse
7   Magnam adipisci labo  weasel_76376674.webm     video/webm
8   Dolore numquam porro  cricket_86749467.webm    video/webm
9   Ut labore quaerat ut
10  Etincidunt consectet
--  --------------------  -----------------------  ----------
```
### Последние посты каждого пользователя

Запрос:
```sql
SELECT users.username, users.email, post.text
FROM users
LEFT JOIN (
    SELECT owner, text
    FROM post
    WHERE id IN (
        SELECT MAX(id)
        FROM post
        GROUP BY owner
    )
) AS post ON users.id = post.owner LIMIT 10;
```

```
------------------  --------------------------  -----------------------------------------------------------------
username            email                       text
Airborne_Tasmanian  A.Tasmanian@yahoo.com       Adipisci quaerat velit etincidunt magnam dolor labore voluptatem.
Military_Chameleon  M.Chameleon@protonmail.com  Voluptatem neque est dolorem porro numquam ut.
Medical_Buzzard     M.Buzzard@outlook.com       Ut sed voluptatem ut amet.
Biting_Eagle        B.Eagle@outlook.com         Voluptatem non modi dolor voluptatem sed est.
Black_Sea           B.Sea@gmail.com             Dolore est dolore sit.
Crystal_Piranha     C.Piranha@protonmail.com    Adipisci voluptatem modi etincidunt.
Yellow_Mammoth      Y.Mammoth@protonmail.com    Adipisci voluptatem voluptatem ipsum labore quiquia.
Nuclear_Moose       N.Moose@hotmail.com         Adipisci ipsum amet quiquia.
Night_Moth          N.Moth@hotmail.com          Tempora dolore neque adipisci quisquam aliquam aliquam.
Vile_Anaconda       V.Anaconda@gmail.com        Porro consectetur quisquam tempora adipisci non quiquia dolorem.
------------------  --------------------------  -----------------------------------------------------------------
```
### Сборная статистика по пользователям

Запрос:
```sql
SELECT u.id, u.username, u.email, COUNT(p.id) AS total_posts, COUNT(up.post_id) AS total_upvotes
FROM users u
LEFT JOIN post p ON p.owner = u.id
LEFT JOIN upvote up ON up.post_id = p.id
GROUP BY u.id, u.username, u.email
ORDER BY total_upvotes DESC LIMIT 10;
```

```
--  -----------------  -------------------------  -----------  -------------
id  username           email                      total_posts  total_upvotes
8   Bastard_Ant        B.Ant@protonmail.com       151          113
89  Spying_Kerotan     S.Kerotan@hotmail.com      175          79
3   Silver_Shark       S.Shark@protonmail.com     105          75
10  Machinegun_Frog    M.Frog@outlook.com         88           69
64  Creeping_Coyote    C.Coyote@protonmail.com    126          67
31  Cannibal_Squirrel  C.Squirrel@protonmail.com  101          67
6   Lost_Agama         L.Agama@gmail.com          79           58
4   Running_Inchworm   R.Inchworm@gmail.com       81           57
63  Punished_Beetle    P.Beetle@protonmail.com    98           56
57  Raging_Gull        R.Gull@hotmail.com         107          55
--  -----------------  -------------------------  -----------  -------------
```

## Заключение

База данных была перенесена с sqlite3 на postgres, для этого был использован pgloader, sqlite3 для изменения структуры базы данных и psql для мелких изменений на Postgres. Ранее написанные запросы были запущены на postgres, нерабочие запросы были исправлены. Можно отметить, что Postgres более строгий к синтаксису запросов, чем sqlite3, однако не работали только 2 из 16 запросов. 