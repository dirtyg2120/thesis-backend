from datetime import datetime
from re import T
from typing import List
from app.models import Report
from app.models import TwitterUser
from app.services.scrape import TwitterScraper


class ReportService:
    def get_report_list(self) -> List[Report]:
        try:
            report_list = Report.objects
            test = []
            for report in report_list:
                test.append(report.to_response())
        except Exception as e:
            print("error: " + str(e))
        return test

    def add_report(self, username) -> Report:
        report_db = Report.objects(username=username).first()

        if report_db is None:
            try:
                user = TwitterUser.objects(username=username).first()
            except Exception as e:
                print("error: " + str(e))
            else:
                report_db = Report(
                    twitter_id=str(user.pk),
                    name=user.name,
                    username=user.username,
                    created_at=user.created_at,
                    followers_count=user.followers_count,
                    followings_count=user.followings_count,
                    scrape_date=user.timestamp,
                    reset_date=datetime.now(),
                    report_count=1,
                )
        else:
            report_db.report_count += 1

        report_db.save()

        return report_db
