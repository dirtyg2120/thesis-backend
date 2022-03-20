from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import Report, TwitterUser
from app.services.clean_database import clean_database

from . import client
from .helpers.mock_models import MockData
from .helpers.report_helpers import check_account, report_account

TWITTER_ID = MockData.user_info()["id_str"]


class TestUserReport:
    @pytest.mark.usefixtures("checked_twitter_account")
    class TestTwitterAccountChecked:
        def test_user_report_twitter_account(self):
            response = client.post(
                f"/api/send-report/{TWITTER_ID}",
            )
            assert response.status_code == 200
            assert Report.objects().count() == 1

            re_response = client.post(
                f"/api/send-report/{TWITTER_ID}",
            )
            assert re_response.status_code == 420
            assert Report.objects().count() == 1

        def test_many_users_report(self):
            report_count = 5
            for _ in range(report_count):
                client = TestClient(app)
                response = client.post(f"/api/send-report/{TWITTER_ID}")
                assert response.status_code == 200
            assert Report.objects().count() == 1
            assert len(Report.objects()[0].reporters) == report_count

        @pytest.mark.parametrize("session_id", ["", "    ", "wrong-session-id"])
        def test_any_session_id(self, session_id):
            # NOTE: this means that session_id can be self-set! :))
            response = client.post(
                f"/api/send-report/{TWITTER_ID}",
                headers={
                    "accept": "application/json",
                    "Cookie": f"session_id={session_id}",
                },
            )
            assert response.status_code == 200

    class TestTwitterAccountNotChecked:
        def test_report_un_checked_account(self):
            response = client.post(
                f"/api/send-report/{TWITTER_ID}",
            )
            assert response.status_code == 404
            assert response.json() == {"detail": "Twitter account has not been checked"}
            assert Report.objects().count() == 0

        def test_report_outdated_result(self, checked_twitter_account):
            assert TwitterUser.objects().count() == 1
            clean_database(timedelta(days=0))
            response = client.post(
                f"/api/send-report/{TWITTER_ID}",
            )
            assert response.status_code == 404
            assert response.json() == {"detail": "Twitter account has not been checked"}
            assert Report.objects().count() == 0


class TestOperatorReport:
    def test_operator_view_reports_success(
        self, create_operator, reported_twitter_account, login_operator
    ):
        view_report_response = client.get(
            "/api/view-reports",
        )
        reports = view_report_response.json()
        assert len(reports) == 1
        assert reports[0]["id"] == TWITTER_ID

    def test_empty_reports(self, create_operator, login_operator):
        view_report_response = client.get(
            "/api/view-reports",
        )
        reports = view_report_response.json()
        assert len(reports) == 0

    def test_two_reports_same_account(self, mock_user_found):
        check_account()
        report_account()
        assert Report.objects().count() == 1
        clean_database(timedelta(days=0))
        assert TwitterUser.objects().count() == 0
        response = client.post(
            f"/api/send-report/{TWITTER_ID}",
        )

        """
            NOTE: Wrong behavior
            - Expect: 404 Error User should not be able to report
                if the report is outdated compared to the twitterUser
            - Current: 420 Error User blocked since already report account
        """
        assert response.status_code == 420
        # check_account()
        # report_account()
        # assert Report.objects().count() == 2
        # view_report_response = client.get(
        #     "/api/view-reports",
        # )
        # reports = view_report_response.json()
        # assert len(reports) == 2
        # assert reports[0].id == reports[1].id
