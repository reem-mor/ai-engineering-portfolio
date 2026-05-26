from app.services.history_service import HistoryService


def test_history_service_can_be_created():
    assert HistoryService() is not None
