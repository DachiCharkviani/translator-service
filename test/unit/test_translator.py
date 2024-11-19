from src.translator import get_translation, get_language_with_retry, query_llm

# def test_chinese():
#     is_english, translated_content = get_translation("这是一条中文消息")
#     assert is_english == False
#     assert translated_content == "This is a Chinese message"

def test_llm_normal_response():
    # assert get_translation("Hier ist dein erstes Beispiel.") == 'Here is your first example.'
    # assert get_language_with_retry("Hier ist dein erstes Beispiel.") == "German"
    assert query_llm("Hier ist dein erstes Beispiel") == (False, 'Here is your first example.')

def test_llm_gibberish_response():
    pass