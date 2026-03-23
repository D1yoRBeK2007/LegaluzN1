import logging
import asyncio
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from supabase import create_client, Client

# --- SOZLAMALAR ---
API_TOKEN = '8650792168:AAG2ZZ75TecqwtmIssmAicEEA6sqk1KWvlA'
SUPABASE_URL = "https://vdvebwbbqgyohdhpfrty.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZkdmVid2JicWd5b2hkaHBmcnR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyNzcxNzMsImV4cCI6MjA4OTg1MzE3M30.QubiSyWWqV8r5B6Jb6W0Wkm-6M0kQ7G0HajHiOGgu8M"

ADMIN_USERNAME = "@lawyer_nematov"
JILD_LINK = "https://t.me/addlist/LAV6HuGmEOJlOGVi"
GURUH_YURIST = -1003851523097
GURUH_MUROJAATCHI = -1003700631184

# Supabase ulanishi
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class ElonStates(StatesGroup):
    til = State()
    asosi_menyu = State()
    soha = State()
    tasnif = State()
    narx = State()
    turi = State()

# Foydalanuvchini bazaga qo'shish funksiyasi
def upsert_user(user_id, full_name, username, lang):
    data = {
        "id": user_id,
        "full_name": full_name,
        "username": username,
        "language": lang
    }
    supabase.table("users").upsert(data).execute()

@dp.message_handler(commands=['start'], state='*')
async def start_cmd(message: types.Message, state: FSMContext):
    await state.finish()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("O'zbek 🇺🇿", "Русский 🇷🇺", "English 🇺🇸")
    await message.answer(f"Assalamu alaykum {message.from_user.first_name}! LegalUZ loyihasiga xush kelibsiz.\nIltimos, tilni tanlang:", reply_markup=markup)
    await ElonStates.til.set()

@dp.message_handler(state=ElonStates.til)
async def select_lang(message: types.Message, state: FSMContext):
    lang = message.text
    # Bazaga saqlash
    upsert_user(message.from_user.id, message.from_user.full_name, message.from_user.username, lang)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("A'zo bo'ldim ✅", callback_data="check_sub"))
    await message.answer(f"Davom etish uchun quyidagi jildga obuna bo'ling:\n{JILD_LINK}", reply_markup=markup)
    await state.update_data(lang=lang)

@dp.callback_query_handler(text="check_sub", state="*")
async def check_subscription(call: types.CallbackQuery, state: FSMContext):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("E'lon joylash", "AI konsultatsiya")
    markup.add("Tayyor hujjat namunalari", "Admin bilan bog'lanish")
    
    await call.message.delete()
    await call.message.answer("Xush kelibsiz! O'zingizga kerakli bo'limni tanlang:", reply_markup=markup)
    await ElonStates.asosi_menyu.set()

@dp.message_handler(state=ElonStates.asosi_menyu)
async def handle_menu(message: types.Message, state: FSMContext):
    if message.text == "E'lon joylash":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Mutaxassis sifatida", "Murojaatchi sifatida")
        markup.add("🔙 Orqaga")
        await message.answer("Kim sifatida e'lon bermoqchisiz?", reply_markup=markup)
    
    elif message.text == "Mutaxassis sifatida":
        await state.update_data(turi="yurist")
        await message.answer("Sohani yozing (masalan: Oila, Shartnoma):", reply_markup=types.ReplyKeyboardRemove())
        await ElonStates.soha.set()
        
    elif message.text == "Murojaatchi sifatida":
        await state.update_data(turi="murojaatchi")
        await message.answer("Sohani yozing (masalan: Uy-joy, Mehnat):", reply_markup=types.ReplyKeyboardRemove())
        await ElonStates.soha.set()

    elif message.text == "Admin bilan bog'lanish":
        await message.answer(f"Takliflaringizni yozing yoki adminga murojaat qiling: {ADMIN_USERNAME}")

@dp.message_handler(state=ElonStates.soha)
async def get_soha(message: types.Message, state: FSMContext):
    await state.update_data(soha=message.text)
    await message.answer("E'lon uchun qisqa tasnif (max 75 ta so'z):")
    await ElonStates.tasnif.set()

@dp.message_handler(state=ElonStates.tasnif)
async def get_tasnif(message: types.Message, state: FSMContext):
    if len(message.text.split()) > 75:
        await message.answer("Tasnif juda uzun! Qisqaroq yozing.")
        return
    await state.update_data(tasnif=message.text)
    await message.answer("Xizmat narxi (masalan: 200k - 1mln yoki Bepul):")
    await ElonStates.narx.set()

@dp.message_handler(state=ElonStates.narx)
async def get_narx(message: types.Message, state: FSMContext):
    data = await state.get_data()
    target_group = GURUH_YURIST if data.get('turi') == "yurist" else GURUH_MUROJAATCHI
    
    # Guruhga yuboriladigan tekst formati
    post_text = (
        f"<b>Sohasi:</b> {data['soha']}\n"
        f"Tasnif: {data['tasnif']}\n"
        f"<b>Narx chegarasi:</b> {message.text}\n\n"
        f"Murojaat uchun: <a href='tg://user?id={message.from_user.id}'>Bog'lanish</a>"
    )
    
    try:
        await bot.send_message(target_group, post_text)
        await message.answer("E'loningiz guruhga muvaffaqiyatli yuborildi! ✅")
        # Menyuga qaytarish
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("E'lon joylash", "AI konsultatsiya")
        markup.add("Tayyor hujjat namunalari", "Admin bilan bog'lanish")
        await message.answer("Asosiy menyu:", reply_markup=markup)
        await ElonStates.asosi_menyu.set()
    except Exception as e:
        logging.error(e)
        await message.answer("Xatolik yuz berdi. Bot guruhda admin ekanligini tekshiring.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
