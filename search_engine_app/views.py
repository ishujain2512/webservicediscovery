import time
from django.shortcuts import render
from .utils import expand_query, semantic_search, load_links_from_mongodb


def result_detail(request):
    # Extract the URL parameter from the request
    url = request.GET.get('url')
    print("URL parameter:", url)

    # Query the MongoDB database to find the detailed information for the URL
    processed_links = load_links_from_mongodb('4thyearproject', 'apis')
    detailed_result = next(
        (link for link in processed_links if link['link'] == url), None)
    print("Detailed Result:", detailed_result)

    # Render the detailed result page with the information
    return render(request, 'temp_detailed_result.html', {'detailed_result': detailed_result})


def home(request):
    return render(request, 'temp_home.html')


def results(request):
    # Start time to measure the time taken to fetch results
    start_time = time.time()

    # Extract search query from the request
    search_query = request.GET.get('query', '')

    # Load processed links from MongoDB
    processed_links = load_links_from_mongodb('4thyearproject', 'apis')

    # Extract descriptions from processed links
    descriptions = [link['processed_description'] for link in processed_links]

    # Expand search query and prepare for semantic search
    expanded_query = expand_query(search_query, threshold=0.6)
    expanded_query1 = expand_query(search_query, threshold=0.1)

    # Prepare relevant links based on similarities
    relevant_links = []
    for expanded_term in expanded_query:
        term_query = expanded_term[1]  # Use the lemmatized term for the query
        similarities = semantic_search(term_query, descriptions)
        for link, relevance in zip(processed_links, similarities):
            if relevance >= 0.2:  # Adjust threshold as needed
                relevant_links.append({
                    "Relevance": relevance,
                    "Name": link['name'],
                    "Category": link['category'],
                    "Description": link['description'],
                    "Link": link['link']
                })

    # Sort relevant links by relevance
    relevant_links.sort(key=lambda x: x['Relevance'], reverse=True)

    # Calculate the time taken to fetch results
    fetch_results_time = time.time() - start_time

    # Prepare data for search term and synonyms
    original_search_term = search_query
    processed_search_terms = []
    for term in expanded_query1:
        term_data = {
            'Term': term[0],
            'ProcessedTerm': term[1],
            'Synonyms': ', '.join(term[2])
        }
        if term_data not in processed_search_terms:
            processed_search_terms.append(term_data)

    ranked_search_terms = []
    for term in expanded_query:
        term_data = {
            'Term': term[0],
            'ProcessedTerm': term[1],
            'Synonyms': ', '.join(term[2])
        }
        if term_data not in ranked_search_terms:
            ranked_search_terms.append(term_data)
    # Pass data to the template
    context = {
        'original_search_term': original_search_term,
        'ranked_search_terms': ranked_search_terms,
        'search_terms': processed_search_terms,
        'results': relevant_links,
        'fetch_results_time': fetch_results_time  # Include time taken to fetch results
    }

    # Render the results template with the context
    return render(request, 'temp_results.html', context)


def error_page(request, status_code=500):
    return render(request, 'error_page.html', status=status_code)
