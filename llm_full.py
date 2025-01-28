import google.generativeai as genai
import PyPDF2
import difflib
import requests

# Disable SSL verification for requests
session = requests.Session()
session.verify = False  # Disable SSL verification for all requests made using this session

# Set the environment variable for SSL certificate (optional if needed for other libraries)
api_key = "AIzaSyBwxUSGHaz8N_EetPwanQ9fFuw7jmEeqT4"
# Step 1: Extract text from PDFs
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def compare_pdfs(original_text, modified_text):
    # Compare the original and modified texts using difflib.ndiff
    diff = difflib.ndiff(original_text.splitlines(), modified_text.splitlines())

    # Create two separate lists for removed and added lines
    removed_lines = []
    added_lines = []

    # Loop through the diff and segregate lines into removed or added
    for line in diff:
        if line.startswith('- '):  # Lines starting with '-' are removed
            removed_lines.append(line[2:])  # Remove the '- ' part to get the actual text
        elif line.startswith('+ '):  # Lines starting with '+' are added
            added_lines.append(line[2:])  # Remove the '+ ' part to get the actual text

    # Combine the removed and added lines into one formatted response
    changes = ""

    if removed_lines:
        changes += "Removed lines:\n"
        changes += "\n".join(removed_lines) + "\n"

    if added_lines:
        changes += "\nAdded lines:\n"
        changes += "\n".join(added_lines) + "\n"

    # Return the combined changes as one response
    print(changes)

# Step 3: Configure Gemini API with your API key
def configure_gemini(api_key):
    genai.configure(api_key=api_key)

# Step 4: Generate a response using Gemini
def generate_response_with_gemini(formatted_changes):
    if not formatted_changes:
        return "No changes detected."

    # Prepare the prompt
    prompt = f"The following changes were made in the NDA document:\n"
    prompt += "\n".join(formatted_changes)
    prompt += "\n\n**Question**: Are these changes trivial or important? Please explain why."

    # API URL for Gemini
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=AIzaSyBwxUSGHaz8N_EetPwanQ9fFuw7jmEeqT4"

    # Headers including the API key for authentication
    headers = {
        "Authorization": f"Bearer AIzaSyBwxUSGHaz8N_EetPwanQ9fFuw7jmEeqT4",
        "Content-Type": "application/json"
    }

    # Payload (the data to send to the API)
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = session.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises exception for 4xx/5xx errors
        return response.json()  # Returning the JSON response
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None

# Helper function to format Gemini response
def format_gemini_response(response):
    if 'candidates' in response:
        model_response = response['candidates'][0]['content']['parts'][0]['text']
        return f"Classification of Changes:\n{model_response}"
    return "No response to format"

# Example usage
def main():
    api_key = "AIzaSyBwxUSGHaz8N_EetPwanQ9fFuw7jmEeqT4"  # Replace with your actual Gemini API key
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

    genai.configure(api_key="AIzaSyBwxUSGHaz8N_EetPwanQ9fFuw7jmEeqT4")
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
