from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import pickle
import re
import pandas as pd
from collections import defaultdict
from serpapi import GoogleSearch
import hashlib
import time
import gc
import os

top_universities_south_india ={
    "Tamil Nadu": [
        "Vellore Institute of Technology (VIT)",
        "SRM Institute of Science and Technology"
    ],
    "Andhra Pradesh": [
        "SRM University, AP",
        "VIT-AP University"
    ],
    "Telangana": [
        "Woxsen University",
        "Malla Reddy University",
    ],
    "Karnataka": [
        "Manipal Academy of Higher Education",
        "Jain University",
        "Christ University",
    ]
}

'''top_universities_south_india ={
    "Tamil Nadu": [
        "Vellore Institute of Technology (VIT)",
        "SRM Institute of Science and Technology",
        "SASTRA Deemed University",
        "Amrita Vishwa Vidyapeetham",
        "Bharath Institute of Higher Education and Research",
        "Hindustan Institute of Technology and Science",
        "Vel Tech Rangarajan Dr. Sagunthala R&D Institute of Science and Technology",
        "Saveetha University",
        "Dr. MGR Educational and Research Institute",
        "Kalasalingam Academy of Research and Education"
    ],
    "Andhra Pradesh": [
        "GITAM Deemed to be University",
        "KL Deemed to be University",
        "Vignan's Foundation for Science, Technology & Research",
        "Sri Sathya Sai Institute of Higher Learning",
        "SRM University, AP",
        "Centurion University of Technology and Management, AP",
        "Andhra Loyola Institute of Engineering and Technology",
        "VIT-AP University"
    ],
    "Telangana": [
        "BITS Pilani, Hyderabad Campus",
        "IIIT Hyderabad",
        "ICFAI Foundation for Higher Education",
        "Woxsen University",
        "Malla Reddy University",
        "Anurag University",
        "CVR College of Engineering"
    ],
    "Karnataka": [
        "Manipal Academy of Higher Education",
        "Jain University",
        "Christ University",
        "NITTE Deemed to be University",
        "Yenepoya Deemed to be University",
        "KLE Academy of Higher Education and Research",
        "Sri Devaraj Urs Academy of Higher Education and Research",
        "Alliance University",
        "Reva University",
        "Azim Premji University",
        "Dayananda Sagar University",
        "Presidency University, Bangalore"
    ]
}'''


for state , university in top_universities_south_india.items():
    state_university_urls[state]={}
    for i in university:
        query=i+" "+"Scholarship"
        #url=search(query=query,num_results=2)
        params = {"q": query ,"api_key": "de71828ce9e9680637aa63ee3773b9680530648d7ea6b8de616e844c6d677c3d"}
        search = GoogleSearch(params)
        results = search.get_dict()["organic_results"]
        result=results[0]
        state_university_urls[state][i]=result["link"] 
        
#pickle.dump(state_university_urls,open('uni_urls',"wb"))
# urls=pickle.load(open("uni_urls",'rb'))


def is_javascript_rendered_page(html):
    return (
        len(html) < 10000 or
        '<noscript>' in html.lower() or
        'window.__INITIAL_STATE__' in html or
        'id="root"' in html or
        not any(tag in html.lower() for tag in ['<h1', '<p', '<div'])
    )

def extract_all_scholarship_info(url):
    print(f"\n🌐 Starting extraction from: {url}")

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
               "Accept-Language": "en-US,en;q=0.9"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html = response.text
    except requests.RequestException as e:
        print(f"❌ Failed to fetch page: {e}")
        return

    use_selenium = is_javascript_rendered_page(html)

    if use_selenium:
        print("⚠️ JavaScript-rendered page detected. Using Selenium...")
        driver = webdriver.Chrome()
        driver.get(url)
        time.sleep(5)
        try:
            container = driver.find_element(By.CSS_SELECTOR, "div.scholarship-wrap")
            partial_html = container.get_attribute('outerHTML')
            soup = BeautifulSoup(partial_html, "lxml")
        except Exception as e:
            print(f"❌ Failed to extract specific content: {e}")
            soup = BeautifulSoup(driver.page_source, "lxml")
        full_html = driver.page_source
        driver.quit()
    else:
        print("✅ Static HTML page detected. Using BeautifulSoup...")
        soup = BeautifulSoup(html, "lxml")
        full_html = html

    # Run scholarship subheading extractor
    print("\n🔍 Extracting structured scholarship content...")
    extract_subheadings_from_soup(soup)

    # Run table extractor using full page HTML
    print("\n📑 Extracting scholarship tables...")
    extract_tables_from_html(full_html)

    print(f"\n✅ Completed all extraction steps for: {url}")

# Helper: separate logic for subheading extraction from parsed soup
def extract_subheadings_from_soup(soup):
    heading_tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'strong'])
    scholarships = []

    for heading in heading_tags:
        heading_text = heading.get_text(strip=True)
        if 'scholarship' not in heading_text.lower():
            continue

        print(f"\n🎯 Found heading: {heading_text}")
        content_elements = []
        sibling = heading.find_next_sibling()
        while sibling and sibling.name not in ['h1', 'h2', 'h3', 'h4', 'strong']:
            if sibling.name in ['div', 'section']:
                content_elements.extend(sibling.find_all(['p', 'li', 'div', 'ul', 'ol'], recursive=False))
            elif sibling.name in ['p', 'li', 'ul', 'ol']:
                content_elements.append(sibling)
            sibling = sibling.find_next_sibling()

        current_subheading = heading_text
        found_data = False

        for element in content_elements:
            text = element.get_text(strip=True)
            if text:
                from_text = extract_fields_from_text(text)
                scholarships.append({
                    'Main_Heading': heading_text,
                    'Subheading': current_subheading,
                    'Content': text,
                    'Amount': from_text['Amount'],
                    'Eligibility': from_text['Eligibility'],
                    'Deadline': from_text['Deadline'],
                    'How_to_Apply': from_text['How_to_Apply']
                })
                found_data = True

        if not found_data:
            print("⚠️ No content found for this heading.")

    if scholarships:
        df = pd.DataFrame(scholarships)
        df.to_csv('scholarships_subheadings.csv', index=False)
        print("\n✅ Saved scholarships_subheadings.csv")
        print(df.head())
    else:
        print("❌ No subheading-based scholarship info found.")
        
def extract_standard_table_data(table):
    rows = table.find_all("tr")
    if not rows:
        return None, None

    if len(rows[0].find_all(["th", "td"])) == 1:
        header_row = rows[1]
        data_rows = rows[2:]
    elif len(rows[0].find_all(["th", "td"])) == 2 and len(rows[1].find_all(["th", "td"])) == 3:
        header_row = rows[1]
        data_rows = rows[2:]
    else:
        header_row = rows[0]
        data_rows = rows[1:]

    headers = [th.get_text(strip=True).lower() for th in header_row.find_all(["th", "td"])]
    last_known_values = [""] * len(headers)

    all_rows = []
    for row in data_rows:
        cols = row.find_all("td")
        if not cols:
            continue
        values = [col.get_text(strip=True) for col in cols]
        values, last_known_values = fill_missing_values_with_last_known(values, last_known_values)
        row_data = dict(zip(headers, values))
        all_rows.append(row_data)

    return all_rows if all_rows else None, headers


# Helper: call your table extractor

def extract_tables_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")

    if not tables:
        print("❌ No tables found on the page.")
        return

    seen_tables = set()
    grouped_tables = defaultdict(list)

    for i, table in enumerate(tables, start=1):
        raw_html = str(table)
        table_hash = hashlib.md5(raw_html.encode()).hexdigest()
        if table_hash in seen_tables:
            continue
        seen_tables.add(table_hash)

        table_data, headers = extract_standard_table_data(table)
        if table_data:
            headers_key = tuple(headers)
            grouped_tables[headers_key].extend(table_data)
        else:
            # fallback to key-value
            kv_data = extract_key_value_table(table)
            if kv_data:
                kv_df = pd.DataFrame([kv_data])
                kv_df.to_csv(f"table_{i}_key_value.csv", index=False)
                print(f"📄 Saved: table_{i}_key_value.csv")

    # Save grouped tables
    for group_index, (headers, data_rows) in enumerate(grouped_tables.items(), start=1):
        df = pd.DataFrame(data_rows)
        df.to_csv(f"table_group_{group_index}.csv", index=False)
        print(f"✅ Saved combined table: table_group_{group_index}.csv")


def fill_missing_values_with_last_known(values, last_known):
    # Ensure alignment
    values = (values + [""] * len(last_known))[:len(last_known)]

    for i in range(len(values)):
        if values[i]:
            last_known[i] = values[i]
        else:
            values[i] = last_known[i]
    
    return values, last_known

links_only = [url for uni in urls.values() for url in uni.values()]
for i in links_only:
    try:
        print(f"🔗 Processing {i}...")
        extract_all_scholarship_info(i)
    except Exception as e:
        print(f"⚠️ Error processing {i}: {e}")urls