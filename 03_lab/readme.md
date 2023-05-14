# НИЯУ МИФИ. ИИКС. Лабораторная работа №3. Мищенко Тимофей, Б20-505. 2023.  

## Разработанные запросы

### Среднее количество лайков у пользователей с наибольшим количеством постов

Запрос:
```sql
SELECT u.username, COUNT(p.id) AS num_posts, AVG(COALESCE(upvote_count, 0)) AS avg_upvotes
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
```

```
--------------  ---------  --------------------
username        num_posts  avg_upvotes
Spying_Kerotan  159        0.4968553459119497
Dire_Chick      125        0.0
Sly_Firefly     119        0.3277310924369748
Midnight_Crow   119        0.11764705882352941
Ghost_Ape       116        0.034482758620689655
Western_Boa     113        0.061946902654867256
Vile_Komodo     111        0.09009009009009009
Bloody_Ape      111        0.05405405405405406
Assassin_Yoshi  109        0.05504587155963303
Rampant_Hawk    109        0.10091743119266056
--------------  ---------  --------------------
```

### Количество подписчиков первого и второго уровня - непосредственные подписчкики + подписчики подписчиков

Запрос:

```sql
WITH RECURSIVE second_handshake_subscribers(user_id, subscriber_id, level) AS (
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
FROM user
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
SELECT post.id, substr(post.text, 1, 20), user.username, user.email
FROM post
INNER JOIN user ON post.owner = user.id
LIMIT 10;
```

```
--  ------------------------  ------------  -------------------
id  substr(post.text, 1, 20)  username      email
1   Modi modi non non do      Pink_Mammoth  P.Mammoth@gmail.com
2   Numquam voluptatem e      Pink_Mammoth  P.Mammoth@gmail.com
3   Labore sed dolor dol      Pink_Mammoth  P.Mammoth@gmail.com
4   Amet tempora eius vo      Pink_Mammoth  P.Mammoth@gmail.com
5   Quisquam neque quaer      Pink_Mammoth  P.Mammoth@gmail.com
6   Adipisci dolor conse      Pink_Mammoth  P.Mammoth@gmail.com
7   Magnam adipisci labo      Pink_Mammoth  P.Mammoth@gmail.com
8   Dolore numquam porro      Pink_Mammoth  P.Mammoth@gmail.com
9   Ut labore quaerat ut      Pink_Mammoth  P.Mammoth@gmail.com
10  Etincidunt consectet      Pink_Mammoth  P.Mammoth@gmail.com
--  ------------------------  ------------  -------------------
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
----  ------------------------  -------
id    substr(post.text, 1, 20)  user_id
1959  Velit adipisci dolor      78
95    Consectetur quaerat       78
1527  Consectetur eius vel      78
----  ------------------------  -------
```

### Посты вместе с прикрепленными файлами

Запрос:

```sql
SELECT post.id, substr(post.text, post.text, 1, 20), attachment.name, attachment.mime
FROM post
LEFT JOIN attachment ON post.attachment = attachment.id LIMIT 10;
```

```
--  ------------------------  -----------------------  ----------
id  substr(post.text, 1, 20)  name                     mime
1   Modi modi non non do
2   Numquam voluptatem e
3   Labore sed dolor dol
4   Amet tempora eius vo      cat_78188589.jpeg        image/jpeg
5   Quisquam neque quaer      caecilian_07486670.jpeg  image/jpeg
6   Adipisci dolor conse
7   Magnam adipisci labo      weasel_76376674.webm     video/webm
8   Dolore numquam porro      cricket_86749467.webm    video/webm
9   Ut labore quaerat ut
10  Etincidunt consectet
--  ------------------------  -----------------------  ----------
```

### Последние посты каждого пользователя

Запрос:

```sql
SELECT user.username, user.email, post.text
FROM user
LEFT JOIN (
    SELECT owner, text
    FROM post
    WHERE id IN (
        SELECT MAX(id)
        FROM post
        GROUP BY owner
    )
) AS post ON user.id = post.owner LIMIT 10;
```

```
----------------  ----------------------  ------------------------------------------------------------------------------------------------------
username          email                   text
Pink_Mammoth      P.Mammoth@gmail.com     Quaerat etincidunt adipisci eius labore dolorem labore quaerat.
Airborne_Eel      A.Eel@hotmail.com       Ipsum tempora dolor voluptatem eius.
Silver_Shark      S.Shark@protonmail.com  Sed porro dolorem dolorem eius magnam sit aliquam. #rostrolateral #nonterritorially #unweft #brokeress
Running_Inchworm  R.Inchworm@gmail.com    Consectetur dolore eius consectetur dolor non adipisci.
Northern_Frill    N.Frill@hotmail.com     Numquam quisquam non est aliquam est sit porro.
Lost_Agama        L.Agama@gmail.com       Quisquam ipsum modi velit amet.
Dirty_Buzzard     D.Buzzard@hotmail.com   Labore non dolor tempora. #parisis #reshows #elects
Bastard_Ant       B.Ant@protonmail.com    Neque velit dolor velit ut quiquia.
Rabid_Firefly     R.Firefly@outlook.com   Labore etincidunt aliquam dolorem quiquia dolore dolore consectetur. #arctian
Machinegun_Frog   M.Frog@outlook.com      Adipisci quisquam non non sed sit ut.
----------------  ----------------------  ------------------------------------------------------------------------------------------------------
```

### Сборная статистика по пользователям

Запрос:

```sql
SELECT u.id, u.username, u.email, COUNT(p.id) AS total_posts, COUNT(up.post_id) AS total_upvotes
FROM user u
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
31  Cannibal_Squirrel  C.Squirrel@protonmail.com  101          67
64  Creeping_Coyote    C.Coyote@protonmail.com    126          67
6   Lost_Agama         L.Agama@gmail.com          79           58
4   Running_Inchworm   R.Inchworm@gmail.com       81           57
63  Punished_Beetle    P.Beetle@protonmail.com    98           56
57  Raging_Gull        R.Gull@hotmail.com         107          55
--  -----------------  -------------------------  -----------  -------------
```

## Запустить запросы на своих данных

Для этого был разработан сценарий `queries.py`; запуск этого сценария выведет результаты работы приведенных выше запросов на файле `tw2tter.db`. Внешняя зависимость: `tabulate`.

```bash
python3 queries.py
```

## Приложение

[Запросы](./queries.py)  

## Заключение

Были разработаны более сложные запросы к разработанной БД. Были использованы оконные функции, рекурсивные запросы и множество различных JOIN.
