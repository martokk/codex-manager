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
        response = client.completions.create(
            model="claude-2",
            prompt=prompt,
            max_tokens_to_sample=max_tokens,
        )
    except anthropic.APIError as e:
        raise e
    return response.completion.strip()


def generate_summary(text: str) -> str:
    """Generates a summary of the inputted text."""
    prompt = f"{HUMAN_PROMPT} Please provide a detailed summary of the following text, capturing all key points and main ideas:\n\n{text}\n\n{AI_PROMPT} Here's a detailed summary of the text:"

    try:
        return api_call(prompt, 1000)
    except anthropic.APIError as e:
        print(f"Error generating summary: {str(e)}")
        raise e


def generate_brief(text: str) -> str:
    """Generates a very brief summary of the inputted text."""
    prompt = f"{HUMAN_PROMPT} Please provide a very brief summary (2-3 sentences) of the following text, capturing only the most essential information:\n\n{text}\n\n{AI_PROMPT} Here's a very brief summary of the text:"

    try:
        return api_call(prompt, 300)
    except anthropic.APIError as e:
        print(f"Error generating brief: {str(e)}")
        raise e


def generate_date_range(text: str) -> Tuple[Optional[int], Optional[int]]:
    """Generates start and end date range from the inputted text."""
    prompt = f"{HUMAN_PROMPT} Please analyze the following text and identify the earliest and latest years mentioned or implied in the content. Return the result as two numbers: the start year and the end year. If no specific years are mentioned, try to infer a reasonable range based on the context. If you can't determine a range, return 'None' for both values.\n\n{text}\n\n{AI_PROMPT} Based on the text, the year range is:"

    try:
        result = api_call(prompt, 100)
        start_year, end_year = map(
            lambda x: int(x) if x.lower() != "none" else None, result.split()
        )
        return (start_year, end_year)
    except (anthropic.APIError, ValueError) as e:
        print(f"Error generating date range: {str(e)}")
        raise e
