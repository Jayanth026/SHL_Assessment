import streamlit as st
import requests

st.title("SHL Assessment Recommender")

q = st.text_area("Enter JD / Query")

if st.button("Recommend"):
    r = requests.post("http://localhost:8000/recommend", json={"query": q})
    data = r.json()["recommended_assessments"]
    st.dataframe(data)
