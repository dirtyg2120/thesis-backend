import logging
from datetime import datetime, timedelta

import networkx as nx
import tweepy

import model
from app.utils import Singleton

from .scrape import TwitterID, TwitterScraper


class ML(metaclass=Singleton):
    def __init__(self):
        logger = logging.getLogger("app")
        logger.warning("Create ML")
        self._scraper = TwitterScraper()
        self._inference = model.Inference()

    def train(self):
        # TODO: for train / re-train purpose
        pass

    def get_analysis_result(self, username: str):
        user_api = self._scraper.get_user_by_username(username)
        user = self.make_ml_user(user_api)
        tweets = self.get_ml_tweets(user_api.id)
        return self._inference.predict(user, tweets), user_api, tweets

    def _create_retweet_node(
        self, tweet_graph: nx.DiGraph, tweet: tweepy.Tweet
    ) -> None:
        """Create a fake tweet node representing all of tweet's retweets"""
        if tweet.public_metrics["retweet_count"] > 0:
            retweet_node = "RT" + str(tweet.id)
            retweet_text = f"RT @usertag: {tweet.text}"
            tweet_graph.add_node(retweet_node, text=retweet_text)
            tweet_graph.add_edge(
                tweet.id, retweet_node, weight=tweet.public_metrics["retweet_count"]
            )

    def _create_tweet_subgraph(self, tweet: tweepy.Tweet) -> nx.DiGraph:
        """
        Create a subgraph rooted at tweet that contains all its replies and retweets.
        """
        tweet_graph = nx.DiGraph()
        tweet_graph.add_node(tweet.id, text=tweet.text)
        self._create_retweet_node(tweet_graph, tweet)

        conversation = self._scraper.get_conversation(tweet.conversation_id)
        for descendant in conversation:
            tweet_graph.add_node(descendant.id, text=descendant.text)
            for referenced in descendant.referenced_tweets:
                if referenced.type == "replied_to":
                    tweet_graph.add_edge(referenced.id, descendant.id)
            self._create_retweet_node(tweet_graph, descendant)

        # Remove unreachable tweets, e.g., replies of deleted tweets
        reachable_nodes = nx.descendants(tweet_graph, tweet.id) | {tweet.id}
        unreachable_nodes = tweet_graph.nodes - reachable_nodes
        tweet_graph.remove_nodes_from(unreachable_nodes)
        return tweet_graph

    def get_ml_tweets(self, user_id: TwitterID) -> nx.DiGraph:
        # NOTE: Can only fetch tweets in a conversation in last 7 days
        # without Academic Research access
        duration = timedelta(days=7)
        now = datetime.utcnow()
        last_week = now - duration
        tweet_graphs = list(
            map(
                self._create_tweet_subgraph,
                tweepy.Paginator(
                    self._scraper.api_v2.get_users_tweets,
                    id=user_id,
                    tweet_fields=["conversation_id", "public_metrics"],
                    exclude=["replies", "retweets"],
                    start_time=last_week.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    max_results=100,
                ).flatten(),
            )
        )
        if tweet_graphs:
            return nx.compose_all(tweet_graphs)
        else:
            return nx.DiGraph()

    def make_ml_user(self, user_api: tweepy.models.User):
        user = {"updated": datetime.utcnow()}
        for field in model.Inference.USER_COLUMNS - {"updated"}:
            user[field] = getattr(user_api, field)
        return user
