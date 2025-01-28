from flask import Flask, jsonify
import google.generativeai as genai
import PyPDF2
import requests
from dotenv import load_dotenv
import os

# Initialize Flask app
app = Flask(__name__)

# Disable SSL verification for requests
session = requests.Session()
session.verify = False  # Disable SSL verification for all requests made using this session

# Load environment variables
load_dotenv(".env")
api_key = os.getenv("GEMINI_API_KEY")

# Function to extract text from PDFs
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

# Function to compare texts and get the list of changes
def get_list_of_changes(original_text, modified_text):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt="Here is the text of the original NDA : "+str(original_text)+"here is the text of the modified NDA:" + str(modified_text) + "Could you compare both of them and list the changes made from the new one to the old one.THE ONLY RESPONSE SHOULD BE IN THE FOLLOWING FORMAT: Existing: line 1 changed to New : line 1 || Existing: line 2 changed to New: line 2"
    
    response = model.generate_content(prompt)
    result=response.text.split("||")
    return result

# Function to classify changes into trivial and non-trivial
def classify_changes(original_text, modified_text):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = "Here is the text of the original NDA : "+str(original_text)+"here is the text of the modified NDA:" + str(modified_text) + "could you compare both of them and tell me which changes are trivial and non-trivial. THE ONLY RESPONSE SHOULD BE IN THE FOLLOWING FORMAT :"+"Trivial Changes: Trivial Change 1 || Trivial Change 2 + Non-Trivial Changes: Non-Trivial Change 1||Non-Trivial Change 2. If there are no changes in either category, return No changes in this field"
    
    result=[]

    while(len(result)<2):
        response = model.generate_content(prompt)
        result = response.text.split("+")

    trivial_changes = (result[0].split(":"))[1].split("||")
    non_trivial_changes = (result[1].split(":"))[1].split("||")
    
    return {"trivial_changes": trivial_changes, "non_trivial_changes": non_trivial_changes}

# Flask API for listing changes
@app.route('/')
def home():
    return "API Guide for dummies"+ "\n" + '''"http://127.0.0.1:5000/list-changes

response= {
  "list_of_changes": [
    "Existing: 4.1 This agreement together with any documents referred to in it constitutes the entire agreement (and supersedes any previous written or oral agreement) between the parties related to the subject matter of this agreement. For the avoidance of doubt, any agreement between a member of the ION Group and a member of the Company\u2019s group remains in force and is unaffected by this agreement.  1.1 Each Receiving Party recognizes  that any breach of this agreement  could cause irreparable harm to the Disclosing Party and that monetary damages would be inadequate to compensate the Disclosing Party for such breach . changed to New: 4.1 This agreement together with any documents referred to in it constitutes the entire agreement (and supersedes any previous written or oral agreement) between the parties related to the subject matter of this agreement. For the avoidance of doubt, any agreement between a member of the ION Group and a member of the Company\u2019s group remains in force and is unaffected by this agreement.  1.1 Each Receiving Party recognizes that any breach of this agreement could cause harm to the Disclosing Party, and the Disclosing Party's liability will be limited to monetary damages only.\n"
  ]
}

http://127.0.0.1:5000/classify-changes
{
  "non_trivial_changes": [
    " Section 4.1 now limits the Disclosing Party's liability to monetary damages only. ",
    " The governing law was changed to Irish law.\n"
  ],
  "trivial_changes": [
    " Minor formatting differences (e.g., spacing, hyphenation) ",
    "  \"irreparable harm\" changed to \"harm\" in section 4.1 "
  ]
}"'''
@app.route('/list-changes', methods=['GET'])
def list_changes():
    original_pdf = 'original_pdf.pdf'  # Path to the original NDA PDF
    modified_pdf = 'modified_pdf.pdf'  # Path to the modified NDA PDF

    original_text = extract_text_from_pdf(original_pdf)
    modified_text = extract_text_from_pdf(modified_pdf)

    changes = get_list_of_changes(original_text, modified_text)
    return jsonify({"list_of_changes": changes})

# Flask API for classifying changes
@app.route('/classify-changes', methods=['GET'])
def classify_changes_api():
    original_pdf = 'original_pdf.pdf'  # Path to the original NDA PDF
    modified_pdf = 'modified_pdf.pdf'  # Path to the modified NDA PDF

    original_text = extract_text_from_pdf(original_pdf)
    modified_text = extract_text_from_pdf(modified_pdf)

    changes = classify_changes(original_text, modified_text)
    return jsonify(changes)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
