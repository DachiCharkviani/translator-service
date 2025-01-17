import openai
import time
import os

# Set up OpenAI API credentials and endpoint
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_BASE")
openai.api_type = "azure"
openai.api_version = "2024-08-01-preview"

deployment_name = "gpt-4-davit"

response = openai.ChatCompletion.create(
    engine=deployment_name,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello!"}
    ]
)

def get_translation(post: str, retries: int = 10, delay: int = 20) -> str:
    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                engine="gpt-4-davit",
                messages=[
                    {"role": "system", "content": '''You are a helpful assistant who translates text to English. If the text is already in English just give back as it is.
                                                  The languages might be given in their dialects but still just translate the language correctly to plain English.
                                                  If the language of the text is unidentifiable or nonsense, respond with 'Unintelligible text.
                                                  Examples of unintelligable text are: 123124, !@#!$#@12313, asdasfagasf, hashmmmwioq, lesgrttttgnasklo, .;.;//;'p[lq,], etc.'''},
                    {"role": "user", "content": post}
                ]
            )
            translation = response.choices[0].message.content.strip()
            # Return "Unintelligible text" if indicated by response
            if translation.lower() == "unintelligible text":
                return "Unintelligible text"
            return translation
        except openai.error.RateLimitError:
            if attempt < retries - 1:
                print(f"Rate limit exceeded, retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
            else:
                print("Translation failed due to rate limit.")
                return None
        except Exception as e:
            return (None, f"Error during translation: {e}", e)

# TODO: Implement Basic LLM integration
def get_language_with_retry(post: str, max_retries: int = 10, initial_delay: int = 20) -> str:
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                engine="gpt-4-davit",
                messages=[
                    {"role": "system", "content": '''You are a helpful assistant. Respond only with the name of the language that the given text is written in.
                                                  Heads up, the languages might be given in their dialects but still just give the name of the language no specification of which dialect it is is needed.
                                                  if it's identifiable. If the text is of unidentifiable language, i.e complete nonsense, respond with 'Unintelligible text.
                                                  Examples of unintelligable text are: 123124, !@#!$#@12313, asdasfagasf, hashmmmwioq, lesgrttttgnasklo, .;.;//;'p[lq,], etc.'''},
                    {"role": "user", "content": post}
                ]
            )
            detected_language = response.choices[0].message.content.strip()
            # Return "Unintelligible text" if indicated by response
            if detected_language.lower() == "unintelligible text":
                return "Unintelligible text"
            return detected_language.split()[0]
        except openai.error.RateLimitError:
            if attempt < max_retries - 1:
                print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print("Failed due to repeated rate limit errors.")
                return None
        except Exception as e:
            return (None, f"Unexpected error during language detection: {e}", e)

def query_llm(post: str) -> tuple[bool, str]:
    """Determines if the post is in English and translates non-English posts to English with robust error handling."""
    try:
        # Attempt to detect the language
        detected_language = get_language_with_retry(post)

        # Check if detected_language is a valid string
        if not isinstance(detected_language, str):
            return False, "Language detection error: unexpected response format."

        # Handle English posts directly
        if detected_language.lower() == "english":
            return True, post

        # Handle unintelligible or unknown languages gracefully
        if detected_language.lower() in ["unintelligible", "unknown"]:
            return False, "Unintelligible text."

        # Attempt translation for non-English posts
        translation = get_translation(post)

        # Check if translation response is valid
        if not isinstance(translation, str):
            return False, "Translation error: unexpected response format."

        return False, translation

    except AttributeError as e:
        # Handle specific cases where the response format is missing or malformed
        print(f"Unexpected error during language detection: {e}")
        return False, "Unexpected error: response format issue."

    except IndexError as e:
        # Handle cases where list indexing fails (e.g., missing choices or message content)
        print(f"Unexpected error during language detection: {e}")
        return False, "Unexpected error: response format issue."

    except Exception as e:
        # Capture any other unexpected error and handle gracefully
        print(f"Unexpected error: {e}")
        return False, "Unexpected error occurred in language detection or translation."
