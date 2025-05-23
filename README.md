# AgriMarket

A Python package for scraping agricultural commodity market data from Agmarknet and saving it to CSV files.

## Project Structure

```
agrimarket/
├── agrimarket/
│   ├── __init__.py
│   └── scraper.py
├── tests/
│   └── test_scraper.py
├── data/
│   ├── Commodity.csv
│   ├── Dates.csv
│   └── scraped_data/
│       └── (commodity subfolders)
│           └── (scraped data files)
├── config/
├── pyproject.toml
└── README.md
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/agrimarket.git
cd agrimarket
```

2. Install UV (if not already installed):

```bash
pip install uv
```

3. Create and activate a virtual environment using UV:

```bash
# Create virtual environment
uv venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Unix/MacOS:
source .venv/bin/activate
```

4. Install the package in development mode:

```bash
uv pip install -e ".[dev]"
```

## Usage

The package provides functionality to scrape agricultural commodity data from Agmarknet. Here's how to use it:

1. Ensure you have a CSV file named `Commodity.csv` in the `data` directory with columns for `Commodity` and `CommodityHead`.

2. Ensure you have a CSV file named `Dates.csv` in the `data` directory with columns for `From` and `To` dates.

3. Run the scraper:

```python
from agrimarket.scraper import main

# This will:
# - Read commodity data from data/Commodity.csv
# - Read date ranges from data/Dates.csv
# - Fetch data for each commodity and date range
# - Save results to CSV files in the data/scraped_data directory
main()
```

The script will create CSV files in the `data/scraped_data` directory, organized in subfolders named after each commodity's `CommodityHead`. The filenames will be in the format `Agri_Data_{CommodityHead}_{date_from_formatted}_{date_to_formatted}.csv`.

## Development

### Running Tests

```bash
python -m pytest
```

### Code Quality

The project uses `ruff` for linting and code formatting. To run the linter:

```bash
uvx ruff check .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

### **Data Source:**

[Agmarknet](https://agmarknet.gov.in/Default.aspx) portal is a GOI (Govt of India) portal on agricultural marketing. The Portal provides both static and dynamic information relating to agricultural marketing in India .

- The static information is about infrastructure- related (Storage, warehousing, Cold Storage, grading and packing facilities), Market – related (market fee/ charges, weighment, handling, market functionaries, development programmes, market laws, composition of market Committees, income and expenditure, etc) and Promotion-related information (Standards, Grades, Labelling, Sanitary and Phyto-Sanitary requirements, Pledge Financing, Marketing Credit and new opportunities available, etc.).
- The dynamic part comprise Price-related information comprising maximum, minimum and modal prices of varieties, total arrivals and dispatches with destination. The portal provides easy access to commodity-wise, variety-wise daily prices and arrivals information of more than 2000 varieties and about 300 commodities from the wholesale markets spread all over the country.

## **Script:**

### **1. What?**

- The Script is aimed to scrape the Historical data from the website of all the different commodities (~350) for 4000+ markets present on the website. However it can also be used to extract daily prices with little modification.

### **2. How?**

- The script now uses `requests` to fetch the HTML content of the pages and `BeautifulSoup` to parse the HTML and extract the table data. Initially, Selenium was used, but since all the data for a given commodity and date range is on a single page, using `requests` is significantly more efficient.

### **3. Challenges, Drawbacks and Concerns!**

- Being a govt. site, the servers might not be powerful enough to handle a very large number of rapid requests for extensive historical data.
- The Dataset could still be very large depending on the time period selected, potentially leading to large CSV files.
- Theoretically, fetching data for multiple or all commodities together could be scaled using techniques like multithreading or distributed computing, but caution is advised regarding the load on the source server.

### **4. Why?**

- The purpose of this project was to brush up web-scraping concepts using libraries like `requests` and `BeautifulSoup`.

### **5. How to use this project?**

- You can learn about web-scraping concepts using `requests` and `BeautifulSoup` by examining the code, which includes comments and documentation for the key methods.
- You can also use this script to download a reasonable amount of data and use it for your Time-Series Forecasting or Analytics & Visualization projects.
- To run the script, make sure you have the required dependencies installed (see `pyproject.toml`) and execute `main.py`.

### **6. Things to Note:**

- This being a govt site, I believe that the servers on the backend are not powerful or smart enough to handle these many requests.
  > I would advise you to play with the script only to learn and not to wreck govt servers as thousands of people rely on this data everyday

Happy Learning! :metal:
