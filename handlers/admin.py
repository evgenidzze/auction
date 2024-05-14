from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from create_bot import job_stores
from db.db_manage import get_user, update_user_sql
from handlers.client import ADMINS
from keyboards.kb import cancel_kb, payment_on_btn, payment_of_btn, black_list_btn, back_to_admin


class FSMAdmin(StatesGroup):
    user_id = State()


async def admin(message):
    if message.from_user.id in ADMINS:
        redis_obj = job_stores.get('default')
        result = redis_obj.redis.get('payment')
        if (result and result.decode('utf-8') == 'off') or not result:
            payment_btn = payment_on_btn
            text = '🔴 Функція деактивована'
        elif result and result.decode('utf-8') == 'on':
            payment_btn = payment_of_btn
            text = '🟢 Функція активна'
        kb = InlineKeyboardMarkup().add(payment_btn, black_list_btn)
        if isinstance(message, types.Message):
            await message.answer(text=f'{text}\n\n👇 Оберіть варіант:', reply_markup=kb)
        else:
            try:
                await message.message.edit_text(text=f'{text}\n\n👇 Оберіть варіант:', reply_markup=kb)
            except:
                pass


async def deny_user_access(call: types.CallbackQuery):
    await FSMAdmin.user_id.set()
    await call.message.edit_text(text='👋🏻 Вітаю!\n'
                                      'Надішліть <b>id</b> користувача для надання або скасування прав:',
                                 parse_mode='html',
                                 reply_markup=InlineKeyboardMarkup().add(back_to_admin))


async def user_access(message: types.Message, state: FSMContext):
    user_id = message.text
    await state.reset_state(with_data=False)
    try:
        user = await get_user(user_id)
        kb = InlineKeyboardMarkup()
        if user.is_blocked:
            kb.add(InlineKeyboardButton(text='🔑 Розблокувати', callback_data=f'access_{user_id}_unblock'))
            await message.answer(text='🚫 Користувач заблокований.', reply_markup=kb)
        else:
            kb.add(InlineKeyboardButton(text='🚫 Заблокувати', callback_data=f'access_{user_id}_block'))
            await message.answer(text='✅ Користувач розблокований.', reply_markup=kb)
    except:
        await message.answer(text='❌ Користувача з таким id не існує.\n'
                                  'Спробуйте ще раз:')


async def set_access(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split('_')
    user_id = data[1]
    action = data[2]
    if action == 'block':
        text = (f'✅ Користувача з id: {user_id} заблоковано.\n'
                f'Надішліть <b>id</b> користувача для надання або скасування прав:')
        await update_user_sql(user_id, is_blocked=1)

    else:
        text = (f'✅ Користувача з id: {user_id} розблоковано.\n'
                f'Надішліть <b>id</b> користувача для надання або скасування прав:')
        await update_user_sql(user_id, is_blocked=0)
    await call.message.edit_text(text=text, parse_mode='html')
    await FSMAdmin.user_id.set()


async def payment_tumbler(call: types.CallbackQuery):
    redis_obj = job_stores.get('default')
    if call.data == 'off_payment':
        redis_obj.redis.set(name='payment', value='off')
    else:
        redis_obj.redis.set(name='payment', value='on')
    await admin(call)
    return


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin, commands=['admin'], state='*')
    dp.register_callback_query_handler(admin, Text(equals='admin'), state='*')
    dp.register_message_handler(user_access, state=FSMAdmin.user_id)
    dp.register_callback_query_handler(set_access, Text(equals='access'))
    dp.register_callback_query_handler(deny_user_access, Text(equals='deny_user_access'), state='*')
    dp.register_callback_query_handler(payment_tumbler, Text(endswith='_payment'), state='*')
