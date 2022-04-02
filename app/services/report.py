from typing import List

from fastapi import Depends, HTTPException

from app.models import Report, TwitterUser
from app.schemas.report import ReportResponse

from .scrape import TwitterScraper


class ReportService:
    def __init__(self, twitter_scraper: TwitterScraper = Depends()):
        self.twitter_scraper = twitter_scraper

    def get_report_list(self) -> List[ReportResponse]:
        """
        Get report list to display to Operator, but not display tweets
        """
        report_list = [report.to_response() for report in Report.objects]
        return report_list


    def add_report(self, twitter_id: str, reporter_id: str) -> Report:
        """
        Precondition: User must check_user before send report,
                      so no need to validate username or check if
                      user exist in DB
        Check if report exist in DB, if yes -> +1 to report_count
                                     if no -> add report to DB
        """
        report_db = Report.objects(twitter_id=twitter_id, expired=False).first()
        user = TwitterUser.objects(twitter_id=twitter_id).first()

        if user is None:
            if report_db:
                report_db.update(expired=True)
            raise HTTPException(404, "Twitter account has not been checked")

        if report_db is None:

            report_db = Report(
                twitter_id=user.twitter_id,
                tweets_count=user.tweets_count,
                name=user.name,
                username=user.username,
                created_at=user.created_at,
                followers_count=user.followers_count,
                followings_count=user.followings_count,
                favourites_count=user.favourites_count,
                listed_count=user.listed_count,
                default_profile=user.default_profile,
                default_profile_image=user.default_profile_image,
                protected=user.protected,
                avatar=user.avatar,
                verified=user.verified,
                tweets=user.tweets,
                scrape_date=user.timestamp,
                reporters=[reporter_id],
                score=user.score,
                expired=True if user is None else False,
            )
        else:
            if reporter_id in report_db.reporters:
                raise HTTPException(
                    status_code=420,
                    detail="User already reported this Twitter Account Recently!",
                )

            report_db.reporters.append(reporter_id)

        report_db.save()
        return report_db
