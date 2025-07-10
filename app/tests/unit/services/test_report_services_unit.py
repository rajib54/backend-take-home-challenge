from app.services import report as report_service

def test_get_url_stats(mocker):
    mock_handler = mocker.patch("app.services.report.report_handler")
    mock_result = mock_handler.get_stats_for_slug.return_value = {
        "slug": "abc123",
        "long_url": "https://example.com",
        "visits": 5,
        "last_visit": "2024-01-01T12:00:00"
    }

    db = mocker.MagicMock()
    result = report_service.get_url_stats(db, "abc123")

    assert result == mock_result
    mock_handler.get_stats_for_slug.assert_called_once_with(db, "abc123")


def test_get_top_urls(mocker):
    mock_handler = mocker.patch("app.services.report.report_handler")
    mock_result = mock_handler.get_top_urls.return_value = [
        {"slug": "one", "visits": 10},
        {"slug": "two", "visits": 8}
    ]

    db = mocker.MagicMock()
    result = report_service.get_top_urls(db, limit=2)

    assert result == mock_result
    mock_handler.get_top_urls.assert_called_once_with(db, 2)
