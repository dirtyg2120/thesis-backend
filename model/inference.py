import pickle
import re
from importlib.resources import open_binary

import networkx as nx
import numpy as np
import pandas as pd
import torch

import model_data

from .sobog import SOBOG

_URL_PATTERN = r"[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"  # noqa: E501


class Inference:
    USER_COLUMNS = [
        "statuses_count",
        "followers_count",
        "friends_count",
        "favourites_count",
        "listed_count",
        "default_profile",
        "default_profile_image",
        "protected",
        "verified",
        "updated",
        "created_at",
        "name",
        "screen_name",
        "description",
    ]

    def __init__(self):
        self.model = self.load_model()
        with open_binary(model_data, "vectorizer.pk") as f:
            self.vectorizer = pickle.load(f)
        with open_binary(model_data, "user_mean.pk") as f:
            self.user_mean: pd.Series = pd.read_pickle(f)
        with open_binary(model_data, "user_std.pk") as f:
            self.user_std: pd.Series = pd.read_pickle(f)

    def preprocessing_user(self, user_dict, user_mean, user_std):
        user_df = pd.DataFrame.from_records([user_dict], columns=self.USER_COLUMNS)
        if "updated" in user_df.columns:
            age = (
                pd.to_datetime(user_df.loc[:, "updated"])
                - pd.to_datetime(user_df.loc[:, "created_at"]).dt.tz_localize(None)
            ) / np.timedelta64(1, "Y")
        else:
            age = (
                pd.to_datetime(pd.to_datetime("today"))
                - pd.to_datetime(user_df.loc[:, "created_at"]).dt.tz_localize(None)
            ) / np.timedelta64(1, "Y")
        user_df["tweet_freq"] = user_df["statuses_count"] / age
        user_df["followers_growth_rate"] = user_df["followers_count"] / age
        user_df["friends_growth_rate"] = user_df["friends_count"] / age
        user_df["favourites_growth_rate"] = user_df["favourites_count"] / age
        user_df["listed_growth_rate"] = user_df["listed_count"] / age
        user_df["followers_friends_ratio"] = user_df["followers_count"] / np.maximum(
            user_df["friends_count"], 1
        )
        user_df["screen_name_length"] = user_df["screen_name"].str.len()
        user_df["num_digits_in_screen_name"] = user_df["screen_name"].str.count(r"\d")
        user_df["name_length"] = user_df["name"].str.len()
        user_df["num_digits_in_name"] = user_df["name"].str.count(r"\d")
        user_df["description_length"] = user_df["description"].str.len()
        normalized_user_df = (user_df[user_mean.index] - user_mean) / user_std
        return normalized_user_df.iloc[0]

    def preprocessing_tweet(self, row):
        rowlist = str(row).split()
        rowlist = [word.strip() for word in rowlist]
        rowlist = [
            word if not word.strip().startswith("#") else "hashtagtag"
            for word in rowlist
        ]
        rowlist = [
            word if not word.strip().startswith("@") else "usertag" for word in rowlist
        ]
        rowlist = [word.lower() for word in rowlist]
        rowlist = [re.sub(_URL_PATTERN, "urltag", word) for word in rowlist]
        return " ".join(rowlist)

    def load_model(self):
        model_dict = {
            "n_user_features": 20,
            "d_user_embed": 20,
            "n_post_features": 5000,
            "d_post_embed": 64,
            "n_gat_layers": 3,
            "d_cls": 32,
            "n_cls_layer": 2,
        }
        model = SOBOG(gpu=0, **model_dict)
        with open_binary(model_data, "model.pt") as f:
            state_dict = torch.load(f, map_location=torch.device("cpu"))
        model.load_state_dict(state_dict)
        model.eval()
        return model

    def inference(self, user, tweet, adj, up):
        # First axis is batch size
        user = torch.Tensor(user).unsqueeze(0)
        tweet = torch.Tensor(tweet).unsqueeze(0)
        adj = torch.Tensor(adj).unsqueeze(0)
        up = torch.Tensor(up).unsqueeze(0)
        user_pred, tweet_pred = self.model.forward(user, tweet, adj, up)
        return user_pred

    def predict(self, user_dict, tweet_graph: nx.DiGraph) -> float:
        user = self.preprocessing_user(user_dict, self.user_mean, self.user_std)

        adj = nx.adjacency_matrix(tweet_graph).A
        np.fill_diagonal(adj, 1.0)

        tweets_text = (
            self.preprocessing_tweet(text)
            for _, text in tweet_graph.nodes(data="text", default="")
        )
        tweet = self.vectorizer.transform(tweets_text).A

        # Not use user post matrix for now
        user_pred = self.inference(user, tweet, adj, [])
        return user_pred.item()


if __name__ == "__main__":
    from datetime import datetime

    sample_user_object = {
        "statuses_count": 23,
        "followers_count": 41,
        "friends_count": 39,
        "favourites_count": 20,
        "listed_count": 55,
        "default_profile": 1,
        "default_profile_image": 0,
        "protected": 0,
        "verified": 0,
        "updated": datetime.fromisoformat("2022-03-28T09:45:23"),
        "created_at": datetime.fromisoformat("2021-02-28T13:30:34"),
        "name": "Quoc Anh",
        "screen_name": "dirtygay2020",
        "description": "Some description here",
    }

    sample_tweet_graph = nx.DiGraph()
    nodes = [
        (30492, {"text": "This tweet is written by TQA"}),
        (31949, {"text": "That's right"}),
        (31950, {"text": "Are you sure?"}),
        (31958, {"text": "Definitely"}),
        (32223, {"text": "This is my second tweet"}),
        (32294, {"text": "Yes! Keep posting new ones!"}),
        (34449, {"text": "Don't reply this"}),
    ]
    edges = [(30492, 31949), (30492, 31950), (31950, 31958), (32223, 32294)]
    sample_tweet_graph.update(nodes=nodes, edges=edges)

    inf = Inference()
    print(inf.predict(sample_user_object, sample_tweet_graph))
