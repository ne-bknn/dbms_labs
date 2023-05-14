import random
import time
from string import ascii_lowercase, digits

import lorem  # type: ignore

from typing import Any, Self, Union

dictionary = [k.strip() for k in open("dictionary.txt", "r").read().splitlines()]


class Query:
    def __init__(self, query: str, values: list[Any]) -> None:
        self.query: str = query
        self.values: list[Any] = values


class AbstractTable:
    """AbstractTable usage:
    ```
    obj = AbstractTable()
    insert_instruction = obj.generate_insert()
    cursor.execute(insert_instruction.query, insert_instruction.values)
    id = cursor.lastrowid
    obj.set_id(id)
    ```
    """

    def set_id(self, id: int) -> None:
        self._id: None | int = id

    def generate_insert(self) -> Query:
        fields = [field for field in self.__dict__.keys() if not field.startswith("_")]
        values = [getattr(self, field) for field in fields]

        table_name = (
            self._table_name
            if hasattr(self, "_table_name")
            else self.__class__.__name__.lower()
        )

        return Query(
            f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({', '.join(['?' for _ in fields])})",  # noqa: E501
            values,
        )


class User(AbstractTable):
    def __init__(self) -> None:
        self.username: str = self.generate_username()
        self.password: str = self.generate_password()
        self.email: str = self.generate_email(self.username)
        self.primary_language: str = self.generate_primary_language()
        self.is_private: bool = self.generate_is_private()
        self._id: int | None = None

    @staticmethod
    def generate_primary_language() -> str:
        return random.choice(["en", "pl", "de", "fr", "es", "ru", "it", "cn"])

    @staticmethod
    def generate_username() -> str:
        # fmt: off
        adjs: list[str] = ["Airborne", "Alive", "Amber", "Armor", "Armored", "Arsenal", "Ashen", "Assassin", "Assault", "Bastard", "Battle", "Big", "Biting", "Bitter", "Black", "Black", "Arts", "Blazing", "Bloody", "Blue", "Bolt", "Brass", "Bronze", "Brown", "Brutal", "Bullet", "Cannibal", "Charging", "Code", "Cold", "Command", "Copper", "Coward", "Crawling", "Creeping", "Crimson", "Crying", "Crystal", "Cunning", "Cyborg", "Dark", "Dead", "Death", "Decoy", "Devil", "Diamond", "Dire", "Dirty", "Dizzy", "Doom", "Eastern", "Emergency", "Engineer", "Espionage", "Evasion", "Fat", "Fire", "Flaming", "Flying", "Frantic", "Frigid", "Garnet", "Ghost", "Glacier", "Goblin", "Gold", "Golden", "Gray", "Greedy", "Green", "Grizzly", "Growling", "Hissing", "Hot", "Howling", "Hulking", "Hungry", "Hunting", "Infinity", "Intelligence", "Iron", "Jungle", "Killer", "King", "Laughing", "Liquid", "Little", "Lonely", "Lost", "Love", "Machinegun", "Mad", "Marionette", "Master", "Medical", "Metal", "Midnight", "Military", "Naked", "New", "Night", "Northern", "Nuclear", "Ochre", "Old", "Otaku", "Panzer", "Peace", "Phantom", "Pink", "Pirate", "Platinum", "Poison", "Police", "Pouncing", "Praying", "Predator", "Prowling", "Psycho", "Punching", "Punished", "Purple", "Pyro", "Queen", "Rabid", "Radio", "Raging", "Rampant", "Rancid", "Ranger", "Raving", "Razor", "Recon", "Red", "Rescue", "Resistance", "Revolver", "Riot", "Roaring", "Rogue", "Rose", "Rumble", "Running", "Sadistic", "Scout", "Scowling", "Screaming", "Security", "Seething", "Sentinel", "Service", "Shadow", "Shining", "Shoot", "Sight", "Signal", "Silent", "Silver", "Sinister", "Skull", "Slasher", "Sly", "Small", "Smoking", "Snatcher", "Sniper", "Solid", "Solidus", "Southern", "Special", "Spitting", "Spunky", "Spying", "Stalking", "Steel", "Stone", "Strange", "Striker", "Stubborn", "Sunny", "Survival", "Sword", "Tactical", "Technical", "The", "Thunder", "Ultra", "Vampire", "Vengeful", "Venom", "Vic", "Vile", "Vulcan", "Warfare", "Western", "White", "Wild", "Yellow", "Zero"]  # noqa: E501
        animals: list[str] = ["Agama", "Alligator", "Anaconda", "Ant", "Ape", "Armadillo", "Baboon", "Badger", "Barracuda", "Basilisk", "Bat", "Bear", "Beast", "Beauty", "Bee", "Beetle", "Bison", "Bluebird", "Boa", "Boss", "Buffalo", "Bull", "Butterfly", "Buzzard", "Camel", "Canine", "Capybara", "Cat", "Centipede", "Chameleon", "Chick", "Chicken", "Cobra", "Cow", "Coyote", "Crab", "Crocodile", "Crow", "Deer", "Dingo", "Doberman", "Dolphin", "Dragon", "Duck", "Eagle", "Eel", "Elephant", "Falcon", "Firefly", "Flying", "Fox", "Flying", "Squirrel", "Fox", "Frill", "Shark", "Frog", "Gator", "Gazelle", "Gecko", "Giant", "Panda", "Gibbon", "Goat", "Gorilla", "Gull", "Gunner", "Harrier", "Hawk", "Hedgehog", "Heron", "Hippo", "Hippopotamus", "Hog", "Hornet", "Horse", "Hound", "Husky", "Hyena", "Iguana", "Inchworm", "Jackal", "Jaguar", "Jaws", "Kangaroo", "Kerotan", "Kid", "Koala", "Komodo", "Dragon", "Leech", "Leopard", "Lion", "Little", "Gray", "Lobster", "Mammoth", "Mantis", "Markhor", "Marlin", "Mastiff", "Mastodon", "Mongoose", "Moose", "Mosquito", "Moth", "Mouse", "Mustang", "Night", "Owl", "Ninja", "Ocelot", "Octopus", "Ogre", "Orca", "Osprey", "Ostrich", "Ox", "Panther", "Parrot", "Peccay", "Pig", "Pigeon", "Piranha", "Platypus", "Puma", "Python", "Rabbit", "Ram", "Raptor", "Rat", "Raven", "Ray", "Rhino", "Roach", "Rooster", "Salamander", "Scorpion", "Sea", "Louce", "Serpent", "Shark", "Sloth", "Slug", "Snake", "Spider", "Squirrel", "Stallion", "Sturgeon", "Swallow", "Tarantula", "Tasmanian", "Devil", "Tengu", "Tiger", "Tortoise", "Tree", "Frog", "Tsuchinoko", "Skipjack", "Tuna", "Swan", "Turtle", "Viper", "Vulture", "Wallaby", "Wasp", "Werewolf", "Whale", "Wolf", "Worm", "Yoshi", "Zebra"]  # noqa: E501
        # fmt: on

        return f"{random.choice(adjs)}_{random.choice(animals)}"

    @staticmethod
    def generate_password() -> str:
        # it was argon2id, but its too slow for generated data
        return "".join(random.choices(ascii_lowercase + digits, k=10))

    @staticmethod
    def generate_email(username) -> str:
        adj = username.split("_")[0]
        animal = username.split("_")[1]
        mailname = f"{adj[0]}.{animal}"
        return f"{mailname}@{random.choice(['gmail.com', 'yahoo.com', 'hotmail.com', 'protonmail.com', 'outlook.com'])}"  # noqa: E501

    @staticmethod
    def generate_is_private() -> bool:
        return random.choice([True, True, True, False])

    def subscribe(self, other: "User") -> Union["Subscription", "FollowRequest"]:
        return (
            Subscription(other, self)
            if not self.is_private
            else FollowRequest(other, self)
        )

    def ban(self, other: "User") -> "UserBan":
        return UserBan(other, self)


class Attachment(AbstractTable):
    def __init__(self, owner: User):
        self._id: int | None = None
        self._owner = owner
        self.owner_id = owner._id
        self.mime = self.generate_mime()
        self.name = self.generate_filename(self.mime)
        self.size = random.randint(1, 1000000)
        self.storage_url = self.generate_url(self.name, self._owner)

    @staticmethod
    def generate_mime() -> str:
        return random.choice(
            [
                "image/jpeg",
                "image/png",
                "image/gif",
                "image/webp",
                "video/mp4",
                "video/webm",
                "video/mpeg",
            ]
        )

    @staticmethod
    def generate_filename(mime: str) -> str:
        format = mime.split("/")[1]
        # fmt: off
        return f"{random.choice(['cat', 'dog', 'fox', 'wolf', 'bird', 'fish', 'horse', 'snake', 'lizard', 'frog', 'turtle', 'hamster', 'rabbit', 'mouse', 'rat', 'pig', 'cow', 'sheep', 'goat', 'chicken', 'duck', 'goose', 'penguin', 'bear', 'panda', 'koala', 'tiger', 'lion', 'leopard', 'cheetah', 'jaguar', 'panther', 'hippo', 'rhino', 'elephant', 'giraffe', 'zebra', 'monkey', 'gorilla', 'orangutan', 'chimpanzee', 'baboon', 'lemur', 'squirrel', 'chipmunk', 'beaver', 'otter', 'raccoon', 'skunk', 'badger', 'weasel', 'ferret', 'mink', 'seal', 'walrus', 'dolphin', 'whale', 'shark', 'fish', 'squid', 'octopus', 'jellyfish', 'crab', 'lobster', 'shrimp', 'snail', 'slug', 'butterfly', 'bee', 'wasp', 'ant', 'dragonfly', 'mosquito', 'fly', 'beetle', 'grasshopper', 'cricket', 'cicada', 'cockroach', 'praying mantis', 'walking stick', 'ladybug', 'spider', 'scorpion', 'centipede', 'millipede', 'earthworm', 'leech', 'slug', 'snake', 'lizard', 'turtle', 'crocodile', 'alligator', 'iguana', 'chameleon', 'gecko', 'salamander', 'newt', 'axolotl', 'frog', 'toad', 'newt', 'salamander', 'caecilian', 'tarantula', 'scorpion', 'millipede', 'centipede', 'crab', 'lobster', 'shrimp', 'barnacle', 'clam', 'oyster', 'snail', 'slug', 'squid', 'octopus', 'jellyfish', 'coral', 'sponge'])}_{str(random.randint(0, 99999999)).zfill(8)}.{format}"  # noqa: E501
        # fmt: on

    @staticmethod
    def generate_url(filename: str, owner: User) -> str:
        cdns = [
            "https://cdn1.tw2tter.com",
            "https://cdn2.tw2tter.com",
            "https://cdn3.tw3tter.com",
        ]

        return f"{random.choice(cdns)}/{owner.username}/{filename}"

    @staticmethod
    def generate_size() -> int:
        return random.randint(1, 10000000)


class Post(AbstractTable):
    def __init__(
        self,
        owner: User,
        repost_of: Self | None = None,
        comment_for: Self | None = None,
        hashtags: list["Hashtag"] | None = None,
        attachment: Attachment | None = None,
    ):
        self._id: int | None = None
        self._owner = owner
        self._comment_for: Self | None = comment_for
        self._repost_of: Self | None = repost_of
        self.owner = owner._id
        self._hashtags = hashtags or []
        self.text = self.generate_text()
        self._attachment = attachment
        self.attachment = attachment._id if attachment else None
        if self._comment_for and self._repost_of:
            raise ValueError("Post cannot be both a reply and a repost")

        self.comment_for = self._comment_for._id if self._comment_for else None
        self.repost_of = self._repost_of._id if self._repost_of else None

    def generate_text(self) -> str:
        hashtags = " " + " ".join(f"#{h.slug}" for h in self._hashtags)
        if self._comment_for or self._repost_of:
            return lorem.sentence() + hashtags

        decider = random.random()
        if decider < 0.1:
            return lorem.sentence() + hashtags
        else:
            return lorem.paragraph() + hashtags

    def upvote(self, user: User) -> "Upvote":
        return Upvote(user, self)


class Subscription(AbstractTable):
    def __init__(self, follower: User, followee: User):
        self.follower = follower._id
        self.followee = followee._id

    def set_id(self, id: int):
        raise NotImplementedError("No id for subscriptions")


class FollowRequest(AbstractTable):
    def __init__(self, from_user: User, to_user: User):
        self.from_user = from_user._id
        self.to_user = to_user._id

        self._from_user = from_user
        self._to_user = to_user

        self._table_name = "follow_request"

    def set_id(self, id: int):
        raise NotImplementedError("No id for follow requests")

    def accept(self) -> tuple[Query, Subscription]:
        delete_query = (
            f"DELETE FROM {self._table_name} WHERE from_user = ? AND to_user = ?"
        )
        args = [self.from_user, self.to_user]

        return Query(delete_query, args), Subscription(self._from_user, self._to_user)


class UserBan(AbstractTable):
    def __init__(self, user: User, by_user: User):
        self.user = user._id
        self.by_user = by_user._id
        self._table_name = "user_ban"

    def set_id(self, id: int):
        raise NotImplementedError("No id for user bans")


class Notification(AbstractTable):
    def __init__(self, user: User, post: Post):
        self.notifiable_id = user._id
        self.post_id = post._id


class Upvote(AbstractTable):
    def __init__(self, user: User, post: Post):
        self.user_id = user._id
        self.post_id = post._id

    def set_id(self, id: int):
        raise NotImplementedError("No id for upvotes")


class Hashtag(AbstractTable):
    def __init__(self) -> None:
        self._id: int | None = None
        self.slug = self.generate_slug()

    @staticmethod
    def generate_slug() -> str:
        return random.choice(dictionary)


class RoleTypes:
    def __init__(self) -> None:
        self.roles = [
            "generic",
            "verified",
            "republican",
            "shadowbanned",
            "moderator",
            "elon_musk",
        ]

        self.slug_to_id: dict[str, int] = {}

    def generate_inserts(self) -> list[Query]:
        return [
            Query("INSERT INTO role_types (name) VALUES (?)", [role])
            for role in self.roles
        ]

    def set_id(self, slug: str, id: int):
        self.slug_to_id[slug] = id


class Role(AbstractTable):
    def __init__(self, user: User, role_types: RoleTypes) -> None:
        self._possible_roles: list[tuple[str, float]] = [
            ("generic", 89.0),
            ("verified", 7.0),
            ("republican", 1.0),
            ("shadowbanned", 1.0),
            ("moderator", 1.0),
            ("elon_musk", 1.0),
        ]

        self._role_types = role_types
        self.role_type_id = self.generate_slug()
        self._user = user
        self.user_id = user._id

    def generate_slug(self) -> int:
        chosen_role = random.choices(
            self._possible_roles,
            cum_weights=[w for _, w in self._possible_roles],
            k=1,
        )[0][0]

        return self._role_types.slug_to_id[chosen_role]

    def set_id(self, id: int):
        raise NotImplementedError("No id for roles")


class PlatformBan(AbstractTable):
    def __init__(self, user: User):
        self.user_id = user._id
        self._user = user
        self._table_name = "platform_ban"
        self.until = self.generate_until()
        self.reason = self.generate_reason()

    @staticmethod
    def generate_reason() -> str:
        return random.choice(
            [
                "spam",
                "harassment",
                "offensive content",
                "impersonation",
            ]
        )

    @staticmethod
    def generate_until() -> int:
        now = int(time.time())
        return int(now + random.normalvariate(50_000, 100_000))
