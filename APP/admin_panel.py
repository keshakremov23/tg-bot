# admin_panel.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from database.db import (
    add_person_to_db, get_all_people, get_person_by_id, delete_person,
    update_person_photo, add_person_audio, get_person_audios,
    delete_audio, get_audio_info, get_people_with_any_audio
)

admin_router = Router()
ADMIN_ID = 1035088857


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# === Состояния ===
class AddPerson(StatesGroup):
    name = State()
    desc = State()
    photo = State()
    audio_loop = State()


class DeletePerson(StatesGroup):
    waiting_id = State()


class AddAudioToPerson(StatesGroup):
    waiting_audio = State()  # ждём аудио для конкретного человека


# === Главное меню ===
@admin_router.message(F.text == "/admin")
async def admin_menu(message: Message):
    if not is_admin(message.from_user.id):
        return await message.answer("Доступ запрещён")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить человека", callback_data="add_start")],
        [InlineKeyboardButton(text="Список всех", callback_data="list_all")],
        [InlineKeyboardButton(text="Управление аудио", callback_data="audio_main")],
        [InlineKeyboardButton(text="Удалить человека", callback_data="del_start")],
    ])
    await message.answer("Админ-панель", reply_markup=kb)


# === Добавление нового человека (оставлено без изменений) ===
@admin_router.callback_query(F.data == "add_start")
async def add_start(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text("Введите имя человека:")
    await state.set_state(AddPerson.name)


@admin_router.message(AddPerson.name)
async def add_name_handler(m: Message, state: FSMContext):
    await state.update_data(name=m.text.strip())
    await m.answer("Введите описание:")
    await state.set_state(AddPerson.desc)


@admin_router.message(AddPerson.desc)
async def add_desc_handler(m: Message, state: FSMContext):
    data = await state.get_data()
    pid = add_person_to_db(data["name"], m.text.strip())
    if not pid:
        return await m.answer("Ошибка создания")
    await state.update_data(person_id=pid)
    await m.answer(f"Создан! ID: {pid}\nОтправьте фото или /skip")
    await state.set_state(AddPerson.photo)


@admin_router.message(AddPerson.photo, F.text == "/skip")
async def skip_photo(m: Message, state: FSMContext):
    await start_audio_loop(m, state)


@admin_router.message(AddPerson.photo, F.photo)
async def save_photo(m: Message, state: FSMContext):
    data = await state.get_data()
    update_person_photo(data["person_id"], m.photo[-1].file_id)
    await m.answer("Фото сохранено")
    await start_audio_loop(m, state)


async def start_audio_loop(m: Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Готово", callback_data="add_finish")]
    ])
    await m.answer("Отправляйте аудио (сколько угодно)\nЗакончили → Готово", reply_markup=kb)
    await state.set_state(AddPerson.audio_loop)


@admin_router.message(AddPerson.audio_loop, F.audio | F.voice)
async def save_audio_new_person(m: Message, state: FSMContext):
    data = await state.get_data()
    file_id = m.audio.file_id if m.audio else m.voice.file_id
    title = m.audio.title or m.audio.file_name or "Голосовое" if m.audio else "Голосовое"
    add_person_audio(data["person_id"], file_id, title)
    await m.answer(f"Добавлено! Всего: {len(get_person_audios(data['person_id']))}")


@admin_router.callback_query(F.data == "add_finish")
async def add_finish(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await cb.message.edit_text(f"Человек ID {data['person_id']} полностью добавлен")
    await state.clear()


# === Список всех ===
@admin_router.callback_query(F.data == "list_all")
async def list_all(cb: CallbackQuery):
    people = get_all_people()
    if not people:
        return await cb.message.edit_text("База пуста")
    text = "Список:\n\n"
    for p in people:
        text += f"ID: {p[0]} | {p[1]} | аудио: {len(get_person_audios(p[0]))}\n"
    await cb.message.edit_text(text)


# === Управление аудио ===
@admin_router.callback_query(F.data == "audio_main")
async def audio_main(cb: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Все аудио", callback_data="audio_all")],
        [InlineKeyboardButton(text="Назад", callback_data="back_admin")],
    ])
    await cb.message.edit_text("Управление аудио", reply_markup=kb)


@admin_router.callback_query(F.data == "audio_all")
async def audio_all(cb: CallbackQuery):
    people = get_people_with_any_audio() or get_all_people()
    if not people:
        return await cb.message.edit_text("Нет людей")

    for p in people:
        pid, name = p[0], p[1]
        audios = get_person_audios(pid)
        kb = [
            [InlineKeyboardButton(text="Добавить аудио", callback_data=f"addaudio_{pid}")],
        ]
        for a in audios:
            kb.append([InlineKeyboardButton(text=a["title"][:45], callback_data=f"play_{a['id']}")])
        kb.append([InlineKeyboardButton(text="Назад", callback_data="audio_main")])

        await cb.message.answer(
            f"{name} (ID: {pid})\nАудио: {len(audios)}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
        )


# === Добавление аудио к существующему человеку ===
@admin_router.callback_query(F.data.startswith("addaudio_"))
async def start_add_audio_to_person(cb: CallbackQuery, state: FSMContext):
    person_id = int(cb.data.split("_")[1])
    person = get_person_by_id(person_id)
    if not person:
        return await cb.answer("Человек не найден", show_alert=True)

    await state.update_data(target_person_id=person_id)
    await state.set_state(AddAudioToPerson.waiting_audio)
    await cb.message.edit_text(f"Отправьте аудио для {person['name']} (ID {person_id})\n/отмена — выйти")


@admin_router.message(AddAudioToPerson.waiting_audio, F.text == "/отмена")
async def cancel_add_audio(m: Message, state: FSMContext):
    await m.answer("Добавление отменено")
    await state.clear()


@admin_router.message(AddAudioToPerson.waiting_audio, F.audio | F.voice)
async def save_audio_to_existing_person(m: Message, state: FSMContext):
    data = await state.get_data()
    pid = data["target_person_id"]
    file_id = m.audio.file_id if m.audio else m.voice.file_id
    title = m.audio.title or m.audio.file_name or "Голосовое" if m.audio else "Голосовое"

    add_person_audio(pid, file_id, title)
    count = len(get_person_audios(pid))
    person = get_person_by_id(pid)

    await m.answer(f"Аудио добавлено к {person['name']}\nВсего аудио: {count}")
    await state.clear()


# === Воспроизведение и удаление ===
@admin_router.callback_query(F.data.startswith("play_"))
async def play_audio(cb: CallbackQuery):
    audio_id = int(cb.data.split("_")[1])
    audio = get_audio_info(audio_id)
    if not audio:
        return await cb.answer("Не найдено", show_alert=True)
    person = get_person_by_id(audio["person_id"])
    await cb.message.answer_audio(audio["audio_file_id"], caption=f"{person['name']} — {audio['title']}")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Удалить", callback_data=f"del_{audio_id}")],
        [InlineKeyboardButton(text="Назад", callback_data="audio_all")],
    ])
    await cb.message.answer("Действия:", reply_markup=kb)


@admin_router.callback_query(F.data.startswith("del_"))
async def delete_audio_handler(cb: CallbackQuery):
    audio_id = int(cb.data.split("_")[1])
    delete_audio(audio_id)
    await cb.message.edit_text("Аудио удалено")


# === Удаление человека ===
@admin_router.callback_query(F.data == "del_start")
async def del_start(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text("Введите ID для удаления:")
    await state.set_state(DeletePerson.waiting_id)


@admin_router.message(DeletePerson.waiting_id)
async def process_delete(m: Message, state: FSMContext):
    try:
        pid = int(m.text)
        if delete_person(pid):
            await m.answer(f"Человек {pid} удалён со всеми аудио")
        else:
            await m.answer("Ошибка")
    except ValueError:
        await m.answer("Неверный ID")
    finally:
        await state.clear()


# === Назад ===
@admin_router.callback_query(F.data == "back_admin")
async def back_admin(cb: CallbackQuery):
    await admin_menu(cb.message)