from typing import List


async def get_list_of_words(telegram_user_id: int) -> List[dict]:
    list_temp = [{'foreign_word': 'boy', 'native_word': 'хлопець', 'learning_status': 0, 'card_id': '111'},
                 {'foreign_word': 'car', 'native_word': 'авто', 'learning_status': 0, 'card_id': '112'},
                 {'foreign_word': 'cat', 'native_word': 'кіт', 'learning_status': 0, 'card_id': '113'},
                 {'foreign_word': 'bandage', 'native_word': 'бандаж', 'learning_status': 1, 'card_id': '114'},
                 {'foreign_word': 'as', 'native_word': 'як', 'learning_status': 2, 'card_id': '115'},
                 ]
    return list_temp
