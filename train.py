from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import mlflow
import mlflow.sklearn

# 🔥 active autolog
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.sklearn.autolog()

def train_model():
    data = load_iris()
    X = data.data
    y = data.target

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    with mlflow.start_run():
        model = RandomForestClassifier()
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        print("Accuracy :", accuracy)

        # mlflow.log_metric("accuracy", accuracy)
        # mlflow.sklearn.log_model(model, "model")
        # mlflow.end_run()

        # exemple de fleur
        sample = [[5.1, 3.5, 1.4, 0.2]]

        prediction = model.predict(sample)

        print(prediction)

    joblib.dump(model, "model.pkl")
    print("Model saved as model.pkl")

if __name__ == "__main__":
    train_model()
