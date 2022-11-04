import logging
import re
import asyncio
from .. import loader, utils
from telethon.tl.types import Message


logger = logging.getLogger(__name__)


@loader.tds
class IrisLabMod(loader.Module):
    """Показывает лаб/жертв. Возможны задержки на получение инф-ции"""

    strings = {
        "name": "IrisLab",
        "saved": "💾 <b>Заметка с именем </b><code>{}</code><b> сохранена</b>.",
        "no_reply": "🚫 <b>Требуется реплай на контент заметки.</b>",
        "no_name": "🚫 <b>Укажите имя заметки.</b>",
        "no_note": "🚫 <b>Данная заметка не найдена или она не существует.</b>",
        "available_notes": "💾 <b>Текущие заметки:</b>\n",
        "no_notes": "😔 <b>У тебя пока что нет заметок</b>",
        "deleted": "🙂 <b>Заметка с именем </b><code>{}</code> <b>удалена</b>",
        "lab_data": {
            "имя": "(.*) Досье лаборатории (.*)",
            "рук": "(.*) Руководитель: (.*)",
            "корп": "(.*) В составе Корпорации (.*)",
            "пат": "(.*) Имя патогена: (.*)",
            "гпат": "(.*) Готовых патогенов: (.*) из (.*)",
            "квала": "(.*) Квалификация учёных: (.*)",
            "нпат": "(.*) Новый патоген: (.*)",
            "зз": "(.*) Заразность: (.*)",
            "имн": "(.*) Иммунитет: (.*)",
            "лтл": "(.*) Летальность: (.*)",
            "стата": "(.*) Био-опыт: (.*)",
            "сб": "(.*) Служба безопасности: (.*)",
            "бт": "(.*) Био-опыт: (.*)",
            "бр": "(.*) Био-ресурс: (.*)",
            "со": "(.*) Спецопераций: (.*)",
            "пр": "(.*) Предотвращены: (.*)",
            "зар": "(.*) Заражённых: (.*)",
            "бол": "(.*) Своих болезней: (.*)",
            "г": "<b> Руководитель в состоянии горячки",
        },
    }

    async def client_ready(self, client, db):
        db.set("Iris", "chat_biowar", 5443619563)

        self.client = client
        self.db = db
        self._notes = self.get("victims_list", {})

    async def message_q(
        self,
        text: str,
        user_id: int,
        mark_read: bool = False,
        delete: bool = False,
    ):
        """Отправляет сообщение и возращает ответ"""
        async with self.client.conversation(user_id) as conv:
            msg = await conv.send_message(text)
            response = await conv.get_response()
            if mark_read:
                await conv.mark_read()

            if delete:
                await msg.delete()
                await response.delete()

            return response

    async def лcmd(self, message):
        """Модуль который выдаст вам статистику вашей лаборатории (лаб)"""
        lab = await self.message_q(".Лаб", 5443619563, mark_read=True, delete=True)
        args_raw = utils.get_args_raw(message)
        if not args_raw:
            return await utils.answer(message, lab.text)

        data, text = self.strings("lab_data"), []
        flags = "".join(args_raw.split(" ")).split("-")
        if "" in flags:
            flags.remove("")
        for flag in flags:
            search = re.search(data[flag], lab.text) if flag in data else None
            if search:
                if flag == "be":
                    num = search.group().split(":")[-1].replace(" ", "")
                    if num[-1] == "k":
                        num = (
                            int(num[:-1].replace(",", "")) * 100 / 100 * 10
                            if "," in num
                            else int(num[:-1]) * 1000 / 100 * 10
                        )
                    elif num[:-1] != "k":
                        num = int(num) / 100 * 10
                    text.append(f"{search.group()} | {num}")
                elif flag == "d":
                    text.append(search.group()[:-1])
                else:
                    text.append(search.group())
            elif flag == "parametrs":
                text = """
имя: Имя лаборатории
рук: Руководитель
корп: Корпорация
стата: Био-опыт, Био-ресурс, Руководитель, Готовых патогенов

пат: Имя патогена
гпат: Готовых патогенов
квала: Квалификация учёных 👨‍🔬
нпат: Новый патоген через... ⏱

зз: Заразность 
имн: Иммунитет 🛡️
лтл: Летальность ☠️
сб: Служба безопасности 

бт: Био-опыт ☣️
бр: Био-ресурс 🧬
со: Спецопераций 😷
пр: Предотвращены 🥽

зар: заражённых 🤒
бол: Своих болезней 🤒

г: Горячка руководителя 
ежа: Ежедневная премия(ежа) 💸"""
                return await utils.answer(message, text)
            elif flag == "v":
                await asyncio.sleep(3)
                victims = await self.message_q(
                    "Мои жертвы", 5443619563, mark_read=True, delete=True
                )
                result = re.search(
                    r"""(.*) Ежедневная премия: (.*)""", victims.text
                ).group()
                text.append(result)
            elif flag in data:
                app_text = (
                    "✅ Все патогены приготовлены" if flag == "np" else "❌ Горячки нету"
                )
                text.append(app_text)
            else:
                text.append(f"Параметр -{flag} не указан.")
            return await utils.answer(message, "\n".join(text))

    async def жcmd(self, message):
        """Комманда показывает ваши жертвы"""
        victims = await self.message_q(
            "Мои жертвы",
            5443619563,
            mark_read=True,
            delete=True,
        )

        args_raw = utils.get_args_raw(message)

        if not args_raw:
            await utils.answer(message, victims.text)
    
    async def болcmd(self, message):

        """Комманда показывает ваши болезни"""

        victims = await self.message_q(

            "Мои болезни",

            5443619563,

            mark_read=True,

            delete=True,

        )

        args_raw = utils.get_args_raw(message)

        if not args_raw:

            await utils.answer(message, victims.text)
            
    async def upgcmd(self, message):
        """Увеличивает зз/имун и тд.Как использовать(Пример) .upg летальность (число 1-5)"""
        args = utils.get_args(message)
        characteristics = (
            "заразность",
            "летальность",
            "иммунитет",
            "безопасность",
            "разработка",
            "патоген",
        )
        if len(args) != 2:
            await utils.answer(message, "Указано больше или меньше двух параметров")
        elif args[0].lower() not in characteristics:
            await utils.answer(message, "Данного улучшения не существует")
        elif not args[1].isdigit():
            await utils.answer(message, "Второй параметр не является числом")
        elif int(args[1]) > 5 or int(args[1]) < 0:
            await utils.answer(message, "Уровень указан вне допустимого диапазона")
        else:
            await message.respond(f"++{args[0].lower()} {args[1]}")

    async def gcmd(self, message: Message):
        """<name> - показывает заметку"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_name"))
            return

        asset = self._get_note(args)
        if not asset:
            await utils.answer(message, self.strings("no_note"))
            return

        await self._client.send_message(
            message.peer_id,
            await self._db.fetch_asset(asset["id"]),
            reply_to=getattr(message, "reply_to_msg_id", False),
        )

        if message.out:
            await message.delete()

    async def svcmd(self, message):
        """<name> - для сохранения заметки"""
        args = utils.get_args_raw(message)
        folder = "victims_list"

        reply = await message.get_reply_message()
        if not (reply and args):
            await utils.answer(message, self.strings("no_reply"))
            return
        if folder not in self._notes:
            self._notes[folder] = {}
            logger.warning(f"Created new folder {folder}")

        asset = await self._db.store_asset(reply)

        type_ = "☣️"

        self._notes[folder][args] = {"id": asset, "type": type_}

        self.set("victims_list", self._notes)

        await utils.answer(message, self.strings("saved").format(args, folder))

    def _get_note(self, name: str):
        for notes in self._notes.values():
            for note, asset in notes.items():
                if note == name:
                    return asset

    def _del_note(self, name: str):
        for category, notes in self._notes.copy().items():
            for note in notes.copy():
                if note == name:
                    del self._notes[category][note]

                if not self._notes[category]:
                    del self._notes[category]

                self.set("victims_list", self._notes)
                return True

        return False

    async def dcmd(self, message: Message):
        """<name> - удаляет заметку"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_name"))
            return

        asset = self._get_note(args)
        if not asset:
            await utils.answer(message, self.strings("no_note"))
            return

        with contextlib.suppress(Exception):
            await (await self._db.fetch_asset(asset["id"])).delete()

        self._del_note(args)

        await utils.answer(message, self.strings("deleted").format(args))

    async def listcmd(self, message: Message):
        """[folder] - показывает все заметки"""
        args = utils.get_args_raw(message)

        if not self._notes:
            await utils.answer(message, self.strings("no_notes"))
            return

        result = self.strings("available_notes")
        if not args or args not in self._notes:
            for category, notes in self._notes.items():
                result += f"\n🔸 <b>{category}</b>\n"
                for note, asset in notes.items():
                    result += f"    {asset['type']} <code>{note}</code>\n"

            await utils.answer(message, result)
            return

        for note, asset in self._notes[args].items():
            result += f"{asset['type']} <code>{note}</code>\n"

        await utils.answer(message, result)

    async def iccmd(self, message: Message):
        """Комманда котрая вычисляет сколько 🧬Био-ресурсов или же ic☣️ нужно\nПример: .ic <характеристика> <уровень С> <уровень До>"""
        args = utils.get_args(message)
        if not args or len(args) != 3 or not args[1].isdigit() or not args[2].isdigit():
            await utils.answer(
                message,
                "🚫| <b>Чтобы использовать калькулятор напишите .ic <навык> <уровень С> <уровень До></b>",
            )
            return

        skill, from_lvl, to_lvl = args
        from_lvl, to_lvl = int(from_lvl), int(to_lvl)
        amount = (
            await self._client.inline_query(
                "@hikkaftgbot", f"{skill}#{from_lvl}#{to_lvl}"
            )
        )[0].title

        if not amount.isdigit():
            await utils.answer(message, amount)
            return

        amount = f"{int(amount):,}".replace(",", " ")

        await utils.answer(
            message,
            f"🍀| Чтобы увеличить навык «{skill}» с {from_lvl} до {to_lvl} уровня"
            f" потребуется: {amount} био-ресурсов🧬 или же ic☣️",
        )
