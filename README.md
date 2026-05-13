# FAA Service Difficulty Reports (SDRs) - Odor/Fume Scraper

This project scrapes Service Difficulty Reports from the FAA website focusing on reports mentioning odor, fume, sulfur, and decontamination issues.

## Purpose

Extract and analyze FAA Service Difficulty Reports that mention:
- Odor
- Fume
- Sulfur
- Dirty Sock
- Dirty Smell
- Decontamination

## Setup

### Requirements
- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone or navigate to this repository
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the scraper:

```bash
python faa_sdr_scraper.py
```

The script will:
1. Query the FAA SDR database for reports matching the keywords
2. Parse and extract relevant data
3. Save results to `faa_sdr_results.csv`

## Output

The CSV file (`faa_sdr_results.csv`) contains the following columns:
- Report Number
- Date
- Aircraft Type
- Description
- Category
- Resolution Status

## Files

- `faa_sdr_scraper.py` - Main scraper script
- `requirements.txt` - Python dependencies
- `faa_sdr_results.csv` - Output data (generated after running)

## Notes

- FAA website: https://sdrs.faa.gov/Query.aspx
- Be respectful of the FAA servers; the scraper includes delays between requests
- Data is pulled from public FAA records
