import os
from glob import glob
from random import choice
from emoji import emojize

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove,\
    ReplyKeyboardMarkup, ParseMode, error
from telegram.ext import ConversationHandler
from telegram.ext import messagequeue as mq

import logging
from bot import subscribers
from db import db, get_or_create_user, get_user_emo, toggle_subscription, get_subscribers
from utils import get_keyboard, isconcepts

def greet_user(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    emo = get_user_emo(db, user)
    user_data['emo'] = emo
    text = 'Че нада, пля? {}'.format(emo)
    update.message.reply_text(text, reply_markup = get_keyboard())

def talk_to_me(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    emo = get_user_emo(db, user)
    user_text = "{}! Cам {}... {}".format(user['first_name'], update.message.text, emo)
    logging.info("User: %s, Chat ID: %s, Message: %s", user['username'],
                user['chat_id'], update.message.text)
    update.message.reply_text(user_text, reply_markup = get_keyboard())

def send_cat_picture(bot, update, user_data):
    cat_list = glob('images/cat*.jp*g')
    cat_pic = choice(cat_list)
    bot.send_photo(chat_id = update.message.chat_id, photo = open(cat_pic, 'rb'), reply_markup = get_keyboard())

def change_avatar(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    if 'emo' in user:
        del user['emo']
    emo = get_user_emo(db, user)
    update.message.reply_text('Готово: {}'.format(emo), reply_markup = get_keyboard())

def get_contact(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    print(update.message.contact)
    update.message.reply_text('Готово: {}'.format(get_user_emo(db, user)), reply_markup = get_keyboard())

def get_location(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    print(update.message.location)
    update.message.reply_text('Готово: {}'.format(get_user_emo(db, user)), reply_markup = get_keyboard())

def check_user_photo(bot, update, user_data):
    update.message.reply_text('Обрабатываю фото')
    os.makedirs('downloads', exist_ok=True)
    photo_file = bot.getFile(update.message.photo[-1].file_id)
    filename = os.path.join('downloads', '{}.jpg'.format(photo_file.file_id))
    photo_file.download(filename)
    image_has_cat = False
    concepts = isconcepts(filename, 1)
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

def anketa_start(bot, update, user_data):
    update.message.reply_text('Как вас зовут? Напишите имя и фамилию', reply_markup=ReplyKeyboardRemove())
    return "name"

def anketa_get_name(bot, update, user_data):
    user_name=update.message.text
    if len(user_name.split(" ")) != 2:
        update.message.reply_text("Пожалуйста введите имя И фамилию!")
        return "name"
    else:
        user_data['anketa_name'] = user_name
        reply_keyboard = [["1", "2", "3", "4", "5"]]
        update.message.reply_text(
            "Оцените нашего бота от 1 до 5", 
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return "rating"

def anketa_rating(bot, update, user_data):
    user_data['anketa_rating'] = update.message.text
    update.message.reply_text("""Напишите отзыв в свободной форме
или /skip чтобы пропустить этот шаг.""")
    return "comment"

def anketa_comment(bot, update, user_data):
    user_data['anketa_comment'] = update.message.text
    text = """
<b>Фамилия Имя:</b> {anketa_name}
<b>Оценка:</b> {anketa_rating}
<b>Комментарий:</b> {anketa_comment}""".format(**user_data)
    update.message.reply_text(text, reply_markup=get_keyboard(), parse_mode=ParseMode.HTML)
    return ConversationHandler.END

def anketa_skip_comment(bot, update, user_data):
    text = """
<b>Фамилия Имя:</b> {anketa_name}
<b>Оценка:</b> {anketa_rating}""".format(**user_data)
    update.message.reply_text(text, reply_markup=get_keyboard(), parse_mode=ParseMode.HTML)
    return ConversationHandler.END

def dontknow(bot, update, user_data):
    update.message.reply_text('Не понимаю')

def subscribe(bot, update):
    user = get_or_create_user(db, update.effective_user, update.message)
    if not user.get('subscribed'):
        toggle_subscription(db, user)
    update.message.reply_text('Вы подписались')

def unsubscribe(bot, update):
    user = get_or_create_user(db, update.effective_user, update.message)
    if user.get('subscribed'):
        toggle_subscription(db, user)
        update.message.reply_text('Вы отписались')
    else:
        update.message.reply_text('Вы и не подписывались.. Жмите /subscribe')

def show_inline(bot, update, user_data):
    inlinekbd = [[InlineKeyboardButton("Смешно", callback_data="1"),
                    InlineKeyboardButton("Не смешно", callback_data="0")]]
    kbd_markup = InlineKeyboardMarkup(inlinekbd)
    update.message.reply_text("Заходят в бар бесконечное число математиков",
        reply_markup=kbd_markup)

def inline_button_pressed(bot, update):
    query = update.callback_query
    try:
        user_choice = int(query.data)
        text = ":-)" if user_choice > 0 else ":-("
    except TypeError:
        text = "Что-то пошло не так"
    bot.edit_message_text(text=text, chat_id=query.message.chat.id, message_id=query.message.message_id)

@mq.queuedmessage
def send_updates(bot, job):
    for user in get_subscribers(db):
        try:
            bot.send_message(user['chat_id'], 'FUCK')
        except error.BadRequest:
            print('Chat {} not found'.format(user['chat_id']))
            toggle_subscription(db, user)

def set_alarm(bot, update, args, job_queue):
    try:
        seconds = abs(int(args[0]))
        job_queue.run_once(alarm, seconds, context=update.message.chat_id)
    except(IndexError, ValueError):
        update.message.reply_text('Введите количество секунд после /alarm')

@mq.queuedmessage
def alarm(bot, job):
    bot.send_message(job.context, 'Пип Пип Пип Пип, Будильник пищит!!!')