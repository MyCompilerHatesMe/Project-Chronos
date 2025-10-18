import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
import time
import re
from urllib.parse import quote_plus


class FragmentReconstructor:
    def __init__(self, gemini_api_key):
        self.fragment = ""
        self.reconstructed = ""
        self.contextual_sources = []
        self.unclear_terms = []

        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def identify_unclear_terms(self, text):
        """Use Gemini to identify slang, abbreviations, and unclear terms"""
        prompt = f"""Analyze this text and identify all slang terms, abbreviations, acronyms, and cultural references that might need explanation:

Text: "{text}"

Return ONLY a JSON array of terms that need explanation, like: ["smh", "g2g", "Top 8", "ttyl"]
Do not include common words. Focus on internet slang, abbreviations, and cultural references."""

        try:
            response = self.model.generate_content(prompt)
            terms_text = response.text.strip()

            # Extract terms from response
            import json
            # Try to parse as JSON
            try:
                terms = json.loads(terms_text)
            except:
                # Fallback: extract words in brackets or quotes
                terms = re.findall(r'["\']([^"\']+)["\']', terms_text)

            return terms
        except Exception as e:
            print(f"Error identifying terms: {e}")
            return []

    def reconstruct_text(self, fragment):
        """Reconstruct the fragmented text into complete sentences"""
        prompt = f"""You are reconstructing fragmented, informal text into complete, coherent sentences.

Original Fragment: "{fragment}"

Rules:
1. Expand all abbreviations and slang into full words
2. Make complete grammatical sentences
3. Preserve the original meaning and tone
4. Make it readable and understandable

Return ONLY the reconstructed text, nothing else."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error reconstructing: {e}"

    def search_term(self, term):
        """Search for a specific term prioritizing formal sources"""
        urls = []

        # Search with multiple strategies
        search_queries = [
            f"site:merriam-webster.com OR site:britannica.com OR site:wikipedia.org {term}",
            f"{term} definition etymology academic",
            f"{term} meaning scholarly source",
        ]

        for query in search_queries:
            search_url = f"https://www.bing.com/search?q={quote_plus(query)}"

            try:
                response = requests.get(search_url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find relevant URLs from search results
                for result in soup.find_all('li', class_='b_algo')[:5]:
                    link = result.find('a')
                    if link and link.get('href'):
                        url = link.get('href')
                        if url.startswith('http') and self._is_reputable_source(url):
                            urls.append(url)

                if len(urls) >= 3:
                    break
            except Exception as e:
                print(f"Search error for '{term}': {e}")
                continue

        # Priority fallback: try direct dictionary URLs
        if len(urls) < 2:
            priority_sources = [
                f"https://www.merriam-webster.com/dictionary/{quote_plus(term)}",
                f"https://en.wikipedia.org/wiki/{quote_plus(term.replace(' ', '_'))}",
                f"https://www.britannica.com/search?query={quote_plus(term)}",
            ]
            urls.extend(priority_sources)

        return list(dict.fromkeys(urls))[:3]  # Remove duplicates, keep order, return top 3

    def _is_reputable_source(self, url):
        """Check if URL is from a reputable source"""
        # Tier 1: Academic and dictionary sources (highest priority)
        tier1_domains = [
            'merriam-webster.com', 'britannica.com', 'wikipedia.org',
            'dictionary.com', 'oxfordlearnersdictionaries.com', 'oed.com',
            'cambridge.org', 'etymonline.com'
        ]

        # Tier 2: Reputable media and educational sources
        tier2_domains = [
            '.edu', '.gov', 'smithsonianmag.com', 'nationalgeographic.com',
            'scientificamerican.com', 'bbc.com', 'economist.com',
            'nature.com', 'jstor.org', 'archive.org'
        ]

        # Tier 3: General reputable sources
        tier3_domains = [
            'nytimes.com', 'theguardian.com', 'washingtonpost.com',
            'reuters.com', 'apnews.com'
        ]

        # Block known unreliable or informal sources
        blocked_domains = [
            'urbandictionary.com', 'reddit.com', 'quora.com',
            'yahoo.answers', 'facebook.com', 'twitter.com'
        ]

        url_lower = url.lower()

        # Block unreliable sources
        if any(blocked in url_lower for blocked in blocked_domains):
            return False

        # Accept any tier of reputable sources
        all_reputable = tier1_domains + tier2_domains + tier3_domains
        return any(domain in url_lower for domain in all_reputable)

    def scrape_definition(self, url, term):
        """Scrape definition/explanation from a URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()

            # Get title
            title = soup.find('title')
            title = title.get_text().strip() if title else term

            # Try to find definition content based on the source
            content = ""

            # Merriam-Webster specific
            if 'merriam-webster.com' in url:
                definition = soup.find('div', class_='vg') or soup.find('span', class_='dtText')
                if definition:
                    content = definition.get_text(separator=' ', strip=True)

            # Wikipedia specific
            elif 'wikipedia.org' in url:
                # Get first few paragraphs
                paragraphs = soup.find_all('p', limit=3)
                content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])

            # Britannica specific
            elif 'britannica.com' in url:
                article = soup.find('div', class_='topic-paragraph') or soup.find('section', class_='md-article-body')
                if article:
                    content = article.get_text(separator=' ', strip=True)

            # Dictionary.com specific
            elif 'dictionary.com' in url:
                definition = soup.find('div', {'data-type': 'word-definition-content'}) or soup.find('section',
                                                                                                     class_='e1hk9ate4')
                if definition:
                    content = definition.get_text(separator=' ', strip=True)

            # Generic fallback
            if not content:
                definition_selectors = [
                    soup.find('div', class_='meaning'),
                    soup.find('div', class_='definition'),
                    soup.find('article'),
                    soup.find('main')
                ]

                for selector in definition_selectors:
                    if selector:
                        content = selector.get_text(separator=' ', strip=True)
                        break

            if not content:
                content = soup.get_text(separator=' ', strip=True)

            # Limit content to reasonable length
            content = content[:1500]

            # Clean up content
            content = re.sub(r'\s+', ' ', content).strip()

            return {
                'term': term,
                'url': url,
                'title': title,
                'content': content,
                'source_type': self._identify_source_type(url)
            }
        except Exception as e:
            print(f"  Error scraping {url}: {e}")
            return None

    def _identify_source_type(self, url):
        """Identify the type of source for better formatting"""
        url_lower = url.lower()

        # Dictionaries
        if 'merriam-webster.com' in url_lower:
            return 'Merriam-Webster Dictionary'
        elif 'dictionary.com' in url_lower:
            return 'Dictionary.com'
        elif 'oxford' in url_lower:
            return 'Oxford Dictionary'
        elif 'cambridge' in url_lower:
            return 'Cambridge Dictionary'
        elif 'etymonline.com' in url_lower:
            return 'Etymology Dictionary'

        # Encyclopedias
        elif 'britannica.com' in url_lower:
            return 'Encyclopedia Britannica'
        elif 'wikipedia.org' in url_lower:
            return 'Wikipedia'

        # Academic & Government
        elif '.edu' in url_lower:
            return 'Educational Institution'
        elif '.gov' in url_lower:
            return 'Government Source'
        elif 'jstor.org' in url_lower:
            return 'Academic Journal (JSTOR)'
        elif 'nature.com' in url_lower:
            return 'Nature Journal'

        # Reputable Media
        elif 'smithsonianmag.com' in url_lower:
            return 'Smithsonian Magazine'
        elif 'nationalgeographic.com' in url_lower:
            return 'National Geographic'
        elif 'scientificamerican.com' in url_lower:
            return 'Scientific American'
        elif 'bbc.com' in url_lower:
            return 'BBC'
        elif 'economist.com' in url_lower:
            return 'The Economist'
        elif 'nytimes.com' in url_lower:
            return 'The New York Times'
        elif 'theguardian.com' in url_lower:
            return 'The Guardian'
        elif 'reuters.com' in url_lower:
            return 'Reuters'
        elif 'apnews.com' in url_lower:
            return 'Associated Press'

        # Default
        else:
            return 'Reputable Source'

    def gather_contextual_sources(self, terms):
        """Search and scrape contextual information for unclear terms"""
        print(f"\n🔍 Gathering context for {len(terms)} terms...")

        for i, term in enumerate(terms, 1):
            print(f"\n[{i}/{len(terms)}] Researching: '{term}'")

            urls = self.search_term(term)
            print(f"  Found {len(urls)} sources")

            for url in urls[:2]:  # Scrape top 2 URLs per term
                print(f"  Scraping: {url[:60]}...")
                data = self.scrape_definition(url, term)
                if data:
                    self.contextual_sources.append(data)
                    print(f"  ✓ Success")
                time.sleep(1)

    def generate_reconstruction_report(self, fragment):
        """Generate the complete reconstruction report"""
        print("\n" + "=" * 80)
        print("STARTING RECONSTRUCTION PROCESS")
        print("=" * 80)

        self.fragment = fragment

        # Step 1: Identify unclear terms
        print("\n📝 Step 1: Identifying unclear terms...")
        self.unclear_terms = self.identify_unclear_terms(fragment)
        print(f"Found terms: {', '.join(self.unclear_terms)}")

        # Step 2: Reconstruct the text
        print("\n🔧 Step 2: Reconstructing text...")
        self.reconstructed = self.reconstruct_text(fragment)
        print(f"Reconstructed: {self.reconstructed}")

        # Step 3: Gather contextual sources
        if self.unclear_terms:
            self.gather_contextual_sources(self.unclear_terms)

        # Step 4: Generate final report
        print("\n📄 Step 4: Generating final report...")
        return self.format_report()

    def format_report(self):
        """Format the final reconstruction report"""
        report = "--- RECONSTRUCTION REPORT ---\n\n"

        # Section 1: Original Fragment
        report += "[Original Fragment]\n\n"
        report += f"> \"{self.fragment}\"\n\n"

        # Section 2: AI-Reconstructed Text
        report += "[AI-Reconstructed Text]\n\n"
        report += f"> \"{self.reconstructed}\"\n\n"

        # Section 3: Contextual Sources
        report += "[Contextual Sources]\n\n"

        if self.contextual_sources:
            # Group by term
            sources_by_term = {}
            for source in self.contextual_sources:
                term = source['term']
                if term not in sources_by_term:
                    sources_by_term[term] = []
                sources_by_term[term].append(source)

            for term, sources in sources_by_term.items():
                report += f"* {term}\n"
                for source in sources:
                    source_type = source.get('source_type', 'Reference')
                    report += f"  - {source['url']} ({source_type})\n"
                report += "\n"
        else:
            report += "No additional context needed.\n\n"

        return report

    def save_report(self, report, filename=None):
        """Save report to file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reconstruction_report_{timestamp}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n💾 Report saved to: {filename}")
        return filename


# Example usage
if __name__ == "__main__":
    # Set your Gemini API key
    GEMINI_API_KEY = "<YOUR_API_KEY>"

    # Initialize reconstructor
    reconstructor = FragmentReconstructor(GEMINI_API_KEY)

    # Example fragmented text
    fragment = input("Enter fragmented text: ").strip()

    if not fragment:
        # Default example
        fragment = "smh at the top 8 drama. ppl need to chill. g2g, ttyl."
        print(f"Using example: {fragment}")

    # Generate reconstruction report
    report = reconstructor.generate_reconstruction_report(fragment)

    # Print report
    print("\n" + "=" * 80)
    print(report)
    print("=" * 80)

    # Save report
    reconstructor.save_report(report)