import time
import os
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Dict
from dataclasses import dataclass

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs


@dataclass
class DateRange:
    """Class to hold date range information"""
    from_date: str
    to_date: str


def get_url(Commodity, CommodityHead, date_from, date_to):
    """Given a Commodity, CommodityHead, and date range, returns the complete URL to be browsed"""
    base_url = "https://agmarknet.gov.in/SearchCmmMkt.aspx"
    parameters = {
        "Tx_Commodity": Commodity,
        "Tx_State": "0",
        "Tx_District": 0,
        "Tx_Market": 0,
        "DateFrom": date_from,
        "DateTo": date_to,
        "Fr_Date": date_from,
        "To_Date": date_to,
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


def save_as_csv(soup, CommodityHead, date_from, date_to):
    """Extract data from soup and write it to Csv file with date range in filename"""
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
            # Format dates for filename (e.g., 01-Jan-2020 to 01Jan2020)
            date_from_formatted = date_from.replace('-', '')
            date_to_formatted = date_to.replace('-', '')

            # Create the base directory for scraped data
            base_dir = "./data/scraped_data"
            os.makedirs(base_dir, exist_ok=True)

            # Create a subdirectory for the commodity
            commodity_dir = os.path.join(base_dir, CommodityHead)
            os.makedirs(commodity_dir, exist_ok=True)

            # Construct the full filename within the commodity subdirectory
            filename = os.path.join(commodity_dir, f"Agri_Data_{CommodityHead}_{date_from_formatted}_{date_to_formatted}.csv")

            with open(filename, mode="ab") as f:
                pd.DataFrame(rows, columns=headers).to_csv(
                    f, header=f.tell() == 0, index=False
                )

        except ValueError:
            pass
    return


def process_commodity(commodity_row: pd.Series, date_range: DateRange) -> Tuple[str, bool, str]:
    """Process a single commodity for a given date range.
    
    Args:
        commodity_row: A pandas Series containing commodity information
        date_range: DateRange object containing from_date and to_date
        
    Returns:
        Tuple containing (commodity_head, success_status, error_message)
    """
    try:
        url = get_url(commodity_row.Commodity, commodity_row.CommodityHead, date_range.from_date, date_range.to_date)
        response = requests.get(url)
        response.raise_for_status()
        soup = bs(response.content, "html.parser")
        save_as_csv(soup, commodity_row.CommodityHead, date_range.from_date, date_range.to_date)
        return commodity_row.CommodityHead, True, ""
    except requests.exceptions.RequestException as e:
        return commodity_row.CommodityHead, False, str(e)
    except Exception as e:
        return commodity_row.CommodityHead, False, str(e)


def process_date_range(date_range: DateRange, df_commodities: pd.DataFrame, max_workers: int) -> Dict[str, List[Tuple[str, bool, str]]]:
    """Process all commodities for a given date range.
    
    Args:
        date_range: DateRange object containing from_date and to_date
        df_commodities: DataFrame containing commodity information
        max_workers: Maximum number of worker threads
        
    Returns:
        Dictionary containing results for each commodity
    """
    print(f"--- Fetching data for date range: {date_range.from_date} to {date_range.to_date} ---")
    results = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all commodity processing tasks
        future_to_commodity = {
            executor.submit(process_commodity, commodity_row, date_range): commodity_row
            for commodity_row in df_commodities.itertuples(index=False)
        }

        # Process completed tasks as they finish
        for future in as_completed(future_to_commodity):
            commodity_head, success, error = future.result()
            if success:
                print(f"Successfully saved data for {commodity_head} for {date_range.from_date} to {date_range.to_date}.")
            else:
                print(f"Error processing {commodity_head} for {date_range.from_date} to {date_range.to_date}: {error}")
            results[commodity_head] = (success, error)

    return results


def main():
    """Fetches agricultural commodity data using HTTP requests and saves it as CSV files.

    This function reads commodity information from a CSV file, retrieves corresponding data from a website, and saves the results. It handles errors gracefully and reports the status for each commodity.

    """
    start_time = time.time()

    # read Commodity data from csv file
    df_commodities = pd.read_csv("./data/Commodity.csv")
    # read Dates data from csv file
    df_dates = pd.read_csv("./data/Dates.csv")

    # Convert dates to DateRange objects
    date_ranges = [DateRange(row.From, row.To) for row in df_dates.itertuples(index=False)]

    # Number of worker threads for commodity processing
    commodity_workers = min(32, (os.cpu_count() or 1) * 4)
    # Number of worker threads for date range processing (use fewer threads to avoid overwhelming the server)
    date_workers = min(4, os.cpu_count() or 1)

    # Process date ranges in parallel
    with ThreadPoolExecutor(max_workers=date_workers) as date_executor:
        # Submit all date range processing tasks
        future_to_date = {
            date_executor.submit(process_date_range, date_range, df_commodities, commodity_workers): date_range
            for date_range in date_ranges
        }

        # Process completed date ranges as they finish
        for future in as_completed(future_to_date):
            date_range = future_to_date[future]
            try:
                results = future.result()
                print(f"Completed processing date range: {date_range.from_date} to {date_range.to_date}")
            except Exception as e:
                print(f"Error processing date range {date_range.from_date} to {date_range.to_date}: {e}")

    end_time = time.time()
    print(f"Total time taken: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
