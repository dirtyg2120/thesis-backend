from typing import List

from fastapi import Depends, HTTPException

from app.models import BotPrediction
from app.models.report import Report, ReportKey
from app.schemas.report import ReportResponse

from .scrape import TwitterScraper


class ReportService:
    def __init__(self, twitter_scraper: TwitterScraper = Depends()):
        self._scraper = twitter_scraper

    def _make_response(self, report: Report) -> ReportResponse:
        twitter_id = report.report_key.twitter_id
        user = self._scraper.get_user_by_id(twitter_id)
        return ReportResponse(
            id=report.report_key.twitter_id,
            avatar=user.profile_image_url,
            username=user.screen_name,
            created_at=user.created_at,
            scrape_date=report.report_key.scrape_date,
            report_count=len(report.reporters),
            score=report.score,
        )

    def get_report_list(self) -> List[ReportResponse]:
        """
        Get report list to display to Operator, but not display tweets
        """
        return list(map(self._make_response, Report.objects))

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
        prediction_db = BotPrediction.objects(user_id=twitter_id).first()

        if prediction_db is None:
            if report_db:
                report_db.update(expired=True)
            raise HTTPException(404, "Twitter account has not been checked")

        if report_db is None:
            report_db = Report(
                report_key=ReportKey(
                    twitter_id=twitter_id,
                    scrape_date=prediction_db.timestamp,
                ),
                reporters=[reporter_id],
                score=prediction_db.score,
                expired=False,
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
