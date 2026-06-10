from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import *
from database import *

# ===== FSM STATES =====
class RegisterState(StatesGroup):
    waiting_name = State()

class BuyCreditsState(StatesGroup):
    waiting_amount = State()

class AdminState(StatesGroup):
    add_outline = State()
    add_v2ray = State()
    broadcast = State()
    delete_key = State()          # NEW: admin delete key

# ===== KEYBOARDS =====
def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👤 User Info", callback_data="user_info"),
            InlineKeyboardButton(text="📝 Register", callback_data="register")
        ],
        [
            InlineKeyboardButton(text="🔗 Refer", callback_data="refer"),
            InlineKeyboardButton(text="🔑 Generate Key", callback_data="generate_key")
        ],
        [
            InlineKeyboardButton(text="📋 My Keys", callback_data="my_keys"),
            InlineKeyboardButton(text="🖥 Server Status", callback_data="server_status")
        ],
        [
            InlineKeyboardButton(text="💰 Buy Credits", callback_data="buy_credits"),
            InlineKeyboardButton(text="📢 Channel", url=CHANNEL_URL)
        ]
    ])

def key_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🔵 Outline ({OUTLINE_KEY_COST} Credits)", callback_data="gen_outline")],
        [InlineKeyboardButton(text=f"🟣 V2RAY ({V2RAY_KEY_COST} Credits)", callback_data="gen_v2ray")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_main")]
    ])

def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Outline Keys", callback_data="admin_add_outline"),
            InlineKeyboardButton(text="➕ V2RAY Keys", callback_data="admin_add_v2ray")
        ],
        [
            InlineKeyboardButton(text="🗑 Delete Key", callback_data="admin_delete_key"),   # NEW
            InlineKeyboardButton(text="📊 Stats", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="📋 Pending Requests", callback_data="admin_pending"),
            InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast")
        ]
    ])

def back_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_main")]
    ])

def admin_back_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Admin Panel", callback_data="admin_back")]
    ])

# ===== START =====
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    args = message.text.split()
    user = get_user(message.from_user.id)

    if not user:
        ref_id = None
        if len(args) > 1 and args[1].startswith("ref_"):
            try:
                ref_id = int(args[1].replace("ref_", ""))
                if ref_id == message.from_user.id:
                    ref_id = None
            except:
                ref_id = None
        # create_user already adds REGISTER_CREDITS inside
        create_user(message.from_user.id, message.from_user.username, message.from_user.full_name, ref_id)
        if ref_id:
            add_credits(ref_id, REFER_CREDITS)

    await message.answer(
        f"✨ <b>Premium VPN Bot မှ ကြိုဆိုပါသည်</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🌐 <b>{SERVER_NAME}</b>\n"
        f"📍 Server: {SERVER_LOCATION}\n\n"
        f"အောက်ပါ ခလုပ်များကို အသုံးပြုနိုင်ပါသည်-",
        reply_markup=main_keyboard(), parse_mode="HTML"
    )

async def cb_back_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        f"✨ <b>Premium VPN Bot မှ ကြိုဆိုပါသည်</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🌐 <b>{SERVER_NAME}</b>\n\n"
        f"အောက်ပါ ခလုပ်များကို အသုံးပြုနိုင်ပါသည်-",
        reply_markup=main_keyboard(), parse_mode="HTML"
    )

# ===== USER INFO =====
async def cb_user_info(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("Register ဦးလုပ်ပါ!", show_alert=True)
        return
    keys = get_user_keys(callback.from_user.id)
    await callback.message.edit_text(
        f"👤 <b>User Information</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: <code>{callback.from_user.id}</code>\n"
        f"👤 Name: {user['full_name']}\n"
        f"💰 Credits: <b>{user['credits']}</b>\n"
        f"🔑 Total Keys: <b>{len(keys)}</b>\n"
        f"✅ Status: Registered",
        reply_markup=back_keyboard(), parse_mode="HTML"
    )

# ===== REGISTER =====
async def cb_register(callback: CallbackQuery, state: FSMContext):
    user = get_user(callback.from_user.id)
    if user and user.get("registered"):
        await callback.answer("မှတ်ပုံတင်ပြီးဖြစ်သည်!", show_alert=True)
        return
    await callback.message.edit_text(
        "📝 <b>Register</b>\n\nသင်၏အမည်ကိုရိုက်ထည့်ပါ-",
        parse_mode="HTML"
    )
    await state.set_state(RegisterState.waiting_name)

async def register_name(message: Message, state: FSMContext):
    await state.clear()
    # If user doesn't exist yet, create with default credits (though usually already exists via /start)
    user = get_user(message.from_user.id)
    if not user:
        create_user(message.from_user.id, message.from_user.username, message.from_user.full_name, None)
    await message.answer(
        f"✅ <b>Register အောင်မြင်ပါသည်!</b>\n\n"
        f"👤 Name: {message.text}\n"
        f"💰 Credits: <b>{REGISTER_CREDITS}</b> ရောက်ပြီ\n\n"
        f"🎉 Generate Key နှိပ်ပြီး VPN Key ထုတ်ပါ!",
        reply_markup=main_keyboard(), parse_mode="HTML"
    )

# ===== REFER =====
async def cb_refer(callback: CallbackQuery):
    # Static refer link as requested: https://t.me/bug303
    ref_link = f"{REFER_BASE_URL}?start=ref_{callback.from_user.id}"
    await callback.message.edit_text(
        f"🔗 <b>Referral System</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"မိတ်ဆွေများကို invite လုပ်ပြီး Credits ရယူပါ!\n\n"
        f"🎁 Per invite: <b>{REFER_CREDITS} Credits</b>\n\n"
        f"🔗 သင်၏ Link:\n<code>{ref_link}</code>",
        reply_markup=back_keyboard(), parse_mode="HTML"
    )

# ===== GENERATE KEY =====
async def cb_generate_key(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("Register ဦးလုပ်ပါ!", show_alert=True)
        return
    await callback.message.edit_text(
        f"🔑 <b>Generate VPN Key</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💰 သင်၏ Credits: <b>{user['credits']}</b>\n\n"
        f"Key အမျိုးအစား ရွေးချယ်ပါ-",
        reply_markup=key_type_keyboard(), parse_mode="HTML"
    )

async def cb_gen_outline(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("Register ဦးလုပ်ပါ!", show_alert=True)
        return
    if user["credits"] < OUTLINE_KEY_COST:
        await callback.answer(f"Credits မလုံလောက်ပါ! {OUTLINE_KEY_COST} Credits လိုသည်", show_alert=True)
        return
    key = get_outline_key()
    if not key:
        await callback.answer("Outline Keys ကုန်သွားပြီ! Admin ထံဆက်သွယ်ပါ", show_alert=True)
        return
    deduct_credits(callback.from_user.id, OUTLINE_KEY_COST)
    save_key(callback.from_user.id, "Outline", key)
    remaining = user["credits"] - OUTLINE_KEY_COST
    await callback.message.edit_text(
        f"✅ <b>Outline Key ရရှိပြီ!</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🔵 Type: Outline VPN\n\n"
        f"🔑 Key:\n<code>{key}</code>\n\n"
        f"💰 Credits ကျန်: <b>{remaining}</b>",
        reply_markup=back_keyboard(), parse_mode="HTML"
    )

async def cb_gen_v2ray(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("Register ဦးလုပ်ပါ!", show_alert=True)
        return
    if user["credits"] < V2RAY_KEY_COST:
        await callback.answer(f"Credits မလုံလောက်ပါ! {V2RAY_KEY_COST} Credits လိုသည်", show_alert=True)
        return
    key = get_v2ray_key()
    if not key:
        await callback.answer("V2RAY Keys ကုန်သွားပြီ! Admin ထံဆက်သွယ်ပါ", show_alert=True)
        return
    deduct_credits(callback.from_user.id, V2RAY_KEY_COST)
    save_key(callback.from_user.id, "V2RAY", key)
    remaining = user["credits"] - V2RAY_KEY_COST
    await callback.message.edit_text(
        f"✅ <b>V2RAY Key ရရှိပြီ!</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🟣 Type: V2RAY VPN\n\n"
        f"🔑 Key:\n<code>{key}</code>\n\n"
        f"💰 Credits ကျန်: <b>{remaining}</b>",
        reply_markup=back_keyboard(), parse_mode="HTML"
    )

# ===== MY KEYS =====
async def cb_my_keys(callback: CallbackQuery):
    keys = get_user_keys(callback.from_user.id)
    if not keys:
        text = "📋 <b>My Keys</b>\n\nKey မရှိသေးပါ!"
    else:
        lines = ["📋 <b>My Keys</b>\n━━━━━━━━━━━━━━━━"]
        for i, k in enumerate(keys[:10], 1):
            icon = "🔵" if k["key_type"] == "Outline" else "🟣"
            lines.append(f"{i}. {icon} {k['key_type']}\n<code>{k['key_value']}</code>\n")
        text = "\n".join(lines)
    await callback.message.edit_text(text, reply_markup=back_keyboard(), parse_mode="HTML")

# ===== SERVER STATUS =====
async def cb_server_status(callback: CallbackQuery):
    outline_count, v2ray_count = count_keys()
    await callback.message.edit_text(
        f"🖥 <b>Server Status</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🌐 {SERVER_NAME}\n"
        f"📍 Location: {SERVER_LOCATION}\n"
        f"🟢 Status: Online\n\n"
        f"🔑 <b>Available Keys</b>\n"
        f"🔵 Outline: <b>{outline_count}</b>\n"
        f"🟣 V2RAY: <b>{v2ray_count}</b>",
        reply_markup=back_keyboard(), parse_mode="HTML"
    )

# ===== BUY CREDITS =====
async def cb_buy_credits(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "💰 <b>Buy Credits</b>\n\n"
        "ဝယ်လိုသော Credits ပမာဏ ရိုက်ထည့်ပါ-\n"
        "ဥပမာ: <code>50</code>, <code>100</code>, <code>200</code>",
        parse_mode="HTML"
    )
    await state.set_state(BuyCreditsState.waiting_amount)

async def buy_credits_amount(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("ကိန်းဂဏန်းသာ ရိုက်ထည့်ပါ!")
        return
    amount = int(message.text)
    await state.clear()
    create_credit_request(message.from_user.id, amount)

    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                admin_id,
                f"💰 <b>Credit Request</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"👤 {message.from_user.full_name}\n"
                f"🆔 <code>{message.from_user.id}</code>\n"
                f"💰 Amount: <b>{amount} Credits</b>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="✅ Approve", callback_data=f"apv_{message.from_user.id}_{amount}"),
                    InlineKeyboardButton(text="❌ Reject", callback_data=f"rej_{message.from_user.id}")
                ]])
            )
        except:
            pass

    await message.answer(
        f"✅ <b>Request တင်ပြီ!</b>\n\n"
        f"💰 {amount} Credits တောင်းဆိုထားသည်\n"
        f"Admin approve ပြီးသည်နှင့် Credits ရောက်မည်",
        reply_markup=main_keyboard(), parse_mode="HTML"
    )

# ===== ADMIN HANDLERS =====
async def cmd_admin(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("👑 <b>Admin Panel</b>\n━━━━━━━━━━━━━━━━", reply_markup=admin_keyboard(), parse_mode="HTML")

async def cb_admin_back(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await state.clear()
    await callback.message.edit_text("👑 <b>Admin Panel</b>", reply_markup=admin_keyboard(), parse_mode="HTML")

async def cb_admin_stats(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    total_users = count_users()
    outline, v2ray = count_keys()
    await callback.message.edit_text(
        f"📊 <b>Bot Statistics</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"👥 Total Users: <b>{total_users}</b>\n"
        f"🔵 Outline Keys: <b>{outline}</b>\n"
        f"🟣 V2RAY Keys: <b>{v2ray}</b>",
        reply_markup=admin_back_keyboard(), parse_mode="HTML"
    )

async def cb_admin_add_outline(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text(
        "➕ <b>Outline Keys ထည့်မည်</b>\n\n"
        "Key တစ်ခုချင်းစီ တစ်ကြောင်းချင်း ရိုက်ပါ\n"
        "ပြီးလျှင် /done ရိုက်ပါ",
        parse_mode="HTML"
    )
    await state.set_state(AdminState.add_outline)
    await state.update_data(keys=[])

async def cb_admin_add_v2ray(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text(
        "➕ <b>V2RAY Keys ထည့်မည်</b>\n\n"
        "Key တစ်ခုချင်းစီ တစ်ကြောင်းချင်း ရိုက်ပါ\n"
        "ပြီးလျှင် /done ရိုက်ပါ",
        parse_mode="HTML"
    )
    await state.set_state(AdminState.add_v2ray)
    await state.update_data(keys=[])

async def admin_collect_keys(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    current = await state.get_state()
    data = await state.get_data()
    keys_list = data.get("keys", [])

    if message.text == "/done":
        count = len(keys_list)
        if current == AdminState.add_outline:
            for k in keys_list:
                add_outline_key(k)
            await message.answer(f"✅ Outline Keys <b>{count}</b> ခု ထည့်ပြီ!", reply_markup=admin_keyboard(), parse_mode="HTML")
        elif current == AdminState.add_v2ray:
            for k in keys_list:
                add_v2ray_key(k)
            await message.answer(f"✅ V2RAY Keys <b>{count}</b> ခု ထည့်ပြီ!", reply_markup=admin_keyboard(), parse_mode="HTML")
        else:
            await message.answer("State error. ထပ်ကြိုးစားပါ.")
        await state.clear()
    else:
        keys_list.append(message.text.strip())
        await state.update_data(keys=keys_list)
        await message.answer(f"✅ {len(keys_list)} ခု - ဆက်ရိုက်ပါ သို့မဟုတ် /done")

# ===== ADMIN DELETE KEY ===== (NEW)
async def cb_admin_delete_key(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text(
        "🗑 <b>Delete Key</b>\n\n"
        "ဖျက်လိုသော Key အပြည့်အစုံကို ရိုက်ထည့်ပါ။\n"
        "(Outline သို့မဟုတ် V2RAY key value တစ်ခုလုံး)\n\n"
        "ပယ်ဖျက်လိုပါက /cancel ရိုက်ပါ။",
        parse_mode="HTML"
    )
    await state.set_state(AdminState.delete_key)

async def admin_delete_key_handler(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    key_value = message.text.strip()
    if key_value == "/cancel":
        await state.clear()
        await message.answer("❌ Key ဖျက်ခြင်းကို ပယ်ဖျက်လိုက်ပြီ။", reply_markup=admin_keyboard())
        return
    
    deleted = delete_key_from_pool(key_value)
    if deleted:
        await message.answer(
            f"✅ Key ကို အောင်မြင်စွာ ဖျက်ပြီးပါပြီ။\n\n`{key_value}`",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
    else:
        await message.answer(
            f"❌ Key မတွေ့ပါ။ ထပ်မံစစ်ဆေးပါ။\n\n`{key_value}`",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )
    await state.clear()

# ===== ADMIN PENDING REQUESTS =====
async def cb_admin_pending(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    requests = get_pending_requests()
    if not requests:
        await callback.answer("Pending requests မရှိပါ", show_alert=True)
        return
    for req in requests:
        await callback.message.answer(
            f"💰 <b>Credit Request</b>\n"
            f"👤 User ID: <code>{req['user_id']}</code>\n"
            f"💰 Amount: <b>{req['amount']} Credits</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="✅ Approve", callback_data=f"apv_req_{req['$id']}"),
                InlineKeyboardButton(text="❌ Reject", callback_data=f"rej_req_{req['$id']}")
            ]])
        )

async def cb_approve_req(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    doc_id = callback.data.replace("apv_req_", "")
    user_id, amount = approve_credit_request(doc_id)
    if user_id:
        await callback.answer(f"✅ {amount} Credits ထည့်ပြီ!")
        await callback.message.edit_reply_markup(reply_markup=None)
        try:
            await callback.bot.send_message(user_id, f"✅ <b>Credits ရောက်ပြီ!</b>\n\n💰 <b>{amount} Credits</b> ထည့်ပြီးပါပြီ!", parse_mode="HTML")
        except:
            pass

async def cb_reject_req(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    doc_id = callback.data.replace("rej_req_", "")
    reject_credit_request(doc_id)
    await callback.answer("❌ Rejected!")
    await callback.message.edit_reply_markup(reply_markup=None)

async def cb_approve_direct(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    parts = callback.data.split("_")
    uid = int(parts[1])
    amt = int(parts[2])
    add_credits(uid, amt)
    await callback.answer(f"✅ {amt} Credits ထည့်ပြီ!")
    await callback.message.edit_reply_markup(reply_markup=None)
    try:
        await callback.bot.send_message(uid, f"✅ <b>Credits ရောက်ပြီ!</b>\n\n💰 <b>{amt} Credits</b> ထည့်ပြီးပါပြီ!", parse_mode="HTML")
    except:
        pass

# ===== ADMIN BROADCAST =====
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text("📢 Broadcast message ကို ရိုက်ထည့်ပါ:")
    await state.set_state(AdminState.broadcast)

async def admin_broadcast_msg(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    await state.clear()
    users = get_all_users()
    sent, failed = 0, 0
    for user in users:
        try:
            await message.bot.send_message(
                user["user_id"],
                f"📢 <b>Announcement</b>\n━━━━━━━━━━━━━━━━\n{message.text}",
                parse_mode="HTML"
            )
            sent += 1
        except:
            failed += 1
    await message.answer(f"✅ Broadcast ပြီ!\n✅ Sent: {sent}\n❌ Failed: {failed}", reply_markup=admin_keyboard())

# ===== REGISTER HANDLERS =====
def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_admin, Command("admin"))

    dp.callback_query.register(cb_back_main, F.data == "back_main")
    dp.callback_query.register(cb_user_info, F.data == "user_info")
    dp.callback_query.register(cb_register, F.data == "register")
    dp.callback_query.register(cb_refer, F.data == "refer")
    dp.callback_query.register(cb_generate_key, F.data == "generate_key")
    dp.callback_query.register(cb_gen_outline, F.data == "gen_outline")
    dp.callback_query.register(cb_gen_v2ray, F.data == "gen_v2ray")
    dp.callback_query.register(cb_my_keys, F.data == "my_keys")
    dp.callback_query.register(cb_server_status, F.data == "server_status")
    dp.callback_query.register(cb_buy_credits, F.data == "buy_credits")

    dp.message.register(register_name, RegisterState.waiting_name)
    dp.message.register(buy_credits_amount, BuyCreditsState.waiting_amount)
    dp.message.register(admin_collect_keys, AdminState.add_outline)
    dp.message.register(admin_collect_keys, AdminState.add_v2ray)
    dp.message.register(admin_delete_key_handler, AdminState.delete_key)   # NEW
    dp.message.register(admin_broadcast_msg, AdminState.broadcast)

    dp.callback_query.register(cb_admin_back, F.data == "admin_back")
    dp.callback_query.register(cb_admin_stats, F.data == "admin_stats")
    dp.callback_query.register(cb_admin_add_outline, F.data == "admin_add_outline")
    dp.callback_query.register(cb_admin_add_v2ray, F.data == "admin_add_v2ray")
    dp.callback_query.register(cb_admin_delete_key, F.data == "admin_delete_key")   # NEW
    dp.callback_query.register(cb_admin_pending, F.data == "admin_pending")
    dp.callback_query.register(cb_admin_broadcast, F.data == "admin_broadcast")
    dp.callback_query.register(cb_approve_req, F.data.startswith("apv_req_"))
    dp.callback_query.register(cb_reject_req, F.data.startswith("rej_req_"))
    dp.callback_query.register(cb_approve_direct, F.data.startswith("apv_"))
