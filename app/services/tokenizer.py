from transformers import GPT2Tokenizer


def count_tokens(text, model_name="gpt2"):
    # Load the tokenizer for the specified model
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)

    # Tokenize the text
    tokens = tokenizer.encode(text)

    # Return the number of tokens
    return len(tokens)
