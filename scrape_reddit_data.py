import os
import pandas as pd
import praw
from dotenv import load_dotenv
from typing import Optional, List, Dict

load_dotenv()


class APIClient:
    def __init__(self, subreddits: List[str], search_terms: List[str]):
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = os.getenv("REDDIT_USER_AGENT")

        # initialize search_terms and subreddit
        self.search_terms = search_terms
        self.subreddits = subreddits
        self.time_filters = ["day", "week", "month", "year", "all"]

        self.reddit: Optional[praw.Reddit] = None
        self.posts: List[Dict] = []

    def connect(self) -> None:
        # try to connect to reddit via praw
        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
            )

            # Test connection
            _ = self.reddit.user.me()
            print("Reddit client initialized successfully.")

        except Exception as e:
            print(f"Failed to initialize Reddit client: {e}")
            raise

    def fetch_posts(self, limit: int = 100) -> None:
        # check if reddit is connected
        if not self.reddit:
            raise RuntimeError("Reddit client not initialized. Call connect() first.")

        try:
            # search individual keyword for each subreddit
            for subreddit in self.subreddits:
                for keyword in self.search_terms:
                    for time_filter in self.time_filters:
                        print(f"Searching '{keyword}' in r/{subreddit}...")

                        for post in self.reddit.subreddit(subreddit).search(
                            keyword, sort="top", limit=limit, time_filter=time_filter
                        ):
                            self.posts.append(
                                {
                                    "id": post.id,
                                    "title": post.title,
                                    "selftext": post.selftext,
                                    "score": post.score,
                                    "num_comments": post.num_comments,
                                    "view_count": post.view_count,
                                    "upvote_ratio": post.upvote_ratio,
                                    "subreddit": post.subreddit.display_name,
                                    "created_utc": post.created_utc,
                                }
                            )

            print(f"Fetched {len(self.posts)} posts.")
        except Exception as e:
            print(f"Failed to fetch posts: {e}")
            raise

    def export_to_dataframe(self) -> pd.DataFrame:
        if not self.posts:
            raise ValueError("No posts to export.")
        data = pd.DataFrame(self.posts)
        print("📦 Exported posts to DataFrame.")
        return data


if __name__ == "__main__":
    client = APIClient(
        # subreddits=['GooglePixel']
        # subreddit=['iphone']
        subreddits=["samsunggalaxy"],
        search_terms=[
            "honest review",
            "first impression",
            "user experience",
            "worst thing about",
            "why I returned it",
            "issue",
            "pros and cons",
            "is it worth it",
            "regret buying",
            "it keeps crashing",
            "battery issue",
            "buggy update",
            "customer service",
            "I wish it had",
            "feature request",
            "missing feature",
            "they should add",
            "improvement idea",
        ],
    )

    client.connect()
    client.fetch_posts(limit=100)
    df = client.export_to_dataframe()
    df.to_csv("reddit_api_galaxy.csv")
    df.to_csv("reddit_api_googlepixel.csv")
    df.to_csv("reddit_api_iPhone.csv")
    print(df.head())
