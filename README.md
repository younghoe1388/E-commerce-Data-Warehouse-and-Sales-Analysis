# E-commerce Data Warehouse: Star Schema Design and Sales Analytics

Building a star schema data warehouse for 500K+ online retail transactions to enable sales trend analysis and customer insights.

---

## Project Overview

This project processes the UCI Online Retail dataset (541,909 transactions) through a complete ETL pipeline, builds a star schema data warehouse, and provides 6 analytical queries for business insights.

**Key Deliverables:**
- Cleaned and standardized transaction data
- Star schema model (1 fact table + 3 dimension tables)
- Sales analysis queries (monthly trends, top products, customer segmentation, return rate, etc.)

---

## Tech Stack

| Category | Tools |
|----------|-------|
| Language | Python 3.x |
| Data Processing | pandas, numpy |
| Database | SQLite |
| Development | PyCharm / Jupyter Notebook |

---

## Project Structure
├── Online Retail.xlsx # Raw dataset (UCI)
├── data_exploration.py # ETL pipeline: cleaning → modeling → export
├── sales_analysis.py # 6 analytical SQL queries
├── requirements.txt # Python dependencies
└── README.md # Project documentation


---

## Data Model (Star Schema)

The data warehouse consists of 4 tables:

| Table | Type | Description |
|-------|------|-------------|
| `fact_sales` | Fact Table | Transaction-level records (quantity, price, total amount) |
| `dim_product` | Dimension | Product details (StockCode, Description) |
| `dim_customer` | Dimension | Customer details (CustomerID, Country) |
| `dim_date` | Dimension | Date attributes (year, month, day, weekday, is_weekend) |

### Foreign Key Relationships
fact_sales.product_id → dim_product.StockCode
fact_sales.customer_id → dim_customer.CustomerID
fact_sales.date_id → dim_date.date_id


---
