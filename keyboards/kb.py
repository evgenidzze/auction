from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

eng_btn = InlineKeyboardButton(text='🇬🇧 English', callback_data='eng')
ua_btn = InlineKeyboardButton(text='🇺🇦 Українська', callback_data='ua')
language_kb = InlineKeyboardMarkup(row_width=1).add(ua_btn, eng_btn)

my_auctions_btn = InlineKeyboardButton('🗃 Мої лоти', callback_data='my_auctions')
settings_btn = InlineKeyboardButton('⚙️ Налаштування', callback_data='settings')
help_btn = InlineKeyboardButton('🆘 Допомога', callback_data='help')
main_kb = InlineKeyboardMarkup(row_width=1).add(my_auctions_btn, settings_btn, help_btn)

create_auction = InlineKeyboardButton('🏷 Створити лот', callback_data='create_auction')
back_to_main_btn = InlineKeyboardButton('« Назад', callback_data='main_menu')

cancel_btn = InlineKeyboardButton(text='❌ Відміна', callback_data='main_menu')
cancel_kb = InlineKeyboardMarkup().add(cancel_btn)

tw_four_btn = InlineKeyboardButton(text='24 години', callback_data='24')
forty_eight_btn = InlineKeyboardButton(text='48 годин', callback_data='48')
lot_time_kb = InlineKeyboardMarkup(row_width=2).add(tw_four_btn, forty_eight_btn)

change_media_btn = InlineKeyboardButton(text='🎞 Змінити медіа', callback_data='change_media')
change_description_btn = InlineKeyboardButton(text='🔤 Змінити опис', callback_data='change_desc')
change_start_price_btn = InlineKeyboardButton(text='💰 Змінити стартову ціну', callback_data='change_start_price')
change_duration_btn = InlineKeyboardButton(text='⏳ Змінити тривалість лоту', callback_data='change_lot_time')
change_steps_btn = InlineKeyboardButton(text='🪙 Змінити кроки ставки', callback_data='change_price_steps')
publish_btn = InlineKeyboardButton(text='✅ Опублікувати', callback_data='publish_lot')
ready_to_publish_kb = InlineKeyboardMarkup().add(change_media_btn).add(change_description_btn).add(
    change_start_price_btn).add(change_duration_btn).add(change_steps_btn)

delete_lot_btn = InlineKeyboardButton(text='🗑 Видалити лот', callback_data='delete_lot')
delete_kb = InlineKeyboardMarkup().add(delete_lot_btn).add(
    InlineKeyboardButton(text='« Назад', callback_data='my_auctions'))
# bets_kb = InlineKeyboardMarkup(row_width=3).add(bet_500_btn, bet_1000_btn, bet_2000_btn)

back_to_ready_btn = InlineKeyboardButton(text='« Назад', callback_data='back_to_ready')
back_to_ready_kb = InlineKeyboardMarkup().add(back_to_ready_btn)

gbr_btn = InlineKeyboardButton(text='🇬🇧 GBR', callback_data='GBR')
uah_btn = InlineKeyboardButton(text='🇺🇦 UAH', callback_data='UAH')
usd_btn = InlineKeyboardButton(text='🇺🇸 USD', callback_data='USD')
currency_kb = InlineKeyboardMarkup(row_width=1).add(gbr_btn, uah_btn, usd_btn)

cancel_to_start_btn = InlineKeyboardButton(text='« Назад', callback_data='start')
cancel_to_start_kb = InlineKeyboardMarkup().add(cancel_to_start_btn)

decline_lot_btn = InlineKeyboardButton(text='❌ Відхилити')
accept_lot_btn = InlineKeyboardButton(text='✅ Підтвердити')

decline_lot_deletion_btn = InlineKeyboardButton(text='❌ Відхилити')
accept_lot_deletion_btn = InlineKeyboardButton(text='✅ Підтвердити')