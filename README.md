# 🇵🇭 COMELEC 2025 Election Results Scraper

This Python project is a scraper and ETL (Extract, Transform, Load) pipeline designed to gather precinct-level election results from the [COMELEC 2025 election results site](https://2025electionresults.comelec.gov.ph). It drills down from regions to precincts and extracts actual vote counts for senators and party-lists. 

Will probably expand this in the future for local election data.

---

## ✅ Features

- Extracts Philippine election data by locality (region → precinct)
- Fetches precinct-level vote counts (summary, senators, party-lists)
- Modular ETL structure
- Real-time CSV writing (memory-efficient)
- Automatically resumes from last saved point

---

## 📦 Requirements

- Python 3.8+
- Libraries:
  - `pandas`
  - `requests`

Install via:

```bash
pip install pandas requests
```

---

🚀 How It Works
**Step 1: Extract Locality Hierarchy**

```python
main()
```

This function:

- Fetches and saves regional → provincial → city → barangay → precinct data
- Outputs to:
  - `regions.csv`
  - `provinces.csv`
  - `cities.csv`
  - `baranggays.csv`
  - `precincts.csv`

Each level is fetched through the COMELEC’s API structure.

**Step 2: Extract Precinct-Level Vote Data**
```python
transform_er_data()
```
This function:

- Reads `precincts.csv` to determine the list of precincts
- Skips precincts already processed (based on `precinct_info.csv`)
- For each precinct, it fetches:
  - General vote data (registered, actual, valid ballots)
  - Senator-level votes
  - Party-list votes
- Outputs are written to:
  - `precinct_info.csv`
  - `precinct_senators.csv`
  - `precinct_partylist.csv`

---

📄 **Output Files**

| File                    | Description                       |
|-------------------------|----------------------------------|
| `regions.csv`           | Region-level locality info        |
| `provinces.csv`         | Provinces under each region       |
| `cities.csv`            | Cities and municipalities         |
| `baranggays.csv`        | Barangays under each city         |
| `precincts.csv`         | List of precincts per barangay    |
| `precinct_info.csv`     | Summary info per precinct         |
| `precinct_senators.csv` | Senatorial vote count per precinct|
| `precinct_partylist.csv`| Party-list vote count per precinct|

---

🧪 **Future Improvements**

- Upload the raw CSV files for people to use in their own ETL projects
- Make a Script to transform and load data to a more efficient and clean database (I will probably use MySQL).
- Make own data analysis and create a dashboard
- Document the entire process properly, maybe deploy the results online.
- Add better error handling and retry logic
- Add multiprocessing to speed up extraction

---

⚠️ **Disclaimer**

This project is **not** affiliated with COMELEC. It is provided for educational and analytical use only. Use responsibly and ethically.
