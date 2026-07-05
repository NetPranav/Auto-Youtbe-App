# AI Provider Abstraction & Workflows

## The Abstraction Layer
The system does not depend exclusively on OpenAI. Using a library like `litellm` (or a custom wrapper), we can switch models just by changing an environment variable.

```python
# Pseudo-code example of abstraction
class AIProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        pass

class OpenAIProvider(AIProvider):
    # Implements via openai library
    
class LocalOllamaProvider(AIProvider):
    # Implements via local localhost:11434 endpoints
```

## Agent Roles
We utilize multi-agent workflows for quality control, specifically in the Content Engine.

1. **The Researcher Agent:**
   - **System Prompt:** "You are an expert YouTube strategist. Given these news headlines, pick the one most likely to go viral in the [NICHE] space. Output JSON with topic and rationale."
   
2. **The Writer Agent:**
   - **System Prompt:** "You are a master storyteller. Write a 10-minute script on [TOPIC]. Hook the viewer in the first 10 seconds. Use engaging, fast-paced language."

3. **The Critic Agent (The Secret Sauce):**
   - **System Prompt:** "You are a harsh YouTube critic. Read the following script. Score it on Hook, Pacing, and Clarity. If the score is below 8/10, output exactly what needs changing."
   - **Loop:** The Writer takes the Critic's notes and rewrites. This loops up to 3 times.

4. **The SEO Agent:**
   - **System Prompt:** "Generate a highly clickable YouTube Title (under 60 chars) and 3 tags based on this script."

## Hallucination Mitigation
- **Grounding:** The Writer agent is fed the raw scraped facts from the Researcher. It is instructed strictly NOT to invent facts.
- **Critic Verification:** The Critic agent has a verification step to ensure the script doesn't deviate wildly from the initial source URL's context.
