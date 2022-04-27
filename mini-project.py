from pdfminer.high_level import extract_text
 
import docx2txt
import nltk
import re
import os
import csv
 
 
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('maxent_ne_chunker')
#nltk.download('words')
#nltk.download('stopwords')

PHONE_REG = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')
YEAR_REG = re.compile(r'\b[21][09][0-9][0-9]')
DIRECTORY = r"/home/parth/Downloads/nlp/resume/"
INFO_ROWS = []
index = 0

SKILLS_DB = [
    'machine learning',
    'data science',
    'java',
    'javascript',
    'react',
    'python',
    'word',
    'excel',
    'English',
]

RESERVED_WORDS = [
    'school',
    'college',
    'university',
    'academy',
    'faculty',
    'institute',
    'faculdades',
    'Schola',
    'schule',
    'lise',
    'lyceum',
    'lycee',
    'polytechnic',
    'kolej',
    'ünivers',
    'okul',
]

def extract_year_of_graduation(text):
    year = re.findall(YEAR_REG, text)
    year.sort(key = int)
    return year[len(year)-1]
 
def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def extract_text_from_docx(docx_path):
    txt = docx2txt.process(docx_path)
    if txt:
        return txt.replace('\t', ' ')
    return None

def extract_phone_number(resume_text):
    phone = re.findall(PHONE_REG, resume_text)
 
    if phone:
        number = ''.join(phone[0])
 
        if resume_text.find(number) >= 0 and len(number) <= 16:
            return number
    return None

def extract_emails(resume_text):
    return re.findall(EMAIL_REG, resume_text)

def extract_skills(input_text):
    stop_words = set(nltk.corpus.stopwords.words('english'))
    word_tokens = nltk.tokenize.word_tokenize(input_text)
 
    # remove the stop words
    filtered_tokens = [w for w in word_tokens if w not in stop_words]
 
    # remove the punctuation
    filtered_tokens = [w for w in word_tokens if w.isalpha()]
 
    # generate bigrams and trigrams (such as artificial intelligence)
    bigrams_trigrams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))
 
    # we create a set to keep the results in.
    found_skills = set()
 
    # we search for each token in our skills database
    for token in filtered_tokens:
        if token.lower() in SKILLS_DB:
            found_skills.add(token)
 
    # we search for each bigram and trigram in our skills database
    for ngram in bigrams_trigrams:
        if ngram.lower() in SKILLS_DB:
            found_skills.add(ngram)
 
    return found_skills

def extract_education(input_text):
    organizations = []
 
    # first get all the organization names using nltk
    for sent in nltk.sent_tokenize(input_text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk, 'label') and chunk.label() == 'ORGANIZATION':
                organizations.append(' '.join(c[0] for c in chunk.leaves()))
 
    # we search for each bigram and trigram for reserved words
    # (college, university etc...)
    education = set()
    for org in organizations:
        for word in RESERVED_WORDS:
            if org.lower().find(word) <= 0:
                education.add(org)
 
    return education

def add_information_to_csv(rows):
    fields = ['resume','email','phone','graduation year']
    csv_file = "records.csv"
    with open(csv_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        csvwriter.writerows(rows)

def print_information(text, filename):
    phone = extract_phone_number(text)
    email = extract_emails(text)
    skills = extract_skills(text)
    education = extract_education(text)
    year = extract_year_of_graduation(text)

    row = []
    row.append(filename)
    row.append(email[0])
    row.append(phone)
    row.append(year)
    global index
    INFO_ROWS.append(row)
    index+=1

 
    # print("phone\n" + phone)
    # print("email\n" + email[0])
    # print("******************************")
    # print(skills)
    # print("******************************")
    # print(education)
    # print("******************************")
    # print("graduation year\n" + year)
    # print("filename\n"+ filename)

if __name__ == '__main__':
    # text = ''
    #

    for filename in os.listdir(DIRECTORY):
        f = os.path.join(DIRECTORY, filename)
        if os.path.isfile(f):
            if f.endswith('.docx'):
                text = extract_text_from_docx(f)
                print(text)
                print_information(text, filename)
            elif f.endswith('.pdf'):
                text = extract_text_from_pdf(f)
                print(text)
                print_information(text, filename)
            else:
                print("Only .pdf and .docx file formats are supported")

    print(INFO_ROWS)

    add_information_to_csv(INFO_ROWS)
 
