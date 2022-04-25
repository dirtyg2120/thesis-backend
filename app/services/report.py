from typing import List

from fastapi import Depends, HTTPException

from app.models import BotPrediction, ProcessedReport, Report
from app.models.report import ReportKey
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
        report_db = Report.objects(
            report_key__twitter_id=twitter_id, expired=False
        ).first()
        prediction_db = BotPrediction.objects(user__twitter_id=twitter_id).first()

        if prediction_db is None:
            if report_db:
                report_db.update(expired=True)
            raise HTTPException(404, "Twitter account has not been checked")

        if report_db is None:
            report_db = Report(
                report_key=ReportKey(
                    twitter_id=prediction_db.user.twitter_id,
                    scrape_date=prediction_db.timestamp,
                ),
                user=prediction_db.user,
                tweets=prediction_db.tweets,
                reporters=[reporter_id],
                score=prediction_db.score,
                expired=prediction_db is None,
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

    def process_report(self, twitter_id: str, method: str):
        report_db = Report.objects(
            report_key__twitter_id=twitter_id, expired=False
        ).first()
        full_details = full_details = self.twitter_scraper.get_full_details(
            twitter_id, tweets_num=2
        )
        label = int()
        if method == "approve":
            label = 1 if report_db.score >= 0.5 else 0
        elif method == "reject":
            label = 0 if report_db.score >= 0.5 else 1

        ProcessedReport.objects(twitter_id=twitter_id).update_one(
            user=full_details._json, label=label, upsert=True
        )
