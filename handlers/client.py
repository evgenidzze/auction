import datetime
from copy import deepcopy
from typing import List
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, MediaGroupFilter
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.deep_linking import decode_payload
from aiogram_media_group import media_group_handler
from telegraph import Telegraph
from create_bot import bot, scheduler, i18n, _, storage_group
from db.db_manage import add_new_user, create_lot, get_lot, make_bid_sql, get_user_lots, delete_lot_sql, \
    get_user, update_user_sql, update_lot_sql, create_question, get_question, \
    create_answer, get_question_or_answer, get_answer, delete_answer, delete_question_db, User
from handlers.middleware import HiddenUser
from keyboards.kb import language_kb, main_kb, cancel_kb, lot_time_kb, \
    create_auction, back_to_main_btn, cancel_btn, delete_kb, back_to_ready_kb, back_to_ready_btn, currency_kb, \
    decline_lot_deletion_btn, accept_lot_deletion_btn, anti_kb, ready_to_publish_kb, publish_btn, quest_answ_kb, \
    back_to_messages, back_to_questions_kb, back_to_answers_kb, back_to_answers_btn, back_to_questions
from utils.utils import lot_ending, create_user_lots_kb, send_post, payment_approved, payment_kb_generate, \
    new_bid_caption, send_post_fsm, create_photo_album, create_question_kb, create_answers_kb, username_in_text, \
    phone_in_text

channel_id = '-1002061444176'
ADMINS = [397875584, 432530900]


# ADMINS = [397875584]


class FSMClient(StatesGroup):
    delete_answer = State()
    choose_answer = State()
    send_answer = State()
    choose_question = State()
    question = State()
    change_city = State()
    sniper_time = State()
    city = State()
    currency = State()
    change_price_steps = State()
    change_media = State()
    change_desc = State()
    change_start_price = State()
    change_lot_time = State()
    change_lot = State()
    price_steps = State()
    media = State()
    lot_time_living = State()
    price = State()
    language = State()
    description = State()


async def start(message: types.Message, state: FSMContext):
    if message.text == '/start':
        await FSMClient.language.set()
        text = _('<b>Оберіть мову / Choose a language:</b>')
        if isinstance(message, types.Message):
            await message.answer(text=text, parse_mode='html',
                                 reply_markup=language_kb)
        elif isinstance(message, types.CallbackQuery):
            await message.message.edit_text(text=text, parse_mode='html',
                                            reply_markup=language_kb)
    else:
        args = decode_payload(message.get_args())
        lot_id = args.split('_')[-1]
        owner_id = args.split('_')[-2]
        await state.update_data(lot_id_question=lot_id)
        await state.update_data(owner_id=owner_id)
        await FSMClient.question.set()
        await message.answer(text=_('Напишіть ваше запитання:'), reply_markup=cancel_kb)


async def lot_question(message: types.Message, state: FSMContext):
    name_in_text = await username_in_text(message.text, message.from_user.username)
    phone_num_in_text = await phone_in_text(text=message.text)
    if name_in_text or phone_num_in_text:
        await message.answer(text=_('Схоже ви намагались обмінятись контактними даними. Перефразуйте ваше запитання:'),
                             reply_markup=InlineKeyboardMarkup().add(back_to_answers_btn))
        return
    data = await state.get_data()
    lot_id = data.get('lot_id_question')
    lot = await get_lot(lot_id)
    owner_id = data.get('owner_id')
    await create_question(message.text, sender_id=message.from_user.id, lot_id=lot_id, owner_id=owner_id)
    await message.answer(text=_('✅ Власник лоту отримав ваше запитання!\n'
                                'Очікуйте на відповідь.'), reply_markup=main_kb)
    await bot.send_message(chat_id=owner_id,
                           text=_("💬 Ви отримали запитання по лоту <a href='{lot_link}'><b>{lot_desc}</b></a>").format(
                               lot_desc=lot.description[:25], lot_link=lot.lot_link),
                           parse_mode='html', reply_markup=main_kb, disable_web_page_preview=True)
    await state.reset_state(with_data=True)


async def main_menu(call, state: FSMContext):
    clean_text = "Вітаю, <b>{first_name}!</b><a href='https://telegra.ph/file/5f63d10b734d545a032cc.jpg'>⠀</a>\n"
    text = _(clean_text).format(first_name=call.from_user.username)
    if isinstance(call, types.CallbackQuery):
        if call.data in ('en', 'uk'):
            await add_new_user(telegram_id=call.from_user.id, language=call.data)
            text = _(clean_text, locale=call.data).format(first_name=call.from_user.username)
        await state.reset_state(with_data=True)
        await call.message.edit_text(text=text, parse_mode='html',
                                     reply_markup=main_kb)
    else:
        await call.answer(text=text, parse_mode='html', reply_markup=main_kb)
    await state.reset_state(with_data=True)


async def my_chats(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(with_data=True)
    await call.message.edit_text(text=_('👇 Оберіть варіант:'), reply_markup=quest_answ_kb)


async def question_list(call: types.CallbackQuery):
    await call.answer()
    question_texts_list = await get_question_or_answer(call.from_user.id, model_name='question')
    kb = await create_question_kb(question_texts_list, call.from_user.id)
    kb.add(back_to_messages)
    if question_texts_list:
        await FSMClient.choose_question.set()
        await call.message.edit_text(text=_('👇 Оберіть запитання щоб відповісти або видалити:'), reply_markup=kb)
    else:
        try:
            await call.message.edit_text(text=_('🤷🏻‍♂️ У вас немає повідомлень.'), reply_markup=quest_answ_kb)
        except:
            pass


async def answer_question(call: types.CallbackQuery, state: FSMContext):
    question_id = call.data
    await state.update_data(question_id=question_id)
    question = await get_question(question_id)
    await FSMClient.send_answer.set()
    await call.message.edit_text(
        text=_('👇 Надішліть відповідь або видаліть запитання:\n'
               '<b>{question_text}</b>').format(question_text=question.question),
        parse_mode='html', reply_markup=back_to_questions_kb)


async def delete_question(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'delete_question':
        data = await state.get_data()
        question_id = data.get('question_id')
        await delete_question_db(question_id)
        await call.message.edit_text(text=_("✅ Повідомлення видалено"))
    await answers_list(call)
    return


async def answers_list(call: types.CallbackQuery):
    await call.answer()
    answer_list = await get_question_or_answer(call.from_user.id, model_name='answer')
    kb = await create_answers_kb(answer_list, recipient_id=call.from_user.id)
    kb.add(back_to_messages)
    if answer_list:
        await FSMClient.choose_answer.set()
        if call.data in ('read', 'delete_question'):
            await call.message.answer(text=_('👇 Оберіть відповідь щоб прочитати:'), reply_markup=kb)
        else:
            await call.message.edit_text(text=_('👇 Оберіть відповідь щоб прочитати:'), reply_markup=kb)
    else:
        try:
            await call.message.edit_text(text=_('🤷🏻‍♂️ У вас немає повідомлень.'), reply_markup=quest_answ_kb)
        except:
            pass


async def choose_answer(call: types.CallbackQuery, state: FSMContext):
    answer_id = call.data
    await state.update_data(answer_id=answer_id)
    answer_record = await get_answer(answer_id)
    lot = await get_lot(answer_record.lot_id)
    await call.message.edit_text(
        text=_('📦 Лот: <a href="{lot_link}"><b>{lot_desc}</b></a>\n\n'
               'Відповідь: <i>{answer_text}</i>').format(answer_text=answer_record.answer,
                                                         lot_desc=lot.description[:25], lot_link=lot.lot_link),
        parse_mode='html', reply_markup=back_to_answers_kb, disable_web_page_preview=True)
    await FSMClient.delete_answer.set()


async def del_read_answer(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'read':
        data = await state.get_data()
        answer_id = data.get('answer_id')
        await delete_answer(answer_id)
        await call.message.edit_text(text=_("✅ Повідомлення видалено"))
    await answers_list(call)
    return


async def send_answer(message: types.Message, state: FSMContext):
    answer_text = message.text
    name_in_text = await username_in_text(answer_text, message.from_user.username)
    phone_num_in_text = await phone_in_text(text=answer_text)
    if name_in_text or phone_num_in_text:
        await message.answer(text=_('Схоже ви намагались обмінятись контактними даними. Перефразуйте вашу відповідь:'),
                             reply_markup=InlineKeyboardMarkup().add(back_to_questions))
        return
    data = await state.get_data()
    question_id = data.get('question_id')
    question = await get_question(question_id)
    lot = await get_lot(lot_id=question.lot_id)
    await create_answer(answer=answer_text, sender_id=message.from_user.id, lot_id=question.lot_id,
                        recipient_id=question.sender_id)
    await message.answer(text='Відповідь надіслано.', reply_markup=main_kb)
    await bot.send_message(chat_id=question.sender_id, text=_(
        "Автор лоту <a href='{lot_link}'><b>{lot_desc}</b></a> надіслав вам відповідь.").format(
        lot_desc=lot.description[:20], lot_link=lot.lot_link), parse_mode='html', reply_markup=quest_answ_kb,
                           disable_web_page_preview=True)
    await delete_question_db(question_id)


async def my_auctions(call: types.CallbackQuery):
    lots = await get_user_lots(call.from_user.id)
    kb = await create_user_lots_kb(lots)
    kb.add(create_auction, back_to_main_btn)
    await FSMClient.change_lot.set()
    await call.message.edit_text(text=_('Оберіть існуючий аукціон або створіть новий:'), parse_mode='html',
                                 reply_markup=kb)


async def ask_city(call: types.CallbackQuery):
    user = await get_user(call.from_user.id)
    if user.is_blocked:
        await bot.send_message(chat_id=call.from_user.id, text=_('Вас було заблоковано за порушення правил.'))
        return
    await FSMClient.city.set()
    await call.message.edit_text(text=_('🌆 Вкажіть ваше місто:'),
                                 parse_mode='html',
                                 reply_markup=cancel_kb)


async def ask_currency(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await FSMClient.currency.set()
    await message.answer(text=_('🫰🏼 Оберіть валюту:'),
                         parse_mode='html',
                         reply_markup=currency_kb)


async def ask_description(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(currency=call.data)
    await FSMClient.description.set()
    await call.message.edit_text(text=_('📝 Напишіть опис для лоту:\n\n'
                                        '<i>Наприклад: Навушники Marshall Major IV Bluetooth Black</i>'),
                                 parse_mode='html',
                                 reply_markup=cancel_kb)


async def ask_price(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await FSMClient.price.set()
    data = await state.get_data()
    currency = data.get('currency')
    await message.answer(text=_('💰 Вкажіть стартову ціну в {currency}:').format(currency=currency),
                         reply_markup=cancel_kb)


async def ask_price_steps(message: types.Message, state: FSMContext):
    if message.text.isdigit() or await state.get_state() == 'FSMClient:price_steps':
        if await state.get_state() != 'FSMClient:price_steps':
            await state.update_data(price=message.text)
        await FSMClient.price_steps.set()
        await message.answer(text=_('Напишіть крок ставки через пробіл (від 1 до 3 кроків):\n'
                                    'Наприклад: 500 1000 1500'), reply_markup=cancel_kb)
    else:
        await message.answer(text=_('❌ Потрібно ввести числове значення.'))
        await ask_price(message, state)


async def ask_lot_living(message: types.Message, state: FSMContext):
    if all(step.isdigit() for step in message.text.split(' ')):
        await state.update_data(price_steps=message.text)
        await FSMClient.lot_time_living.set()
        kb = deepcopy(lot_time_kb).add(cancel_btn)
        await message.answer(text=_('🕙 Скільки буде тривати аукціон?'), reply_markup=kb)
    else:
        await message.answer(text=_('❌ Потрібно ввести числові значення.'))
        await ask_price_steps(message, state)


async def ask_media(call: [types.CallbackQuery, types.Message], state: FSMContext):
    text = _('📸 Надішліть фото і відео:\n'
             '<i>До 5 фото та до 1 відео</i>')
    if isinstance(call, types.CallbackQuery):
        await state.update_data(lot_time_living=call.data)
        await call.message.edit_text(text=text, reply_markup=cancel_kb, parse_mode='html')
    else:
        await call.answer(text=text, reply_markup=cancel_kb, parse_mode='html')

    await FSMClient.media.set()


@media_group_handler(storage_driver=storage_group)
async def ready_lot(messages: List[types.Message], state: FSMContext):
    photos_id, videos_id = [], []
    html = ''
    print(messages)
    for message in messages:
        if message.content_type == 'photo':
            photos_id.append(message.photo[-1].file_id)
            html += f"<img src='{await message.photo[-1].get_url()}'/><br>"
            await state.update_data(photo_id=message.photo[0].file_id)
        elif message.content_type == 'video':
            videos_id.append(message.video.file_id)
            await state.update_data(video_id=message.video.file_id)
        else:
            await message.answer(text=_('❌ Надішліть фото або відео.'), parse_mode='html')
            await ask_media(message, state)
            return

    if html and len(photos_id) > 1:
        telegraph = Telegraph()
        telegraph.create_account(short_name='Shopogolic')
        photos_link = await create_photo_album(tg=telegraph, html=html)
        await state.update_data(photos_link=photos_link)

    if len(photos_id) > 5 or len(videos_id) > 1:
        await messages[0].answer(text=_('❌ Максимум 5 фото і 1 відео.\n'
                                        'Надішліть ще раз ваші медіафайли:'), reply_markup=cancel_kb)
    else:
        fsm_data = await state.get_data()
        kb = deepcopy(ready_to_publish_kb)
        kb.add(cancel_btn, publish_btn)
        if isinstance(messages[0], types.Message):
            msg = await send_post_fsm(fsm_data, messages[0].from_user.id)
            await msg.reply(text=_('⬆️ Лот готовий до публікації!\n'
                                   'Перевірте всю інформацію і натисніть <b>✅ Опублікувати</b>, коли будете готові.'),
                            reply_markup=kb, parse_mode='html')
        elif isinstance(messages, types.CallbackQuery):
            text = _('Лот готовий!\nОпублікувати?')

            if messages.data != 'back_to_ready' and await state.get_state() and 'steps' not in await state.get_state():
                await send_post_fsm(fsm_data, messages.from_user.id)
                await messages.message.reply_to_message.reply(text=text, reply_markup=kb)
            else:
                await messages.message.edit_text(text=text, reply_markup=kb)
    await state.reset_state(with_data=False)


async def lot_publish(message: types.CallbackQuery, state: FSMContext):
    fsm_data = await state.get_data()
    video_id = fsm_data.get('video_id')
    photo_id = fsm_data.get('photo_id')
    description = fsm_data.get('description')
    start_price = fsm_data.get('price')
    currency: str = fsm_data.get('currency')
    city: str = fsm_data.get('city')
    price_steps: str = fsm_data.get('price_steps')
    photos_link: str = fsm_data.get('photos_link')
    new_lot_id = await create_lot(fsm_data, message.from_user.id)
    channel = await bot.get_chat(channel_id)
    for admin_id in ADMINS:
        await send_post(message.from_user.id, admin_id, photo_id, video_id, description, start_price,
                        price_steps, currency=currency, city=city, lot_id=new_lot_id, moder_review=True,
                        photos_link=photos_link)
    await message.message.edit_text(
        text=_("✅ Лот відправлено не модерацію, незабаром він з'явиться у каналі <b><a href='{invite_link}'>"
               "{username}</a></b>.").format(invite_link=channel.invite_link, username=channel.username),
        parse_mode='html', reply_markup=main_kb)


async def make_bid(message: types.CallbackQuery):
    bid_data = message.data.split('_')
    lot_id = bid_data[2]
    lot = await get_lot(lot_id)
    if lot:
        last_bid = lot.last_bid
        owner_id = lot.owner_telegram_id
        last_bidder_id = lot.bidder_telegram_id
        bid_count = lot.bid_count
        user = await get_user(owner_id)
        currency = lot.currency
        anti_sniper_time: datetime.time = user.anti_sniper
        if str(message.from_user.id) == lot.owner_telegram_id and message.from_user.id != 397875584:
            await message.answer(text=_('❌ На свій лот не можна робити ставку.'))
            return
        job = scheduler.get_job(lot_id)
        if job:
            cur_time = datetime.datetime.now().replace(tzinfo=None)
            next_run_time = job.next_run_time.replace(tzinfo=None)
            left_job_time: datetime.timedelta = next_run_time - cur_time
            left_minutes = int(left_job_time.total_seconds() // 60)
            if left_minutes <= anti_sniper_time.minute:
                new_next_run_time = cur_time + datetime.timedelta(minutes=anti_sniper_time.minute)
                """continue auction (uncomment)"""
                scheduler.modify_job(lot_id, next_run_time=new_next_run_time)
            price = int(bid_data[1]) + last_bid
            await make_bid_sql(lot_id, price, bidder_id=message.from_user.id, bid_count=bid_count)
            lot_post = message.message
            caption = await new_bid_caption(lot_post, message.from_user.first_name, price, currency,
                                            owner_locale=user.language, bid_count=bid_count + 1,
                                            photos_link=lot.photos_link)
            await bot.edit_message_caption(chat_id=channel_id, message_id=lot_post.message_id, caption=caption,
                                           reply_markup=lot_post.reply_markup, parse_mode='html')
            await bot.send_message(chat_id=owner_id,
                                   text=_(
                                       "💸 Нова ставка на ваш лот!\n\n<a href='{lot_post}'><b>👉 Перейти до лоту.</b></a>").format(
                                       lot_post=lot_post.url),
                                   parse_mode='html',
                                   reply_markup=main_kb)
            if last_bidder_id:
                await bot.send_message(chat_id=last_bidder_id,
                                       text=_(
                                           "👋 Вашу ставку на лот <a href='{lot_post}'><b>{lot_name}</b></a> перебили.\n\n"
                                           "<a href='{lot_post}'><b>👉 Перейти до лоту.</b></a>").format(
                                           lot_post=lot_post.url, lot_name=lot.description), reply_markup=main_kb,
                                       parse_mode='html')
            await message.answer(text=_('✅ Ставку прийнято!'))
        else:
            await message.answer(text=_('Лот ще не опубліковано.'))
    else:
        await message.answer(text=_('❌ Аукціон закінчено'))


async def show_lot(message: types.CallbackQuery, state: FSMContext):
    lot_id = message.data
    await state.update_data(change_lot=lot_id)
    await state.reset_state(with_data=False)
    lot = await get_lot(lot_id)
    video_id = lot.video_id
    photo_id = lot.photo_id
    description = lot.description
    start_price = lot.start_price
    price_steps = lot.price_steps
    currency = lot.currency
    city = lot.city
    photos_link = lot.photos_link
    await send_post(message.from_user.id, message.from_user.id, photo_id, video_id, description, start_price,
                    price_steps, currency=currency, city=city, change_lot_view=True, photos_link=photos_link)
    await message.message.answer(text=_('Бажаєте видалити лот?'), reply_markup=delete_kb)


async def change_media(call: types.CallbackQuery, state: FSMContext):
    await FSMClient.change_media.set()
    await call.message.edit_text(text=_('📸 Надішліть фото і відео:\n'
                                        '<i>До 5 фото та до 1 відео</i>'), reply_markup=back_to_ready_kb,
                                 parse_mode='html')


async def change_desc(call: types.CallbackQuery, state: FSMContext):
    await FSMClient.change_desc.set()
    await call.message.edit_text(text=_('📝 Напишіть опис для лоту:\n\n'
                                        '<i>Наприклад: Навушники Marshall Major IV Bluetooth Black</i>'),
                                 parse_mode='html',
                                 reply_markup=back_to_ready_kb)


async def change_start_price(call: types.CallbackQuery, state: FSMContext):
    await FSMClient.change_start_price.set()
    fsm_data = await state.get_data()
    currency = fsm_data.get('currency')
    text = _('💰 Вкажіть стартову ціну в {currency}:').format(currency=currency)
    if isinstance(call, types.CallbackQuery):
        await call.message.edit_text(text=text, reply_markup=back_to_ready_kb)
    elif isinstance(call, types.Message):
        await call.answer(text=text, reply_markup=back_to_ready_kb)


async def change_lot_time(call: types.CallbackQuery):
    await FSMClient.change_lot_time.set()
    kb = deepcopy(lot_time_kb).add(back_to_ready_btn)
    await call.message.edit_text(text=_('🕙 Скільки буде тривати аукціон?'), reply_markup=kb)


async def change_price_steps(call: types.CallbackQuery):
    await FSMClient.change_price_steps.set()
    await call.message.edit_text(text=_('Напишіть крок ставки через пробіл (від 1 до 3 кроків):\n'
                                        'Наприклад: 500 1000 1500'), reply_markup=back_to_ready_kb)


async def change_city(call: types.CallbackQuery):
    await FSMClient.change_city.set()
    await call.message.edit_text(text=_('Надішліть нову назву міста:'), reply_markup=back_to_ready_kb)


async def set_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await ready_lot(message, state)


async def set_start_price(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(price=message.text)
        await ready_lot(message, state)
    else:
        await message.answer(text=_('❌ Потрібно ввести числове значення.'))
        await change_start_price(message, state)


async def set_lot_time(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(lot_time_living=call.data)
    await ready_lot(call, state)


async def set_price_steps(message: types.Message, state: FSMContext):
    await state.update_data(price_steps=message.text)
    if all(step.isdigit() for step in message.text.split(' ')):
        await state.update_data(price_steps=message.text)
        await ready_lot(message, state)
    else:
        await message.answer(text=_('❌ Потрібно ввести числові значення.'))
        await change_start_price(message, state)


async def set_new_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await ready_lot(message, state)


async def delete_lot(call: types.CallbackQuery, state: FSMContext):
    fsm_data = await state.get_data()
    lot_id = fsm_data.get('change_lot')
    lot = await get_lot(lot_id)
    accept_btn = deepcopy(accept_lot_deletion_btn)
    accept_btn.callback_data = f'lot_deletion_accept_{lot_id}'
    decline_btn = deepcopy(decline_lot_deletion_btn)
    decline_btn.callback_data = f'lot_deletion_decline_{lot_id}'
    kb = InlineKeyboardMarkup().add(decline_btn, accept_btn)
    if lot.lot_link:
        await call.message.edit_text(text=_('✅ Запит на видалення створено.'))
        for admin_id in ADMINS:
            await bot.send_message(chat_id=admin_id,
                                   text=_('<b>⚠️ Користувач {url} хоче видалити лот:\n</b>'
                                          '{lot_link}').format(url=call.from_user.url, lot_link=lot.lot_link),
                                   parse_mode='html', reply_markup=kb)
    else:
        await call.message.edit_text(_('✅ Лот видалено.'), reply_markup=main_kb)
        await delete_lot_sql(lot_id)


async def time_left_popup(call: types.CallbackQuery):
    data = call.data.split('_')
    lot_id = data[-1]
    job = scheduler.get_job(lot_id)
    if job:
        end_lot_time = job.next_run_time.replace(tzinfo=None)
        left_time: datetime.timedelta = end_lot_time - datetime.datetime.now().replace(tzinfo=None)
        hours, rem = divmod(left_time.seconds, 3600)
        minutes = divmod(rem, 60)[0]
        if left_time.days == 0:
            text = _('До завершення {hours}год, {minutes}хв').format(hours=hours, minutes=minutes)
        elif left_time.days == 1:
            text = _('До завершення {days} день, {hours}год, {minutes}хв').format(days=left_time.days, hours=hours,
                                                                                  minutes=minutes)
        else:
            text = _('До завершення {days} дні(-в), {hours}год, {minutes}хв').format(days=left_time.days, hours=hours,
                                                                                     minutes=minutes)
        await call.answer(text=text)
    else:
        await call.answer(text=_('Лот не опублікований.'))


async def accept_lot(call: types.CallbackQuery, state: FSMContext):
    accept = call.data.split('_')
    new_lot_id = accept[1]
    lot = await get_lot(new_lot_id)
    if lot:
        video_id = lot.video_id
        photo_id = lot.photo_id
        description = lot.description
        start_price = lot.start_price
        price_steps = lot.price_steps
        city = lot.city
        currency = lot.currency
        owner_id = lot.owner_telegram_id
        photos_link = lot.photos_link

        if not scheduler.get_job(new_lot_id):
            msg = await send_post(owner_id, channel_id, photo_id, video_id, description, start_price,
                                  price_steps, currency=currency, city=city, lot_id=new_lot_id, moder_review=None,
                                  photos_link=photos_link)
            await update_lot_sql(lot_id=new_lot_id, lot_link=msg.url, message_id=msg.message_id)
            scheduler.add_job(lot_ending, trigger='interval', id=new_lot_id, hours=lot.lot_time_living,
                              kwargs={'job_id': new_lot_id, 'msg_id': msg.message_id})
            # scheduler.add_job(lot_ending, trigger='interval', id=new_lot_id, seconds=20,
            #                   kwargs={'job_id': new_lot_id, 'msg_id': msg.message_id})
            channel = await bot.get_chat(chat_id=channel_id)
            await call.answer()
            text = _("✅ Готово!\n"
                     "Лот <b><a href='{msg_url}'>{desc}...</a></b> "
                     "опубліковано в каналі <b><a href='{channel_link}'>"
                     "{channel_name}</a></b>").format(msg_url=msg.url,
                                                      desc=description[:15],
                                                      channel_link=channel.invite_link,
                                                      channel_name=channel.username)
            await call.message.edit_caption(caption=text, parse_mode='html', reply_markup=main_kb)
            await bot.send_message(chat_id=owner_id, text=text, parse_mode='html', reply_markup=main_kb)
        else:
            await call.answer(text=_('Лот вже опубліковано.'))
    else:
        await call.answer(text=_('Лот вже відхилено.'))


async def decline_lot(call: types.CallbackQuery):
    await call.answer()
    decline = call.data.split('_')
    new_lot_id = decline[1]
    lot = await get_lot(new_lot_id)
    if lot:
        if scheduler.get_job(new_lot_id):
            await call.answer(text=_('Лот вже опубліковано.'))
        else:
            owner_id = lot.owner_telegram_id
            await delete_lot_sql(new_lot_id)
            await call.message.answer(text='✅ Лот успішно відхилено')
            await bot.send_message(chat_id=owner_id,
                                   text=_("❗️Нажаль ваш лот <b>{desc}...</b> не пройшов модерацію.").format(
                                       desc=lot.description[:15]),
                                   parse_mode='html', reply_markup=main_kb)
    else:
        await call.answer(text=_('Лот вже відхилено.'))


async def lot_deletion(call: types.CallbackQuery):
    data = call.data.split('_')
    action = data[2]
    lot_id = data[-1]
    lot = await get_lot(lot_id)
    text = None
    if lot:
        if action == 'accept':
            text = _('✅ Ваш лот <b>{desc}...</b> видалено').format(desc=lot.description[:15])
            await call.message.edit_text(_('✅ Лот видалено.'), reply_markup=main_kb)
            await delete_lot_sql(lot_id)
            scheduler.remove_job(lot_id)
            await bot.delete_message(chat_id=channel_id, message_id=lot.message_id)
        elif action == 'decline':
            text = _('❌ Ваш лот <b>{desc}...</b> не видалено.\n'
                     f'Запит відхилено.').format(desc=lot.description[:15])
            await call.message.edit_text(_('✅ Видалення відхилено.'), reply_markup=main_kb)
        if text:
            await bot.send_message(chat_id=lot.owner_telegram_id, text=text, parse_mode='html', reply_markup=main_kb)
    else:
        await call.answer(text=_('Запит вже оброблений.'))


async def anti_sniper(call: types.CallbackQuery):
    user = await get_user(call.from_user.id)
    await FSMClient.sniper_time.set()
    await call.message.edit_text(text=_('⏱ Ваш поточний час антиснайпингу - {minute}хв.\n'
                                        'Якщо хочете змінити - оберіть варіант нижче:').format(
        minute=user.anti_sniper.minute), reply_markup=anti_kb)


async def new_sniper_time(call: types.CallbackQuery, state: FSMContext):
    new_time = datetime.time(hour=0, minute=int(call.data), second=0)
    await update_user_sql(telegram_id=call.from_user.id, anti_sniper=new_time)
    await call.message.edit_text(text=_('✅ Час антиснайпингу змінено на {minute}хв').format(minute=new_time.minute),
                                 reply_markup=main_kb)
    await state.reset_state(with_data=False)


async def help_(call: types.CallbackQuery):
    await call.message.edit_text(text=_("По всім запитанням @Oleksandr_Polis\n\n"
                                        "<i>Що таке <a href='https://telegra.ph/Antisnajper-03-31'>"
                                        "<b>⏱ Антиснайпер?</b></a></i>\n"),
                                 reply_markup=InlineKeyboardMarkup().add(back_to_main_btn), parse_mode='html',
                                 disable_web_page_preview=True)


async def get_contact(call: types.CallbackQuery):
    bidder_id = call.data.split('_')[-2]
    lot_id = call.data.split('_')[-1]
    lot = await get_lot(lot_id)
    token = lot.paypal_token
    winner_tg = await bot.get_chat(bidder_id)
    owner: User = await get_user(call.from_user.id)

    await call.answer()
    if await payment_approved(token):
        await call.message.answer(text=_("<b>📦 Лот {desc}...</b>\n"
                                         "✅Оплата пройшла успішно!\n"
                                         "Можете зв'язатись з переможцем https://t.me/{username}.")
                                  .format(desc=lot.description[:15], username=winner_tg.username),
                                  reply_markup=main_kb)
        await delete_lot_sql(lot_id=lot.id)

    else:
        kb = await payment_kb_generate(bidder_id, token, lot_id, owner_locale=owner.language)
        await call.message.answer(text=_('<b>📦 Лот {desc}...</b>\n'
                                         '❌ Оплату не зафіксовано.\n'
                                         "Щоб зв'язатись з переможцем, оплатіть комісію і натисніть <b>Отримати контакт</b>.").format(
            desc=lot.description[:25]),
            reply_markup=kb, parse_mode='html')


def register_client_handlers(dp: Dispatcher):
    dp.middleware.setup(HiddenUser())
    dp.middleware.setup(i18n)
    dp.register_message_handler(start, commands=['start'], state='*')
    dp.register_callback_query_handler(start, Text(equals='start'), state='*')
    dp.register_callback_query_handler(main_menu, Text(equals='main_menu'), state='*')
    dp.register_message_handler(main_menu, commands=['main_menu'], state='*')
    dp.register_callback_query_handler(get_contact, Text(startswith='get_winner'), state='*')
    dp.register_callback_query_handler(main_menu, state=FSMClient.language)
    dp.register_callback_query_handler(my_auctions, Text(equals='my_auctions'), state='*')
    dp.register_callback_query_handler(my_chats, Text(equals='chats'), state='*')
    dp.register_callback_query_handler(question_list, Text(equals='questions'), state='*')
    dp.register_callback_query_handler(answer_question, state=FSMClient.choose_question)
    dp.register_callback_query_handler(choose_answer, state=FSMClient.choose_answer)
    dp.register_callback_query_handler(del_read_answer, state=FSMClient.delete_answer)
    dp.register_callback_query_handler(answers_list, Text(equals='answers'), state='*')
    dp.register_callback_query_handler(ask_city, Text(equals='create_auction'), state='*')
    dp.register_message_handler(ask_currency, state=FSMClient.city)
    dp.register_callback_query_handler(ask_description, state=FSMClient.currency)
    dp.register_message_handler(ask_price, state=FSMClient.description)
    dp.register_message_handler(ask_price_steps, state=FSMClient.price)
    dp.register_message_handler(ask_lot_living, state=FSMClient.price_steps)
    dp.register_callback_query_handler(ask_media, state=FSMClient.lot_time_living)
    dp.register_message_handler(ready_lot, MediaGroupFilter(is_media_group=False), state=FSMClient.media,
                                content_types=types.ContentType.all())
    dp.register_message_handler(ready_lot, MediaGroupFilter(is_media_group=True), state=FSMClient.media,
                                content_types=types.ContentType.all())
    dp.register_callback_query_handler(ready_lot, Text(equals='back_to_ready'), state='*')
    dp.register_callback_query_handler(lot_publish, Text(equals='publish_lot'))

    dp.register_callback_query_handler(make_bid, Text(startswith='bid'))
    dp.register_callback_query_handler(show_lot, state=FSMClient.change_lot)

    dp.register_callback_query_handler(change_media, Text(equals='change_media'))
    dp.register_callback_query_handler(change_desc, Text(equals='change_desc'))
    dp.register_callback_query_handler(change_start_price, Text(equals='change_start_price'))
    dp.register_callback_query_handler(change_lot_time, Text(equals='change_lot_time'))
    dp.register_callback_query_handler(change_price_steps, Text(equals='change_price_steps'))
    dp.register_callback_query_handler(change_city, Text(equals='change_city'))

    dp.register_message_handler(ready_lot, state=FSMClient.change_media, content_types=types.ContentType.all())
    dp.register_message_handler(set_desc, state=FSMClient.change_desc)
    dp.register_message_handler(set_start_price, state=FSMClient.change_start_price)
    dp.register_callback_query_handler(set_lot_time, state=FSMClient.change_lot_time)
    dp.register_message_handler(set_price_steps, state=FSMClient.change_price_steps)
    dp.register_message_handler(set_new_city, state=FSMClient.change_city)

    dp.register_callback_query_handler(delete_lot, Text(equals='delete_lot'))
    dp.register_callback_query_handler(time_left_popup, Text(startswith='time_left'))

    dp.register_callback_query_handler(lot_deletion, Text(startswith='lot_deletion_'), state='*')
    dp.register_callback_query_handler(accept_lot, Text(startswith='accept'), state='*')
    dp.register_callback_query_handler(decline_lot, Text(startswith='decline'), state='*')

    dp.register_callback_query_handler(help_, Text(equals='help'))

    dp.register_callback_query_handler(anti_sniper, Text(equals='anti_sniper'))
    dp.register_callback_query_handler(new_sniper_time, state=FSMClient.sniper_time)

    dp.register_message_handler(lot_question, state=FSMClient.question)
    dp.register_message_handler(send_answer, state=FSMClient.send_answer)

    dp.register_callback_query_handler(delete_question, Text(equals='delete_question'), state='*')
