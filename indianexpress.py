import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
url = 'https://indianexpress.com/todays-paper/'
articles = []
# Send a GET request to the webpage
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')
divs = soup.find_all('div', class_='today-paper')
for div in divs:
  li_elements = div.find_all('li')
  for li in li_elements:
    a_tag = li.find('a')
    strong = li.find('strong')
    if a_tag and 'href' in a_tag.attrs:
      href = a_tag['href']
      articles.append(href)

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")


from datetime import datetime
# Function to summarize multiple articles using the tokenizer and model directly
today = str(datetime.today().date())
def summarize_articles(articles, max_length=130, min_length=30):
    """
    Summarizes a list of articles using the BART model directly.

    Parameters:
        articles (list of str): List of articles to summarize.
        max_length (int): Maximum length of the summary.
        min_length (int): Minimum length of the summary.

    Returns:
        list of str: List of summarized texts.
    """
    summaries = []

    for article in articles:
        long_text = ""
        response = requests.get(article)
        soup = BeautifulSoup(response.content, 'html.parser')
        divs = soup.find_all('div', class_='story_details')
        title = soup.find('title').text

        for div in divs:
            long_text += div.get_text()
        try:
            # Encode the article text (tokenization)
            inputs = tokenizer.encode("summarize: " + long_text, return_tensors="pt", max_length=1024, truncation=True)

            # Generate the summary using the model
            summary_ids = model.generate(inputs, max_length=max_length, min_length=min_length, length_penalty=2.0, num_beams=4, early_stopping=True)

            # Decode the generated summary
            summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            print(summary)
            # Append the summary to the list
            summaries.append([today,title,summary])
        except Exception as e:
            print(f"Error summarizing article: {e}")
            summaries.append(None)  # Append None if an error occurs

    return summaries



# Summarize all articles


# Print the summaries
# for i, summary in enumerate(summaries):
#     print(f"Summary of Article {i+1}: {summary}\n")


from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

def save_to_gsheet(new_row):


# Define the scope for Google Sheets API and Google Drive API
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Load the credentials.json
    creds = Credentials.from_service_account_file('gsheet.json', scopes=SCOPES)
    
    # Authorize and connect to Google Sheets
    client = gspread.authorize(creds)
    sheet = client.open('news_summary').sheet1  # Change to your Google Sheet name
    print(sheet.get_all_records())
    #sheet.append_rows(summaries)
    #print("Rows added successfully.")

if __name__ == "__main__":
  summaries = summarize_articles(articles)
  save_to_gsheet(summaries)
