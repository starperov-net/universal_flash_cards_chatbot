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
    result: dict = translate_client.translate(input_.line, target_language=input_.native_lang)
    translated_text_language: str = input_.native_lang
    if result["detectedSourceLanguage"] not in [input_.native_lang, input_.foreign_lang]:
        raise ValueError(f"Your word is {result['detectedSourceLanguage']},"
                         f"translated as {result['translatedText']}")

    if result["detectedSourceLanguage"] == input_.native_lang:
        result: dict = translate_client.translate(input_.line, target_language=input_.foreign_lang)  # type: ignore
        translated_text_language: str = input_.foreign_lang  # type: ignore

    return TranslateResponse(
        input_text=input_.line,
        translated_text=result["translatedText"],
        input_text_language=result["detectedSourceLanguage"],
        translated_text_language=translated_text_language
    )
