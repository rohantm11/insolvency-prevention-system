# Sample data for testing

## Insolvency (company) analysis

Sample CSV files are in this folder:

| File / folder | Use case |
|---------------|----------|
| **single_company_sample.csv** | One company – use in **Insolvency Analysis** or **Compare Companies** |
| **sample_company_data.csv** | Three companies – use in **Insolvency Analysis** → Bulk Upload |
| **good/** | **3,000 single-company CSVs** (not at risk) – same format as single_company_sample.csv, unique names and stats. Use any file in Insolvency Analysis or Compare. |
| **bad/** | **3,000 single-company CSVs** (at risk of insolvency) – same format, unique names and stats. Use any file in Insolvency Analysis or Compare. |

### How to test in the browser

1. Open **http://localhost:5173** → **Insolvency Analysis**.
2. **Single company:** Switch to "Bulk Upload", click "Click to Select CSV File", choose `data/single_company_sample.csv`, then click "Analyze All Companies" (it will analyze the one row).  
   Or use **Compare Companies**: upload this file as Company A or B and click "Analyze A" / "Analyze B".
3. **Multiple companies:** In Insolvency Analysis → Bulk Upload, select `data/sample_company_data.csv` and click "Analyze All Companies". You’ll see results for all three (Acme = healthy, Borderline = grey zone, Distressed = at risk).

### Getting more data

- **Download template:** In the app, use **Download CSV template** on the Insolvency or Employee page to get the correct column headers.
- **Regenerate 6k single-company files (3k good + 3k bad):** From project root:
  ```powershell
  .\backend\venv\Scripts\Activate.ps1
  python scripts/generate_single_company_files.py --output-dir data
  ```
  This creates `data/good/00001.csv` … `data/good/03000.csv` and `data/bad/00001.csv` … `data/bad/03000.csv`. Each file is one company, same format as single_company_sample.csv.
- **Generate one combined CSV for bulk upload:** From project root:
  ```powershell
  python scripts/generate_data.py --healthy 10 --at-risk 5 --output-dir data
  ```
  This creates `data/company_data.csv` (and employee data) for bulk analysis.

### Employee / layoff data

| File / folder | Use case |
|---------------|----------|
| **employees/** | **One CSV per company** (6,000 files) – each file has **400–700 employee records** (random per company) for that company. Filename = `COMP_GOOD_00001.csv`, `COMP_BAD_00001.csv`, etc., matching `company_id` from `good/` and `bad/`. Use in **Layoff Simulation** (upload one file = one company’s workforce). |

For **Employee Scoring** and **Layoff Simulation**, use **Download CSV template** on the Employee Scoring page, or use the pre-generated files in `data/employees/`.

**Generate employee CSVs (after generating 6k company files):** From project root:
```powershell
python scripts/generate_employees.py --data-dir data
```
This reads all company CSVs from `data/good/` and `data/bad/`, and for each company writes `data/employees/<company_id>.csv` with 400–700 random employee rows (optional: `--min-employees 400 --max-employees 700`).
