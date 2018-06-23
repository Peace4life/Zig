
# coding: utf-8

# In[ ]:


# -*- coding: utf-8 -*-
import telebot
import config
import pb
import datetime
import pytz
import json
import traceback

P_TIMEZONE = pytz.timezone(config.TIMEZONE)
TIMEZONE_COMMON_NAME = config.TIMEZONE_COMMON_NAME
@bot.message_handler(commands=['start'])
def start_command(message):
   bot.send_message(
       message.chat.id,
       'Greetings! I can show you PrivatBank exchange rates.\n' +
       'To get the exchange rates press /exchange.\n' +
       'To get help press /help.'
   )

@bot.message_handler(commands=['help'])
def help_command(message):
   keyboard = telebot.types.InlineKeyboardMarkup()
   keyboard.add(
       telebot.types.InlineKeyboardButton(
           ‘Message the developer’, url='telegram.me/baba404'
       )
   )
   bot.send_message(
       message.chat.id,
       '1) To receive a list of available currencies press /exchange.\n' +
       '2) Click on the currency you are interested in.\n' +
       '3) You will receive a message containing information regarding the source and the target currencies, ' +
       'buying rates and selling rates.\n' +
       '4) Click “Update” to receive the current information regarding the request. ' +
       'The bot will also show the difference between the previous and the current exchange rates.\n' +
       '5) The bot supports inline. Type @<botusername> in any chat and the first letters of a currency.',
       reply_markup=keyboard
   )
@bot.message_handler(commands=['exchange'])
def exchange_command(message):<br>  keyboard = telebot.types.InlineKeyboardMarkup()
  keyboard.row(
      telebot.types.InlineKeyboardButton('USD', callback_data='get-USD')
  )
  keyboard.row(
    telebot.types.InlineKeyboardButton('EUR', callback_data='get-EUR'),
    telebot.types.InlineKeyboardButton('RUR', callback_data='get-RUR')
  )

  bot.send_message(message.chat.id, ‘Click on the currency of choice:', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
   data = query.data
   if data.startswith('get-'):
       get_ex_callback(query)
def get_ex_callback(query):
   bot.answer_callback_query(query.id)
   send_exchange_result(query.message, query.data[4:])
def send_exchange_result(message, ex_code):
   bot.send_chat_action(message.chat.id, 'typing')
   ex = pb.get_exchange(ex_code)
   bot.send_message(
       message.chat.id, serialize_ex(ex),
       reply_markup=get_update_keyboard(ex),
       parse_mode='HTML'
   )
def serialize_ex(ex_json, diff=None):
   result = '<b>' + ex_json['base_ccy'] + ' -> ' + ex_json['ccy'] + ':</b>\n\n' +             'Buy: ' + ex_json['buy']
   if diff:
       result += ' ' + serialize_exchange_diff(diff['buy_diff']) + '\n' +                  'Sell: ' + ex_json['sale'] +                  ' ' + serialize_exchange_diff(diff['sale_diff']) + '\n'
   else:
       result += '\nSell: ' + ex_json['sale'] + '\n'
   return result

def serialize_exchange_diff(diff):
   result = ''
   if diff > 0:
       result = '(' + str(diff) + ' <img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="" src="https://s.w.org/images/core/emoji/72x72/2197.png">" src="https://s.w.org/images/core/emoji/72x72/2197.png">)'
   elif diff < 0:
       result = '(' + str(diff)[1:] + ' <img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="" src="https://s.w.org/images/core/emoji/72x72/2198.png">" src="https://s.w.org/images/core/emoji/72x72/2198.png">)'
   return result
@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
   data = query.data
   if data.startswith('get-'):
       get_ex_callback(query)
   else:
       try:
           if json.loads(data)['t'] == 'u':
               edit_message_callback(query)
       except ValueError:
           pass

def edit_message_callback(query):
   data = json.loads(query.data)['e']
   exchange_now = pb.get_exchange(data['c'])
   text = serialize_ex(
       exchange_now,
       get_exchange_diff(
           get_ex_from_iq_data(data),
           exchange_now
       )
   ) + '\n' + get_edited_signature()
   if query.message:
       bot.edit_message_text(
           text,
           query.message.chat.id,
           query.message.message_id,
           reply_markup=get_update_keyboard(exchange_now),
           parse_mode='HTML'
       )
   elif query.inline_message_id:
       bot.edit_message_text(
           text,
           inline_message_id=query.inline_message_id,
           reply_markup=get_update_keyboard(exchange_now),
           parse_mode='HTML'
       )
def get_exchange_diff(last, now):
   return {
       'sale_diff': float("%.6f" % (float(now['sale']) - float(last['sale']))),
       'buy_diff': float("%.6f" % (float(now['buy']) - float(last['buy'])))
   }


