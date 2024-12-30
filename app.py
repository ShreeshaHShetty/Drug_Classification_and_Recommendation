from flask import Flask, request, render_template
import joblib
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# Load model, vectorizer, and dataset
vectorizer = joblib.load('tfidfvectorizer.pkl')
model = joblib.load('passmodel.pkl')
df = pd.read_csv('drugsComTrain_raw.tsv', sep='\t')

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Function to suggest top drugs
def top_drugs_extractor(condition):
    # Filter top-rated drugs for the given condition
    df_top = df[(df['rating'] >= 9) & (df['usefulCount'] >= 100)].sort_values(by=['rating', 'usefulCount'], ascending=[False, False])
    drug_lst = df_top[df_top['condition'] == condition]['drugName'].head(10).tolist()  # Retrieve more options

    # Remove duplicates using set and return the top unique drugs
    unique_drugs = list(set(drug_lst))[:3]  # Convert to set to remove duplicates and take the first 3
    return unique_drugs if unique_drugs else ["No recommended drugs found."]

# Predict route
@app.route('/predict', methods=['POST'])
def predict():
    # Get input text from form
    input_text = request.form['text']
    transformed_text = vectorizer.transform([input_text])  # Transform text
    prediction = model.predict(transformed_text)[0]        # Predict condition
    
    # Suggest top drugs for the predicted condition
    top_drugs = top_drugs_extractor(prediction)
    
    # Return prediction and top drugs to the result page
    return render_template('result.html', condition=prediction, drugs=top_drugs)

# Run app
if __name__ == "__main__":
    app.run(debug=True)
