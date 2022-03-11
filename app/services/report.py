from datetime import datetime
from typing import List

from app.core.config import settings
from app.models import Report, TwitterUser
from app.services.scrape import TwitterScraper


class ReportService:
    def get_report_list(self) -> List[Report]:
        """
        Get report list to display to Operator, but not display tweets
        """
        report_list = [report.to_response() for report in Report.objects]
        return report_list

    def add_report(self, username: str) -> Report:
        """
        Precondition: User must check_user before send report,
                      so no need to validate username or check if
                      user exist in DB
        Check if report exist in DB, if yes -> +1 to report_count
                                     if no -> add report to DB
        """
        report_db = Report.objects(username=username).first()

        if report_db is None:
            try:
                user = TwitterUser.objects(username=username).first()
                recent_tweets = TwitterScraper().get_tweet_info(
                    user.twitter_id, settings.TWEETS_NUMBER
                )
            except Exception as e:
                # Dunno wat wrong :))
                print("Something wrong: " + str(e))
            else:
                report_db = Report(
                    twitter_id=user.twitter_id,
                    name=user.name,
                    username=user.username,
                    created_at=user.created_at,
                    followers_count=user.followers_count,
                    followings_count=user.followings_count,
                    tweets=recent_tweets,
                    scrape_date=user.timestamp,
                    reset_date=datetime.now(),
                    report_count=1,
                )
        else:
            report_db.report_count += 1

        report_db.save()

        return report_db
