import time
from urllib.parse import urlencode

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def get_url(Commodity, CommodityHead):
    """Given a Commodity and a CommodityHead, returns the complete URL to be browsed"""
    base_url = "https://agmarknet.gov.in/SearchCmmMkt.aspx"
    parameters = {
        "Tx_Commodity": Commodity,
        "Tx_State": "0",
        "Tx_District": 0,
        "Tx_Market": 0,
        "DateFrom": "01-Jan-2020",
        "DateTo": "31-Jan-2020",
        "Fr_Date": "01-Jan-2020",
        "To_Date": "31-Jan-2020",
        "Tx_Trend": 0,
        "Tx_CommodityHead": CommodityHead,
        "Tx_StateHead": "--Select--",
        "Tx_DistrictHead": "--Select--",
        "Tx_MarketHead": "--Select--",
    }
    query = urlencode(parameters)
    return "?".join([base_url, query])


def get_all_tables(soup):
    """Extracts and returns all tables in a soup object"""
    return soup.find_all("table")


def get_table_headers(table):
    """Given a table soup, returns all the headers"""
    headers = []
    for th in table.find("tr").find_all("th"):
        headers.append(th.text.strip())
    return headers


def get_table_rows(table):
    """Given a table, returns all its rows"""
    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = []
        # grab all td tags in this table row
        tds = tr.find_all("td")
        for td in tds:
            cells.append(td.text.strip())
        rows.append(cells)
    return rows


def save_as_csv(soup, CommodityHead):
    """Extract data from soup and write it to Csv file"""
    # extract all the tables from the web page
    tables = get_all_tables(soup)

    # iterate over all tables
    for table in tables:
        # get the table headers
        headers = get_table_headers(table)
        # get all the rows of the table
        rows = get_table_rows(table)
        # save table as csv file
        try:
            with open(f"./data/Agri_Data_{CommodityHead}_Jan_2020.csv", mode="ab") as f:
                pd.DataFrame(rows, columns=headers).to_csv(
                    f, header=f.tell() == 0, index=False
                )

        except ValueError:
            pass
    return


def main():
    """Fetches agricultural commodity data using HTTP requests and saves it as CSV files.

    This function reads commodity information from a CSV file, retrieves corresponding data from a website, and saves the results. It handles errors gracefully and reports the status for each commodity.

    """
    start_time = time.time()

    # read Commodity data from csv file
    df = pd.read_csv("./data/CommodityAndCommodityHeadsv2.csv")
    for row in df.itertuples(index=False):
        url = get_url(row.Commodity, row.CommodityHead)
        print(f"Fetching data for {row.CommodityHead} from {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes
            soup = bs(response.content, "html.parser")
            save_as_csv(soup, row.CommodityHead)
            print(f"Successfully saved data for {row.CommodityHead}.")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {row.CommodityHead}: {e}")
        except Exception as e:
            print(f"An error occurred while processing {row.CommodityHead}: {e}")

    end_time = time.time()
    print(f"Total time taken: {end_time - start_time:.2f} seconds")


def main_with_selenium():
    """Fetches agricultural commodity data using Selenium and saves it as CSV files.

    This function automates a headless Chrome browser to navigate through web pages, extract table data for each commodity, and save the results. It handles pagination and ensures all available data is collected for each commodity.

    """
    start_time = time.time()
    # service = Service(executable_path='chromedriver_win32/chromedriver')
    # driver = webdriver.Chrome(service=service)
    options = Options()
    options.add_argument("--headless")
    # Initialize the driver once before the loop
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    # read Commodity data from csv file
    df = pd.read_csv("./data/CommodityAndCommodityHeadsv2.csv")
    for row in df.itertuples(index=False):
        url = get_url(row.Commodity, row.CommodityHead)
        # driver.get('https://bit.ly/3h0JRse')
        driver.get(url)
        # driver.maximize_window()
        # sleep(10)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        # get the soup
        soup = get_soup(driver)
        save_as_csv(soup, row.CommodityHead)

        while True:
            try:
                driver.find_element(By.XPATH, "//input[contains(@alt, '>')]").click()
                # sleep(5)
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
                soup = get_soup(driver)
                save_as_csv(soup, row.CommodityHead)

            except:
                print("No more pages left")
                break
        # sleep(5)

    # Close the driver after processing all commodities
    driver.quit()

    end_time = time.time()
    print(f"Total time taken: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
