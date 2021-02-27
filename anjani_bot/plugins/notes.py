""" Fucking Notes. """
# Copyright (C) 2020 - 2021  UserbotIndo Team, <https://github.com/userbotindo.git>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import AsyncIOMotorCollection

from typing import ClassVar

from pyrogram import filters
from pyrogram.errors import RPCError
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from anjani_bot import Plugin, listener
from anjani_bot.utils import md_parse_button, build_keyboard
from anjani_bot.utils.msg_types import Types, get_note_type

# list all supported format for now
GET_FORMAT = {
    Types.TEXT.value: self.bot.send_message,
    Types.DOCUMENT.value: self.bot.send_document,
    Types.PHOTO.value: self.bot.send_photo,
    Types.VIDEO.value: self.bot.send_video,
    Types.STICKER.value: self.bot.send_sticker,
    Types.AUDIO.value: self.bot.send_audio,
    Types.VOICE.value: self.bot.send_voice,
    Types.VIDEO_NOTE.value: self.bot.send_video_note,
    Types.ANIMATION.value: self.bot.send_animation,
}

class NotesDB:
    notes_db = AsyncIOMotorCollection
    lock: asyncio.locks.Lock
    
    async def __on_load__(self):
       self.notes_db = self.bot.get_collection("NOTES")
       self.lock = asyncio.Lock()

    async def __migrate__(self, old_chat, new_chat):
        async with self.lock:
            await self.notes_db.update_one(
                {'chat_id': old_chat},
                {"$set": {
                    'chat_id': new_chat
                }},
            )
    
    async def save_notes(self, chat_id, note_name, note_data, msgtype, file=None):
        """ Save Notes Data. """
        async with self.lock:
            await self.notes_db.update_one(
                {'chat_id': chat_id}, {"$set": {
                    'text': text,
                    'note_name': note_name,
                    'note_data': note_data,
                    'msgtype': msgtype,
                    'file': None
                }},
                upsert=True)


class Notes(plugin.Plugin):
    name: ClasVar[str] = "Notes"
    helpable: ClassVar[bool] = False # Disable for now

    @listener.on("save", can_change_info=True)
    async def save_note(self, message):
        chat_id = message.chat.id
        """ Saved notes handler """
        note_name, text, data_type, content = await get_note_type(message)
        
        if not note_name:
            return await message.reply(await self.bot.text(chat_id, "note-name-error"))
        
        if data_type == Types.TEXT:
            _text, _, = await md_parse_button(text)
            if not _text:
               return await message.reply(await self.bot.text(chat_id, "notes-data-empty"))
        await self.save_notes(chat_id, note_name, data_type, content)