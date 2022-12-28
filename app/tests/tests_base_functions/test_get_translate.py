from unittest.mock import patch, call

import pytest
from pydantic import ValidationError

from app.base_functions.translator import get_translate, translate_client
from app.scheme.transdata import ISO639_1, TranslateRequest
# used to load the environment variables required for the function get_translate
from app.settings import settings  # noqa !!!


@pytest.mark.parametrize(
    ("translate_request", "mock_translate_return_value", "right_answer"),
    (
        (
            TranslateRequest(
                native_lang=ISO639_1.English, foreign_lang=ISO639_1.Ukrainian, line="makes"
            ),
            {
                "translatedText": "робить",
                "detectedSourceLanguage": "en",
                "input": "makes",
            },
            "робить",
        ),
        (
            TranslateRequest(
                native_lang=ISO639_1.Russian,
                foreign_lang=ISO639_1.Ukrainian,
                line="унылая пора",
            ),
            {
                "translatedText": "похмура пора",
                "detectedSourceLanguage": "ru",
                "input": "унылая пора",
            },
            "похмура пора",
        ),
        (
            TranslateRequest(
                native_lang=ISO639_1.English,
                foreign_lang=ISO639_1.Ukrainian,
                line="    assemble  ",
            ),
            {
                "translatedText": "зібрати",
                "detectedSourceLanguage": "en",
                "input": "assemble",
            },
            "зібрати",
        ),
    ),
)
def test_get_translate(translate_request, mock_translate_return_value, right_answer):

    with patch.object(
        translate_client, "translate", return_value=mock_translate_return_value
    ) as mock_translate:
        assert get_translate(input_=translate_request).translated_text == right_answer
    calls = [call(translate_request.line, target_language=translate_request.native_lang),
             call(translate_request.line, target_language=translate_request.foreign_lang)]
    mock_translate.assert_has_calls(calls)


def test_validate_in_data():
    with pytest.raises(ValidationError) as exc_info:
        TranslateRequest(
            native_lang=ISO639_1.English, foreign_lang=ISO639_1.English, line="    assemble  "
        )
    assert exc_info.value.errors() == [
        {
            "loc": ("foreign_lang",),
            "msg": "foreign_lang must not be equal to native_lang",
            "type": "value_error",
        }
    ]


def test_matching_indicated_and_recognized_lang():
    translate_request = TranslateRequest(
        native_lang=ISO639_1.Haitian, foreign_lang=ISO639_1.Ukrainian, line="    assemble  "
    )
    mock_translate_return_value = {
        "translatedText": "зібрати",
        "detectedSourceLanguage": "en",
        "input": "assemble",
    }

    with patch.object(
        translate_client, "translate", return_value=mock_translate_return_value
    ) as mock_translate:
        with pytest.raises(ValueError) as exc_info:
            get_translate(input_=translate_request)
        assert "Your word is" in str(exc_info.value)

    mock_translate.assert_called_once_with(
        translate_request.line,  target_language=translate_request.native_lang
    )
