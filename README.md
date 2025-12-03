# User Search Log Analysis – ETL + AI Classification + EDA Visualization

## 📝 Project Overview

This project combines **ETL pipelines, AI keyword classification, and EDA visualization** to process and analyze user search log data. The goal is to understand user behavior, identify popular content types, and generate insights for recommendations or marketing.

![alt text](images/image.png)

---

## 📂 Directory Structure

```bash
LOG_SEARCH_ETL/
│
├── log_search/ # raw parquet data
│
├── outputs/
│ ├── charts/ # charts output
│ ├── top_keyword_by_month/ # top keywords by month
│ ├── top1_keywords/ # top 1 keyword per month
│ └── top3_keywords/ # top 3 keywords per month
│ └── keyword_classified_top30.csv
│
├── .env # environment variables (API key, config)
├── .gitignore
│
├── ai_keyword_classifier.py
├── eda_keywords.ipynb
├── ETL_log_search.ipynb
│
├── top_keyword_by_month.py
├── top_keywords_analysis.py
│
└── README.md

```

## 🎯 Main Objectives

### 1. Analyze User Behavior

- Track the keywords users search for.

- Identify content types of interest: movies, shows, sports, animation, etc.

### 2. Big Data Processing & ETL

- Read parquet files across multiple directories, clean missing data, and standardize columns.

- Compute top keywords per user per month (e.g., June, July).

- Export intermediate results to CSV for reporting or visualization.

### 3. AI Keyword Classification

- Standardize keyword text (normalize accents, split words, fix typos).

- Assign the most relevant content category based on predefined types:
  Action, Romance, Comedy, Drama, K-Drama, C-Drama, Animation, Reality Show, Sports, TV Channel, News, Other.

- Helps understand user preferences and support recommendation systems.

### 4. Exploratory Data Analysis (EDA) & Visualization

- Explore and visualize trends across June and July.

- Analyze the popularity changes of keywords between months.

- Compare user retention of top1 keyword between months.

- Visualize category distribution in top keywords.

---

## Data Processing Workflow

The entire pipeline consists of **4 main stages**:
**Data Ingestion → Data Cleaning & Transformation → AI Keyword Classification → EDA & Visualization**

### 1️⃣ **Data Ingestion**

- **Goal:** Read and consolidate search log data from multiple .parquet directories.

- **Tool:** PySpark for efficient large-scale data processing.

- **Raw data contains:** eventID, datetime, user_id, keyword, category, platform, networkType, userPlansMap.

### 2️⃣ **Data Cleaning & Transformation**

2️⃣ Data Cleaning & Transformation

- **Goal:** Standardize data and create monthly analysis datasets.

**Steps:**

1. Remove rows with **null/empty keywords.**

2. Normalize text (trim whitespace, lowercase, remove special chars if needed).

3. Extract `month` from `datetime`.

4. Compute top keywords per user:

`top1_keywords` → most searched keyword per user per month.

`top3_keywords` → top 3 keywords per user per month.

5. Save intermediate results to:
   `outputs/top_keyword_by_month/`, `outputs/top1_keywords/`, `outputs/top3_keywords/`

**Note:** In production, these would ideally be written to a database (PostgreSQL, MySQL, or NoSQL). For this project:

- Saving as CSV allows easy sharing on GitHub.

- Your EDA scripts read CSVs to generate charts.

### 3️⃣ **AI Keyword Classification**

- **Goal:** Assign content categories for top keywords to better understand user interests.

- **Tool:** ai_keyword_classifier.py using OpenRouter API (free tier).

- **Process:**

  1. Select top 30 keywords from aggregated data.

  2. Send keywords to API → receive category predictions:
     - `Action`, `Romance`, `Comedy`, `Drama`, `K-Drama`, `C-Drama`, `Animation`, `Reality Show`, `Sports`, `TV Channel`, `News`, `Other`…
  3. Receive category predictions:
     ```json
     {
       "NARUTO": "Animation",
       "Running Man": "Reality Show",
       "The Heirs": "K-Drama"
     }
     ```
  4. Export results:
     - **CSV:** `outputs/keyword_classified_top30.csv`
     - **JSON:** (optional for quick checking).

- **Note:**  
   Free API limits requests, so only top 30 keywords are classified. Paid API could extend to all keywords.

### 4️⃣ **EDA & Visualization**

- **Goal:** Visualize ETL & AI classification results to analyze search trends.

- **Tool:** `matplotlib`, `seaborn`, `pandas`.

- Charts auto-save to `outputs/charts/` as `.png`.

**Charts include:**

- **Top 20 most searched keywords** (combined months)

- **Heatmap:** Compare search frequency June vs July

- **User behavior:** top1 keyword retention from June → July

- **Keyword trend analysis:** rising/falling popularity

- **Category distribution** in top 30 keywords

---

## 📊 Sample Charts

- **Top 20 keywords:**
  ![alt text](outputs/charts/top20_keywords_overall.png)

- **Heatmap June vs July:**
  ![alt text](outputs/charts/heatmap_top20_keywords_t6_t7.png)

- **User top1 retention:**
  ![alt text](outputs/charts/user_top1_change_ratio.png)

- **Keyword trend analysis:**
  ![alt text](outputs/charts/top10_keyword_growth_t6_to_t7.png)

- **Category distribution (top30):**
  ![alt text](outputs/charts/keyword_category_distribution_bar.png)

![alt text](outputs/charts/keyword_category_distribution.png)

## 💡 Recommended Improvements (Future)

1. **Save to a database** instead of CSV for scalability and easier queries.

2. **Classify all keywords** (beyond top 30) if using paid AI API.

3. **Interactive dashboard** (Plotly, Dash, or Streamlit) instead of static PNG charts.

4. **Automated pipeline** using Airflow for daily/weekly updates.
