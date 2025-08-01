import requests

def search_google_with_serpapi(query):
    api_key = "130c93b20bd51f7be8cc1cd7bb525e7d18c97c42aef97021c10f255b3b3edd05"  # Replace with your actual SerpAPI key

    if not query:
        print("⚠️ No query entered. Exiting.")
        return

    params = {
        "q": query,
        "engine": "google",
        "api_key": api_key,
        "num": 1
    }

    print("📡 Sending request to SerpAPI...\n")
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        data = response.json()
        
        print("✅ Response received.\n")
        
        results = data.get("organic_results", [])
        if not results:
            print("❌ No results found.")
            return

        print(f"🔎 Top {len(results)} Results for: \"{query}\"\n")
        for i, result in enumerate(results, start=1):
            print(f"{i}. {result.get('title')}")
            print(f"   {result.get('link')}")
            print(f"   {result.get('snippet', '')}\n")

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

# Run
user_input = input("Enter the query: ")
search_google_with_serpapi(user_input)
