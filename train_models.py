import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

# -----------------------------
# HEART MODEL (FIXED PROPERLY)
# -----------------------------

# Read dataset
heart = pd.read_csv("dataset/heart.csv")

#  FIX: split single column into multiple columns
if len(heart.columns) == 1:
    heart = heart[heart.columns[0]].str.split(",", expand=True)

    heart.columns = ['age','sex','cp','trestbps','chol','fbs',
                     'restecg','thalach','exang','oldpeak',
                     'slope','ca','thal','target']

# convert to numeric
heart = heart.apply(pd.to_numeric)

# split X and y
X = heart.drop("target", axis=1)
y = heart["target"]

model = RandomForestClassifier()
model.fit(X, y)

pickle.dump(model, open("models/heart_model.pkl", "wb"))

print("✅ Heart model trained successfully")


# KIDNEY MODEL (FIXED FINAL)

kidney = pd.read_csv("dataset/kidney_disease.csv")

# select needed columns
kidney = kidney[['bp','bgr','sc','classification']]

#  CLEAN DATA (IMPORTANT)
kidney['classification'] = kidney['classification'].str.strip()

# map values
kidney['classification'] = kidney['classification'].map({
    'ckd':1,
    'notckd':0
})

# REMOVE NaN rows
kidney = kidney.dropna()

# split
X = kidney[['bp','bgr','sc']]
y = kidney['classification']

model2 = RandomForestClassifier()
model2.fit(X, y)

pickle.dump(model2, open("models/kidney_model.pkl", "wb"))

print("✅ Kidney model trained successfully")