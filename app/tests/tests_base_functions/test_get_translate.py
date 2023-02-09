from unittest.mock import call, patch

import pytest
from pydantic import ValidationError

from app.base_functions.translator import get_translate, translate_client
from app.scheme.transdata import TranslateRequest

# used to load the environment variables required for the function get_translate
from app.settings import settings  # noqa !!!


@pytest.mark.parametrize(
    ("translate_request", "mock_translate_return_value", "right_answer"),
    (
        (
            TranslateRequest(
                native_lang="en",
                foreign_lang="uk",
                line="makes",
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
                native_lang="ru",
                foreign_lang="uk",
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
                native_lang="en",
                foreign_lang="uk",
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
def test_get_translate(
    translate_request: TranslateRequest,
    mock_translate_return_value: dict,
    right_answer: str,
) -> None:

    with patch.object(
        translate_client, "translate", return_value=mock_translate_return_value
    ) as mock_translate:
        assert get_translate(input_=translate_request).translated_text == right_answer
    calls = [
        call(
            translate_request.line,
            target_language=translate_request.native_lang,
            source_language=translate_request.foreign_lang,
        ),
        call(
            translate_request.line,
            target_language=translate_request.foreign_lang,
            source_language=translate_request.native_lang,
        ),
    ]
    mock_translate.assert_has_calls(calls)


def test_validate_in_data() -> None:
    with pytest.raises(ValidationError) as exc_info:
        TranslateRequest(
            native_lang="en",
            foreign_lang="en",
            line="    assemble  ",
        )
    assert exc_info.value.errors() == [
        {
            "loc": ("foreign_lang",),
            "msg": "foreign_lang must not be equal to native_lang",
            "type": "value_error",
        }
    ]


def test_matching_indicated_and_recognized_lang() -> None:
    translate_request = TranslateRequest(
        native_lang="ht",
        foreign_lang="uk",
        line="    assemble  ",
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
        assert "it means" in str(exc_info.value)

    calls = [
        call(
            "assemble",
            target_language=translate_request.native_lang,
            source_language=translate_request.foreign_lang,
        ),
        call(
            "assemble",
            target_language=translate_request.foreign_lang,
            source_language=translate_request.native_lang,
        ),
        call(
            "assemble",
            target_language=translate_request.native_lang,
            source_language=mock_translate_return_value["detectedSourceLanguage"],
        ),
        call("assemble", target_language=translate_request.native_lang),
    ]
    mock_translate.assert_has_calls(calls)
