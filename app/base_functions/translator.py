from google.cloud import translate_v2 as translate  # type: ignore

from app.scheme.transdata import TranslateRequest, TranslateResponse  # type: ignore
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
    # translated_text_language: str = input_.native_lang
    input_detected_language: dict = translate_client.detect_language(input_.line)

    # attempt to translate from foreign language to native language
    result: dict = translate_client.translate(input_.line, target_language=input_.native_lang,
                                              source_language=input_.foreign_lang)

    if result['translatedText'] != result['input'] and input_detected_language['language'] == input_.foreign_lang.value:
        return TranslateResponse(
            input_text=input_.line,
            translated_text=result["translatedText"],
            input_text_language=input_.foreign_lang,
            translated_text_language=input_.native_lang
        )

    # attempt to translate from native language to foreign language
    result: dict = translate_client.translate(input_.line, target_language=input_.foreign_lang,  # type: ignore
                                              source_language=input_.native_lang)

    # catch a case when input_text same as in other language
    # in this case get_language method  can return other language, not native language
    # for prevent this, we try to translate from native language to detected language
    # if we get a same text we understand that translation was correct
    # we need 'if' because translate method don't allow target_language has been same source_language
    if input_.native_lang != input_detected_language['language']:
        similar_language_request: dict = translate_client.translate(input_.line, target_language=input_.native_lang,
                                                                    source_language=input_detected_language['language'])
        is_similar_language: bool = similar_language_request['input'] == similar_language_request['translatedText']
    else:
        is_similar_language: bool = True  # type: ignore

    if result['translatedText'] != result['input'] and (
            input_detected_language['language'] == input_.native_lang.value or is_similar_language):
        return TranslateResponse(
            input_text=input_.line,
            translated_text=result["translatedText"],
            input_text_language=input_.native_lang,
            translated_text_language=input_.foreign_lang
        )

    result: dict = translate_client.translate(input_.line, target_language=input_.native_lang)  # type: ignore

    # select from google-translate available languages full name for input_language
    input_text_language: str = \
        [el['name'] for el in translate_client.get_languages() if el['language'] == result['detectedSourceLanguage']][0]

    raise ValueError(f"In {input_text_language}, "
                     f"it means {result['translatedText']}")
