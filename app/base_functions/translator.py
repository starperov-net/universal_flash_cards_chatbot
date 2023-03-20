from google.cloud import translate_v2 as translate  # type: ignore

from app.scheme.transdata import TranslateRequest, TranslateResponse

# noqa !!!used to load the environment variables required for the function get_translateimporta
from app.settings import settings  # noqa !!!

translate_client = translate.Client()


def get_translate(
    input_: TranslateRequest, translate_client: translate.Client = translate_client
) -> TranslateResponse:
    """Translates a word or phrase.

    - clears spaces before and after
    - The specified input and input languages cannot be the same
    - if the recognized language does not match the specified input - an exception is thrown
    for the function to work correctly, it is necessary to set the GOOGLE_APPLICATION_CREDENTIALS
    environment variable containing the path to the file with credentials
    (the file must be available at this path)
    """

    results = translate_client.get_languages()
    print('full list', len(results))
    for language in results:
        print(u"{name} ({language})".format(**language))

    print('list for target language = uk', len(results))
    results = translate_client.get_languages(target_language='uk')

    for language in results:
        print(u"{name} ({language})".format(**language))

    # translated_text_language: str = input_.native_lang
    input_detected_language: dict = translate_client.detect_language(input_.line)
    print('----------detected language-', input_detected_language)
    # attempt to translate from foreign language to native language
    result: dict = translate_client.translate(
        input_.line,
        target_language=input_.native_lang,
        source_language=input_.foreign_lang,
    )

    # if attempt was access and detected language of input word is equal foreign language this user
    # we need check and fix (if necessary) input text (User could make a mistake)
    if (
        result["translatedText"] != result["input"]
        and input_detected_language["language"] == input_.foreign_lang
    ):
        return fixed_TranslateResponse(input_text=input_.line,
                                                       translated_text=result["translatedText"],
                                                       input_text_language=input_.foreign_lang,
                                                       translated_text_language=input_.native_lang,)

    # attempt to translate from native language to foreign language
    result: dict = translate_client.translate(  # type: ignore
        input_.line,
        target_language=input_.foreign_lang,
        source_language=input_.native_lang,
    )

    # catch a case when input_text same as in other language
    # in this case get_language method  can return other language, not native language
    # for prevent this, we try to translate from native language to detected language
    # if we get a same text we understand that translation was correct
    # we need 'if' because translate method don't allow target_language has been same source_language
    if input_.native_lang != input_detected_language["language"]:
        similar_language_request: dict = translate_client.translate(
            input_.line,
            target_language=input_.native_lang,
            source_language=input_detected_language["language"],
        )
        is_similar_language: bool = (
            similar_language_request["input"]
            == similar_language_request["translatedText"]
        )
    else:
        is_similar_language: bool = True  # type: ignore

    if result["translatedText"] != result["input"] and (
        input_detected_language["language"] == input_.native_lang or is_similar_language
    ):
        return fixed_TranslateResponse(
            input_text=input_.line,
            translated_text=result["translatedText"],
            input_text_language=input_.native_lang,
            translated_text_language=input_.foreign_lang,
        )

    result: dict = translate_client.translate(input_.line, target_language=input_.native_lang)  # type: ignore

    # select from google-translate available languages full name for input_language
    input_text_language: str = [
        el["name"]
        for el in translate_client.get_languages()
        if el["language"] == result["detectedSourceLanguage"]
    ][0]

    raise ValueError(
        f"In {input_text_language}, " f"it means {result['translatedText']}"
    )

def fixed_TranslateResponse(input_text: str,
                                                       translated_text: str,
                                                       input_text_language: str,
                                                       translated_text_language: str) -> TranslateResponse:
    returned_translate: dict = translate_client.translate(translated_text, target_language=input_text_language)
    print('-------------', input_text, returned_translate["translatedText"])

    return TranslateResponse(
    input_text=returned_translate["translatedText"],
    translated_text=translated_text,
    input_text_language=input_text_language,
    translated_text_language=translated_text_language,
    )
