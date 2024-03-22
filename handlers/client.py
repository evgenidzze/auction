import datetime
from copy import deepcopy

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import InlineKeyboardMarkup
from apscheduler.jobstores.base import ConflictingIdError

from create_bot import bot, scheduler
from db_manage import add_new_user, create_lot, get_lot, make_bid_sql, get_user_lots, delete_lot_sql, \
    get_user, update_user_sql, update_lot_sql
from keyboards.kb import language_kb, main_kb, cancel_kb, lot_time_kb, \
    ready_to_publish_kb, create_auction, back_to_main_btn, cancel_btn, publish_btn, delete_kb, back_to_ready_kb, \
    back_to_ready_btn, currency_kb, cancel_to_start_kb, decline_lot_deletion_btn, accept_lot_deletion_btn
from utils import lot_ending, create_user_lots_kb, send_post, send_post_fsm

PAYMENT_TOKEN = '410694247:TEST:1e8bd1d0-8cc4-4941-ad13-962522d42b66'
channel_id = '-1002014559137'
ADMINS = [397875584, 432530900]


# class UserAccess(BaseMiddleware):
#     async def on_pre_process_update(self, update: types.Update, data: dict):
#         if 'message' in update:
#             user_id = update.message.from_user.id
#         elif 'callback_data' in:
#             user_id = update.callback_query.from_user.id
#         user = await get_user(user_id)
#         if user.is_blocked:
#             await bot.send_message(chat_id=user_id, text='Вас було заблоковано за порушення правил.')
#             raise CancelHandler()


class FSMClient(StatesGroup):
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


async def start(message: types.Message):
    await FSMClient.language.set()
    if isinstance(message, types.Message):
        await message.answer(text=f'<b>Оберіть мову / Choose a language:</b>', parse_mode='html',
                             reply_markup=language_kb)
    elif isinstance(message, types.CallbackQuery):
        await message.message.edit_text(text=f'<b>Оберіть мову / Choose a language:</b>', parse_mode='html',
                                        reply_markup=language_kb)


async def main_menu(call: types.CallbackQuery, state: FSMContext):
    if call.data in ('eng', 'ua'):
        await add_new_user(telegram_id=call.from_user.id, language=call.data)
    await state.reset_state(with_data=True)

    user = await get_user(call.from_user.id)
    print(user.city)
    if not user.currency:
        await FSMClient.currency.set()
        await call.message.edit_text(text='Оберіть валюту:', reply_markup=currency_kb)
        return

    try:
        await call.message.edit_text(text=f'Вітаю, <b>{call.from_user.first_name}</b>', parse_mode='html',
                                     reply_markup=main_kb)
    except:
        pass


async def set_currency(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(with_data=False)
    currency = call.data
    await update_user_sql(telegram_id=call.from_user.id, currency=currency)
    user = await get_user(call.from_user.id)

    if not user.city:
        await FSMClient.city.set()
        await call.message.edit_text(text=f'✅ Ви обрали {currency}.\n'
                                       f'В любий момент валюту можна змінити в <b>Налаштуваннях</b>.',
                                  parse_mode='html')
        await call.message.answer(text='🌆 Вкажіть ваше місто:', reply_markup=cancel_to_start_kb)
        return
    else:
        await call.message.answer(text=f'✅ Ви обрали {currency}.\n'
                                       f'В любий момент валюту можна змінити в <b>Налаштуваннях</b>.',
                                  parse_mode='html', reply_markup=main_kb)


async def set_city(message: types.Message, state: FSMContext):
    city = message.text.title()
    await update_user_sql(telegram_id=message.from_user.id, city=city)
    await message.answer(text=f'✅ Місто {city} збережено.\n'
                              f'В любий момент місто можна змінити в <b>Налаштуваннях</b>.',
                         parse_mode='html', reply_markup=main_kb)
    await state.reset_state(with_data=False)


async def my_auctions(call: types.CallbackQuery):
    lots = await get_user_lots(call.from_user.id)
    kb = await create_user_lots_kb(lots)
    kb.add(create_auction, back_to_main_btn)
    await FSMClient.change_lot.set()
    text = 'Оберіть існуючий аукціон або створіть новий:'
    await call.message.edit_text(text=text, parse_mode='html',
                                 reply_markup=kb)
    # if call.data == 'delete_lot':
    #     await call.message.edit_text(text=text, parse_mode='html',
    #                               reply_markup=kb)
    # else:
    #     await call.message.answer(text=text, parse_mode='html',
    #                                  reply_markup=kb)


async def ask_description(call: types.CallbackQuery):
    user = await get_user(call.from_user.id)
    if user.is_blocked:
        await bot.send_message(chat_id=call.from_user.id, text='Вас було заблоковано за порушення правил.')
        return
    await FSMClient.description.set()
    await call.message.edit_text(text='📝 Напишіть опис для лоту:\n\n'
                                      '<i>Наприклад: Навушники Marshall Major IV Bluetooth Black</i>',
                                 parse_mode='html',
                                 reply_markup=cancel_kb)


async def ask_price(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await FSMClient.price.set()
    user = await get_user(message.from_user.id)
    await message.answer(text=f'💰 Вкажіть стартову ціну в {user.currency}:', reply_markup=cancel_kb)


async def ask_price_steps(message: types.Message, state: FSMContext):
    if message.text.isdigit() or await state.get_state() == 'FSMClient:price_steps':
        if await state.get_state() != 'FSMClient:price_steps':
            await state.update_data(price=message.text)
        await FSMClient.price_steps.set()
        await message.answer(text='Напишіть крок ставки через пробіл (від 1 до 3 кроків):\n'
                                  'Наприклад: 500 1000 1500', reply_markup=cancel_kb)
    else:
        await message.answer(text='❌ Потрібно ввести числове значення.')
        await ask_price(message, state)


async def ask_lot_living(message: types.Message, state: FSMContext):
    if all(step.isdigit() for step in message.text.split(' ')):
        await state.update_data(price_steps=message.text)
        await FSMClient.lot_time_living.set()
        kb = deepcopy(lot_time_kb).add(cancel_btn)
        await message.answer(text='🕙 Скільки буде тривати аукціон?', reply_markup=kb)
    else:
        await message.answer(text='❌ Потрібно ввести числові значення.')
        await ask_price_steps(message, state)


async def ask_media(call: [types.CallbackQuery, types.Message], state: FSMContext):
    if isinstance(call, types.CallbackQuery):
        await state.update_data(lot_time_living=call.data)
        await call.message.edit_text(text='📸 Надішліть одне фото або відео:', reply_markup=cancel_kb)
    else:
        await call.answer(text='📸 Надішліть одне фото або відео:', reply_markup=cancel_kb)

    await FSMClient.media.set()


async def ready_lot(message: [types.Message, types.CallbackQuery], state: FSMContext):
    if isinstance(message, types.Message):
        if message.content_type == 'photo':
            await state.update_data(photo=message.photo[0].file_id)
        elif message.content_type == 'video':
            await state.update_data(video=message.video.file_id)
        elif await state.get_state() and 'change' not in await state.get_state():
            await message.answer(text='❌ Надішліть фото або відео.')
            await ask_media(message, state)
            return
    await state.reset_state(with_data=False)
    fsm_data = await state.get_data()
    kb = deepcopy(ready_to_publish_kb)
    kb.add(cancel_btn, publish_btn)
    if isinstance(message, types.Message):
        await send_post_fsm(fsm_data, message.from_user.id)
        await message.reply(text='Лот готовий!\n'
                                 'Опублікувати?', reply_markup=kb)
    elif isinstance(message, types.CallbackQuery):
        if message.data != 'back_to_ready' and await state.get_state() and 'steps' not in await state.get_state():
            await send_post_fsm(fsm_data, message.from_user.id)
            await message.message.reply_to_message.reply(text='Лот готовий!\n'
                                                              'Опублікувати?', reply_markup=kb)
        else:
            await message.message.edit_text(text='Лот готовий!\n'
                                                 'Опублікувати?', reply_markup=kb)


async def lot_publish(message: types.CallbackQuery, state: FSMContext):
    fsm_data = await state.get_data()
    video_id = fsm_data.get('video')
    photo_id = fsm_data.get('photo')
    description = fsm_data.get('description')
    start_price = fsm_data.get('price')
    price_steps: str = fsm_data.get('price_steps')
    new_lot_id = await create_lot(fsm_data, message.from_user.id)
    channel = await bot.get_chat(channel_id)
    for admin_id in ADMINS:
        await send_post(message.from_user.id, admin_id, video_id, photo_id, description, start_price,
                        price_steps, lot_id=new_lot_id, moder_review=True)

    await message.message.edit_text(
        text=f"✅ Лот відправлено не модерацію, незабаром він з'явиться у каналі <b><a href='{channel.invite_link}'>{channel.username}</a></b>.",
        parse_mode='html')
    #


async def make_bid(message: types.CallbackQuery):
    bid_data = message.data.split('_')
    lot_id = bid_data[2]
    lot = await get_lot(lot_id)
    if lot:
        last_bid = lot.last_bid
        owner_id = lot.owner_telegram_id
        user = await get_user(owner_id)
        currency = user.currency
        anti_sniper: datetime.time = user.anti_sniper
        if str(message.from_user.id) == lot.owner_telegram_id and message.from_user.id != 397875584:
            await message.answer(text='❌ На свій лот не можна робити ставку.')
            return
        job = scheduler.get_job(lot_id)
        cur_time = datetime.datetime.now().replace(tzinfo=None)
        next_run_time = job.next_run_time.replace(tzinfo=None)
        left_job_time: datetime.timedelta = next_run_time - cur_time
        left_minutes = int(left_job_time.total_seconds() // 60)
        if left_minutes <= anti_sniper.minute:
            next_run_time = job.next_run_time
            new_next_run_time = next_run_time + datetime.timedelta(minutes=anti_sniper.minute)
            # scheduler.modify_job(lot_id, next_run_time=new_next_run_time)
        price = int(bid_data[1]) + last_bid
        await make_bid_sql(lot_id, price, bidder_id=message.from_user.id)
        lot_post = message.message
        old_text = lot_post.caption.split('\n💰')
        first_part_caption = old_text[0] + f'    - {message.from_user.first_name} ставить {price}{currency}\n'
        caption = first_part_caption + '\n💰 ' + old_text[1].lstrip()
        await bot.edit_message_caption(chat_id=channel_id, message_id=lot_post.message_id, caption=caption,
                                       reply_markup=lot_post.reply_markup)
        await bot.send_message(chat_id=owner_id, text=f"💸 Нова ставка на ваш лот!\n\n{lot_post.url}", parse_mode='html')
        await message.answer(text='✅ Ставку прийнято!')
    else:
        await message.answer(text='❌ Аукціон закінчено')


async def edit_lot(message: types.CallbackQuery, state: FSMContext):
    lot_id = message.data
    await state.update_data(change_lot=lot_id)
    await state.reset_state(with_data=False)
    lot = await get_lot(lot_id)
    video_id = lot.video_id
    photo_id = lot.photo_id
    description = lot.description
    start_price = lot.start_price
    price_steps = lot.price_steps
    await send_post(message.from_user.id, message.from_user.id, video_id, photo_id, description, start_price,
                    price_steps)
    await message.message.answer(text='Бажаєте видалити лот?', reply_markup=delete_kb)


async def change_media(call: types.CallbackQuery, state: FSMContext):
    await FSMClient.change_media.set()
    await call.message.edit_text(text='📸 Надішліть одне фото або відео:', reply_markup=back_to_ready_kb)


async def change_desc(call: types.CallbackQuery, state: FSMContext):
    await FSMClient.change_desc.set()
    await call.message.edit_text(text='📝 Напишіть опис для лоту:\n\n'
                                      '<i>Наприклад: Навушники Marshall Major IV Bluetooth Black</i>',
                                 parse_mode='html',
                                 reply_markup=back_to_ready_kb)


async def change_start_price(call: types.CallbackQuery, state: FSMContext):
    await FSMClient.change_start_price.set()
    user = await get_user(call.from_user.id)
    if isinstance(call, types.CallbackQuery):
        await call.message.edit_text(text=f'💰 Вкажіть стартову ціну в {user.currency}:', reply_markup=back_to_ready_kb)
    elif isinstance(call, types.Message):
        await call.answer(text=f'💰 Вкажіть стартову ціну в {user.currency}:', reply_markup=back_to_ready_kb)


async def change_lot_time(call: types.CallbackQuery, state: FSMContext):
    await FSMClient.change_lot_time.set()
    kb = deepcopy(lot_time_kb).add(back_to_ready_btn)
    await call.message.edit_text(text='🕙 Скільки буде тривати аукціон?', reply_markup=kb)


async def change_price_steps(call: types.CallbackQuery, state: FSMContext):
    await FSMClient.change_price_steps.set()
    await call.message.edit_text(text='Напишіть крок ставки через пробіл (від 1 до 3 кроків):\n'
                                      'Наприклад: 500 1000 1500', reply_markup=back_to_ready_kb)


async def set_desc(message: types.Message, state: FSMContext):
    print(message.text)
    await state.update_data(description=message.text)
    await ready_lot(message, state)


async def set_start_price(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(price=message.text)
        await ready_lot(message, state)
    else:
        await message.answer(text='❌ Потрібно ввести числове значення.')
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
        await message.answer(text='❌ Потрібно ввести числові значення.')
        await change_start_price(message, state)


async def delete_lot(call: types.CallbackQuery, state: FSMContext):
    fsm_data = await state.get_data()
    lot_id = fsm_data.get('change_lot')
    lot = await get_lot(lot_id)
    accept_btn = deepcopy(accept_lot_deletion_btn)
    accept_btn.callback_data = f'lot_deletion_accept_{lot_id}'
    decline_btn = deepcopy(decline_lot_deletion_btn)
    decline_btn.callback_data = f'lot_deletion_decline_{lot_id}'
    kb = InlineKeyboardMarkup().add(decline_btn, accept_btn)
    for admin_id in ADMINS:
        await call.message.edit_text(text='✅ Запит на видалення створено.')
        await bot.send_message(chat_id=admin_id, text=f'<b>⚠️ Користувач {call.from_user.url} хоче видалити лот:\n</b>'
                                                      f'{lot.lot_link}', parse_mode='html', reply_markup=kb)


async def time_left_popup(call: types.CallbackQuery):
    data = call.data.split('_')
    lot_id = data[-1]
    # lot = await get_lot(lot_id)
    job = scheduler.get_job(lot_id)
    if job:
        end_lot_time = job.next_run_time.replace(tzinfo=None)
        left_time: datetime.timedelta = end_lot_time - datetime.datetime.now().replace(tzinfo=None)
        hours, rem = divmod(left_time.seconds, 3600)
        minutes = divmod(rem, 60)[0]
        if left_time.days == 0:
            text = f'До завершення {hours}год, {minutes}хв'
        elif left_time.days == 1:
            text = f'До завершення {left_time.days} день, {hours}год, {minutes}хв'
        else:
            text = f'До завершення {left_time.days} дні(-в), {hours}год, {minutes}хв'
        await call.answer(text=text)


async def accept_lot(call: types.CallbackQuery):
    accept = call.data.split('_')
    new_lot_id = accept[1]
    lot = await get_lot(new_lot_id)
    if lot:
        video_id = lot.video_id
        photo_id = lot.photo_id
        description = lot.description
        start_price = lot.start_price
        price_steps = lot.price_steps
        owner_id = lot.owner_telegram_id

        if not scheduler.get_job(new_lot_id):
            msg = await send_post(call.from_user.id, channel_id, video_id, photo_id, description, start_price,
                                  price_steps,
                                  new_lot_id)
            await update_lot_sql(lot_id=new_lot_id, lot_link=msg.url, message_id=msg.message_id)
            # scheduler.add_job(lot_ending, trigger='interval', id=new_lot_id, hours=lot.lot_time_living,
            #                   kwargs={'job_id': new_lot_id, 'msg_id': msg.message_id})
            scheduler.add_job(lot_ending, trigger='interval', id=new_lot_id, seconds=60,
                              kwargs={'job_id': new_lot_id, 'msg_id': msg.message_id})
            channel = await bot.get_chat(chat_id=channel_id)
            await call.answer()
            await call.message.edit_caption(caption=f"✅ Готово!\n"
                                                    f"Лот <b><a href='{msg.url}'>{description[:15]}...</a></b> опубліковано в каналі <b><a href='{channel.invite_link}'>{channel.username}</a></b>",
                                            parse_mode='html', reply_markup=main_kb)
            await bot.send_message(chat_id=owner_id, text=f"✅ Готово!\n"
                                                          f"Лот <b><a href='{msg.url}'>{description[:15]}</a></b> опубліковано в каналі <b><a href='{channel.invite_link}'>{channel.username}</a></b>",
                                   parse_mode='html', reply_markup=main_kb)
        else:
            await call.answer(text='Лот вже опубліковано.')
    else:
        await call.answer(text='Лот вже відхилено.')


async def decline_lot(call: types.CallbackQuery):
    decline = call.data.split('_')
    new_lot_id = decline[1]
    lot = await get_lot(new_lot_id)
    if lot:
        if scheduler.get_job(new_lot_id):
            await call.answer(text='Лот вже опубліковано.')
        else:
            owner_id = lot.owner_telegram_id
            await delete_lot_sql(new_lot_id)
            await bot.send_message(chat_id=owner_id,
                                   text=f"❗️Нажаль ваш лот <b>{lot.description[:15]}...</b> не пройшов модерацію.\n",
                                   parse_mode='html', reply_markup=main_kb)
    else:
        await call.answer(text='Лот вже відхилено.')


async def lot_deletion(call: types.CallbackQuery):
    data = call.data.split('_')
    action = data[2]
    lot_id = data[-1]
    lot = await get_lot(lot_id)
    text = None
    if lot:
        if action == 'accept':
            text = f'✅ Ваш лот <b>{lot.description[:15]}...</b> видалено'
            await call.message.edit_text('✅ Лот видалено.')
            await delete_lot_sql(lot_id)
            scheduler.remove_job(lot_id)
            await bot.delete_message(chat_id=channel_id, message_id=lot.message_id)
        elif action == 'decline':
            text = f'❌ Ваш лот <b>{lot.description[:15]}...</b> не видалено.\n'
            f'Запит відхилено.'
            await call.message.edit_text('✅ Видалення відхилено.')
        if text:
            await bot.send_message(chat_id=lot.owner_telegram_id, text=text, parse_mode='html', reply_markup=main_kb)
    else:
        await call.answer(text='Запит вже оброблений.')


async def settings(message: types.Message, state: FSMContext):
    pass


async def help_(message: types.Message, state: FSMContext):
    pass


async def success(message: types.Message):
    bidder_id = message.successful_payment.invoice_payload
    bidder = await bot.get_chat(chat_id=bidder_id)
    await message.answer(text='✅ Оплата успішна.\n'
                              f"Можете зв'язатись з переможцем: {bidder.user_url}")


async def pre_checkout_query_handler(query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, True)


def register_client_handlers(dp: Dispatcher):
    # dp.setup_middleware(UserAccess())
    dp.register_message_handler(start, commands=['start'], state='*')
    dp.register_callback_query_handler(start, Text(equals='start'), state='*')
    dp.register_callback_query_handler(main_menu, Text(equals='main_menu'), state='*')
    dp.register_message_handler(success, content_types=types.ContentType.SUCCESSFUL_PAYMENT)
    dp.register_pre_checkout_query_handler(pre_checkout_query_handler)
    dp.register_callback_query_handler(main_menu, state=FSMClient.language)
    dp.register_callback_query_handler(my_auctions, Text(equals='my_auctions'))
    dp.register_callback_query_handler(ask_description, Text(equals='create_auction'), state='*')
    dp.register_message_handler(ask_price, state=FSMClient.description)
    dp.register_message_handler(ask_price_steps, state=FSMClient.price)
    dp.register_message_handler(ask_lot_living, state=FSMClient.price_steps)
    dp.register_callback_query_handler(ask_media, state=FSMClient.lot_time_living)
    dp.register_message_handler(ready_lot, state=FSMClient.media, content_types=types.ContentType.all())
    dp.register_callback_query_handler(ready_lot, Text(equals='back_to_ready'), state='*')
    dp.register_callback_query_handler(lot_publish, Text(equals='publish_lot'))

    dp.register_callback_query_handler(make_bid, Text(startswith='bid'))
    dp.register_callback_query_handler(edit_lot, state=FSMClient.change_lot)

    dp.register_callback_query_handler(change_media, Text(equals='change_media'))
    dp.register_callback_query_handler(change_desc, Text(equals='change_desc'))
    dp.register_callback_query_handler(change_start_price, Text(equals='change_start_price'))
    dp.register_callback_query_handler(change_lot_time, Text(equals='change_lot_time'))
    dp.register_callback_query_handler(change_price_steps, Text(equals='change_price_steps'))

    dp.register_message_handler(ready_lot, state=FSMClient.change_media, content_types=types.ContentType.all())
    dp.register_message_handler(set_desc, state=FSMClient.change_desc)
    dp.register_message_handler(set_start_price, state=FSMClient.change_start_price)
    dp.register_callback_query_handler(set_lot_time, state=FSMClient.change_lot_time)
    dp.register_message_handler(set_price_steps, state=FSMClient.change_price_steps)

    dp.register_callback_query_handler(delete_lot, Text(equals='delete_lot'))
    dp.register_callback_query_handler(time_left_popup, Text(startswith='time_left'))

    dp.register_callback_query_handler(set_currency, state=FSMClient.currency)
    dp.register_message_handler(set_city, state=FSMClient.city)
    dp.register_callback_query_handler(lot_deletion, Text(startswith='lot_deletion_'), state='*')
    dp.register_callback_query_handler(accept_lot, Text(startswith='accept'), state='*')
    dp.register_callback_query_handler(decline_lot, Text(startswith='decline'), state='*')

    dp.register_callback_query_handler(settings, Text(equals='settings'))
    dp.register_callback_query_handler(help_, Text(equals='help'))
