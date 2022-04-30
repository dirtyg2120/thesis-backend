import pickle
import re
from importlib.resources import open_binary, open_text

import networkx as nx
import numpy as np
import pandas as pd
import torch

import model_data

from .sobog import SOBOG

_URL_PATTERN = r"[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"  # noqa: E501


class Inference:
    def __init__(self):
        self.user_columns = [
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

        self.model = self.load_model()
        with open_binary(model_data, "vectorizer.pk") as f:
            self.vectorizer = pickle.load(f)
        with open_text(model_data, "user_mean.csv") as f:
            self.user_mean = pd.read_csv(f)
        with open_text(model_data, "user_std.csv") as f:
            self.user_std = pd.read_csv(f)

    def create_user_dataframe(self, user):
        return pd.DataFrame([user], columns=self.user_columns)

    def preprocessing_user(self, user_df, user_mean, user_std):
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
        user_df.replace({False: 0, True: 1}, inplace=True)
        user_df = user_df.select_dtypes("number").fillna(0.0)
        return (user_df - user_mean) / user_std

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

    def vectorizing_tweet(self, tweets):
        v = self.vectorizer.transform(tweets)
        return v.A[np.newaxis, :]

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

    def generate_adj_matrix(self, graph):
        adj = nx.adjacency_matrix(graph).A
        np.fill_diagonal(adj, 1.0)
        return adj[np.newaxis, :]

    def generate_user_post_matrix(self, tweet_df):
        return (tweet_df["parent_id"] == 0).astype("int").values[np.newaxis, :]

    def inference(self, user, tweet, adj, up):
        user = torch.Tensor(user)
        tweet = torch.Tensor(tweet)
        adj = torch.Tensor(adj)
        up = torch.Tensor(up)
        user_pred, tweet_pred = self.model.forward(user, tweet, adj, up)
        return user_pred

    def predict(self, user_object, tweet_graph: nx.DiGraph) -> float:
        user_df = self.create_user_dataframe(user_object)
        user_df = self.preprocessing_user(user_df, self.user_mean, self.user_std)
        user = user_df.values

        adj = self.generate_adj_matrix(tweet_graph)
        tweets_text = np.array(
            [
                self.preprocessing_tweet(text)
                for _, text in tweet_graph.nodes(data="text", default="")
            ]
        )
        tweet = self.vectorizing_tweet(tweets_text)
        up = self.generate_user_post_matrix(tweet_df)
        user_pred = self.inference(user, tweet, adj, up)
        return user_pred.item()


if __name__ == "__main__":
    sample_user_object = [
        23,
        41,
        39,
        20,
        55,
        1.0,
        0.0,
        0.0,
        0.0,
        "2022/03/28 09:45:23.19485",
        "2021/02/28 13:30:34.00023",
        "Quoc Anh",
        "dirtygay2020",
        "Some description here",
    ]
    sample_tweet_object = pd.DataFrame(
        [
            {"id": 30492, "text": "This tweet is written by TQA", "parent_id": 0},
            {"id": 31949, "text": "That's right", "parent_id": 30492},
            {"id": 31950, "text": "Are you sure?", "parent_id": 30492},
            {"id": 31958, "text": "Definitely", "parent_id": 31950},
            {"id": 32223, "text": "This is my second tweet", "parent_id": 0},
            {"id": 32294, "text": "Yes! Keep posting new ones!", "parent_id": 32223},
            {"id": 34449, "text": "Don't reply this", "parent_id": 0},
        ]
    )
    inf = Inference()
    print(inf.predict(sample_user_object, sample_tweet_object))
