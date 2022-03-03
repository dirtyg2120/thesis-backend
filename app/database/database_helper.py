def profile_helper(profile) -> dict:
    return {
        "twitter_id": str(profile["twitter_id"]),
        "name": profile["name"],
        "username": profile["username"],
        "created_at": profile["created_at"],
        "followers_count": profile["followers_count"],
        "followings_count": profile["followings_count"],
        "avatar": profile["avatar"],
        "banner": profile["banner"],
    }
