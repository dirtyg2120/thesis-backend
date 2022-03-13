from typing import List

from app.models import Report
from app.schemas.report import ReportResponse

from .scrape import TwitterScraper


class ReportService:
    def get_report_list(self) -> List[ReportResponse]:
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
            user = TwitterScraper().get_user_by_username(username)

            report_db = Report(
                twitter_id=user.twitter_id,
                name=user.name,
                username=user.username,
                created_at=user.created_at,
                followers_count=user.followers_count,
                followings_count=user.followings_count,
                verified=user.verified,
                tweets=user.tweets,
                scrape_date=user.timestamp,
                report_count=1,
                score=user.score,
            )
        else:
            report_db.report_count += 1

        report_db.save()

        return report_db
