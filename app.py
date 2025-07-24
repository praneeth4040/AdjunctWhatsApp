import requests

def search_google(query):
    API_KEY = "AIzaSyBKQK56XpTkcveb7OyixRr0SDvnQ57VM3I"
    CX = "334ab8aafab43484c"
    url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        "q": query,
        "key": API_KEY,
        "cx": CX
    }

    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")

        if response.status_code != 200:
            return f"❌ API Error: {response.status_code} - {response.text}"
        
        data = response.json()
        print("Response JSON:", data)  # Debug

        if "items" not in data:
            return "❌ No results found or API limit reached."

        results = []
        for item in data["items"][:3]:
            title = item.get('title', 'No title')
            snippet = item.get('snippet', 'No description available')
            link = item.get('link', '')
            results.append(f"*{title}*\n_{snippet}_\n🔗 {link}")

        return "\n\n".join(results)

    except Exception as e:
        return f"❌ Exception: {str(e)}"
