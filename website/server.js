import { GoogleGenAI } from "@google/genai";
import express from "express";
import "dotenv/config";

const app = express();
const port = 3000;

app.use(express.json());
app.use(express.static("public"))

const ai = new GoogleGenAI({});

const searchTool = {
    googleSearch: {},
};

const sysInstruction = `
You are Project Chronos. An AI designed and specialising in reconstructing fragmented text.
You will be given an input fragment. This is the minute to minute you must follow
You will be given a google search tool, use it to verify everything.
1) Analyze the fragment for context, slang, and missing words.
2) Reconstruct the text to the best of your ability, filling in gaps and explaining slang.
3) Provide a list of web pages that you got your information from, with links. 
Maximum 2 results per term you searched.
you do not need to provide links for the explanation for the slang, just the meaning.
make sure the links are in the format of "Website->Link" ensure only the -> is between the link and website name. nothing else.
4) Format your output as a report with sections for the original fragment, the reconstructed text, and the sources.
6) The report should be in plain text format, suitable for reading in a console.
The 6th point means, no mark down formatting, only plain text. NO **, *, _. ONLY spacing.
`


const config = {
    tools: [searchTool],
    thinkingConfig: {
        thinkingBudget: -1, //dynamic thinking
    },
    systemInstruction: sysInstruction,
}

async function generateText(prompt) {
    const response = await ai.models.generateContent({
        model: "gemini-2.5-flash",
        contents: prompt,
        config: config,
    })
    return response.text;
}

app.post("/generate", async (req, res) => {
    try{
        const text = await generateText(req.body.fragment);
        res.json({response: text});
    }catch (error){
        console.error(error);
        res.status(500).json({
            error: "Failed to generate content"
        })
    }
});

app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
})