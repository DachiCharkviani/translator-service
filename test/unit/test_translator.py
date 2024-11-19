from src.translator import get_translation, get_language_with_retry, query_llm
from mock import patch
import openai
import ipytest

#Mock tests
@patch.object(openai.ChatCompletion, 'create')
def test_unexpected_language(mocker):
  # we mock the model's response to return a random message
  mocker.return_value.choices[0].message.content = 123

  # assert the expected behavior
  result = query_llm("Hier ist dein erstes Beispiel.")
  print(result)
  assert result == (False, 'Language detection error: unexpected response format.')

@patch.object(openai.ChatCompletion, 'create')
def test_malformed_translation(mocker):
    # Mock the model's response to a translation request with a malformed translation output
    mocker.return_value.choices[0].message.content = None  # Simulate a None response

    # The function should return a translation error due to an unexpected format
    result = query_llm("Hier ist ein weiteres Beispiel.")
    print(result)
    assert result == (False, 'Language detection error: unexpected response format.')

@patch.object(openai.ChatCompletion, 'create')
def test_unintelligible_response(mocker):
    # Mock the LLM's response to detect an unintelligible post
    mocker.return_value.choices[0].message.content = "Unintelligible"

    # The function should handle this as unintelligible text
    result = query_llm("asdfgqwertyui")
    print(result)
    assert result == (False, "Unintelligible text.")

@patch.object(openai.ChatCompletion, 'create')
def test_empty_response(mocker):
    # Mock the model to return an empty string, simulating an incomplete response
    mocker.return_value.choices[0].message.content = ""

    # The function should return an appropriate error message for empty output
    result = query_llm("Voici un exemple vide.")
    print(result)
    assert result == (False, "Language detection error: unexpected response format.")

ipytest.run('-vv')

def test_llm_normal_response():
    #One sample test
    isEnglish, message = query_llm("Hier ist dein erstes Beispiel")
    print(message)
    assert query_llm("Hier ist dein erstes Beispiel.") == (False, 'Here is your first example.')
    #Already in English
    assert query_llm("This is an example in English.") == (True, "This is an example in English.")
    assert query_llm("How are you doing today?") == (True, "How are you doing today?")
    #Non English ones
    assert query_llm("C'est une belle journée.") == (False, "It's a beautiful day.")
    assert query_llm("¿Dónde está la biblioteca?") == (False, "Where is the library?")

def test_llm_gibberish_response():
    #Complete and utter gibberish testing
    assert query_llm("!!! ??!!") == (False, "Unintelligible text.")
    assert query_llm("¿sdfoijwoeirj sdf sdklfj") == (False, "Unintelligible text.")
    assert query_llm("lskdjf 234 jflsdf 09") == (False, "Unintelligible text.")