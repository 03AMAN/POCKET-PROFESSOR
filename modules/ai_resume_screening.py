from flask import Blueprint, request, render_template, current_app
import os
import docx2txt
import PyPDF2
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertTokenizer, BertModel
import torch
import logging
# Blueprint setup
ai_resume_screening_bp = Blueprint('ai_resume_screening', __name__, template_folder='../templates')
# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Load models
nlp = spacy.load('en_core_web_sm')
bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased')
SECTIONS = ['experience', 'skills', 'education', 'projects']
#  Ensures upload folder exists
def ensure_upload_folder(upload_folder='uploads'):
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        logging.error(f"Error reading PDF: {e}")
    return text
def extract_text_from_docx(file_path):
    try:
        return docx2txt.process(file_path)
    except Exception as e:
        logging.error(f"Error reading DOCX: {e}")
        return ""
def extract_text_from_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logging.error(f"Error reading TXT: {e}")
        return ""
def extract_text(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file_path.endswith('.txt'):
        return extract_text_from_txt(file_path)
    else:
        logging.warning(f"Unsupported format for {file_path}")
        return ""
def preprocess_text(text):
    doc = nlp(text.lower())
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(tokens)
def get_bert_embeddings(text):
    inputs = bert_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = bert_model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
def generate_section_embeddings(text):
    sections = {section: "" for section in SECTIONS}
    for section in SECTIONS:
        if section in text.lower():
            sections[section] = " ".join([sent.text for sent in nlp(text).sents if section in sent.text.lower()])
    return {section: get_bert_embeddings(preprocess_text(content)) for section, content in sections.items() if content}
def generate_explanations(job_description, resume):
    explanations = []
    job_sections = generate_section_embeddings(job_description)
    resume_sections = generate_section_embeddings(resume)
    for section, job_emb in job_sections.items():
        if section in resume_sections:
            res_emb = resume_sections[section]
            score = cosine_similarity([job_emb], [res_emb])[0][0]
            explanations.append(f"{section.capitalize()} section similarity: {round(score, 2)}")
    return explanations if explanations else ["No specific sections matched significantly."]
def generate_suggestions(job_description, resume):
    suggestions = []
    job_sections = generate_section_embeddings(job_description)
    resume_sections = generate_section_embeddings(resume)

    for section in SECTIONS:
        if section in job_sections:
            job_emb = job_sections[section]
            if section in resume_sections:
                res_emb = resume_sections[section]
                score = cosine_similarity([job_emb], [res_emb])[0][0]
                if score < 0.5:
                    suggestions.append(f"Improve your {section} section (score: {round(score,2)}).")
                else:
                    suggestions.append(f"{section} section is decent (score: {round(score,2)}), but can be refined.")
            else:
                suggestions.append(f"Add a {section} section to your resume.")
        else:
            suggestions.append(f"{section} section not emphasized in the job description.")
    suggestions.append("Customize your resume with measurable achievements and relevant skills.")
    return suggestions
def save_resume_file(resume_file):
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], resume_file.filename)
    resume_file.save(upload_path)
    return upload_path

# ROUTES
@ai_resume_screening_bp.route("/resume-screening")
def matchresume():
    return render_template('ai_resume_screening.html')

@ai_resume_screening_bp.route('/matcher', methods=['GET', 'POST'])
def matcher():
    if request.method == 'GET':
        # Just render the page (probably with an upload form)
        return render_template('ai_resume_screening.html')

    # POST request handling below
    job_description = request.form.get('job_description', '')
    resume_files = request.files.getlist('resumes')

    if not job_description or not resume_files:
        return render_template('ai_resume_screening.html', message="Upload resumes and enter a job description.")

    job_description_processed = preprocess_text(job_description)
    resumes_raw = [extract_text(save_resume_file(file)) for file in resume_files]
    resumes_processed = [preprocess_text(resume) for resume in resumes_raw]

    job_embedding = get_bert_embeddings(job_description_processed)
    resume_embeddings = [get_bert_embeddings(resume) for resume in resumes_processed]
    similarities = cosine_similarity([job_embedding], resume_embeddings)[0]
    top_indices = similarities.argsort()[-5:][::-1]
    top_resumes = [resume_files[i].filename for i in top_indices]
    similarity_scores = [round(similarities[i], 2) for i in top_indices]

    if all(score < 0.5 for score in similarity_scores):
        return render_template('ai_resume_screening.html', message="No strong matches found.",
                               top_resumes=top_resumes, similarity_scores=similarity_scores)

    suggestions_list = []
    explanations_list = []
    for i in top_indices:
        suggestions_list.append(generate_suggestions(job_description, resumes_raw[i]))
        explanations_list.append(generate_explanations(job_description, resumes_raw[i]))

    return render_template('ai_resume_screening.html', message="Top matching resumes:",
                           top_resumes=top_resumes, similarity_scores=similarity_scores,
                           resume_suggestions=suggestions_list, score_explanations=explanations_list)
