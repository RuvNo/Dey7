import PyPDF2
import nltk
import requests
import os
import re

from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer


def get_models_list():
    url = "http://ollama:11434/api/tags"

    response = requests.get(url)

    if response.status_code == 200:
        response_data = response.json()
        return response_data["models"]
    else:
        print("Failed to connect to Ollama Docker:", response.status_code, response.text)


def get_model(name):
    url = "http://ollama:11434/api/pull"

    data = {
        "name": name,
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        # Parse the JSON response
        print(f"Model successfully loaded")
        return True
    else:
        print("Failed to load model: ", response.status_code, response.text)
        return False


def filename_to_productname(filename):
    match = re.search(r'XBO.*?(?=\.pdf)', filename)
    if match:
        return match.group(0)
    return None


def sentences_to_embeddings(sentences, pdf_path, model):
    embeddings = model.encode(sentences)

    sentences = [f"{filename_to_productname(pdf_path)}: {sentence}" for sentence in sentences]

    return list(zip(sentences, embeddings))


def text_to_sentences(text_str):
    return sent_tokenize(text_str)


def pdf_to_text(pdf_path):
    # Open the PDF file in read-binary mode
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Initialize an empty string to store the text
        text = ''

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()

    return text


def pdf_to_embeddings(pdf_path, model):
    text = pdf_to_text(pdf_path)
    sentences = text_to_sentences(text)
    embeddings = sentences_to_embeddings(sentences, pdf_path, model)
    return embeddings


def initialize_embeddings(model):
    directory = "source_files"
    file_paths = [os.path.join(directory, filename) for filename in os.listdir(directory) if os.path.isfile(os.path.join(directory, filename))]

    sentences_with_embeddings = [pdf_to_embeddings(path, model) for path in file_paths]

    return sentences_with_embeddings


def get_semantic_search_result(entries, question, model):
    flat_entries = sum(entries, [])
    source_embeddings = [entry[1] for entry in flat_entries]
    query_embeddings = model.encode(question)
    similarities = model.similarity(source_embeddings, query_embeddings)

    entries_with_similarities = list(zip(flat_entries, [tensor[0].item() for tensor in similarities]))
    filtered_similarities = list(filter(lambda entry: entry[1] > 0.45, entries_with_similarities))
    return [entry[0][0] for entry in filtered_similarities]


def main():
    nltk.download('punkt_tab')

    transformer_model = SentenceTransformer("all-MiniLM-L6-v2")

    context_with_embeddings = initialize_embeddings(transformer_model)

    model_choice = input("Do you want to use tinyllama (a) or llama3 (b)?\n(a,b) ")
    model_name = 'tinyllama' if model_choice == 'a' else 'llama3'
    models = get_models_list()
    model = [m for m in models if m["name"] == f"{model_name}:latest"]

    if not model:
        print("No model found.")
        print("Downloading model...")
        get_model(model_name)
        models = get_models_list()
        print("Model downloaded successfull")
        print(models)
    else:
        print("Model found.")
        print(models)

    url = "http://ollama:11434/api/generate"

    question = input("Question: ")
    print("...thinking...")

    finished = False

    while not finished:
        context = get_semantic_search_result(context_with_embeddings, question, transformer_model)
#         prompt = f"""
# Bitte beantworte die folgende Frage: {question}.
# Berücksichtige dabei, falls angebracht, die nachfolgenden Quellen:
# ############################Quellen############################
# {context}
# ########################################################
# """
        data = {
            "model": "tinyllama",
            "prompt": question,
            "stream": False
        }

        response = requests.post(url, json=data)

        if response.status_code == 200:

            response_data = response.json()
            print(f"Answer: {response_data['response']}")
            cont = input("Do you want to continue the chat?\n(y, n) ")
            if cont == 'y':
                question = input("What is your next question?\nQuestion: ")
                print("...thinking...")
            else:
                finished = True
                print("Okay. Thank you very much and come back soon. (y)")
        else:
            print("Failed to connect to Ollama Docker:", response.status_code, response.text)


if __name__ == '__main__':
    main()
