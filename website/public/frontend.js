const inputField = document.getElementById("promptInput");
const submitButton = document.getElementById("generateBtn");
const outputArea = document.getElementById("responseOutput");

function linkify(text) {
    //basically finds all Website->Link patterns and converts them to clickable links
    const urlRegex = /(.+?)->(https?:\/\/[^\s]+)/gm;
    return text.replace(urlRegex, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-indigo-400 hover:underline">$1</a>');
}

submitButton.addEventListener("click", async () => {
    const prompt = inputField.value;
    outputArea.textContent = "Generating...";

    const response = await fetch("/generate", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ fragment: prompt }),
    });

    const data = await response.json();
    outputArea.innerHTML = linkify(data.response);
});