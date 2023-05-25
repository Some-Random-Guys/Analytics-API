import random
from wordcloud import WordCloud as wc
import matplotlib.pyplot as plt
import mplcyberpunk

from .DB import DB
from collections import Counter
from .helpers import get_top_users_by_words, get_top_words, get_top_channels_by_words


async def wordcloud(db: DB, guild_id: int, user_id: int = None, channel_id: int = None):
    messages = await get_top_words(db=db, guild_id=guild_id, user_id=user_id, channel_id=channel_id)

    # messages is a list of tuples
    # each tuple is (author_id, message_content)

    # get all the words
    messages = [message[1] for message in messages]
    print(messages[:5])
    words = []

    # create a wordcloud
    wordcloud = wc(width=1920, height=1080, background_color="black").generate(" ".join(words))

    # plot the wordcloud
    plt.figure(figsize=(16, 9))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    mplcyberpunk.add_glow_effects()

    # save image
    name = f"{random.randint(1, 100000000)}.png"
    try:
        plt.savefig(name, format='png')
    except Exception as e:
        print(e)

    plt.close()

    return name


async def get_top_users(db: DB, guild_id: int, type_: str, amount: int = 10):
    # type_ can be either "messages" or "words" or "characters"

    if type_ == "messages":
        db.cur.execute(
            f"""
                SELECT author_id, COUNT(author_id) AS count
                FROM `{guild_id}` WHERE is_bot = 0
                GROUP BY author_id
                ORDER BY count DESC
                LIMIT {amount};
            """
        )
        return db.cur.fetchall()

    elif type_ == "words":
        return await get_top_users_by_words(db=db, guild_id=guild_id, amount=amount)

    elif type_ == "characters":
        # get all messages
        db.cur.execute(
            f"""
                        SELECT author_id, message_content
                        FROM `{guild_id}` WHERE is_bot = 0
                    """
        )
        res = db.cur.fetchall()

        # Count characters for each user
        char_counts = Counter()

        for author_id, message in res:
            char_counts[author_id] += len(message)

        # Get the top users and their character counts
        top_users = char_counts.most_common()

        return top_users[:amount]


async def get_top_users_visual(db: DB, guild_id: int, client, type_: str, amount: int = 10) -> str:
    res = await get_top_users(db=db, guild_id=guild_id, type_=type_, amount=amount)
    plt.style.use("cyberpunk")

    # get member object from id and get their nickname, if not found, use "Deleted User"
    labels = []
    guild = client.get_guild(guild_id)

    for i in res:
        try:
            # get member
            member = guild.get_member(i[0])
            # get nickname
            labels.append(f"{member.nick or member.name} | {i[1]}")

        except Exception:
            labels.append("Unknown User")

    pie, texts, autotexts = plt.pie([value for _, value in res], labels=labels, autopct="%1.1f%%")

    for text in autotexts:
        text.set_color('black')

    for text in texts:
        text.set_color('white')

    plt.title(f"Top {amount} Members by {type_}")

    mplcyberpunk.add_glow_effects()

    # save image
    name = f"{random.randint(1, 100000000)}.png"
    try:
        plt.savefig(name, format='png', dpi=600)
    except Exception as e:
        print(e)

    plt.close()  # todo fix /UserWarning: Glyph 128017 (\N{SHEEP}) missing from current font.

    return name


async def get_top_channels(db: DB, guild_id: int, type_: str, amount: int = 10):
    if type_ == "messages":
        db.cur.execute(
            f"""
                SELECT channel_id, COUNT(author_id) AS count
                FROM `{guild_id}` WHERE is_bot = 0
                GROUP BY channel_id
                ORDER BY count DESC
                LIMIT {amount};
            """
        )
        return db.cur.fetchall()

    elif type_ == "words":
        return await get_top_channels_by_words(db=db, guild_id=guild_id, amount=amount)

    elif type_ == "characters":
        # get all messages
        db.cur.execute(
            f"""
                        SELECT channel_id, message_content
                        FROM `{guild_id}` WHERE is_bot = 0
                    """
        )
        res = db.cur.fetchall()

        # Count characters for each user
        char_counts = Counter()

        for channel_id, message in res:
            char_counts[channel_id] += len(message)

        # Get the top users and their character counts
        top_channels = char_counts.most_common()

        return top_channels[:amount]


async def get_top_channels_visual(db: DB, guild_id: int, client, type_: str, amount: int = 10) -> str:
    res = await get_top_channels(db=db, guild_id=guild_id, type_=type_, amount=amount)
    plt.style.use("cyberpunk")

    labels = []
    guild = client.get_guild(guild_id)

    for i in res:
        try:
            channel = await guild.fetch_channel(i[0])

            # get channel name
            labels.append(f"{channel.name} | {i[1]}")

        except Exception as e:
            labels.append(f"Unknown Channel | {i[1]}")

    pie, texts, autotexts = plt.pie([value for _, value in res], labels=labels, autopct="%1.1f%%")

    for text in autotexts:
        text.set_color('black')

    for text in texts:
        text.set_color('white')

    plt.title(f"Top {amount} Channels by {type_}")

    mplcyberpunk.add_glow_effects()

    # save image
    name = f"{random.randint(1, 100000000)}.png"
    try:
        plt.savefig(name, format='png', dpi=600)
    except Exception as e:
        print(e)

    plt.close()  # todo fix /UserWarning: Glyph 128017 (\N{SHEEP}) missing from current font.

    return name