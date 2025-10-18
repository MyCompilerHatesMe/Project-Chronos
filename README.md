# Project-Chronos: The AI Archaeologist

## Team Details

- Aadi Jha - SE25UMCS030
- TVNS Saicharan - SE25UCSE071
- I Sai Pranav Nihal - SE25UCSE096

## Project Description

Project Chronos is an Gemini-powered application designed to reconstruct fragmented digital information from a digital archaeological site, which consists of a vast and incomplete archive of ancient web pages and forum posts. The primary challenge is dealing with information gaps, obscure language, and forgotten cultural references, which make interpreting these digital relics difficult. Project Chronos aims to develop an intelligent system capable of piecing together these fragments, interpreting slang and contextual cues, and restoring missing information to provide a coherent understanding of the digital past.

## Setup Instructions

### For the Python CLI:
Paste the following command in your terminal and run it to install all the required packages.

```pip install -r requirements.txt```

Create a ```.env``` file in the project directory and paste ```set GOOGLE_API_KEY=<YOUR_API_KEY>``` in the file

Get your API key from the [Google AI Studio](https://aistudio.google.com/) and paste it in place of ```<YOUR_API_KEY>```

### For the website.

#### Prerequisites

Make sure you have [Node.js](https://nodejs.org/) and `npm` installed on your system. You can verify this by running:
```bash
node -v
npm -v
```

#### Getting the Files

```bash
git clone https://github.com/MyCompilerHatesMe/Project-Chronos.git
```

#### Change the present working directory

```bash
cd website
```

#### Create an Environment file

Create a ```.env``` file and inside the website directory and paste in ```GOOGLE_API_KEY=<YOUR_API_KEY_HERE>```

the above step is the same as the one for the CLI.

#### Installing packages

While inside the website directory run the below command to install all necessary packages.

```npm install``` 

#### Running the application

Now, to serve the page, run

```node server.js```

Go into your browser and type in ```localhost:3000``` to access the project.


## Usage Guide

Coming soon!
