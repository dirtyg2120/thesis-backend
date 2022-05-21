from typing import List

from fastapi import Depends, HTTPException

from app.models import BotPrediction, ProcessedReport
from app.models.report import Report, ReportKey
from app.schemas.report import (
    ApprovedReport,
    ProcessedReportResponse,
    ReportResponse,
    WaitingReport,
)

from .ml import ML
from .scrape import TwitterScraper


class ReportService:
    def __init__(self, twitter_scraper: TwitterScraper = Depends(), ml: ML = Depends()):
        self._scraper = twitter_scraper
        self._ml = ml

    def _make_waiting_report(self, report: Report) -> WaitingReport:
        user = report.user
        return WaitingReport(
            id=report.report_key.twitter_id,
            avatar=user.avatar,
            username=user.screen_name,
            created_at=user.created_at,
            scrape_date=report.report_key.scrape_date,
            report_count=len(report.reporters),
            score=report.score,
        )

    def _make_approved_report(self, report) -> ApprovedReport:
        user = report.user
        return ApprovedReport(
            id=report.user_id,
            avatar=user.avatar,
            username=user.screen_name,
            created_at=user.created_at,
            label=report.label,
            scrape_date=report.user["updated"],
        )

    def get_report_list(self) -> ReportResponse:
        """
        Get report list to display to Operator, but not display tweets
        """
        waiting_reports = list(
            map(self._make_waiting_report, Report.objects(expired=False))
        )
        approved_reports = list(
            map(self._make_approved_report, ProcessedReport.objects)
        )
        return ReportResponse(waiting=waiting_reports, approved=approved_reports)

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
                user=prediction_db.user,
                tweets=prediction_db.tweets,
            )
        else:
            if reporter_id in report_db.reporters:
                raise HTTPException(
                    status_code=420,
                    detail="User already reported this Twitter Account Recently!",
                )

            report_db.reporters.append(reporter_id)

        return report_db.save()

    def approve_report(self, twitter_id: str):
        report_db = Report.objects(
            report_key__twitter_id=twitter_id, expired=False
        ).first()
        if report_db:
            report_db.update(expired=True)

            label = 0 if report_db.score >= 0.5 else 1
            ProcessedReport.objects(user_id=twitter_id).update_one(
                user=report_db.user,
                tweet_graph=report_db.tweets,
                label=label,
                upsert=True,
            )

    def reject_report(self, twitter_id: str):
        Report.objects(report_key__twitter_id=twitter_id, expired=False).first().update(
            expired=True
        )

    def export(self) -> List[ProcessedReportResponse]:
        processed_report_list = []
        for report in ProcessedReport.objects:
            report_dict = report.to_mongo()
            resp = ProcessedReportResponse(
                user_id=report_dict["_id"],
                user=report_dict["user"],
                tweet_graph=report_dict["tweet_graph"],
                label=report_dict["label"],
            )
            processed_report_list.append(resp)
        return processed_report_list
