from clarifai.rest import ClarifaiApp
from telegram import ReplyKeyboardMarkup, KeyboardButton

import settings

def get_keyboard():
    contact_button = KeyboardButton('Прислать контакты', request_contact=True)
    location_button = KeyboardButton('Прислать координаты', request_location=True)
    my_keyboard = ReplyKeyboardMarkup([
                                        ['Прислать кошака', 'Сменить аватарку'],
                                        [contact_button, location_button],
                                        ['Заполнить анкету', 'Прислать шутку']
                                        ], resize_keyboard=True)
    return my_keyboard

def isconcepts(file_name, max_concepts):
    app = ClarifaiApp(api_key=settings.CLARIFY_KEY)
    model = app.public_models.general_model
    response = model.predict_by_filename(file_name, max_concepts=max_concepts)
    if response['status']['code'] == 10000:
        return response['outputs'][0]['data']['concepts']
    else:
        print('Статус не ОК')



if __name__ == "__main__":
    print(isconcepts('images/cat-1.jpg', 1))
    print(isconcepts('images/notcat.jpg', 1))