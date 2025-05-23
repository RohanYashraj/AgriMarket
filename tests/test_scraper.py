from unittest.mock import MagicMock

import pytest
from bs4 import BeautifulSoup as bs
from agrimarket.scraper import (
    get_all_tables,
    get_table_headers,
    get_table_rows,
    get_url,
    main,
)


@pytest.mark.parametrize(
    "commodity, commodity_head, expected_url",
    [
        (
            1,
            "Wheat",
            "https://agmarknet.gov.in/SearchCmmMkt.aspx?Tx_Commodity=1&Tx_State=0&Tx_District=0&Tx_Market=0&DateFrom=01-Jan-2020&DateTo=31-Jan-2020&Fr_Date=01-Jan-2020&To_Date=31-Jan-2020&Tx_Trend=0&Tx_CommodityHead=Wheat&Tx_StateHead=--Select--&Tx_DistrictHead=--Select--&Tx_MarketHead=--Select--",
        ),
        (
            2,
            "Rice",
            "https://agmarknet.gov.in/SearchCmmMkt.aspx?Tx_Commodity=2&Tx_State=0&Tx_District=0&Tx_Market=0&DateFrom=01-Jan-2020&DateTo=31-Jan-2020&Fr_Date=01-Jan-2020&To_Date=31-Jan-2020&Tx_Trend=0&Tx_CommodityHead=Rice&Tx_StateHead=--Select--&Tx_DistrictHead=--Select--&Tx_MarketHead=--Select--",
        ),
        (
            3,
            "Jowar",
            "https://agmarknet.gov.in/SearchCmmMkt.aspx?Tx_Commodity=3&Tx_State=0&Tx_District=0&Tx_Market=0&DateFrom=01-Jan-2020&DateTo=31-Jan-2020&Fr_Date=01-Jan-2020&To_Date=31-Jan-2020&Tx_Trend=0&Tx_CommodityHead=Jowar&Tx_StateHead=--Select--&Tx_DistrictHead=--Select--&Tx_MarketHead=--Select--",
        ),
    ],
)
def test_get_url(commodity, commodity_head, expected_url):
    """Test the get_url function with various inputs."""
    assert get_url(commodity, commodity_head) == expected_url


def test_get_all_tables():
    """Test the get_all_tables function."""
    html_content = """
    <html>
    <body>
        <table><thead><tr><th>Header 1</th></tr></thead><tbody><tr><td>Data 1</td></tr></tbody></table>
        <p>Some text</p>
        <table><thead><tr><th>Header 2</th></tr></thead><tbody><tr><td>Data 2</td></tr></tbody></table>
    </body>
    </html>
    """
    soup = bs(html_content, "html.parser")
    tables = get_all_tables(soup)
    assert len(tables) == 2
    # You might add more assertions here to check the content of the tables found


def test_get_table_headers():
    """Test the get_table_headers function."""
    html_content = """
    <table>
        <thead>
            <tr>
                <th>Header 1</th>
                <th>Header 2</th>
                <th>Header 3</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>Data 1</td><td>Data 2</td><td>Data 3</td></tr>
        </tbody>
    </table>
    """
    soup = bs(html_content, "html.parser")
    table = soup.find("table")
    headers = get_table_headers(table)
    assert headers == ["Header 1", "Header 2", "Header 3"]


def test_get_table_rows():
    """Test the get_table_rows function."""
    html_content = """
    <table>
        <thead>
            <tr>
                <th>Header 1</th>
                <th>Header 2</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>Data 1a</td><td>Data 1b</td></tr>
            <tr><td>Data 2a</td><td>Data 2b</td></tr>
            <tr><td>Data 3a</td><td>Data 3b</td></tr>
        </tbody>
    </table>
    """
    soup = bs(html_content, "html.parser")
    table = soup.find("table")
    rows = get_table_rows(table)
    assert len(rows) == 3
    assert rows[0] == ["Data 1a", "Data 1b"]
    assert rows[1] == ["Data 2a", "Data 2b"]
    assert rows[2] == ["Data 3a", "Data 3b"]


# Note: Testing main, main_with_selenium, and save_as_csv would require mocking
# external dependencies (requests, file I/O, selenium). These are more complex
# integration tests and are not included in this basic unit test suite.


def test_main_function(monkeypatch):
    """Test the main function with mocking using monkeypatch."""
    # Mock pandas.read_csv
    mock_df = MagicMock()
    mock_df.itertuples.return_value = [
        MagicMock(Commodity=1, CommodityHead="Wheat"),
        MagicMock(Commodity=2, CommodityHead="Rice"),
    ]
    mock_read_csv_mock = MagicMock(return_value=mock_df)
    monkeypatch.setattr("pandas.read_csv", mock_read_csv_mock)

    # Mock requests.get
    mock_response = MagicMock()
    mock_response.content = b"<html>...</html>"  # Dummy HTML content
    mock_response.raise_for_status.return_value = None  # Simulate a successful request
    mock_requests_get_mock = MagicMock(return_value=mock_response)
    monkeypatch.setattr("requests.get", mock_requests_get_mock)

    # Mock BeautifulSoup constructor (bs)
    mock_soup_instance = MagicMock()
    mock_bs_mock = MagicMock(return_value=mock_soup_instance)
    monkeypatch.setattr("main.bs", mock_bs_mock)

    # Mock save_as_csv
    mock_save_as_csv_mock = MagicMock()
    monkeypatch.setattr("main.save_as_csv", mock_save_as_csv_mock)

    # Mock time.time
    monkeypatch.setattr(
        "time.time", MagicMock(side_effect=[0, 10])
    )  # Simulate time for duration check

    # Mock get_url (less critical to mock the function itself if inputs are controlled)
    # Alternatively, you could let the real get_url run if you provide specific inputs
    # and want to test the URL generation as part of this integration test.
    # For isolation, let's keep it simple and assume get_url works.
    mock_get_url_mock = MagicMock(return_value="http://fakeurl.com")
    monkeypatch.setattr("main.get_url", mock_get_url_mock)

    # Run the main function
    main()

    # Assertions
    mock_read_csv_mock.assert_called_once_with(
        "./data/CommodityAndCommodityHeadsv2.csv"
    )

    # Assert get_url was called for each commodity
    assert mock_get_url_mock.call_count == 2
    mock_get_url_mock.assert_any_call(1, "Wheat")
    mock_get_url_mock.assert_any_call(2, "Rice")

    # Assert requests.get was called for each URL
    assert mock_requests_get_mock.call_count == 2
    mock_requests_get_mock.assert_called_with(
        "http://fakeurl.com"
    )  # Check it was called with the mocked URL

    # Assert raise_for_status was called on the response
    assert mock_response.raise_for_status.call_count == 2

    # Assert BeautifulSoup was called for each response
    assert mock_bs_mock.call_count == 2
    mock_bs_mock.assert_called_with(mock_response.content, "html.parser")

    # Assert save_as_csv was called for each commodity with the correct soup
    assert mock_save_as_csv_mock.call_count == 2
    mock_save_as_csv_mock.assert_any_call(mock_soup_instance, "Wheat")
    mock_save_as_csv_mock.assert_any_call(mock_soup_instance, "Rice")

    # The time assertion would require capturing stdout, which is more complex.
    # We'll rely on the time.time mock ensuring the calculation works if the print statement is reached.


# Note: Testing main_with_selenium with monkeypatch is significantly more complex due to mocking
# the entire Selenium browser interaction and is not included in this set.
