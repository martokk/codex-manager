import os
import time
from typing import Tuple, Optional
import anthropic
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# Initialize the Anthropic client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


# Define a retry decorator
# @retry(
#     stop=stop_after_attempt(2),
#     wait=wait_fixed(2),
#     retry=retry_if_exception_type(anthropic.APIError),
# )
def api_call(prompt: str, max_tokens: int) -> str:
    try:
        # response = client.completions.create(
        #     model="claude-3-5-sonnet-20240620",
        #     prompt=prompt,
        #     max_tokens_to_sample=max_tokens,
        # )

        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=max_tokens,
            temperature=0,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        )
    except anthropic.APIError as e:
        raise e

    text = message.content[0].text
    return text


def generate_summary(text: str) -> str:
    """Generates a summary of the inputted text."""
    # prompt = f"{HUMAN_PROMPT} Please provide a detailed summary of the following text, capturing all key points and main ideas:\n\n{text}\n\n{AI_PROMPT} Here's a detailed summary of the text:"

    prompt = f"""
    {HUMAN_PROMPT} You are tasked with summarizing and compressing an article while retaining all important information. Your goal is to create a condensed version that can be used as input for another language model prompt. Here is the article you need to summarize:

<article>
\n\n{text}\n\n
</article>

Follow these steps to summarize and compress the article:

1. Read the entire article carefully to understand its main points, key details, and overall structure.

2. Identify the core information, including:
   - Main topic or thesis
   - Key arguments or points
   - Important facts, data, or statistics
   - Crucial examples or case studies
   - Significant conclusions or implications

3. Remove unnecessary words, phrases, or sentences that do not contribute to the core information. This may include:
   - Redundant statements
   - Excessive adjectives or adverbs
   - Lengthy introductions or conclusions
   - Tangential information or anecdotes
   - Repetitive examples

4. Compress the remaining information by:
   - Combining related ideas into concise sentences
   - Using more precise and efficient language
   - Eliminating transition words or phrases when possible
   - Replacing long phrases with shorter equivalents

5. Ensure that all important information from the original article is retained in your summary. Do not omit any crucial facts, arguments, or conclusions.

6. Maintain the logical flow and structure of the original article in your compressed version.

7. Double-check your summary to make sure it accurately represents the original article's content and intent.

The summary should be significantly shorter than the original article while retaining all important information. Just provide the summary, do not provide "Here's the summary of the article" or something similar, just the summary.
---
{AI_PROMPT}
    """

    try:
        return api_call(prompt, 1000)
    except anthropic.APIError as e:
        print(f"Error generating summary: {str(e)}")
        raise e


def generate_brief(text: str) -> str:
    """Generates a very brief summary of the inputted text."""
    prompt = f"""
    {HUMAN_PROMPT} You are tasked with creating an extremely concise summary of an article in 1-3 sentences. Your goal is to capture the absolute essence of the article in a brief format that can be quickly understood. Here is the article you need to summarize:

    <article>
    \n\n{text}\n\n
    </article>

    Follow these steps to create the brief summary:

    1. Carefully read the entire article to grasp its core message and main points.

    2. Identify the single most important idea or theme of the article.

    3. Determine 1-2 key supporting points or details that are crucial to understanding the main idea.

    4. Craft 1-3 sentences that encapsulate the main idea and key supporting points. These sentences should:
    - Clearly state the central theme or argument of the article
    - Include only the most critical supporting information
    - Provide a complete but extremely condensed overview of the article's content

    5. Ensure your brief summary:
    - Is no longer than 3 sentences
    - Captures the essence of the article without any extraneous details
    - Is clear and easily understandable, even to someone unfamiliar with the topic
    - Accurately represents the original article's main point and intent

    6. Review your brief summary to confirm it provides a clear, concise, and accurate representation of the article's core message.

    Provide only the 1-3 sentence brief summary, without any introductory phrases like "Here's a brief summary" or similar statements.

    {AI_PROMPT}
    """

    try:
        return api_call(prompt, 300)
    except anthropic.APIError as e:
        print(f"Error generating brief: {str(e)}")
        raise e


def generate_date_range(text: str) -> Tuple[Optional[int], Optional[int]]:
    """Generates start and end date range from the inputted text."""
    prompt = f"""
    {HUMAN_PROMPT} You are an expert historian of the Ancient Sol universe. Your task is to analyze an article and determine the time period it covers or refers to within this universe. You need to identify the earliest and latest years mentioned or implied in the content, and return them as a pair of years (year_start, year_end). 

    Here is a timeline of major events in the Ancient Sol universe to help you contextualize the article:

    1. 10,901 PN: Atlasian Republic is formed.
    2. 11,108 PN: Cyclopeans are the first humans to land on the moon.
    3. 11,125 PN: Atlasians establish the first human city on Mars, Atlas City.
    4. 11,302 PN: Cyclopeans begin terraforming Venus.
    5. 11,311 PN: Mars declares independence from Earth.
    6. 11,355 PN: Polygonals develop a new type of propulsion system.
    7. 11,440 PN - 11,450 PN: World War on Earth involving multiple civilizations.
    8. 11,497 PN: The Sun's recurring micronova strikes the Sol system.
    9. 11,507 PN: Kalen completes the Phobos Monolith with a message to future civilizations.

    Now, here is the article you need to analyze:
    
    <article>
    \n\n{text}\n\n
    </article>

    Follow these steps to determine the date range:

    1. Carefully read the entire article, paying special attention to any mentions of dates, years, or historical events.

    2. Identify all explicit mentions of years or dates in the article.

    3. Look for implicit references to time periods, such as:
    - Mentions of historical events with known dates
    - References to technological advancements or cultural phenomena associated with specific time periods
    - Descriptions of societal or political conditions characteristic of certain eras

    4. If exact years are mentioned:
    - Identify the earliest year mentioned (year_start)
    - Identify the latest year mentioned (year_end)

    5. If no exact years are mentioned, infer the most likely time period based on the context and content of the article.

    6. If the article seems to focus on a single year or a very short period:
    - Use that year for both year_start and year_end
    - Or use your judgment to expand slightly to cover the most likely period discussed

    7. If you cannot determine a specific date range:
    - Use your best judgment to estimate a plausible range based on the content
    - If even an estimate is impossible, use None for both values

    8. Format your response as a tuple: (year_start, year_end)

    Rules:
    - Both year_start and year_end should be years in the format YYYY (e.g., 2023)
    - year_start must be less than or equal to year_end
    - If you can't determine a start or end year, use None for that value
    - Do not include any explanation or additional text, just the tuple of two values

    Examples of valid responses:
    (1950, 1970)
    (2000, 2000)
    (1800, None)
    (None, 2022)
    (None, None)

    Analyze the article and provide the date range as a tuple of two values.

    {AI_PROMPT}
    """
    try:
        result = api_call(prompt, 100)
        # Parse the result, handling potential "None" values
        start_year, end_year = eval(result)
        return (start_year, end_year)
    except (anthropic.APIError, ValueError, SyntaxError) as e:
        print(f"Error generating date range: {str(e)}")
        raise e
