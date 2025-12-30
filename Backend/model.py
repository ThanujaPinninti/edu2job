import pandas as pd
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

df = pd.read_csv("job_role_dataset.csv")

le_degree = LabelEncoder()
le_spec = LabelEncoder()
le_job = LabelEncoder()

df["degree"] = le_degree.fit_transform(df["degree"])
df["specialization"] = le_spec.fit_transform(df["specialization"])
df["job_role"] = le_job.fit_transform(df["job_role"])
df["skills"] = df["skills"].apply(lambda x: [i.strip() for i in x.split(",")])
df["certifications"] = df["certifications"].apply(lambda x: [i.strip() for i in x.split(",")])

mlb_skills = MultiLabelBinarizer()
mlb_certs = MultiLabelBinarizer()

skills_encoded = mlb_skills.fit_transform(df["skills"])
certs_encoded = mlb_certs.fit_transform(df["certifications"])

skills_df = pd.DataFrame(skills_encoded, columns=mlb_skills.classes_)
certs_df = pd.DataFrame(certs_encoded, columns=mlb_certs.classes_)

X = pd.concat(
    [df[["degree", "specialization", "cgpa"]], skills_df, certs_df],
    axis=1
)

y = df["job_role"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(" Model Accuracy:", round(accuracy * 100, 2), "%")

joblib.dump(model, "job_model.pkl")
joblib.dump(le_degree, "le_degree.pkl")
joblib.dump(le_spec, "le_spec.pkl")
joblib.dump(le_job, "le_job.pkl")
joblib.dump(mlb_skills, "mlb_skills.pkl")
joblib.dump(mlb_certs, "mlb_certs.pkl")
joblib.dump(accuracy, "model_accuracy.pkl")

print("Model & accuracy saved successfully")
