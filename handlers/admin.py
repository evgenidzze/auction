from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db_manage import get_user, update_user_sql
from keyboards.kb import main_kb, cancel_kb


class FSMAdmin(StatesGroup):
    user_id = State()


async def admin(message: types.Message):
    await FSMAdmin.user_id.set()
    await message.answer(text='👋🏻 Вітаю!\n'
                              'Надішліть <b>id</b> користувача для надання або скасування прав:', parse_mode='html', reply_markup=cancel_kb)


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


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin, commands=['admin'], state='*')
    dp.register_message_handler(user_access, state=FSMAdmin.user_id)
    dp.register_callback_query_handler(set_access, Text(startswith='access'))
