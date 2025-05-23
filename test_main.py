import pytest
from bs4 import BeautifulSoup as bs
from main import get_url, get_all_tables, get_table_headers, get_table_rows

def test_get_url():
    """Test the get_url function."""
    commodity = 1
    commodity_head = "Wheat"
    expected_url = "https://agmarknet.gov.in/SearchCmmMkt.aspx?Tx_Commodity=1&Tx_State=0&Tx_District=0&Tx_Market=0&DateFrom=01-Jan-2020&DateTo=31-Jan-2020&Fr_Date=01-Jan-2020&To_Date=31-Jan-2020&Tx_Trend=0&Tx_CommodityHead=Wheat&Tx_StateHead=--Select--&Tx_DistrictHead=--Select--&Tx_MarketHead=--Select--"
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