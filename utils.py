import datetime
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from create_bot import bot, scheduler
from db_manage import get_lot, get_user, delete_lot_sql
from keyboards.kb import decline_lot_btn, accept_lot_btn, main_kb


async def lot_ending(job_id, msg_id: types.Message):
    lot = await get_lot(job_id)
    scheduler.remove_job(job_id)
    if lot:
        owner_telegram_id = lot.owner_telegram_id
        bidder_telegram_id = lot.bidder_telegram_id
        if bidder_telegram_id:
            await bot.send_message(chat_id=bidder_telegram_id,
                                   text=f'🏆 Вітаю! Ви перемогли у аукціоні <b>{lot.description[:25]}</b>\n'
                                        f'Очікуйте повідомлення від продавця.',
                                   parse_mode='html')
            from handlers.client import PAYMENT_TOKEN
            await bot.send_invoice(owner_telegram_id, 'Buy', "Щоб зв'язатись з переможцем, оплатіть комісію.", bidder_telegram_id, PAYMENT_TOKEN, 'UAH',
                                   [types.LabeledPrice('Price Label', 5 * 100)])
        else:
            await bot.send_message(chat_id=owner_telegram_id,
                             text=f'Ваш лот <b>{lot.description[:15]}...</b> завершився без ставок.', parse_mode='html',
                             reply_markup=main_kb)

        """close auction"""
        from handlers.client import channel_id
        await bot.delete_message(chat_id=channel_id, message_id=msg_id)
        await delete_lot_sql(lot_id=lot.id)
    else:
        scheduler.remove_job(job_id)


async def create_price_step_kb(price_steps, new_lot_id, currency):
    kb = InlineKeyboardMarkup()
    for price in price_steps.split(' ')[:3]:
        btn = InlineKeyboardButton(text=f'+{price} {currency}', callback_data=f'bid_{price}_{new_lot_id}')
        kb.insert(btn)
    return kb


async def create_user_lots_kb(lots):
    kb = InlineKeyboardMarkup(row_width=1)
    for lot in lots:
        lot = lot[0]
        kb.add(InlineKeyboardButton(text=f'{lot.description}', callback_data=f'{lot.id}'))
    return kb


async def send_post(user_id, send_to_id, video_id, photo_id, description, start_price, price_steps, lot_id=None,
                    moder_review=None):
    user = await get_user(user_id=user_id)
    user_city = user.city
    anti_sniper: datetime.time = user.anti_sniper
    kb = await create_price_step_kb(price_steps, lot_id, user.currency)
    if lot_id and moder_review:
        decline_lot_btn.callback_data = f'decline_{lot_id}'
        accept_lot_btn.callback_data = f'accept_{lot_id}'
        kb.add(decline_lot_btn, accept_lot_btn)
    elif not moder_review:
        kb.add(InlineKeyboardButton(text='⏳', callback_data=f'time_left_{lot_id}'))
    caption = f"<b>{description}</b>\n\n" \
              f"🏙 <b>Місто:</b> {user_city}\n\n" \
              f"👇 <b>Ставки учасників:</b>\n\n" \
              f"💰 <b>Стартова ціна:</b> {start_price} {user.currency}\n" \
              f"⏱ <b>Антиснайпер</b> {anti_sniper.strftime('%M')} хв.\n"
    msg = None
    if photo_id:
        msg = await bot.send_photo(chat_id=send_to_id, photo=photo_id, caption=caption, parse_mode='html',
                                   reply_markup=kb)
    if video_id:
        msg = await bot.send_video(chat_id=send_to_id, photo=video_id, caption=caption, parse_mode='html',
                                   reply_markup=kb)
    if msg:
        return msg


async def send_post_fsm(fsm_data, user_id):
    video_id = fsm_data.get('video')
    photo_id = fsm_data.get('photo')
    description = fsm_data.get('description')
    start_price = fsm_data.get('price')
    price_steps: str = fsm_data.get('price_steps')
    await send_post(user_id, user_id, video_id, photo_id, description, start_price,
                    price_steps)
