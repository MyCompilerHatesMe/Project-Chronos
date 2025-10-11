import os
from google import genai 
from google.genai import types


client = genai.Client()


systemInstruction = """
You are Project Chronos. An AI designed and specialising in reconstructing fragmented text.
You will be given an input fragment. This is the minute to minute you must follow
You will be given a google search tool, use it to verify everything.
1) Analyze the fragment for context, slang, and missing words.
2) Reconstruct the text to the best of your ability, filling in gaps and explaining slang.
3) Provide a list of web pages that you got your information from, with links. 
Maximum 2 results per term you searched.
you do not need to provide links for the explanation for the slang, just the meaning.
4) Format your output as a report with sections for the original fragment, the reconstructed text, and the sources.
6) The report should be in plain text format, suitable for reading in a console.
The 6th point means, no mark down formatting, only plain text. NO **, *, _. ONLY spacing.
"""

searchTool = types.Tool(
    google_search=types.GoogleSearch()
)

config = types.GenerateContentConfig(
    system_instruction=systemInstruction,
    thinking_config=types.ThinkingConfig(thinking_budget=-1), #dynamic thinking budget
    tools=[searchTool]
)

def text_reconstruction(fragment):
    prompt = f"Reconstruct this old text and reconstruct according to the system instructions:\n\n'{fragment}'"
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=fragment,
        config=config,
    )
    return response.text.strip()