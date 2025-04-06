#!/usr/bin/env python3

import os
import sys
import json
import logging
import whois
from concurrent.futures import ThreadPoolExecutor, as_completed

FOLDER="results"

def load_domain_data(base_name):
    """
    loads whois data of base_name from results/base_name.json
    """
    os.makedirs(FOLDER, exist_ok=True)
    file_path = os.path.join(FOLDER, f"{base_name}.json")

    if not os.path.isfile(file_path):
        return {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_domain_data(base_name, domain_data):
    """
    saves data of base_name to results/base_name.json in JSON format
    """
    os.makedirs(FOLDER, exist_ok=True)
    file_path = os.path.join(FOLDER, f"{base_name}.json")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(domain_data, f, indent=2, default=str)

def is_domain_registered(whois_info):
    """
    fetch WHOIS info dictionary
    """
    if not whois_info:
        return False
    
    domain_name = whois_info.get("domain_name")
    registrar = whois_info.get("registrar")

    if not domain_name or not registrar:
        return False

    if isinstance(domain_name, list):
        domain_is_nonempty = any(entry for entry in domain_name if entry)
    else:
        domain_is_nonempty = bool(str(domain_name).strip())
    
    if isinstance(registrar, list):
        registrar_is_nonempty = any(entry for entry in registrar if entry)
    else:
        registrar_is_nonempty = bool(str(registrar).strip())
    
    return domain_is_nonempty and registrar_is_nonempty

def fetch_whois_data(domain):
    """
    performs whois lookup for single domain
    """
    try:
        w = whois.whois(domain)
        return dict(w)
    except Exception:
        return {}

def print_table(rows, headers):
    """
    to print in table format in terminal output
    """
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    header_str = " | ".join(
        str(h).ljust(col_widths[i]) for i, h in enumerate(headers)
    )
    print(header_str)
    print("-" * len(header_str))

    for row in rows:
        row_str = " | ".join(
            str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)
        )
        print(row_str)

def main():
    whois_logger = logging.getLogger('whois')
    whois_logger.setLevel(logging.CRITICAL)

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <base_name> [--extensive] [--print fields]")
        print("Example: python main.py bitmesra --extensive --print registrar,org")
        sys.exit(1)

    base_name = sys.argv[1]

    if '--extensive' in sys.argv:
        tld_file = 'tlds_extensive.txt'
    else:
        tld_file = 'tlds.txt'

    print_fields = []
    if '--print' in sys.argv:
        idx = sys.argv.index('--print')

        if idx + 1 < len(sys.argv):
            print_arg = sys.argv[idx + 1]
            print_fields = [field.strip() for field in print_arg.split(',') if field.strip()]

    # load cached 
    domain_data = load_domain_data(base_name)

    try:
        with open(tld_file, 'r', encoding='utf-8') as f:
            tlds = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Could not find {tld_file} in the current folder.")
        sys.exit(1)
    
    domains_to_lookup = []
    for tld in tlds:
        domain = f"{base_name}{tld}"

        if domain not in domain_data:
            domains_to_lookup.append(domain)
    
    total = len(domains_to_lookup)
    completed = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_domain = {
            executor.submit(fetch_whois_data, domain): domain
            for domain in domains_to_lookup
        }
        for future in as_completed(future_to_domain):
            domain = future_to_domain[future]

            try:
                whois_dict = future.result()
                domain_data[domain] = whois_dict
            except Exception:
                domain_data[domain] = {}
            
            completed += 1
            print(f"{completed}/{total} completed", end='\r', flush=True)
    
    print()

    if print_fields:
        headers = ["Domain"] + print_fields
        rows = []

        for tld in tlds:
            domain = f"{base_name}{tld}"
            data = domain_data.get(domain, {})
            if is_domain_registered(data):
                row = [domain]
                for field in print_fields:
                    value = data.get(field, "")

                    if isinstance(value, list):
                        value = ", ".join(str(v) for v in value if v)
                    row.append(value)
                rows.append(row)

        if rows:
            print_table(rows, headers)
        else:
            print("No registered domains found with the specified fields")
    
    else:
        for tld in tlds:
            domain = f"{base_name}{tld}"
            data = domain_data.get(domain, {})
            if is_domain_registered(data):
                print(domain)

    save_domain_data(base_name, domain_data)

if __name__ == "__main__":
    main()