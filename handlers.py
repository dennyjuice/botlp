import os
from glob import glob
from random import choice
from emoji import emojize

import logging
from utils import get_keyboard, get_user_emo, isconcepts

def greet_user(bot, update, user_data):
    emo = get_user_emo(user_data)
    user_data['emo'] = emo
    text = 'Че нада, пля? {}'.format(emo)
    update.message.reply_text(text, reply_markup = get_keyboard())

def talk_to_me(bot, update, user_data):
    emo = get_user_emo(user_data)
    user_text = "{}! Cам {}... {}".format(update.message.chat.first_name, update.message.text, emo)
    logging.info("User: %s, Chat ID: %s, Message: %s", update.message.chat.username,
                update.message.chat.id, update.message.text)
    update.message.reply_text(user_text, reply_markup = get_keyboard())

def send_cat_picture(bot, update, user_data):
    cat_list = glob('images/cat*.jp*g')
    cat_pic = choice(cat_list)
    bot.send_photo(chat_id = update.message.chat_id, photo = open(cat_pic, 'rb'), reply_markup = get_keyboard())

def change_avatar(bot, update, user_data):
    if 'emo' in user_data:
        del user_data['emo']
    emo = get_user_emo(user_data)
    update.message.reply_text('Готово: {}'.format(emo), reply_markup = get_keyboard())

def get_contact(bot, update, user_data):
    print(update.message.contact)
    update.message.reply_text('Готово: {}'.format(get_user_emo(user_data)), reply_markup = get_keyboard())

def get_location(bot, update, user_data):
    print(update.message.location)
    update.message.reply_text('Готово: {}'.format(get_user_emo(user_data)), reply_markup = get_keyboard())

def check_user_photo(bot, update, user_data):
    update.message.reply_text('Обрабатываю фото')
    os.makedirs('downloads', exist_ok=True)
    photo_file = bot.getFile(update.message.photo[-1].file_id)
    filename = os.path.join('downloads', '{}.jpg'.format(photo_file.file_id))
    photo_file.download(filename)
    image_has_cat = False
    concepts = isconcepts(filename)
    for concept in concepts:
        if (concept['name'] == 'кошка' or concept['name'] == 'котенок'):
            image_has_cat = True
    if image_has_cat:
        update.message.reply_text(emojize('О, кошак! Скопирую себе... Спасиб :smiley_cat:', use_aliases=True), reply_markup = get_keyboard())
        new_filename = os.path.join('images', 'cat_{}.jpg'.format(photo_file.file_id))
        os.rename(filename, new_filename)
    else:
        mess = ' '.join('%s' % (concept['name']) for concept in concepts)
        update.message.reply_text('Походу это {}'.format(mess))
        update.message.reply_text('Ну норм, че...', reply_markup = get_keyboard())
        os.remove(filename)