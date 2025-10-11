// gets references to the input, button, and output elements
const inputField = document.getElementById("promptInput");
const submitButton = document.getElementById("generateBtn");
const outputArea = document.getElementById("responseOutput");

// converts Website->Link patterns in the text to clickable links
function linkify(text) {
    const urlRegex = /(.+?)->(https?:\/\/[^\s]+)/gm;
    return text.replace(urlRegex, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-indigo-400 hover:underline">$1</a>');
}

// handles the button click event
submitButton.addEventListener("click", async () => {
    const prompt = inputField.value;
    outputArea.textContent = "Generating...";

    // sends the fragment to the backend for reconstruction
    const response = await fetch("/generate", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ fragment: prompt }),
    });

    // gets the reconstructed response and updates the output
    const data = await response.json();
    outputArea.innerHTML = linkify(data.response);
});