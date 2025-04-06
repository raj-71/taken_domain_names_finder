# Taken Domain Names Finder

A simple fast Python script to check if domains (based on a base name and multiple TLDs) are already registered. The script uses Python’s `whois` library under the hood and caches results in JSON format to avoid repeated WHOIS lookups.

---

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic](#basic)
  - [Extensive TLDs](#extensive-tlds)
  - [Printing Specific Fields](#printing-specific-fields)
- [Configuration](#configuration)
- [Output Structure](#output-structure)
- [License](#license)

---

## Introduction

This tool lets you quickly check a set of TLDs (Top-Level Domains) for a chosen base name (e.g., `mydomain.com`, `mydomain.org`, `mydomain.net`). By default, it uses a small set of TLDs, but you can also enable an “extensive” mode that attempts a larger list of TLDs.

Whenever you run the script, it caches each WHOIS query result in a JSON file under the `results/` folder. This helps avoid unnecessary WHOIS queries for domains you have already checked.

---

## Features

1. **WHOIS Lookup**: Checks if a domain is registered based on `domain_name` and `registrar` fields from the WHOIS data.
2. **Threaded Processing**: Uses multithreading to speed up lookups.
3. **Caching**: Stores previously fetched WHOIS data to `results/<base_name>.json`.
4. **Easy to Extend**: You can add more TLDs to the `tlds.txt` or `tlds_extensive.txt` files.

---

## Installation

1. **Clone or Download** the repository:
   ```bash
   git clone https://github.com/raj-71/taken_domain_names_finder.git
   cd taken_domain_names_finder
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # For Linux/Mac
   
   # or
   venv\Scripts\activate      # For Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   The key dependency is the [python-whois](https://pypi.org/project/python-whois/) package.

---

## Usage

From the project folder, run:

```bash
python main.py <base_name> [--extensive] [--print fields]
```

### Basic

By default, the script uses `tlds.txt` to look up domains:
```bash
python main.py mydomain
```
This will check each TLD in `tlds.txt` (like `.com`, `.org`, etc.). Any registered domains will be printed in the console.

### Extensive TLDs

To use the more comprehensive TLD list in `tlds_extensive.txt`, add the `--extensive` flag:
```bash
python main.py mydomain --extensive
```
This will search against a larger set of TLDs, which could take more time.

### Printing Specific Fields

You can also ask the script to print certain fields from the WHOIS data for each registered domain. For example, to print the **registrar** and **org** fields, run:
```bash
python main.py mydomain --print registrar,org
```
You can mix and match any fields available in the WHOIS data. Fields are printed in a table-like format.

---

## Configuration

- **`tlds.txt`**: Contains a small list of commonly used TLDs.
- **`tlds_extensive.txt`**: Contains an extended list of TLDs.
- **`results/`**: Stores `<base_name>.json` files, which cache WHOIS data for each domain checked.

You can customize the TLD list by editing `tlds.txt` or `tlds_extensive.txt` directly.

---

## Output Structure

- **Terminal Output**: 
  - When no specific fields are requested (`--print` is not used), the script prints the fully qualified domain names (FQDN) of all domains that are registered.
  - When using `--print fields`, it prints a table with the chosen fields for each registered domain.

- **Results Folder**: 
  - `results/<base_name>.json` will store a dictionary of WHOIS data for each `<base_name><tld>` key.

An example snippet (for `mydomain`) might look like:
```json
{
  "mydomain.com": {
    "domain_name": "MYDOMAIN.COM",
    "registrar": "Example Registrar, Inc.",
    "creation_date": "2021-01-01 00:00:00",
    "expiration_date": "2023-01-01 00:00:00",
    "name_servers": [
      "NS1.EXAMPLE.COM",
      "NS2.EXAMPLE.COM"
    ],
    ...
  },
  "mydomain.org": { ... },
  ...
}
```