# import pandas as pd
# from flask import Flask, request, render_template
# from sentence_transformers import SentenceTransformer, util
# import numpy as np

# app = Flask(__name__)

# # Load scholarships from CSV
# scholarships_df = pd.read_csv("scholarship.csv")

# # Load BERT-based model
# model = SentenceTransformer('all-MiniLM-L6-v2')

# # Precompute embeddings for scholarships
# corpus = (scholarships_df["Eligibility"] + " " + scholarships_df["Scholarship_Details"]).tolist()
# scholarship_embeddings = model.encode(corpus, convert_to_tensor=True)

# @app.route("/", methods=["GET", "POST"])
# def search_scholarships():
#     scholarships = []
#     states = ["Tamil Nadu", "Andhra Pradesh", "Telangana", "Karnataka", "Multiple States"]
#     universities = scholarships_df["University"].unique().tolist()

#     if request.method == "POST":
#         state = request.form.get("state")
#         university = request.form.get("university")
#         eligibility = request.form.get("eligibility", "").strip()

#         # Filter scholarships using pandas
#         filtered_df = scholarships_df.copy()
#         if state and state != "All":
#             filtered_df = filtered_df[filtered_df["State"] == state]
#         if university and university != "All":
#             filtered_df = filtered_df[filtered_df["University"] == university]

#         if eligibility and not filtered_df.empty:
#             # Compute embedding for user input
#             user_embedding = model.encode(eligibility, convert_to_tensor=True)
#             # Compute cosine similarity
#             filtered_indices = filtered_df.index.tolist()
#             filtered_embeddings = scholarship_embeddings[filtered_indices]
#             similarities = util.cos_sim(user_embedding, filtered_embeddings).numpy().flatten()
#             # Add similarity scores to dataframe
#             filtered_df = filtered_df.copy()  # Avoid SettingWithCopyWarning
#             filtered_df["Similarity"] = similarities
#             # Sort by similarity (descending)
#             filtered_df = filtered_df.sort_values(by="Similarity", ascending=False)
#             # Convert to list of tuples for template
#             scholarships = [tuple(x) + (x["Similarity"],) for _, x in filtered_df.iterrows()]
#         else:
#             # No eligibility input or no filtered results, return filtered data
#             scholarships = [tuple(x) for _, x in filtered_df.iterrows()]

#     return render_template(
#         "index.html",
#         scholarships=scholarships,
#         states=states,
#         universities=universities
#     )

# if __name__ == "__main__":
#     app.run(debug=True)
    
    
    
    
import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import string

# Load and process data
@st.cache_data
def load_data():
    df = pd.read_csv('scholarship.csv')
    df['combined_text'] = df['Scholarship Details'].fillna('') + ' ' + df['Eligibility'].fillna('')
    df['cleaned'] = df['combined_text'].apply(clean_text)
    return df

def clean_text(text):
    text = text.lower()
    text = ''.join([c for c in text if c not in string.punctuation])
    tokens = text.split()
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    return ' '.join(tokens)

@st.cache_resource
def fit_vectorizer(cleaned_texts):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(cleaned_texts)
    return vectorizer, tfidf_matrix

def search_scholarships(query, vectorizer, tfidf_matrix, df, top_n=5):
    query_cleaned = clean_text(query)
    query_vector = vectorizer.transform([query_cleaned])
    cosine_sim = cosine_similarity(query_vector, tfidf_matrix).flatten()
    top_indices = cosine_sim.argsort()[-top_n:][::-1]
    return df.iloc[top_indices]

# Streamlit UI
st.title("🎓 Scholarship Search Engine")
st.markdown("Enter a query like: *engineering scholarships in India* or *financial aid for girl students*")

query = st.text_input("🔍 Search Scholarships")

if query:
    df = load_data()
    vectorizer, tfidf_matrix = fit_vectorizer(df['cleaned'])
    results = search_scholarships(query, vectorizer, tfidf_matrix, df)
    
    st.subheader("🔎 Top Matching Scholarships")
    st.dataframe(results[['State', 'University', 'Scholarship Details', 'Amount', 'Deadline', 'Eligibility']])
