# AgriMarket

A Python package for scraping agricultural commodity market data from Agmarknet and saving it to CSV files.

## Project Structure

```
agrimarket/
├── agrimarket/
│   ├── __init__.py
│   └── scraper.py
├── data/
│   ├── Commodity.csv
│   ├── Dates.csv
│   └── scraped_data/
│       └── (commodity subfolders)
│           └── (scraped data files)
├── pyproject.toml
├── uv.lock
└── README.md
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/rohanyashraj/agrimarket.git
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
# - Fetch data for each commodity and date range in parallel
# - Save results to CSV files in the data/scraped_data directory
main()
```

The script will create CSV files in the `data/scraped_data` directory, organized in subfolders named after each commodity's `CommodityHead`. The filenames will be in the format `Agri_Data_{CommodityHead}_{date_from_formatted}_{date_to_formatted}.csv`.

### Parallelization

The scraper implements two-level parallelization for improved performance:

1. **Date Range Level**: Multiple date ranges are processed simultaneously

   - Uses a thread pool with up to 4 workers (or number of CPU cores, whichever is less)
   - Each date range is processed independently

2. **Commodity Level**: Within each date range, multiple commodities are processed in parallel
   - Uses a thread pool with up to 32 workers (or 4x CPU cores, whichever is less)
   - Each commodity is processed independently

This parallelization strategy ensures efficient resource utilization while being respectful to the server's capacity.

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

- The script uses `requests` to fetch the HTML content of the pages and `BeautifulSoup` to parse the HTML and extract the table data.
- Implements two-level parallelization for efficient data collection:
  - Date ranges are processed in parallel
  - Commodities within each date range are processed in parallel
- Data is organized in commodity-specific subfolders for better organization

### **3. Challenges, Drawbacks and Concerns!**

- Being a govt. site, the servers might not be powerful enough to handle a very large number of rapid requests for extensive historical data.
- The Dataset could still be very large depending on the time period selected, potentially leading to large CSV files.
- The parallelization is carefully tuned to balance performance with server load:
  - Date range parallelization is limited to prevent overwhelming the server
  - Commodity parallelization is more aggressive but still within reasonable limits

### **4. Why?**

- The purpose of this project was to brush up web-scraping concepts using libraries like `requests` and `BeautifulSoup`.
- Implement efficient parallelization techniques for better performance.
- Organize data in a structured way for easier analysis.

### **5. How to use this project?**

- You can learn about web-scraping concepts using `requests` and `BeautifulSoup` by examining the code.
- Study the parallelization implementation using `concurrent.futures.ThreadPoolExecutor`.
- Use the scraped data for Time-Series Forecasting or Analytics & Visualization projects.
- To run the script, make sure you have the required dependencies installed (see `pyproject.toml`).

### **6. Things to Note:**

- This being a govt site, I believe that the servers on the backend are not powerful or smart enough to handle these many requests.
  > I would advise you to play with the script only to learn and not to wreck govt servers as thousands of people rely on this data everyday

Happy Learning! :metal:

**Author:** Rohan Yashraj Gupta
