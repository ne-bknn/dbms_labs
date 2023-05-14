### Search for a user by username

Query: `SELECT username FROM user WHERE username LIKE '%Cat%' LIMIT 10;`

```
------------
username
Nuclear_Cat
Punching_Cat
------------
```



### Amount of English users

Query: `SELECT COUNT(*) FROM user WHERE primary_language = 'en';`

```
--------
COUNT(*)
112
--------
```



### Users by language

Query: `SELECT primary_language, COUNT(*) FROM user GROUP BY primary_language LIMIT 10;`

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



### Amount of posts by user

Query: `SELECT COUNT(*) FROM post WHERE owner = 'Death_Louce';`

```
--------
COUNT(*)
0
--------
```



### Top users by amount of posts

Query: `SELECT username, COUNT(*) as n_posts FROM post JOIN user ON post.owner = user.id group by username order by n_posts desc LIMIT 10;`

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



### Top posts by amount of comments

Query: `SELECT comment_for AS parent, COUNT(*) AS n_comments FROM post WHERE parent IS NOT NULL GROUP BY parent ORDER BY n_comments DESC LIMIT 10;`

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



### Total CDN usage, in MB

Query: `SELECT (SUM(size) / 1024 / 1024) AS total_size FROM attachment;`

```
----------
total_size
4913
----------
```



### CDN usage by user, in MB

Query: `SELECT username, (SUM(size) / 1024 / 1024) as storage_used FROM attachment JOIN user ON attachment.owner_id = user.id GROUP BY username LIMIT 10;`

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



### Average subscribers per privacy status

Query: `SELECT is_private, AVG(n_subscribers) as subscribers_average FROM (SELECT followee, user.is_private, COUNT(*) AS n_subscribers FROM subscription JOIN user ON followee = user.id  GROUP BY followee  ORDER BY n_subscribers DESC) GROUP BY is_private;`

```
----------  -------------------
is_private  subscribers_average
0           5.902439024390244
1           1.0
----------  -------------------
```



