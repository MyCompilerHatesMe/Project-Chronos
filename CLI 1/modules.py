import google.generativeai as genai
import os
import requests
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def text_reconstruction(fragment):
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"Reconstruct this old digital text and explain its slang or missing words:\n\n'{fragment}'"
    response = model.generate_content(prompt)
    return response.text.strip()

def web_search(query):
    api_key = os.getenv("SEARCH_API_KEY")
    params = {"q": query, "api_key": api_key}
    res = requests.get("https://serpapi.com/search", params=params).json()
    results = []
    for r in res.get("organic_results", [])[:5]:
        results.append(r["link"])
    return results


def report_generation(fragment, reconstruction, source):
    report = "--- RECONSTRUCTION REPORT ---\n\n"
    report += f"[Original Fragment]\n> {fragment}\n\n"
    report += f"[AI-Reconstructed Text]\n> {reconstruction}\n\n"
    report += "[Contextual Sources]\n"
    for s in source:
        report += f"* {s}\n"
    return report
