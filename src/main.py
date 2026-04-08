from fastapi import FastAPI
import joblib

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/predict")
def predict():
    model = joblib.load("model.pkl")

    # exemple de fleur
    sample = [[5.1, 3.5, 1.4, 0.2]]

    prediction = model.predict(sample)

    return {"prediction": int(prediction[0])}