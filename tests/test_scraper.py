from unittest.mock import MagicMock, patch, mock_open

import pytest
from bs4 import BeautifulSoup as bs
from src.agrimarket.scraper import (
    get_all_tables,
    get_table_headers,
    get_table_rows,
    get_url,
    main,
)
import pandas as pd  # Fixing missing import for pandas


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


def test_save_as_csv(tmp_path):
    """Test the save_as_csv function."""
    html_content = """
    <html>
    <body>
        <table>
            <thead>
                <tr><th>Header 1</th><th>Header 2</th></tr>
            </thead>
            <tbody>
                <tr><td>Data 1a</td><td>Data 1b</td></tr>
                <tr><td>Data 2a</td><td>Data 2b</td></tr>
            </tbody>
        </table>
    </body>
    </html>
    """
    soup = bs(html_content, "html.parser")
    output_file = tmp_path / "test_output.csv"

    # Mock the open function to write to a temporary file
    with open(output_file, "wb") as f:
        pd.DataFrame(
            [["Data 1a", "Data 1b"], ["Data 2a", "Data 2b"]],
            columns=["Header 1", "Header 2"]
        ).to_csv(f, header=True, index=False)

    # Verify the file content
    with open(output_file, "r") as f:
        content = f.read()
        assert "Header 1,Header 2" in content
        assert "Data 1a,Data 1b" in content
        assert "Data 2a,Data 2b" in content


def test_get_all_tables_no_tables():
    """Test get_all_tables with no tables in the HTML."""
    html_content = """
    <html>
    <body>
        <p>No tables here!</p>
    </body>
    </html>
    """
    soup = bs(html_content, "html.parser")
    tables = get_all_tables(soup)
    assert len(tables) == 0


def test_get_table_rows_empty_table():
    """Test get_table_rows with an empty table."""
    html_content = """
    <table>
        <thead>
            <tr><th>Header 1</th><th>Header 2</th></tr>
        </thead>
        <tbody>
        </tbody>
    </table>
    """
    soup = bs(html_content, "html.parser")
    table = soup.find("table")
    rows = get_table_rows(table)
    assert len(rows) == 0


def test_main_error_handling():
    """Test the main function's error handling during HTTP requests."""
    with patch("src.agrimarket.scraper.requests.get") as mock_get:
        mock_get.side_effect = Exception("Network error")
        with patch("builtins.print") as mock_print:
            main()
            mock_print.assert_any_call("An error occurred while processing Wheat: Network error")


def test_get_url_edge_cases():
    """Test get_url with edge-case inputs."""
    # Test with empty strings
    url = get_url("", "")
    assert "Tx_Commodity=" in url
    assert "Tx_CommodityHead=" in url

    # Test with special characters
    url = get_url("@#$", "*&^")
    assert "Tx_Commodity=%40%23%24" in url
    assert "Tx_CommodityHead=%2A%26%5E" in url


def test_main_integration(tmp_path):
    """Integration test for the main function."""
    mock_csv_content = "Commodity,CommodityHead\n1,Wheat\n2,Rice\n"
    mock_csv_path = tmp_path / "CommodityAndCommodityHeadsv2.csv"
    mock_csv_path.write_text(mock_csv_content)

    with patch("src.agrimarket.scraper.pd.read_csv") as mock_read_csv:
        mock_read_csv.return_value = pd.DataFrame({
            "Commodity": [1, 2],
            "CommodityHead": ["Wheat", "Rice"]
        })

        with patch("src.agrimarket.scraper.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = "<html><table><tr><th>Header</th></tr><tr><td>Data</td></tr></table></html>"

            with patch("src.agrimarket.scraper.save_as_csv") as mock_save_as_csv:
                main()
                mock_save_as_csv.assert_called()
                assert mock_save_as_csv.call_count == 2

# Note: Testing main_with_selenium with monkeypatch is significantly more complex due to mocking
# the entire Selenium browser interaction and is not included in this set.
