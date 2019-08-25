from emoji import emojize
from random import choice
from clarifai.rest import ClarifaiApp
from telegram import ReplyKeyboardMarkup, KeyboardButton

import settings

def get_user_emo(user_data):
    if 'emo' in user_data:
        return user_data['emo']
    else:
        user_data['emo'] = emojize(choice(settings.USER_EMOJI), use_aliases=True)
        return user_data['emo']

def get_keyboard():
    contact_button = KeyboardButton('Прислать контакты', request_contact=True)
    location_button = KeyboardButton('Прислать координаты', request_location=True)
    my_keyboard = ReplyKeyboardMarkup([
                                        ['Прислать кошака', 'Сменить аватарку'],
                                        [contact_button, location_button],
                                        ['Заполнить анкету']
                                        ], resize_keyboard=True)
    return my_keyboard

def isconcepts(file_name):
    app = ClarifaiApp(api_key=settings.CLARIFY_KEY)
    model = app.public_models.general_model
    response = model.predict_by_filename(file_name, max_concepts=1)
    if response['status']['code'] == 10000:
        return response['outputs'][0]['data']['concepts']
    else:
        print('Статус не ОК')



if __name__ == "__main__":
    print(isconcepts('images/cat-1.jpg'))
    print(isconcepts('images/notcat.jpg'))