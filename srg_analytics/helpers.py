from .DB import DB
from collections import Counter


async def is_ignored(db: DB, channel_id: int = None, user_id: int = None):
    if channel_id is None and user_id is None:
        raise ValueError("channel_id and user_id cannot both be None")

    channel_ignored = False
    user_ignored = False

    # Ignore based on channel_id
    if channel_id is not None:
        db.cur.execute(
            f"""
                        SELECT * FROM `config` WHERE data1 = {channel_id} AND _key = 'channel_ignore'
                    """
        )
        res = db.cur.fetchone()
        try:
            channel_ignored = res[0] == channel_id
        except TypeError:
            channel_ignored = False

    # Ignore based on user_id
    if user_id is not None:
        db.cur.execute(
            f"""
                        SELECT data1 FROM `config` WHERE data1 = {user_id} AND _key = 'user_ignore';
                    """
        )
        # get the data1 and check if it is equal to user_id
        res = db.cur.fetchone()
        try:
            user_ignored = res[0] == user_id
        except TypeError:
            user_ignored = False

    if True in [channel_ignored, user_ignored]:
        return True
