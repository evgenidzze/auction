from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from create_bot import _

eng_btn = InlineKeyboardButton(text=_('🇬🇧 English'), callback_data='en')
ua_btn = InlineKeyboardButton(text=_('🇺🇦 Українська'), callback_data='uk')
language_kb = InlineKeyboardMarkup(row_width=1).add(ua_btn, eng_btn)

my_auctions_btn = InlineKeyboardButton(_('🗃 Мої лоти      ⠀⠀⠀⠀⠀⠀⠀'), callback_data='my_auctions')
my_ads_btn = InlineKeyboardButton(_('📋 Мої оголошення   ⠀⠀⠀'), callback_data='my_ads')
# settings_btn = InlineKeyboardButton('⚙️ Налаштування', callback_data='settings')
help_btn = InlineKeyboardButton(_('🆘 Допомога ⠀   ⠀⠀⠀⠀⠀⠀'), callback_data='help')
create_auction_btn = InlineKeyboardButton(_('🏷 Створити лот     ⠀⠀⠀⠀'), callback_data='create_auction')
anti_sniper_btn = InlineKeyboardButton(_('⏱ Антиснайпер      ⠀⠀⠀⠀'), callback_data='anti_sniper')
chats_btn = InlineKeyboardButton(_('💬 Повідомлення'), callback_data='chats')
create_advert_btn = InlineKeyboardButton(_('📣 Створити оголошення'), callback_data='create_ad')
main_kb = InlineKeyboardMarkup(row_width=1).add(create_auction_btn, create_advert_btn, my_auctions_btn, my_ads_btn, anti_sniper_btn, chats_btn,
                                                help_btn)

back_to_main_btn = InlineKeyboardButton(_('« Назад'), callback_data='main_menu')
back_to_messages = InlineKeyboardButton(_('« Назад'), callback_data='chats')

cancel_btn = InlineKeyboardButton(text=_('❌ Відміна'), callback_data='main_menu')
cancel_kb = InlineKeyboardMarkup().add(cancel_btn)

tw_four_btn = InlineKeyboardButton(text=_('24 години'), callback_data='24')
forty_eight_btn = InlineKeyboardButton(text=_('48 годин'), callback_data='48')
seven_days = InlineKeyboardButton(text=_('7 днів'), callback_data='168')
lot_time_kb = InlineKeyboardMarkup(row_width=2).add(tw_four_btn, forty_eight_btn, seven_days)

change_media_btn = InlineKeyboardButton(text=_('🎞 Змінити медіа ⠀⠀⠀⠀⠀⠀'), callback_data='change_media')
change_description_btn = InlineKeyboardButton(text=_('🔤 Змінити опис ⠀  ⠀⠀⠀⠀⠀'), callback_data='change_desc')
change_start_price_btn = InlineKeyboardButton(text=_('💰 Змінити стартову ціну ⠀'), callback_data='change_start_price')
change_duration_btn = InlineKeyboardButton(text=_('⏳ Змінити тривалість лоту'), callback_data='change_lot_time')
change_steps_btn = InlineKeyboardButton(text=_('🪙 Змінити кроки ставки  ⠀'), callback_data='change_price_steps')
change_city_btn = InlineKeyboardButton(text=_('🏙 Змінити місто                ⠀'), callback_data='change_city')
publish_btn = InlineKeyboardButton(text=_('✅ Опублікувати'), callback_data='publish_lot')
publish_adv_btn = InlineKeyboardButton(text=_('✅ Опублікувати'), callback_data='publish_adv')
ready_to_publish_kb = InlineKeyboardMarkup().add(change_media_btn).add(change_description_btn).add(
    change_start_price_btn).add(change_duration_btn).add(change_steps_btn).add(change_city_btn)
ready_to_publish_ad_kb = InlineKeyboardMarkup().add(change_media_btn).add(change_description_btn).add(change_city_btn)

delete_lot_btn = InlineKeyboardButton(text=_('🗑 Видалити лот'), callback_data='delete_lot')
delete_lot_kb = InlineKeyboardMarkup().add(delete_lot_btn).add(
    InlineKeyboardButton(text=_('« Назад'), callback_data='my_auctions'))

delete_ad_btn = InlineKeyboardButton(text=_('🗑 Видалити оголошення'), callback_data='delete_ad')
delete_ad_kb = InlineKeyboardMarkup().add(delete_ad_btn).add(
    InlineKeyboardButton(text=_('« Назад'), callback_data='my_ads'))

back_to_ready_btn = InlineKeyboardButton(text=_('« Назад'), callback_data='back_to_ready')
back_to_ready_kb = InlineKeyboardMarkup().add(back_to_ready_btn)

back_to_ready_ad_btn = InlineKeyboardButton(text=_('« Назад'), callback_data='back_to_ready_ad')
back_to_ready_ad_kb = InlineKeyboardMarkup().add(back_to_ready_ad_btn)


gbr_btn = InlineKeyboardButton(text='🇬🇧 GBR', callback_data='GBR')
uah_btn = InlineKeyboardButton(text='🇺🇦 UAH', callback_data='UAH')
usd_btn = InlineKeyboardButton(text='🇺🇸 USD', callback_data='USD')
currency_kb = InlineKeyboardMarkup(row_width=1).add(gbr_btn, uah_btn, usd_btn, cancel_btn)

cancel_to_start_btn = InlineKeyboardButton(text='« Назад', callback_data='start')
cancel_to_start_kb = InlineKeyboardMarkup().add(cancel_to_start_btn)

decline_lot_btn = InlineKeyboardButton(text=_('❌ Відхилити'))
accept_lot_btn = InlineKeyboardButton(text=_('✅ Підтвердити'))

decline_lot_deletion_btn = InlineKeyboardButton(text='❌ Відхилити')
accept_lot_deletion_btn = InlineKeyboardButton(text='✅ Підтвердити')

anti_5_btn = InlineKeyboardButton(text=_('5хв'), callback_data='5')
anti_10_btn = InlineKeyboardButton(text=_('10хв'), callback_data='10')
anti_15_btn = InlineKeyboardButton(text=_('15хв'), callback_data='15')
anti_kb = InlineKeyboardMarkup().add(anti_5_btn, anti_10_btn, anti_15_btn).add(back_to_main_btn)

quest_answ_kb = InlineKeyboardMarkup(row_width=2)
questions_btn = InlineKeyboardButton(_('❔ Запитання'), callback_data='questions')
answers_btn = InlineKeyboardButton(_('💬 Відповіді'), callback_data='answers')
quest_answ_kb.add(answers_btn, questions_btn, back_to_main_btn)

delete_answer_btn = InlineKeyboardButton(text=_('🗑 Видалити'), callback_data='read')
back_to_answers_btn = InlineKeyboardButton(text=_('« Назад'), callback_data='answers')
back_to_answers_kb = InlineKeyboardMarkup().add(delete_answer_btn).add(back_to_answers_btn)

back_to_questions = InlineKeyboardButton(text=_('« Назад'), callback_data='questions')
delete_question_btn = InlineKeyboardButton(text='🗑 Видалити', callback_data='delete_question')
back_to_questions_kb = InlineKeyboardMarkup().add(delete_question_btn).add(back_to_questions)

black_list_btn = InlineKeyboardButton(text='🚫 Чорний список', callback_data='deny_user_access')
payment_on_btn = InlineKeyboardButton(text='Увімкнути оплату', callback_data='on_payment')
payment_of_btn = InlineKeyboardButton(text='Вимкнути оплату', callback_data='off_payment')
back_to_admin = InlineKeyboardButton(text='❌Відміна', callback_data='admin')

subscribe_adv_kb = InlineKeyboardMarkup()
adv_7_days = InlineKeyboardButton(text=_('Оформити на 7 днів'), callback_data='604800')
subscribe_adv_kb.add(adv_7_days).add(cancel_btn)

