# НИЯУ МИФИ. ИИКС. Лабораторная работа №2. Мищенко Тимофей, Б20-505. 2022.

## Генерация тестовых данных

Разработан почти что ORM движок для создания тестовых данных. [Исходный код генератора](./generator.py), [модели](./models.py).

Использование:

```bash
python3 generator.py <количество пользователей>
```

В репозитории приложена уже сгенерированная `tw2tter.db`. Внешняя зависимость генератора - библиотека `lorem`.


## Разработанные запросы

### Поиск пользователя по имени

Запрос: `SELECT username FROM user WHERE username LIKE '%Cat%' LIMIT 10;`

```
------------
username
Nuclear_Cat
Punching_Cat
------------
```

### Количество англоязычных пользователей

Запрос: `SELECT COUNT(*) FROM user WHERE primary_language = 'en';`

```
--------
COUNT(*)
112
--------
```

### Количество пользователей по языкам

Запрос: `SELECT primary_language, COUNT(*) FROM user GROUP BY primary_language LIMIT 10;`

```
----------------  --------
primary_language  COUNT(*)
cn                106
de                112
en                112
es                138
fr                117
it                140
pl                122
ru                134
----------------  --------
```

### Количество постов пользователя Death_Louce

Запрос: `SELECT COUNT(*) FROM post WHERE owner = 'Death_Louce';`

```
--------
COUNT(*)
0
--------
```

### Топ пользователей по количеству постов

Запрос: `SELECT username, COUNT(*) as n_posts FROM post JOIN user ON post.owner = user.id group by username order by n_posts desc LIMIT 10;`

```
--------------  -------
username        n_posts
Spying_Kerotan  159
Dire_Chick      125
Sly_Firefly     119
Midnight_Crow   119
Ghost_Ape       116
Western_Boa     113
Vile_Komodo     111
Bloody_Ape      111
Rampant_Hawk    109
Assassin_Yoshi  109
--------------  -------
```

### Топ постов по количеству комментариев

Запрос: `SELECT comment_for AS parent, COUNT(*) AS n_comments FROM post WHERE parent IS NOT NULL GROUP BY parent ORDER BY n_comments DESC LIMIT 10;`

```
------  ----------
parent  n_comments
272     4
6       4
12415   3
10045   3
7553    3
4193    3
2994    3
2944    3
2695    3
1203    3
------  ----------
```

### Общее использование CDN, в MB

Запрос: `SELECT (SUM(size) / 1024 / 1024) AS total_size FROM attachment;`

```
----------
total_size
4913
----------
```

### Использование CDN по пользователям

Запрос: `SELECT username, (SUM(size) / 1024 / 1024) as storage_used FROM attachment JOIN user ON attachment.owner_id = user.id GROUP BY username LIMIT 10;`

```
------------------  ------------
username            storage_used
Airborne_Eel        1
Airborne_Flying     7
Airborne_Gray       13
Airborne_Hawk       8
Airborne_Leopard    1
Airborne_Lion       1
Airborne_Tasmanian  1
Alive_Alligator     5
Alive_Bee           2
Alive_Heron         1
------------------  ------------
```



### Среднее количество подписок для приватных/публичных пользователей

Запрос: `SELECT is_private, AVG(n_subscribers) as subscribers_average FROM (SELECT followee, user.is_private, COUNT(*) AS n_subscribers FROM subscription JOIN user ON followee = user.id  GROUP BY followee  ORDER BY n_subscribers DESC) GROUP BY is_private;`

```
----------  -------------------
is_private  subscribers_average
0           5.902439024390244
1           1.0
----------  -------------------
```

## Запустить запросы на своих данных

Для этого был разработан сценарий `queries.py`; запуск этого сценария выведет результаты работы приведенных выше запросов на файле `tw2tter.db`. Внешняя зависимость: `tabulate`.

```bash
python3 queries.py
```

## Приложение

[Генератор](./generator.py)  
[Модели](./models.py)  
[Запросы](./queries.py)  

## Заключение

Был разработан сценарий для генерации тестовых данных и ряд запросов для получения актуальной информации для заданной предметной области. Так как работы 2 и 3 отличаются только набором предлагаемых для использования возможностей SQL, в этой лабораторной работе были разработаны запросы, возможности которых я хорошо понимаю (простые join'ы, вложенные запросы). Это позволит сосредоточиться на изучении более сложных возможностей SQL (оконные функции, табличные выражения, сложные join'ы и разница их вариаций) в лабоработорной работе #3.

Также отмечу, что таблицы `notification` и `posttaglink` не были ни заполнены, ни использованы.
