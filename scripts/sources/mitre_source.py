import requests

def fetch_mitre():
    url = "https://attack.mitre.org/api.php?action=ask&format=json&query=[[Category:Technique]]"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("query", {}).get("results", {}).keys():
            results.append({
                "source": "mitre",
                "text": item,
                "metadata": {}
            })
        return results
    except Exception as e:
        print(f"[MITRE] Error: {e}")
        return []
