from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import BotPrediction, Report
from app.models.report import ProcessedReport
from app.services.clean_database import clean_database

from .helpers.mock_models import get_mock_user

TWITTER_ID = get_mock_user().id_str
USERNAME = get_mock_user().screen_name


@pytest.fixture
def checked_twitter_account(client, mock_user_found):
    username = USERNAME
    response = client.get(
        "/api/check", params={"url": f"https://twitter.com/{username}"}
    )
    assert response.status_code == 200
    assert response.json()["user_info"]["username"] == username.lower()
    assert Report.objects().count() == 0


@pytest.fixture
def reported_twitter_account(client, checked_twitter_account):
    response = client.post(
        f"/api/send-report/{TWITTER_ID}",
    )
    assert response.status_code == 200
    assert Report.objects().count() == 1


class TestUserReport:
    @pytest.mark.usefixtures("checked_twitter_account")
    class TestTwitterAccountChecked:
        def test_user_report_twitter_account(self, client):
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

        def test_many_users_report(self, client):
            report_count = 5
            for _ in range(report_count):
                client = TestClient(app)
                response = client.post(f"/api/send-report/{TWITTER_ID}")
                assert response.status_code == 200
            assert Report.objects().count() == 1
            assert len(Report.objects()[0].reporters) == report_count

    class TestTwitterAccountNotChecked:
        def test_report_un_checked_account(self, client):
            response = client.post(
                f"/api/send-report/{TWITTER_ID}",
            )
            assert response.status_code == 404
            assert response.json() == {"detail": "Twitter account has not been checked"}
            assert Report.objects().count() == 0

        def test_report_outdated_result(self, client, checked_twitter_account):
            assert BotPrediction.objects().count() == 1
            clean_database(timedelta(days=0))
            response = client.post(
                f"/api/send-report/{TWITTER_ID}",
            )
            assert response.status_code == 404
            assert response.json() == {"detail": "Twitter account has not been checked"}
            assert Report.objects().count() == 0


class TestOperatorReport:
    def test_operator_view_reports_success(
        self, client, create_operator, reported_twitter_account, login_operator
    ):
        view_report_response = client.get(
            "/api/view-reports",
        )
        reports = view_report_response.json()["waiting"]
        assert len(reports) == 1
        assert reports[0]["id"] == TWITTER_ID

    def test_empty_reports(self, client, create_operator, login_operator):
        view_report_response = client.get(
            "/api/view-reports",
        )
        reports = view_report_response.json()["waiting"]
        assert len(reports) == 0

    def test_two_reports_same_account(
        self,
        client,
        reported_twitter_account,
        create_operator,
        login_operator,
    ):
        assert Report.objects().count() == 1
        clean_database(timedelta(days=0))
        assert BotPrediction.objects().count() == 0
        response = client.post(
            f"/api/send-report/{TWITTER_ID}",
        )
        assert response.status_code == 404

        recheck_response = client.get(f"/api/check?url={USERNAME}")
        assert recheck_response.status_code == 200
        assert BotPrediction.objects().count() == 1

        re_report_response = client.post(
            f"/api/send-report/{TWITTER_ID}",
        )
        assert re_report_response.status_code == 200
        assert Report.objects().count() == 2

        view_report_response = client.get(
            "/api/view-reports",
        )
        reports = view_report_response.json()["waiting"]
        assert len(reports) == 1

    def test_approve_report(
        self,
        client,
        reported_twitter_account,
        create_operator,
        login_operator,
    ):
        assert Report.objects().count() == 1
        response = client.post(
            f"/api/approve-report/{TWITTER_ID}",
        )
        assert response.status_code == 200
        assert ProcessedReport.objects().count() == 1

        assert Report.objects(expired=True).count() == 1
        view_report_response = client.get(
            "/api/view-reports",
        )
        reports = view_report_response.json()["waiting"]
        assert len(reports) == 0

    def test_reject_report(
        self,
        client,
        reported_twitter_account,
        create_operator,
        login_operator,
    ):
        assert Report.objects().count() == 1
        response = client.post(
            f"/api/reject-report/{TWITTER_ID}",
        )
        assert response.status_code == 200
        assert Report.objects().count() == 1

        assert Report.objects(expired=True).count() == 1
        view_report_response = client.get(
            "/api/view-reports",
        )
        reports = view_report_response.json()["waiting"]
        assert len(reports) == 0

    def test_export_report(
        self,
        client,
        reported_twitter_account,
        create_operator,
        login_operator,
    ):
        assert Report.objects().count() == 1
        approve_response = client.post(
            f"/api/approve-report/{TWITTER_ID}",
        )
        assert approve_response.status_code == 200
        assert ProcessedReport.objects().count() == 1

        export_response = client.get("/api/export")
        assert export_response.status_code == 200
        assert ProcessedReport.objects().count() == 1
