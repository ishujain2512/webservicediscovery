from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


def load_links_from_mongodb(database_name, collection_name):
    client = MongoClient()
    db = client[database_name]
    collection = db[collection_name]
    processed_links = list(collection.find())
    client.close()
    return processed_links


def get_synonyms(word, threshold):
    synonyms = []
    original_synsets = wordnet.synsets(word)
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonym = lemma.name()
            # Check if the synonym is not the same as the original word
            if synonym.lower() != word.lower():
                # Calculate the path similarity between the original word and its synonym
                similarity = syn.path_similarity(original_synsets[0])
                if similarity is not None and similarity >= threshold:
                    # Convert the similarity score to a string with 2 decimal places
                    similarity_str = "{:.2f}".format(similarity)
                    # Create a string with the synonym and its relevancy score
                    synonym_str = f"(Relevancy:{similarity_str}) {synonym}"
                    # Add the synonym and its relevancy score to the list of synonyms
                    synonyms.append(synonym_str)
    return synonyms


def expand_query(query, threshold):
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(query.lower())
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    synonyms = [get_synonyms(token, threshold) for token in lemmatized_tokens]
    expanded_terms = []
    for idx, token in enumerate(tokens):
        expanded_terms.append((token, lemmatized_tokens[idx], synonyms[idx]))
        if token.endswith('s'):
            singular_form = token[:-1]  # Remove 's' to get the singular form
            singular_lemma = lemmatizer.lemmatize(singular_form)
            singular_synonyms = get_synonyms(singular_form, threshold)
            expanded_terms.append((token, singular_lemma, singular_synonyms))
    return expanded_terms


def semantic_search(query, descriptions):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(descriptions)
    query_tfidf = vectorizer.transform([query])
    similarities = cosine_similarity(query_tfidf, tfidf_matrix)
    return similarities.flatten()
