import typing
from copy import deepcopy
from typing import Optional
from aiogram import types, Bot
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import base


class HiddenUser(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data):
        from keyboards.kb import main_kb
        from create_bot import _
        if not message.from_user.username:
            await message.answer(text=_("Щоб користуватись ботом потрібно створити або зробити публічним юзернейм у вашому телеграм акаунті."),
                                 reply_markup=main_kb)
            raise CancelHandler()

    async def on_process_callback_query(self, query: types.CallbackQuery, data):
        from keyboards.kb import main_kb
        from create_bot import _
        if not query.from_user.username:
            await query.message.answer(
                text=_("Щоб користуватись ботом потрібно створити або зробити публічним юзернейм у вашому телеграм акаунті."),
                reply_markup=main_kb)
            raise CancelHandler()


class Localization(I18nMiddleware):
    async def get_user_locale(self, action: str, args: tuple) -> Optional[str]:
        from db.db_manage import get_user
        if isinstance(args[0], (types.Message, types.CallbackQuery)):
            user_id = args[0].from_user.id
        else:
            user_id = args[0]
        user = await get_user(user_id)
        if not user:
            return
        return user.language


class MyBot(Bot):
    async def send_message(self, *args, **kwargs):
        from create_bot import i18n
        user_locale = await i18n.get_user_locale(action="action", args=(kwargs.get('chat_id'),))
        from utils.utils import translate_kb
        kwargs['reply_markup'] = await translate_kb(kwargs.get('reply_markup'), locale=user_locale, owner_id=kwargs.get('chat_id'))
        await super().send_message(*args, **kwargs)

    async def edit_message_text(self,
                                text: base.String,
                                chat_id: typing.Union[base.Integer, base.String, None] = None,
                                message_id: typing.Optional[base.Integer] = None,
                                inline_message_id: typing.Optional[base.String] = None,
                                parse_mode: typing.Optional[base.String] = None,
                                entities: typing.Optional[typing.List[types.MessageEntity]] = None,
                                disable_web_page_preview: typing.Optional[base.Boolean] = None,
                                reply_markup: typing.Union[types.InlineKeyboardMarkup,
                                None] = None,
                                ) -> types.Message or base.Boolean:
        from utils.utils import translate_kb
        from create_bot import i18n
        user_locale = await i18n.get_user_locale(action="action", args=(chat_id,))
        reply_markup = await translate_kb(deepcopy(reply_markup), user_locale, owner_id=chat_id)
        return await super().edit_message_text(text=text,
                                               chat_id=chat_id,
                                               message_id=message_id,
                                               inline_message_id=inline_message_id,
                                               parse_mode=parse_mode,
                                               entities=entities,
                                               disable_web_page_preview=disable_web_page_preview,
                                               reply_markup=reply_markup)
