# 🎓 Scholarship Search Engine

A real-time, intelligent platform that scrapes university websites for scholarship listings and converts unstructured text into structured, searchable data. Built with **Streamlit** for a fast and interactive user interface, this tool helps students easily discover relevant scholarships.

---

## 📌 Features

- 🌐 **Real-Time Web Scraping**: Collects scholarship data from official university websites.
- 🧾 **Text-to-Structured Conversion**: Extracts scholarship details using NLP and regex.
- 🔍 **Search & Filter**: Streamlit-based UI to explore scholarships by eligibility, deadline, and more.
- 📊 **Insights Dashboard**: Visualizes trends like most common scholarships, deadlines, etc.
- 💾 **Data Storage**: Structured data saved in CSV or a database for easy retrieval.

---

## 🛠️ Tech Stack

| Component       | Technology                        |
|------------------|------------------------------------|
| Web Scraping     | BeautifulSoup, Requests, Selenium  |
| Text Extraction  | spaCy, Regex, Pandas               |
| Interface        | **Streamlit**                      |
| Data Storage     | CSV / SQLite / MongoDB             |
| Visualization    | Plotly / Altair / Streamlit Charts |

---

## 🧪 How It Works

1. **Scrape**: Real-time web scraping gathers raw data from university sites.
2. **Extract**: NLP pipeline parses relevant scholarship information from unstructured text.
3. **Store**: Saves structured data to a local file or database.
4. **Explore**: Users browse, search, and filter scholarships via Streamlit interface.
5. **Visualize**: Graphs display top categories, upcoming deadlines, and more.

---

## 🚀 Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/scholarship-search-engine.git
   cd scholarship-search-engine
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

4. Open in your browser (automatically opens at):
   ```
   http://localhost:8501
   ```

---

## 📂 Project Structure

```
scholarship-search-engine/
│
├── scraper/                # Web scraping scripts
├── extractor/              # NLP and data extraction logic
├── data/                   # Collected and cleaned data
├── app.py                  # Streamlit UI script
├── requirements.txt        # List of Python dependencies
└── README.md               # Project documentation
```

---

## 👨‍💻 Author

**Simon Prakash**  
Final Year M.Sc. Data Science Student, VIT-AP University  
📌 Web Scraping & NLP Enthusiast  
📧 Email: [your-email]  
🔗 LinkedIn: [your-linkedin]

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
