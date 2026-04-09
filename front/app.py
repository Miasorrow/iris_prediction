import streamlit as st
import requests
import os

st.title("🌸 Iris Predictor", color="green")

st.write("Entre les caractéristiques de la fleur :")

# Inputs utilisateur
sepal_length = st.number_input("Sepal length", value=5.1)
sepal_width = st.number_input("Sepal width", value=3.5)
petal_length = st.number_input("Petal length", value=1.4)
petal_width = st.number_input("Petal width", value=0.2)

if st.button("Prédire"):
    # Juste ca qui a changé c'est pour avoir la bonne url qui est donné en variable dans le docker compose
    url = os.getenv("API_URL")
    
    params = {
        "sepal_length": sepal_length,
        "sepal_width": sepal_width,
        "petal_length": petal_length,
        "petal_width": petal_width
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        prediction = response.json()["prediction"]

        if prediction == 0:
            st.success("🌸 Setosa")
        elif prediction == 1:
            st.success("🌼 Versicolor")
        else:
            st.success("🌺 Virginica")
    else:
        st.error("Erreur API 😢")