import google.generativeai as genai
import PyPDF2
import requests
from dotenv import load_dotenv
import os
# Disable SSL verification for requests
session = requests.Session()
session.verify = False  # Disable SSL verification for all requests made using this session

# Set the environment variable for SSL certificate (optional if needed for other libraries)
load_dotenv(".env")
api_key = os.getenv("GEMINI_API_KEY")
# Step 1: Extract text from PDFs
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

# Example usage
def main():
    original_pdf = 'original_pdf.pdf'  # Path to the original NDA PDF
    modified_pdf = 'modified_pdf.pdf'  # Path to the modified NDA PDF

    # Step 1: Extract text from the PDFs
    original_text = extract_text_from_pdf(original_pdf)
    modified_text = extract_text_from_pdf(modified_pdf)

    # # Step 2: Compare the original and modified PDFs
    # changes = compare_pdfs(original_text, modified_text)

    # # Step 3: Configure Gemini API
    # configure_gemini(api_key)

    # # Step 4: Generate the response using Gemini
    # response = generate_response_with_gemini(changes)

    # # Step 5: Format and print the response
    # if response:
    #     formatted_response1  = format_gemini_response(response)
    #     print(formatted_response1)
    # else:
    #     print("No valid response from Gemini.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Differences between original text and new ones
    prompt="Here is the text of the original NDA : "+str(original_text)+"here is the text of the modified NDA:" + str(modified_text) + "Could you compare both of them and list the changes made from the new one to the old one.THE ONLY RESPONSE SHOULD BE IN THE FOLLOWING FORMAT: Existing: line 1 changed to \n New : line 1 || Existing: line 2 changed to New: line 2"
    response=model.generate_content(prompt)
    print("List of changes")
    print(response.text)

    # Listing out Trivial & Non-Trivial Changes
    prompt="Here is the text of the original NDA : "+str(original_text)+"here is the text of the modified NDA:" + str(modified_text) + "could you compare both of them and tell me which changes are trivial and non-trivial. THE ONLY RESPONSE SHOULD BE IN THE FOLLOWING FORMAT :"+"Trivial Changes: Trivial Change 1 || Trivial Change 2 + Non-Trivial Changes: Non-Trivial Change 1||Non-Trivial Change 2. If there are no changes in either category, return No changes in this field"
    response = model.generate_content(prompt)
    result=response.text.split("+")
    trivial_changes=(result[0].split(":"))[1].split("||")
    non_trivial_changes=(result[1].split(":"))[1].split("||")
    print("Trivial Changes")
    for change in trivial_changes:
      print(change)
    print("Non-Trivial Changes")
    for change in non_trivial_changes:
      print(change)

if __name__ == "__main__":
    main()
