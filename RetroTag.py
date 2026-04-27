from aiogram.filters import Command
from aiogram import F

import logging
import asyncio
import os
from datetime import datetime ,timedelta
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest, TelegramNotFound
from motor .motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from tenacity import retry ,stop_after_attempt ,wait_exponential
import html

TOKEN = "8570750717:AAHiO9Y_2ATnY5VrdyK07BZ7gkVhf07Wu3M"
OWNER_ID = 8557740388
BOT_ID = int(TOKEN.split(':')[0]) if TOKEN else None
BOT_USERNAME = "RetroTagBot"
MONGODB_URI = "mongodb+srv://sarkis05082008_db_user:A105KVUQrNjukToq@cluster0.zfxjgi1.mongodb.net/?appName=Cluster0"
DB_NAME = "RetroTag"


logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

client =None
db =None

users =None
history =None
chats =None
whitelist =None
privacy_log =None
user_languages =None
premium_subscriptions =None
promo_codes =None
chat_languages =None

api_queue =None

LOCALES ={
'ru':{
'need_subscribe':'✉️ Для поиска подпишитесь на канал новостей бота и нажмите кнопку проверки подписки.',
'check_sub_ok':'🎉',
'check_sub_not':'❌ Подписка не обнаружена. Пожалуйста, подпишитесь и нажмите «Проверить подписку».',
'start':"""<b>🎯 RetroTag</b>

<b>📋 Команды:</b>
• /me — твоя история 📜
• /id — твой ID 🆔
• /lang — изменить язык 🌍
• /premium — покупка Premium подписки ⭐

<b>📝 Как использовать:</b>
• Пришли <code>@username</code> или <code>ID</code> — получишь историю 📊
<i>🔒 Все сообщения защищены от пересылки и копирования</i>

Новые промокоды в канале новостей: @NewsRetro — подпишитесь, чтобы первым получать промокоды.""",
'choose_lang':'🌍 Выберите язык / Choose language:',
    'news_channel_button':'🔗 Канал',
    'check_sub_button':'✅ Проверить подписку',
    'promo_announce_channel':'🎉 <b>Новый промокод!</b>\n🔑 Промокод: <code>{code}</code>\n👥 Активаций: {max_uses}\n⭐ Бонус:{premium_days} дней Premium\n📝 Как активировать: отправьте боту <code>/promo {code}</code>',
    'start_pro':"""<b>🎯 RetroTag — PRO</b>

<b>📋 Команды:</b>
• /users — статистика базы 📊
• /pro — список PRO пользователей ⭐
• /list — Premium пользователи ⭐
• /add — повысить пользователя до PRO ⭐
• /dell — понизить пользователя 👤
• /cleardb — очистить базу данных 🗑️
• /premium — Добавить Premium подписку ⭐
• /chats — список чатов
• /codes — статистика промокодов
• /broadcast — рассылка сообщение всем чатам
• /addpromo — создать промокод ⭐""",

'lang_set':'✅ Язык успешно установлен!',
'user_not_found':'👤 Пользователь не найден ❌',
'history_empty':'📜 <b>История пользователя</b> <code>{}</code>\n\n<b>📭 История пуста</b>',
'history_title':'📜 <b>История пользователя</b> <code>{}</code>',
'names':'👥 <b>Имена:</b>',
'usernames':'👤 <b>Usernames:</b>',
'pro_status':'⭐ <b>PRO</b>',
'normal_status':'',
'data_hidden':'👤 Пользователь не найден',
'chat_id':'🆔 ID чата:',
'id_cmd':'ID:',
'username_label':'Username:',
'pro_promoted':'✅ <b>Пользователь повышен до PRO статуса:</b> ⭐',
'pro_demoted':'✅ <b>Пользователь понижен до Обычного статуса:</b> 👤',
'stats_updated':'📊 <b>Обновленная статистика:</b>',
'total_users':'👥 <b>Всего пользователей:</b>',
'pro_users':'⭐ <b>PRO пользователи:</b>',
'normal_users':'👤 <b>Обычные пользователи:</b>',
'premium_users_count':'👥 <b>Premium пользователи:</b>',
'error':'❌ Ошибка',
'example_add':'Пример: <code>/add 123456789</code>',
'example_dell':'Пример: <code>/dell 123456789</code>',
'no_pro_users':'⭐ PRO пользователей нет 📭',
'pro_users_list':'⭐ <b>PRO пользователи:</b>',
'unavailable':'недоступен ❌',
'no_group_chats':'💬 Чатов в базе нет 📭',
'group_chats':'💬 <b>Чаты</b>:',
'channel':'👥 Группа',
'group':'👥 Группа',
'private':'👤 Личный',
'no_title':'Без названия',
'stats_title':'📊 <b>Статистика базы данных</b>',
'view_table':'✨ База данных',
'db_cleared':'🗑️ <b>База данных полностью очищена!</b> ✅',
'all_data_deleted':'<b>Все данные удалены:</b>',
'users_deleted':'• <i>Пользователи</i> 👥',
'history_deleted':'• <i>История</i> 📜',
'chats_deleted':'• <i>Чаты</i> 💬',
'whitelist_deleted':'• <i>PRO пользователи</i> ⭐',
'changes':'<b>Изменения</b>:',
'forwarded_from':'📩 <b>Переслано от: </b>',
'no_username':'<i> </i>',
'broadcast_text_required':'❌ <b>Укажи текст</b>',
'broadcast_completed':'✅ <b>Рассылка завершена</b> 📢',
'delivered_to':'📨 Доставлено в {} из {} чатов',
'welcome_title':'🎉✨ <b>Спасибо, что добавили меня в этот чат!</b> ✨🎉',
'welcome_capabilities':'🤖 <b>Мои возможности:</b>',
'welcome_track':'• <i>Автоматическое отслеживание пользователей</i> 👥',
'welcome_monitor':'• <i>Мониторинг изменений в профилях</i> 📊',
'welcome_protect':'• <i>Защита от нежелательных пользователей</i> 🔒',
'welcome_commands':'📋 <b>Доступные команды:</b>',
'welcome_chatid':'• /chatid — показать ID этого чата',
'welcome_chat_id':'💡 <b>ID чата:</b>',
'welcome_admin_warning':'⚠️ <b>Внимание:</b> Для полной функциональности рекомендуется назначить бота администратором.',
'add_to_chats':'Добавить в свой чат',
'deleted_account':'👻 <b>Удалённый аккаунт</b>',
'returned':'<b>вернулся в чат</b> ✨',
'left':'<b>покинул чат</b> 👋',
'premium_title':'⭐ <b>Premium подписка</b> 💎',
'premium_description':'✨ Приобретите Premium подписку, чтобы скрыть вашу информацию от других пользователей.\n\n🔒 <b>Преимущества:</b>\n• Полная приватность данных\n• Защита от отслеживания\n• Приоритетная поддержка',
'premium_24h':'⏰ 24 часа',
'premium_1month':'📅 1 месяц',
'premium_3months':'📆 3 месяца',
'premium_1year':'🎊 1 год',
'premium_close':'❌ Закрыть',
'premium_already':'✅ У вас уже есть активная Premium подписка! 💎',
'premium_success':'🎉✨ <b>Premium подписка успешно активирована!</b> ✨🎉',
'premium_expires':'⏰ Подписка действительна до: <code>{}</code>',
'premium_time_left':'⏰ <b>Оставшееся время Premium:</b>',
'premium_no_active':'ℹ️ У вас нет активной Premium подписки',
'premium_purchase_receipt':'🎉✨ <b>Новая покупка Premium подписки!</b> ✨🎉\n\n👤 <b>Покупатель:</b> {buyer_name}\n🆔 <b>ID:</b> <code>{buyer_id}</code>\n📱 <b>Username:</b> {buyer_username}\n\n⭐ <b>Тариф:</b> {tariff_name}\n⏰ <b>Действительна до:</b> <code>{expires_str}</code>\n\n💎 <i>Пользователь получил Premium статус!</i>',
'premium_stats_title':'⭐ <b>Статистика Premium пользователей</b> 📊',
'premium_users_count':'👥 <b>Premium пользователей:</b>',
'premium_user_info':'👤 <code>{target_id}</code> — {name}\n⏰ До: <code>{expires_str}</code>\n📊 Осталось: <code>{time_left}</code>',
'premium_no_users':'ℹ️ Premium пользователей нет 📭',
'already_pro':'⚠️ <b>Пользователь уже имеет PRO статус!</b> ⭐\n\n<code>{}</code> — {}',
'promo_only_basic':'ℹ️ Эту команду могут использовать только обычные пользователи.',
'promo_usage':'Использование: <code>/promo ПРОМОКОД</code>',
'promo_not_found':'❌ Промокод не найден или его срок действия истёк.',
'promo_limit_reached':'❌ Лимит активаций этого промокода исчерпан.',
'promo_already_used':'ℹ️ Вы уже использовали этот промокод.',
'promo_activated':'🎉 Premium на 7 дней успешно активирован по промокоду!',
'promo_codes_title':'⭐ <b>Статистика промокодов</b>',
'promo_code_stats':'🔑 {code} — {used}/{max_uses} активаций',
'promo_no_codes':'ℹ️ Промокодов ещё нет.',
'promo_created':'✅ Промокод создан:\n🔑 <code>{code}</code>\n👥 Активаций: {max_uses}\n⏰ Premium: 7 дней',
'promo_invalid_format':'❌ Неверный формат. Использование: <code>/addpromo ПРОМОКОД</code> (без пробелов)',
},
'en':{
'need_subscribe':'✉️ To use search, please subscribe to the bot news channel and press the check subscription button.',
'check_sub_ok':'🎉',
'check_sub_not':'❌ Subscription not found. Please subscribe and press "Check subscription".',
'start':"""<b>🎯 RetroTag</b>

<b>📋 Commands:</b>
• /me — your history 📜
• /id — your ID 🆔
• /lang — change language 🌍
• /premium — buy Premium subscription ⭐

<b>📝 How to use:</b>
• Send <code>@username</code> or <code>ID</code> — get history 📊
<i>🔒 All messages are protected from forwarding and copying</i>

New promo codes in the news channel: @NewsRetro — subscribe to receive promo codes first.""",
'choose_lang':'🌍 Choose language / Выберите язык:',
    'start_pro':"""<b>🎯 RetroTag — PRO</b>

<b>📋 PRO Commands:</b>
• /users — database statistics 📊
• /list — Premium users ⭐
• /pro — PRO users list ⭐
• /add — promote user to PRO ⭐
• /dell — demote user 👤
• /cleardb — clear database 🗑️
• /premium — Add Premium subscription ⭐
• /chats — chat list
• /codes — promo codes statistics
• /broadcast — broadcast message to all chats
• /addpromo — create promo code ⭐
• /promo — promo code activation ⭐""",
'lang_set':'✅ Language successfully set!',
'user_not_found':'👤 User not found ❌',
'history_empty':'📜 <b>User history</b> <code>{}</code> <i>({})</i>\n\n<b>📭 History is empty</b>',
'history_title':'📜 <b>User history</b> <code>{}</code> <i>({})</i>',
'names':'👥 <b>Names:</b>',
'usernames':'👤 <b>Usernames:</b>',
'pro_status':'⭐ <b>PRO</b>',
'normal_status':'',
'data_hidden':'👤 User not found',
'chat_id':'🆔 Chat ID:',
'id_cmd':'ID:',
'username_label':'Username:',
'pro_promoted':'✅ <b>User promoted to PRO status:</b> ⭐',
'pro_demoted':'✅ <b>User demoted to Basic status:</b> 👤',
'stats_updated':'📊 <b>Updated statistics:</b>',
'total_users':'👥 <b>Total users:</b>',
'pro_users':'⭐ <b>PRO users:</b>',
'normal_users':'👤 <b>Basic users:</b>',
'premium_users_count':'👥 <b>Premium users:</b>',
'error':'❌ Error',
'example_add':'Example: <code>/add 123456789</code>',
'example_dell':'Example: <code>/dell 123456789</code>',
'no_pro_users':'⭐ No PRO users 📭',
'pro_users_list':'⭐ <b>PRO users:</b>',
'unavailable':'unavailable ❌',
'no_group_chats':'💬 No chats in database 📭',
'group_chats':'💬 <b>Chats</b>:',
'channel':'👥 Group',
'group':'👥 Group',
'private':'👤 Private',
'no_title':'No title',
'stats_title':'📊 <b>Database statistics</b>',
'view_table':'✨ Database',
'db_cleared':'🗑️ <b>Database completely cleared!</b> ✅',
'all_data_deleted':'<b>All data deleted:</b>',
'users_deleted':'• <i>Users</i> 👥',
'history_deleted':'• <i>History</i> 📜',
'chats_deleted':'• <i>Chats</i> 💬',
'whitelist_deleted':'• <i>PRO users</i> ⭐',
'changes':'<b>Changes</b>:',
'forwarded_from':'📩 <b>Forwarded from: </b>',
'no_username':' ',
'broadcast_text_required':'❌ <b>Specify text</b>',
'broadcast_completed':'✅ <b>Broadcast completed</b> 📢',
'delivered_to':'📨 Delivered to {} of {} chats',
'welcome_title':'🎉✨ <b>Thank you for adding me to this chat!</b> ✨🎉',
'welcome_capabilities':'🤖 <b>My capabilities:</b>',
'welcome_track':'• <i>Automatic user tracking</i> 👥',
'welcome_monitor':'• <i>Monitoring profile changes</i> 📊',
'welcome_protect':'• <i>Protection from unwanted users</i> 🔒',
'welcome_commands':'📋 <b>Available commands:</b>',
'welcome_chatid':'• /chatid — show this chat ID',
'welcome_chat_id':'💡 <b>This chat ID:</b>',
'welcome_admin_warning':'⚠️ <b>Warning:</b> For full functionality, it is recommended to make the bot an administrator.',
'add_to_chats':'Add to your chat',
'deleted_account':'👻 <b>Deleted account</b>',
'returned':'<b>returned to chat</b> ✨',
'left':'<b>left chat</b> 👋',
'premium_title':'⭐ <b>Premium Subscription</b> 💎',
'premium_description':'✨ Purchase a Premium subscription to hide your information from other users.\n\n🔒 <b>Benefits:</b>\n• Complete data privacy\n• Protection from tracking\n• Priority support',
'premium_24h':'⏰ 24 hours',
'premium_1month':'📅 1 month',
'premium_3months':'📆 3 months',
'premium_1year':'🎊 1 year',
'premium_close':'❌ Close',
'premium_already':'✅ You already have an active Premium subscription! 💎',
'premium_success':'🎉✨ <b>Premium subscription successfully activated!</b> ✨🎉',
'premium_expires':'⏰ Subscription valid until: <code>{}</code>',
'premium_time_left':'⏰ <b>Premium time remaining:</b>',
'premium_no_active':'ℹ️ You do not have an active Premium subscription',
'premium_purchase_receipt':'🎉✨ <b>New Premium Subscription Purchase!</b> ✨🎉\n\n👤 <b>Buyer:</b> {buyer_name}\n🆔 <b>ID:</b> <code>{buyer_id}</code>\n📱 <b>Username:</b> {buyer_username}\n\n⭐ <b>Plan:</b> {tariff_name}\n⏰ <b>Valid until:</b> <code>{expires_str}</code>\n\n💎 <i>User received Premium status!</i>',
'premium_stats_title':'⭐ <b>Premium Users Statistics</b> 📊',
'premium_users_count':'👥 <b>Premium users:</b>',
'premium_user_info':'👤 <code>{target_id}</code> — {name}\n⏰ Until: <code>{expires_str}</code>\n📊 Left: <code>{time_left}</code>',
'premium_no_users':'ℹ️ No Premium users 📭',
'already_pro':'⚠️ <b>User already has PRO status!</b> ⭐\n\n<code>{}</code> — {}',
'promo_only_basic':'ℹ️ This command can be used only by basic users.',
'promo_usage':'Usage: <code>/promo PROMOCODE</code>',
'promo_not_found':'❌ Promo code not found or expired.',
'promo_limit_reached':'❌ This promo code has reached its activation limit.',
'promo_already_used':'ℹ️ You have already used this promo code.',
'promo_activated':'🎉 Premium for 7 days has been activated with the promo code!',
'promo_codes_title':'⭐ <b>Promo codes statistics</b>',
'promo_code_stats':'🔑 <code>{code}</code> — {used}/{max_uses} activations, creator: <code>{creator_id}</code>, created: <code>{created_at}</code>',
'promo_no_codes':'ℹ️ There are no promo codes yet.',
'promo_created':'✅ Promo code created:\n🔑 <code>{code}</code>\n👥 Activations: {max_uses}\n⏰ Premium: 7 days',
'promo_invalid_format':'❌ Invalid format. Usage: <code>/addpromo PROMOCODE</code> (no spaces)',
'news_channel_button':'🔗 Channel',
'check_sub_button':'✅ Check subscription',
'promo_announce_channel':'🎉 <b>New promo code!</b>\n🔑 Code: <code>{code}</code>\n👥 Uses: {max_uses}\n⭐ Bonus: {premium_days} days Premium\n📝 How to activate: send to the bot <code>/promo {code}</code>',
'codes_no_access':'',
}
}

async def get_user_language (user_id :int )->str :
    try :
        lang_doc =await user_languages .find_one ({"user_id":user_id })
        return lang_doc .get ("language","ru")if lang_doc else "ru"
    except :
        return "ru"

async def set_user_language (user_id :int ,language :str ):
    try :
        await user_languages .update_one (
        {"user_id":user_id },
        {"$set":{"language":language }},
        upsert =True
        )
    except :
        pass

async def get_text (key :str ,user_id :int =None ,language :str =None ,**kwargs )->str :
    if language :
        lang =language
    elif user_id :
        lang =await get_user_language (user_id )
    else :
        lang ="ru"

    text =LOCALES .get (lang ,LOCALES ['ru']).get (key ,key )
    if kwargs :
        try :
            if '{}'in text or '{0}'in text :
                values =list (kwargs .values ())
                return text .format (*values )
            else :
                return text .format (**kwargs )
        except Exception as e :
            logging .warning (f"Ошибка форматирования текста {key}: {e}")
            return text
    return text

async def api_rate_limiter ():
    while True :
        try :
            await api_queue .put (True )
            await asyncio .sleep (1 /50 )
        except :
            pass

@retry (stop =stop_after_attempt (5 ),wait =wait_exponential (multiplier =1 ,min =2 ,max =10 ))
async def safe_api_call (func ,*args ,**kwargs ):
    await api_queue .get ()
    try :
        return await func (*args ,**kwargs )
    except (TelegramRetryAfter, TelegramNotFound) as e :
        if isinstance (e ,TelegramRetryAfter ):
            await asyncio .sleep (e .retry_after )
            return await func (*args ,**kwargs )
        raise
    except TelegramBadRequest as e :
        error_str =str (e ).lower ()
        if "user_not_participant"in error_str or "user not found"in error_str or "chat not found"in error_str :
            raise Exception ("User not found or not a chat participant")
        if "user is deactivated"in error_str or "user is deleted"in error_str :
            raise Exception ("User is deactivated or deleted")
        raise
    except Exception as e :
        if "timeout"in str (e ).lower ()or "connection"in str (e ).lower ():
            raise Exception ("Connection timeout or error")
        raise
    finally :
        api_queue .task_done ()

async def init_db ():
    await users .create_index ("user_id",unique =True )
    await history .create_index ([("user_id",ASCENDING ),("date",ASCENDING )])
    await chats .create_index ("chat_id",unique =True )
    await whitelist .create_index ("user_id",unique =True )
    await privacy_log .create_index ([("viewer_id",ASCENDING ),("target_id",ASCENDING ),("timestamp",ASCENDING )])
    await user_languages .create_index ("user_id",unique =True )
    await premium_subscriptions .create_index ("user_id",unique =True )
    await premium_subscriptions .create_index ("expires_at")

    try :
        await db ["promo_codes"].create_index ("code",unique =True )
        await db ["promo_codes"].create_index ("creator_id")
    except :
        pass

    try:
        await db["pending_searches"].create_index("user_id", unique=True)
    except:
        pass

    await chat_languages .create_index ("chat_id",unique =True )

    try :
        await whitelist .update_one (
        {"user_id":OWNER_ID },
        {"$set":{"user_id":OWNER_ID }},
        upsert =True
        )
        await users .update_one (
        {"user_id":OWNER_ID },
        {"$set":{"is_pro":True }},
        upsert =True
        )
    except :
        pass

async def is_whitelisted (uid :int )->bool :
    try :
        result =await whitelist .find_one ({"user_id":uid })is not None
        return result
    except :
        return False

async def is_owner_or_pro (uid :int )->bool :
    if uid ==OWNER_ID :
        return True

    return await is_whitelisted (uid )

async def has_active_premium (uid :int )->bool :
    try :
        premium_doc =await premium_subscriptions .find_one ({"user_id":uid })
        if not premium_doc :
            return False
        expires_at =premium_doc .get ("expires_at")
        if expires_at and expires_at >datetime .now ():
            return True
        return False
    except :
        return False

async def get_premium_expires_at (uid :int )->datetime :
    try :
        premium_doc =await premium_subscriptions .find_one ({"user_id":uid })
        if premium_doc :
            return premium_doc .get ("expires_at")
        return None
    except :
        return None

async def log_privacy_access (viewer_id :int ,target_id :int ):
    if viewer_id !=target_id and viewer_id !=OWNER_ID :
        try :
            await privacy_log .insert_one ({
            "viewer_id":viewer_id ,
            "target_id":target_id ,
            "timestamp":datetime .now ()
            })
        except :
            pass

async def get_user_from_api (user_identifier )->types .User :
    try :
        user_info =await safe_api_call (bot .get_chat ,user_identifier )
        return types .User (
        id =user_info .id ,
        is_bot =user_info .type =='bot',
        first_name =user_info .first_name or '',
        last_name =user_info .last_name or '',
        username =user_info .username ,
        language_code =None ,
        is_premium =None ,
        added_to_attachment_menu =None ,
        can_join_groups =None ,
        can_read_all_group_messages =None ,
        supports_inline_queries =None
        )
    except Exception as e :
        error_msg =str (e ).lower ()
        if "not found"in error_msg or "user not found"in error_msg :
            raise Exception ("User not found")
        if "deactivated"in error_msg or "deleted"in error_msg :
            raise Exception ("User is deactivated or deleted")
        if "timeout"in error_msg or "connection"in error_msg :
            raise Exception ("Connection error")
        raise Exception (f"Failed to get user info: {str(e)}")

async def save_user (user :types .User ,skip_history_check =False ):
    if user .id ==BOT_ID or (hasattr (user ,'is_bot')and user .is_bot ):
        return []

    now =datetime .now ().strftime ("%d.%m.%Y %H:%M")
    first_name =user .first_name or ""
    last_name =user .last_name or ""
    name =f"{first_name} {last_name}".strip ()
    un =user .username or ""
    is_pro =await is_whitelisted (user .id )or await has_active_premium (user .id )or user .id ==OWNER_ID

    existing =await users .find_one ({"user_id":user .id })
    changes =[]

    if existing :
        old_name =f"{existing.get('first_name','')} {existing.get('last_name','')}".strip ()
        old_un =existing .get ("username")or ""

        await users .update_one (
        {"user_id":user .id },
        {"$set":{"first_name":first_name ,"last_name":last_name ,"username":un ,"last_seen":now ,"is_pro":is_pro }}
        )

        if not is_pro or skip_history_check :
            if name !=old_name and name :
                last_name_record =await history .find_one (
                {"user_id":user .id ,"type":"name"},
                sort =[("date",-1 )]
                )
                if not last_name_record or last_name_record .get ("value")!=name :
                    await history .insert_one ({"user_id":user .id ,"type":"name","value":name ,"date":now })
                    changes .append (f"🚀 Имя: {old_name or ' '} → {name}")

            if un !=old_un :
                last_un_record =await history .find_one (
                {"user_id":user .id ,"type":"username"},
                sort =[("date",-1 )]
                )
                if not last_un_record or last_un_record .get ("value")!=un :
                    await history .insert_one ({"user_id":user .id ,"type":"username","value":un ,"date":now })
                    if un :
                        changes .append (f"👤 Username: {old_un or ' '} → <b>@{un}</b>")
                    else :
                        changes .append (f"👤 Username: {old_un} →")
    else :
        await users .insert_one ({
        "user_id":user .id ,"first_name":first_name ,"last_name":last_name ,
        "username":un ,"last_seen":now ,"is_pro":is_pro
        })
        if not is_pro :
            if name :await history .insert_one ({"user_id":user .id ,"type":"name","value":name ,"date":now })
            if un :await history .insert_one ({"user_id":user .id ,"type":"username","value":un ,"date":now })

    return changes

async def save_chat (chat :types .Chat ):
    is_new =await chats .find_one ({"chat_id":chat .id })is None
    await chats .update_one (
    {"chat_id":chat .id },
    {"$set":{"title":chat .title or "Личный чат","type":chat .type }},
    upsert =True
    )
    if is_new and chat .type in ['group','supergroup']:
        asyncio .create_task (collect_chat_members (chat .id ))

async def collect_chat_members (chat_id :int ):
    try :
        try :
            bot_member =await bot .get_chat_member (chat_id ,BOT_ID )
            if bot_member .status not in ['administrator','creator']:
                pass
        except :
            pass

        try :
            admins =await safe_api_call (bot .get_chat_administrators ,chat_id )
            for admin in admins :
                if not (hasattr (admin .user ,'is_bot')and admin .user .is_bot ):
                    await save_user (admin .user )
        except Exception as e :
            logging .warning (f"Ошибка при получении администраторов: {e}")

        try :
            count =await safe_api_call (bot .get_chat_member_count ,chat_id )
            collected_users =set ()
            for offset in range (0 ,min (count ,1000 ),200 ):
                try :
                    break
                except Exception as e :
                    logging .warning (f"Ошибка при сборе участников: {e}")
                    break
        except Exception as e :
            logging .warning (f"Не удалось получить количество участников: {e}")

    except Exception as e :
        logging .error (f"Ошибка при сборе участников чата {chat_id}: {e}")

async def update_all_users ():
    while True :
        try :
            print (f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] 🔄 Начинаю автоматическое обновление базы данных...")
            updated_count =0
            async for user_doc in users .find ({}):
                try :
                    fake_user =await get_user_from_api (user_doc ["user_id"])
                    await save_user (fake_user )
                    updated_count +=1
                    await asyncio .sleep (0.01 )
                except Exception as e :
                    logging .warning (f"Не удалось обновить пользователя {user_doc['user_id']}: {e}")
                    continue

            chat_count =0
            async for chat_doc in chats .find ({"chat_id":{"$lt":0 }}):
                try :
                    await collect_chat_members (chat_doc ["chat_id"])
                    chat_count +=1
                    await asyncio .sleep (0.02 )
                except Exception as e :
                    logging .warning (f"Не удалось обновить чат {chat_doc['chat_id']}: {e}")
                    continue

            print (f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] ✅ Обновление завершено: пользователей обновлено {updated_count}, чатов обработано {chat_count}")
        except Exception as e :
            print (f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] ❌ Ошибка при обновлении: {str(e)}")
        await asyncio .sleep (60 )

def generate_permanent_link (user_id :int )->str :
    return f"https://t.me/+{user_id}"

async def get_history (uid :int ,requester_id :int =None ,user_in_db :bool =True )->str :
    lang =await get_user_language (requester_id )if requester_id else "ru"

    is_pro_whitelist =await is_whitelisted (uid )

    if requester_id ==OWNER_ID :
        pass
    elif is_pro_whitelist and uid !=OWNER_ID and requester_id !=uid :
        return await get_text ("user_not_found",requester_id ,language =lang ,uid =uid )

    if not user_in_db :
        if requester_id !=OWNER_ID and not await is_owner_or_pro (requester_id )and requester_id !=uid :
            return await get_text ("user_not_found",requester_id ,language =lang ,uid =uid )

    user_doc =await users .find_one ({"user_id":uid })
    if not user_doc :
        if await is_owner_or_pro (requester_id )or requester_id ==uid :
            status_text =await get_text ("normal_status",requester_id ,language =lang )
            title_text =await get_text ("history_title",requester_id ,language =lang ,uid =uid ,status =status_text )
            empty_text =await get_text ("history_empty",requester_id ,language =lang ,uid =uid ,status =status_text )
            return title_text +"\n\n<b>"+empty_text .split ("\n\n")[-1 ]+"</b>"
        else :
            return await get_text ("user_not_found",requester_id ,language =lang ,uid =uid )

    is_premium =await has_active_premium (uid )
    is_pro =is_pro_whitelist or is_premium or uid ==OWNER_ID

    if uid ==OWNER_ID :
        user_status =await get_text ("pro_status",requester_id ,language =lang )
    elif is_pro_whitelist :
        user_status =await get_text ("pro_status",requester_id ,language =lang )
    elif is_premium :
        expires_at =await get_premium_expires_at (uid )
        if expires_at :
            now =datetime .now ()
            delta =expires_at -now
            days =delta .days
            hours =delta .seconds //3600
            minutes =(delta .seconds %3600 )//60
            if days >0 :
                premium_info =f"⭐ <b>Premium</b> ({days}д {hours}ч)"if lang =="ru"else f"⭐ <b>Premium</b> ({days}d {hours}h)"
            elif hours >0 :
                premium_info =f"⭐ <b>Premium</b> ({hours}ч {minutes}м)"if lang =="ru"else f"⭐ <b>Premium</b> ({hours}h {minutes}m)"
            else :
                premium_info =f"⭐ <b>Premium</b> ({minutes}м)"if lang =="ru"else f"⭐ <b>Premium</b> ({minutes}m)"
            user_status =premium_info
        else :
            user_status ="⭐ <b>Premium</b>"
    else :
        user_status =await get_text ("normal_status",requester_id ,language =lang )

    await log_privacy_access (requester_id ,uid )

    if requester_id !=OWNER_ID and is_pro and not await is_owner_or_pro (requester_id )and requester_id !=uid :
        return await get_text ("user_not_found",requester_id ,language =lang ,uid =uid )

    pipeline =[
    {"$match":{"user_id":uid }},
    {"$sort":{"date":1 }}
    ]
    cursor =history .aggregate (pipeline )
    rows =await cursor .to_list (length =500 )

    if not rows :

        status_display =user_status if user_status else ""
        return await get_text ("history_empty",requester_id ,language =lang ,uid =uid ,status =status_display )

    status_display =user_status if user_status else ""
    text =await get_text ("history_title",requester_id ,language =lang ,uid =uid ,status =status_display )+"\n\n"

    names =[r for r in rows if r ["type"]=="name"]
    if names :
        text +=f"{await get_text('names', requester_id, language=lang)}\n"
        for i ,r in enumerate (names ,1 ):
            text +=f"<code>{i}.</code> <code>[{r['date']}]</code> <b>{r['value']}</b>\n"
        text +="\n"

    usernames =[r for r in rows if r ["type"]=="username"]
    if usernames :
        text +=f"{await get_text('usernames', requester_id, language=lang)}\n"
        prev =None
        deleted_text ="(deleted)"if lang =="en"else "(удалён)"
        returned_text ="returned"if lang =="en"else "вернул(а)"
        for i ,r in enumerate (usernames ,1 ):
            val =f"@{r['value']}"if r ['value']else deleted_text
            if prev and deleted_text in prev :
                if r ['value']:
                    text +=f"<code>{i}.</code> <code>[{r['date']}]</code> <b>✨ {returned_text} @{r['value']}</b>\n"
                else :
                    text +=f"<code>{i}.</code> <code>[{r['date']}]</code> <s>{val}</s>\n"
            else :
                if r ['value']:
                    text +=f"<code>{i}.</code> <code>[{r['date']}]</code> <b>{val}</b>\n"
                else :
                    text +=f"<code>{i}.</code> <code>[{r['date']}]</code> <s>{val}</s>\n"
            prev =val

    return text

async def resolve_user (identifier :str ,from_user_id :int =None )->tuple :
    try :
        if identifier .isdigit ():
            uid =int (identifier )
            user_doc =await users .find_one ({"user_id":uid })
            if user_doc :
                asyncio .create_task (save_user_from_id (uid ))
                return None ,True

            try :
                api_user =await get_user_from_api (uid )
                await save_user (api_user )
                return api_user ,True
            except :
                return None ,False

        elif identifier .startswith ("@"):
            username_query =identifier [1 :].lower ().strip ()
            if not username_query :
                return None ,False

            user_doc =await users .find_one ({
            "username":{"$regex":f"^{username_query}$","$options":"i"}
            })

            if user_doc :
                user_id =user_doc ["user_id"]
                asyncio .create_task (save_user_from_id (user_id ))
                return None ,True

            return None ,False

        return None ,False
    except Exception as e :
        logging .error (f"Ошибка при разрешении пользователя {identifier}: {e}")
        return None ,False

async def save_user_from_id (user_id :int ):
    try :
        api_user =await get_user_from_api (user_id )
        await save_user (api_user )
    except :
        pass

@dp.message(Command("start"))
async def start (m :types .Message ):
    """Обработчик команды /start"""
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return

    if m .chat .type !='private':
        return

    lang =await get_user_language (m .from_user .id )
    lang_doc =await user_languages .find_one ({"user_id":m .from_user .id })
    if not lang_doc :
        keyboard =InlineKeyboardMarkup ()
        keyboard .add (InlineKeyboardButton ("🇷🇺 Русский",callback_data ="lang_ru"))
        keyboard .add (InlineKeyboardButton ("🇬🇧 English",callback_data ="lang_en"))
        await m .answer (await get_text ("choose_lang", user_id=m.from_user.id, language=lang ), reply_markup =keyboard ,protect_content =True )
        return

    if not await is_whitelisted (m .from_user .id ):
        await save_user (m .from_user )
    await save_chat (m .chat )

    bot_username = (await bot.get_me()).username
    add_button = InlineKeyboardButton(
        text="➕ " + await get_text("add_to_chats", user_id=m.from_user.id, language=lang),
        url=f"https://t.me/{bot_username}?startgroup=true"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[add_button]])

    is_pro_user = await is_owner_or_pro(m.from_user.id)
    start_key = "start_pro" if is_pro_user else "start"

    await m .answer (
    await get_text (start_key, user_id=m.from_user.id, language=lang ),
    reply_markup =keyboard ,
    protect_content =True
    )

@dp.callback_query(lambda c: c.data.startswith('lang_'))
async def set_language (callback_query :types .CallbackQuery ):
    """Обработчик выбора языка"""
    if hasattr (callback_query .from_user ,'is_bot')and callback_query .from_user .is_bot :
        return

    lang =callback_query .data .split ('_')[1 ]
    await set_user_language (callback_query .from_user .id ,lang )
    await callback_query .answer (await get_text ("lang_set",callback_query .from_user .id ,language =lang ))

    try :
        await bot .delete_message (callback_query .message .chat .id ,callback_query .message .message_id )
    except :
        pass

    if not await is_whitelisted (callback_query .from_user .id ):
        await save_user (callback_query .from_user )
    await save_chat (callback_query .message .chat )

    bot_username = (await bot.get_me()).username
    add_button = InlineKeyboardButton(
        text="➕ " + (await get_text("add_to_chats", callback_query.from_user.id) if lang == "en" else "Добавить в свой чат"),
        url=f"https://t.me/{bot_username}?startgroup=true"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[add_button]])

    await bot .send_message (
    callback_query .from_user .id ,
    await get_text ("start",callback_query .from_user .id ,language =lang ),
    reply_markup =keyboard ,
    protect_content =True
    )

@dp.message(Command("lang"))
async def lang_cmd (m :types .Message ):
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return
    lang =await get_user_language (m .from_user .id )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
        ]
    )
    await m .answer (await get_text ("choose_lang",m .from_user .id ,language =lang ),reply_markup =keyboard ,protect_content =True )

@dp.message(Command("chatid"))
async def chatid (m :types .Message ):
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return

    if m .chat .type =='private':
        lang_doc =await user_languages .find_one ({"user_id":m .from_user .id })
        if not lang_doc :
            keyboard =InlineKeyboardMarkup ()
            keyboard .add (InlineKeyboardButton ("🇷🇺 Русский",callback_data ="lang_ru"))
            keyboard .add (InlineKeyboardButton ("🇬🇧 English",callback_data ="lang_en"))
            await m .answer (await get_text ("choose_lang",m .from_user .id ,language ="ru"),reply_markup =keyboard ,protect_content =True )
            return

    lang =await get_user_language (m .from_user .id )
    await m .answer (f"<b>{await get_text('chat_id', m.from_user.id, language=lang)}</b>\n<code>{m.chat.id}</code>",protect_content =True )

@dp.message(Command("me"))
async def me (m :types .Message ):
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return
    if m .chat .type !='private':
        return

    lang_doc =await user_languages .find_one ({"user_id":m .from_user .id })
    if not lang_doc :
        keyboard =InlineKeyboardMarkup ()
        keyboard .add (InlineKeyboardButton ("🇷🇺 Русский",callback_data ="lang_ru"))
        keyboard .add (InlineKeyboardButton ("🇬🇧 English",callback_data ="lang_en"))
        await m .answer (await get_text ("choose_lang",m .from_user .id ,language ="ru"),reply_markup =keyboard ,protect_content =True )
        return

    was_in_db =await users .find_one ({"user_id":m .from_user .id })is not None
    await save_user (m .from_user )

    lang =await get_user_language (m .from_user .id )
    history_text =await get_history (m .from_user .id ,m .from_user .id ,user_in_db =was_in_db )

    if await has_active_premium (m .from_user .id ):
        expires_at =await get_premium_expires_at (m .from_user .id )
        if expires_at :
            now =datetime .now ()
            delta =expires_at -now
            days =delta .days
            hours =delta .seconds //3600
            minutes =(delta .seconds %3600 )//60

            if days >365 *30 :
                time_left ="∞"
                expires_str =None
            elif days >0 :
                time_left =f"{days}д {hours}ч {minutes}м"if lang =="ru"else f"{days}d {hours}h {minutes}m"
            elif hours >0 :
                time_left =f"{hours}ч {minutes}м"if lang =="ru"else f"{hours}h {minutes}m"
            else :
                time_left =f"{minutes}м"if lang =="ru"else f"{minutes}m"

            if 'expires_str'not in locals ()or expires_str is not None :
                expires_str =expires_at .strftime ("%d.%m.%Y %H:%M")
            premium_info =f"\n\n{await get_text('premium_time_left', m.from_user.id, language=lang)}\n"
            premium_info +=f"<code>{time_left}</code>\n"
            if expires_str :
                premium_info +=f"📅 {await get_text('premium_expires', m.from_user.id, language=lang, expires_str=expires_str)}"
            history_text +=premium_info

    await m .answer (history_text ,protect_content =True )

@dp.message(Command("id"))
async def id_cmd (m :types .Message ):
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return

    if m .chat .type =='private':
        lang_doc =await user_languages .find_one ({"user_id":m .from_user .id })
        if not lang_doc :
            keyboard =InlineKeyboardMarkup ()
            keyboard .add (InlineKeyboardButton ("🇷🇺 Русский",callback_data ="lang_ru"))
            keyboard .add (InlineKeyboardButton ("🇬🇧 English",callback_data ="lang_en"))
            await m .answer (await get_text ("choose_lang",m .from_user .id ,language ="ru"),reply_markup =keyboard ,protect_content =True )
            return

    lang =await get_user_language (m .from_user .id )
    parts =m .text .split (maxsplit =1 )
    target_user =None
    if len (parts )>1 :
        arg =parts [1 ].strip ()
        if arg .startswith ("@"):
            username_query =arg [1 :].lower ()
            user_doc =await users .find_one ({
            "username":{"$regex":f"^{username_query}$","$options":"i"}
            })
            if user_doc :
                uid =user_doc ["user_id"]
                txt =f"<b>🆔 {await get_text('id_cmd', m.from_user.id, language=lang)}</b> <code>{uid}</code>"
                await m .answer (txt ,protect_content =True )
                return
            else :
                not_found_text ="Пользователь не найден:"if lang =="ru"else "User not found:"
                await m .answer (f"<b>❌ {not_found_text}</b> <code>{arg}</code>",protect_content =True )
                return
    if m .reply_to_message and m .reply_to_message .from_user :
        target_user =m .reply_to_message .from_user
    else :
        target_user =m .from_user
    txt =f"<b>🆔 {await get_text('id_cmd', m.from_user.id, language=lang)}</b> <code>{target_user.id}</code>"
    if target_user .username :
        txt +=f"\n<b>👤 {await get_text('username_label', m.from_user.id, language=lang)}</b> <code>@{target_user.username}</code>"
    await m .answer (txt ,protect_content =True )

@dp.message(Command("stop"))
async def stop_premium (m :types .Message ):
    """Отмена Premium / lifetime Premium для указанного пользователя: /stop <id>"""
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return
    if m .chat .type !='private':
        return

    if not await is_owner_or_pro (m .from_user .id ):
        return

    lang_doc =await user_languages .find_one ({"user_id":m .from_user .id })
    if not lang_doc :
        keyboard =InlineKeyboardMarkup ()
        keyboard .add (InlineKeyboardButton ("🇷🇺 Русский",callback_data ="lang_ru"))
        keyboard .add (InlineKeyboardButton ("🇬🇧 English",callback_data ="lang_en"))
        await m .answer (await get_text ("choose_lang",m .from_user .id ,language ="ru"),reply_markup =keyboard ,protect_content =True )
        return
    lang =await get_user_language (m .from_user .id )

    parts =m .text .split (maxsplit =1 )
    if len (parts )<2 :
        usage ="Использование: /stop 123456789"if lang =="ru"else "Usage: /stop 123456789"
        await m .answer (usage ,protect_content =True )
        return

    try :
        uid =int (parts [1 ])
    except ValueError :
        usage ="Использование: /stop 123456789"if lang =="ru"else "Usage: /stop 123456789"
        await m .answer (usage ,protect_content =True )
        return

    await premium_subscriptions .delete_one ({"user_id":uid })

    if uid !=OWNER_ID and not await is_whitelisted (uid ):
        await users .update_one (
        {"user_id":uid },
        {"$set":{"is_pro":False }},
        upsert =True
        )

    try :
        uinfo =await bot .get_chat (uid )
        uname =html .escape (uinfo .full_name or f"ID: {uid}")
    except :
        uname =f"ID: {uid}"

    if lang =="ru":
        txt =f"⏹ <b>Premium / бессрочный Premium отключён для пользователя:</b>\n<code>{uid}</code> — {uname}"
    else :
        txt =f"⏹ <b>Premium / lifetime Premium disabled for user:</b>\n<code>{uid}</code> — {uname}"
    await m .answer (txt ,protect_content =True )

@dp.message(Command("addpromo"))
async def add_promo (m :types .Message ):
    """Создание промокода PRO пользователями: /addpromo CODE"""
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return
    if m .chat .type !='private':
        return
    if not await is_owner_or_pro (m .from_user .id ):
        return

    lang =await get_user_language (m .from_user .id )
    parts =m .text .split (maxsplit =1 )
    if len (parts )<2 :
        await m .answer (await get_text ('promo_invalid_format',m .from_user .id ,language =lang ),protect_content =True )
        return

    code =parts [1 ].strip ()

    if not code or " "in code :
        await m .answer (await get_text ('promo_invalid_format',m .from_user .id ,language =lang ),protect_content =True )
        return

    try :
        promo_doc ={
        "code":code ,
        "creator_id":m .from_user .id ,
        "created_at":datetime .now (),
        "max_uses":10 ,
        "used_count":0 ,
        "used_by":[],
        "premium_days":7
        }
        await db ["promo_codes"].insert_one (promo_doc )

        text =await get_text (
        'promo_created',
        m .from_user .id ,
        language =lang ,
        code =code ,
        max_uses =promo_doc ["max_uses"]
        )
        await m .answer (text ,protect_content =True )
        # Publish bilingual announcement in the news channel and store message id
        try:
            global BOT_USERNAME
            if not BOT_USERNAME:
                me = await bot.get_me()
                BOT_USERNAME = me.username

            created_at_str = promo_doc["created_at"].strftime("%d.%m.%Y %H:%M") if isinstance(promo_doc.get("created_at"), datetime) else str(promo_doc.get("created_at"))
            ru_text = await get_text('promo_announce_channel', m.from_user.id, language='ru', code=code, used=0, max_uses=promo_doc['max_uses'], premium_days=promo_doc['premium_days'], creator_id=m.from_user.id, created_at=created_at_str)
            en_text = await get_text('promo_announce_channel', m.from_user.id, language='en', code=code, used=0, max_uses=promo_doc['max_uses'], premium_days=promo_doc['premium_days'], creator_id=m.from_user.id, created_at=created_at_str)
            full_text = ru_text + "\n\n" + en_text
            btn_bot = await get_text('🤖RetroTag', m.from_user.id)
            bot_link = f"https://t.me/{BOT_USERNAME}" if BOT_USERNAME else "https://t.me/NewsRetro"
            kb = InlineKeyboardMarkup(row_width=1)
            kb.add(InlineKeyboardButton(text=f"{btn_bot}", url=bot_link))
            try:
                msg = await bot.send_message("@NewsRetro", full_text, reply_markup=kb, disable_web_page_preview=True, protect_content=True)
                await db['promo_codes'].update_one({'code': code}, {'$set': {'announce_channel': '@NewsRetro', 'announce_message_id': msg.message_id}})
            except Exception as e:
                logging.warning(f"Не удалось опубликовать промокод в канале новостей: {e}")
        except Exception:
            pass
    except Exception as e :

        if "duplicate key"in str (e ).lower ():
            await m .answer ("❌ Такой промокод уже существует.",protect_content =True )
        else :
            await m .answer (f"❌ Ошибка при создании промокода.\n<code>{html.escape(str(e))}</code>",protect_content =True )

@dp.message(Command("promo"))
async def activate_promo (m :types .Message ):
    """Активация промокода обычными пользователями: /promo CODE"""
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return
    if m .chat .type !='private':
        return

    lang =await get_user_language (m .from_user .id )

    if await is_owner_or_pro (m .from_user .id ):
        await m .answer (await get_text ('promo_only_basic',m .from_user .id ,language =lang ),protect_content =True )
        return

    parts =m .text .split (maxsplit =1 )
    if len (parts )<2 :
        await m .answer (await get_text ('promo_usage',m .from_user .id ,language =lang ),protect_content =True )
        return

    code =parts [1 ].strip ()
    if not code :
        await m .answer (await get_text ('promo_usage',m .from_user .id ,language =lang ),protect_content =True )
        return

    promo_doc =await db ["promo_codes"].find_one ({"code":code })
    if not promo_doc :
        await m .answer (await get_text ('promo_not_found',m .from_user .id ,language =lang ),protect_content =True )
        return

    max_uses =promo_doc .get ("max_uses",10 )
    used_count =promo_doc .get ("used_count",0 )
    used_by =promo_doc .get ("used_by",[])

    if used_count >=max_uses :
        await m .answer (await get_text ('promo_limit_reached',m .from_user .id ,language =lang ),protect_content =True )
        return

    if m .from_user .id in used_by :
        await m .answer (await get_text ('promo_already_used',m .from_user .id ,language =lang ),protect_content =True )
        return

    days =promo_doc .get ("premium_days",7 )
    now =datetime .now ()
    add_delta =timedelta (days =days )

    current_premium =await premium_subscriptions .find_one ({"user_id":m .from_user .id })
    if current_premium and current_premium .get ("expires_at")and current_premium .get ("expires_at")>now :
        new_expires_at =current_premium .get ("expires_at")+add_delta
        await premium_subscriptions .update_one (
        {"user_id":m .from_user .id },
        {"$set":{"expires_at":new_expires_at ,"last_payment":now }}
        )
    else :
        new_expires_at =now +add_delta
        await premium_subscriptions .update_one (
        {"user_id":m .from_user .id },
        {
        "$set":{
        "user_id":m .from_user .id ,
        "expires_at":new_expires_at ,
        "created_at":now ,
        "last_payment":now
        }
        },
        upsert =True
        )

    await users .update_one (
    {"user_id":m .from_user .id },
    {"$set":{"is_pro":True }},
    upsert =True
    )

    await db ["promo_codes"].update_one (
    {"_id":promo_doc ["_id"]},
    {
    "$set":{"used_count":used_count +1 },
    "$addToSet":{"used_by":m .from_user .id }
    }
    )

    try:
        new_used = used_count + 1
        if new_used >= max_uses:
            announce_channel = promo_doc.get('announce_channel')
            announce_msg_id = promo_doc.get('announce_message_id')
            if announce_channel and announce_msg_id:
                try:
                    await bot.delete_message(announce_channel, announce_msg_id)
                except Exception as e:
                    logging.warning(f"Не удалось удалить объявление промокода: {e}")
                try:
                    await db['promo_codes'].update_one({'_id': promo_doc['_id']}, {'$unset': {'announce_message_id': "", 'announce_channel': ""}})
                except Exception:
                    pass
    except Exception:
        pass

    await m .answer (await get_text ('promo_activated',m .from_user .id ,language =lang ),protect_content =True )
    try:
        expires_str = new_expires_at.strftime("%d.%m.%Y %H:%M") if isinstance(new_expires_at, datetime) else str(new_expires_at)
        tariff_name = f"Promo ({code}) - {days}d"
        await send_receipt_to_pro_users(m.from_user.id, tariff_name, expires_str)
    except Exception as e:
        logging.warning(f"Не удалось отправить уведомления PRO о промо-активации: {e}")

@dp.message(Command("codes"))
async def promo_codes_stats (m :types .Message ):
    """Статистика промокодов: /codes"""
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return
    if m .chat .type !='private':
        return

    lang =await get_user_language (m .from_user .id )

    if not await is_owner_or_pro (m .from_user .id ):
        await m .answer (await get_text ('codes_no_access',m .from_user .id ,language =lang ),protect_content =True )
        return

    text =f"{await get_text('promo_codes_title', m.from_user.id, language=lang)}\n\n"

    query ={}
    if m .from_user .id !=OWNER_ID :
        query ["creator_id"]=m .from_user .id

    cursor =db ["promo_codes"].find (query ).sort ("created_at",ASCENDING )
    has_any =False

    async for promo in cursor :
        has_any =True
        code =promo .get ("code","")
        used =promo .get ("used_count",0 )
        max_uses =promo .get ("max_uses",10 )
        creator_id =promo .get ("creator_id",0 )
        created_at =promo .get ("created_at")
        if isinstance (created_at ,datetime ):
            created_at_str =created_at .strftime ("%d.%m.%Y %H:%M")
        else :
            created_at_str =str (created_at )

        line =await get_text (
        'promo_code_stats',
        m .from_user .id ,
        language =lang ,
        code =code ,
        used =used ,
        max_uses =max_uses ,
        creator_id =creator_id ,
        created_at =created_at_str
        )
        text +=f"{line}\n\n"

    if not has_any :
        text +=await get_text ('promo_no_codes',m .from_user .id ,language =lang )

    await m .answer (text ,protect_content =True )

@dp.message(Command("add"))
async def add (m :types .Message ):
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return
    if not await is_owner_or_pro (m .from_user .id ):
        return
    if m .chat .type !='private':
        return

    lang =await get_user_language (m .from_user .id )

    try :
        uid =int (m .text .split (maxsplit =1 )[1 ])

        if uid ==OWNER_ID :
            error_text ="❌ Нельзя удалить владельца из PRO списка"if lang =="ru"else "❌ Cannot remove owner from PRO list"
            await m .answer (error_text ,protect_content =True )
            return

        if await is_whitelisted (uid ):
            try :
                user =await get_user_from_api (uid )
                user_name =html .escape (user .full_name or await get_text ("unavailable",m .from_user .id ,language =lang ))
            except :
                user_name =f"ID: {uid}"
            await m .answer (
            await get_text ('already_pro',m .from_user .id ,language =lang ,uid =uid ,name =user_name ),
            protect_content =True
            )
            return

        try :
            user =await get_user_from_api (uid )
            user_name =html .escape (user .full_name or await get_text ("unavailable",m .from_user .id ,language =lang ))
        except Exception as e :
            error_msg ="Пользователь не найден в Telegram или недоступен."if lang =="ru"else "User not found in Telegram or unavailable."
            await m .answer (
            f"<b>{await get_text('error', m.from_user.id, language=lang)}</b>\n"
            f"{error_msg}\n"
            f"{await get_text('example_add', m.from_user.id, language=lang)}",
            protect_content =True
            )
            return

        await whitelist .update_one ({"user_id":uid },{"$set":{"user_id":uid }},upsert =True )
        await users .update_one ({"user_id":uid },{"$set":{"is_pro":True }},upsert =True )

        now =datetime .now ()
        user_ids =await users .distinct ("user_id")
        premium_ids =await premium_subscriptions .distinct ("user_id",{"expires_at":{"$gt":now }})
        total_users =len (set (user_ids )|set (premium_ids ))
        pro_users_count =await whitelist .count_documents ({})
        normal_users_count =total_users -pro_users_count
        premium_users_count =await premium_subscriptions .count_documents ({"expires_at":{"$gt":now }})

        await m .answer (
        f"<b>{await get_text('pro_promoted', m.from_user.id, language=lang)}</b>\n"
        f"<code>{uid}</code> — {user_name}\n\n"
        f"<b>{await get_text('stats_updated', m.from_user.id, language=lang)}</b>\n"
        f"{await get_text('total_users', m.from_user.id, language=lang)} <code>{total_users}</code>\n"
        f"{await get_text('pro_users', m.from_user.id, language=lang)} <code>{pro_users_count}</code>\n"
        f"{await get_text('normal_users', m.from_user.id, language=lang)} <code>{normal_users_count}</code>\n"
        f"{await get_text('premium_users_count', m.from_user.id, language=lang)} <code>{premium_users_count}</code>",
        protect_content =True
        )
    except Exception as e :
        await m .answer (f"<b>{await get_text('error', m.from_user.id, language=lang)}</b>\n{await get_text('example_add', m.from_user.id, language=lang)}",protect_content =True )

@dp.message(Command("dell"))
async def dell (m :types .Message ):
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return
    if not await is_owner_or_pro (m .from_user .id ):
        return
    if m .chat .type !='private':
        return

    lang =await get_user_language (m .from_user .id )

    try :
        uid =int (m .text .split (maxsplit =1 )[1 ])

        if uid ==OWNER_ID :
            error_text ="❌ Нельзя удалить владельца из PRO списка"if lang =="ru"else "❌ Cannot remove owner from PRO list"
            await m .answer (error_text ,protect_content =True )
            return
        result =await whitelist .delete_one ({"user_id":uid })
        if result .deleted_count :
            await users .update_one ({"user_id":uid },{"$set":{"is_pro":False }},upsert =True )

            now =datetime .now ()
            user_ids =await users .distinct ("user_id")
            premium_ids =await premium_subscriptions .distinct ("user_id",{"expires_at":{"$gt":now }})
            total_users =len (set (user_ids )|set (premium_ids ))
            pro_users_count =await whitelist .count_documents ({})
            normal_users_count =total_users -pro_users_count
            premium_users_count =await premium_subscriptions .count_documents ({"expires_at":{"$gt":now }})

            await m .answer (
            f"<b>{await get_text('pro_demoted', m.from_user.id, language=lang)}</b>\n"
            f"<code>{uid}</code>\n\n"
            f"<b>{await get_text('stats_updated', m.from_user.id, language=lang)}</b>\n"
            f"{await get_text('total_users', m.from_user.id, language=lang)} <code>{total_users}</code>\n"
            f"{await get_text('pro_users', m.from_user.id, language=lang)} <code>{pro_users_count}</code>\n"
            f"{await get_text('normal_users', m.from_user.id, language=lang)} <code>{normal_users_count}</code>\n"
            f"{await get_text('premium_users_count', m.from_user.id, language=lang)} <code>{premium_users_count}</code>",
            protect_content =True
            )
        else :
            await m .answer (f"<b>⚠️ {await get_text('no_pro_users', m.from_user.id, language=lang)}</b>",protect_content =True )
    except :
        await m .answer (f"<b>{await get_text('error', m.from_user.id, language=lang)}</b>\n{await get_text('example_dell', m.from_user.id, language=lang)}",protect_content =True )

@dp.message(Command("pro"))
async def list_pro (m :types .Message ):
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return
    if not await is_owner_or_pro (m .from_user .id ):
        return
    if m .chat .type !='private':
        return

    lang =await get_user_language (m .from_user .id )

    pro_users_list =[]
    async for doc in whitelist .find ({}):
        user_id =doc .get ("user_id")
        if user_id ==OWNER_ID :
            continue
        try :
            u =await bot .get_chat (user_id )
            name =html .escape (u .full_name or await get_text ("unavailable",m .from_user .id ,language =lang ))
            pro_users_list .append ((user_id ,name ))
        except :
            name =await get_text ('unavailable',m .from_user .id ,language =lang )
            pro_users_list .append ((user_id ,name ))

    if len (pro_users_list )==0 :
        await m .answer (f"<b>{await get_text('no_pro_users', m.from_user.id, language=lang)}</b>",protect_content =True )
        return

    text =f"<b>{await get_text('pro_users_list', m.from_user.id, language=lang)}</b>\n\n"
    for user_id ,name in pro_users_list :
        text +=f"<code>{user_id}</code> — {name}\n"

    await m .answer (text ,protect_content =True )

@dp.message(Command("list"))
async def list_premium (m :types .Message ):
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return
    if not await is_owner_or_pro (m .from_user .id ):
        return
    if m .chat .type !='private':
        return

    lang =await get_user_language (m .from_user .id )

    premium_count =0
    premium_users_list =[]

    now =datetime .now ()
    async for premium_doc in premium_subscriptions .find ({"expires_at":{"$gt":now }}):
        user_id =premium_doc .get ("user_id")
        if not await is_whitelisted (user_id )and user_id !=OWNER_ID :
            expires_at =premium_doc .get ("expires_at")
            if expires_at and expires_at >now :
                try :
                    user_info =await bot .get_chat (user_id )
                    user_name =html .escape (user_info .full_name or await get_text ("unavailable",m .from_user .id ,language =lang ))
                    expires_str =expires_at .strftime ("%d.%m.%Y %H:%M")
                    delta =expires_at -now
                    days =delta .days
                    hours =delta .seconds //3600
                    minutes =(delta .seconds %3600 )//60

                    if days >365 *30 :
                        time_left ="∞"
                    elif days >0 :
                        time_left =f"{days}д {hours}ч {minutes}м"if lang =="ru"else f"{days}d {hours}h {minutes}m"
                    elif hours >0 :
                        time_left =f"{hours}ч {minutes}м"if lang =="ru"else f"{hours}h {minutes}m"
                    else :
                        time_left =f"{minutes}м"if lang =="ru"else f"{minutes}m"

                    premium_users_list .append ({
                    'user_id':user_id ,
                    'name':user_name ,
                    'expires_at':expires_at ,
                    'expires_str':expires_str ,
                    'time_left':time_left
                    })
                    premium_count +=1
                except :
                    continue

    if premium_count ==0 :
        await m .answer (await get_text ("premium_no_users",m .from_user .id ,language =lang ),protect_content =True )
    else :
        text =f"{await get_text('premium_stats_title', m.from_user.id, language=lang)}\n\n"
        text +=f"{await get_text('premium_users_count', m.from_user.id, language=lang)} <code>{premium_count}</code>\n\n"
        premium_users_list .sort (key =lambda x :x ['expires_at'])

        for user_info in premium_users_list :
            premium_user_text = await get_text(
                'premium_user_info',
                user_id=user_info['user_id'],
                language=lang,
                target_id=user_info['user_id'],
                name=user_info['name'],
                expires_str=user_info['expires_str'],
                time_left=user_info['time_left'],
            )
            text +=f"{premium_user_text}\n\n"

        await m .answer (text ,protect_content =True )

@dp.message(Command("chats"))
async def list_chats (m :types .Message ):
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return
    if not await is_owner_or_pro (m .from_user .id ):
        return
    if m .chat .type !='private':
        return

    count =await chats .count_documents ({"chat_id":{"$lt":0 }})
    if count ==0 :
        await m .answer (f"<b>{await get_text('no_group_chats', m.from_user.id)}</b>",protect_content =True )
        return

    text =f"<b>{await get_text('group_chats', m.from_user.id, count)}</b>\n\n"
    async for chat_doc in chats .find ({"chat_id":{"$lt":0 }}):
        title =html .escape (chat_doc .get ("title")or await get_text ("no_title",m .from_user .id ))
        if chat_doc ["chat_id"]<0 :
            if str (chat_doc ["chat_id"]).startswith ("-100"):
                chat_type =await get_text ("channel",m .from_user .id )
            else :
                chat_type =await get_text ("group",m .from_user .id )
        else :
            chat_type =await get_text ("private",m .from_user .id )
        text +=f"• <code>{chat_doc['chat_id']}</code> — {title} ({chat_type})\n"

    if len (text )>4000 :
        parts =[]
        current_part =f"<b>{await get_text('group_chats', m.from_user.id, count)}</b>\n\n"
        lines =text .split ('\n')[2 :]
        for line in lines :
            if len (current_part +line +'\n')>4000 :
                parts .append (current_part )
                current_part =f"<b>🔄 Продолжение / Continue:</b>\n\n{line}\n"
            else :
                current_part +=line +'\n'
        if current_part :
            parts .append (current_part )
        for i ,part in enumerate (parts ,1 ):
            await m .answer (part ,protect_content =True )
    else :
        await m .answer (text ,protect_content =True )

@dp.message(Command("users"))
async def count_users (m :types .Message ):
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return
    if not await is_owner_or_pro (m .from_user .id ):
        return
    if m .chat .type !='private':
        return

    lang =await get_user_language (m .from_user .id )
    now =datetime .now ()
    user_ids =await users .distinct ("user_id")
    premium_ids =await premium_subscriptions .distinct ("user_id",{"expires_at":{"$gt":now }})
    total_users =len (set (user_ids )|set (premium_ids ))
    pro_users_count =await whitelist .count_documents ({})
    normal_users_count =total_users -pro_users_count
    premium_users_count =await premium_subscriptions .count_documents ({"expires_at":{"$gt":now }})

    text =f"{await get_text('stats_title', m.from_user.id, language=lang)}\n\n"
    text +=f"{await get_text('total_users', m.from_user.id, language=lang)} <code>{total_users}</code>\n"
    text +=f"{await get_text('pro_users', m.from_user.id, language=lang)} <code>{pro_users_count}</code>\n"
    text +=f"{await get_text('normal_users', m.from_user.id, language=lang)} <code>{normal_users_count}</code>\n"
    text +=f"{await get_text('premium_users_count', m.from_user.id, language=lang)} <code>{premium_users_count}</code>\n"

    html_button = InlineKeyboardButton(
        text=await get_text("view_table", m.from_user.id, language=lang),
        callback_data="show_users_html"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[html_button]])

    await m .answer (text ,reply_markup =keyboard ,protect_content =True )

@dp.message(Command("cleardb"))
async def cleardb (m :types .Message ):
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return
    if m .from_user .id !=OWNER_ID :
        return
    if m .chat .type !='private':
        return

    try :

        await users .delete_many ({})
        await history .delete_many ({})
        await chats .delete_many ({})
        await whitelist .delete_many ({})
        await privacy_log .delete_many ({})
        await user_languages .delete_many ({})
        await premium_subscriptions .delete_many ({})
        await db ["promo_codes"].delete_many ({})
        await chat_languages .delete_many ({})

        await whitelist .update_one (
        {"user_id":OWNER_ID },
        {"$set":{"user_id":OWNER_ID }},
        upsert =True
        )
        await users .update_one (
        {"user_id":OWNER_ID },
        {"$set":{"is_pro":True }},
        upsert =True
        )

        lang =await get_user_language (m .from_user .id )
        await m .answer (
        f"{await get_text('db_cleared', m.from_user.id, language=lang)}\n\n"
        f"{await get_text('all_data_deleted', m.from_user.id, language=lang)}\n"
        f"{await get_text('users_deleted', m.from_user.id, language=lang)}\n"
        f"{await get_text('history_deleted', m.from_user.id, language=lang)}\n"
        f"{await get_text('chats_deleted', m.from_user.id, language=lang)}\n"
        f"{await get_text('whitelist_deleted', m.from_user.id, language=lang)}",
        protect_content =True
        )
    except Exception as e :
        lang =await get_user_language (m .from_user .id )
        await m .answer (f"<b>{await get_text('error', m.from_user.id, language=lang)}</b>\n<code>{str(e)}</code>",protect_content =True )

@dp.message(Command("premium"))
async def premium_cmd (m :types .Message ):
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return
    if m .chat .type !='private':
        return

    lang_doc =await user_languages .find_one ({"user_id":m .from_user .id })
    if not lang_doc :
        keyboard =InlineKeyboardMarkup ()
        keyboard .add (InlineKeyboardButton ("🇷🇺 Русский",callback_data ="lang_ru"))
        keyboard .add (InlineKeyboardButton ("🇬🇧 English",callback_data ="lang_en"))
        await m .answer (await get_text ("choose_lang",m .from_user .id ,language ="ru"),reply_markup =keyboard ,protect_content =True )
        return

    lang =await get_user_language (m .from_user .id )

    parts =m .text .split (maxsplit =1 )
    if len (parts )>1 and await is_owner_or_pro (m .from_user .id ):
        try :
            uid =int (parts [1 ])
        except ValueError :
            usage ="Использование: /premium 123456789"if lang =="ru"else "Usage: /premium 123456789"
            await m .answer (usage ,protect_content =True )
            return

        far_future =datetime .now ()+timedelta (days =365 *50 )
        await premium_subscriptions .update_one (
        {"user_id":uid },
        {
        "$set":{
        "user_id":uid ,
        "expires_at":far_future ,
        "created_at":datetime .now (),
        "last_payment":datetime .now ()
        }
        },
        upsert =True
        )

        await users .update_one (
        {"user_id":uid },
        {"$set":{"is_pro":True }},
        upsert =True
        )

        try :
            uinfo =await bot .get_chat (uid )
            uname =html .escape (uinfo .full_name or f"ID: {uid}")
        except :
            uname =f"ID: {uid}"

        if lang =="ru":
            txt =f"⭐ <b>Пользователь получил бессрочный Premium:</b>\n<code>{uid}</code> — {uname}"
        else :
            txt =f"⭐ <b>User received lifetime Premium:</b>\n<code>{uid}</code> — {uname}"
        await m .answer (txt ,protect_content =True )
        return

    # Only owner may view full premium users list
    if m .from_user .id == OWNER_ID:
        premium_count =0
        premium_users_list =[]

        now =datetime .now ()
        async for premium_doc in premium_subscriptions .find ({"expires_at":{"$gt":now }}):
            user_id =premium_doc .get ("user_id")
            if not await is_whitelisted (user_id )and user_id !=OWNER_ID :
                expires_at =premium_doc .get ("expires_at")
                if expires_at and expires_at >now :
                    try :
                        user_info =await bot .get_chat (user_id )
                        user_name =html .escape (user_info .full_name or await get_text ("unavailable",m .from_user .id ,language =lang ))
                        expires_str =expires_at .strftime ("%d.%m.%Y %H:%M")
                        delta =expires_at -now
                        days =delta .days
                        hours =delta .seconds //3600
                        minutes =(delta .seconds %3600 )//60

                        if days >365 *30 :
                            time_left ="∞"
                        elif days >0 :
                            time_left =f"{days}д {hours}ч {minutes}м"
                        elif hours >0 :
                            time_left =f"{hours}ч {minutes}м"
                        else :
                            time_left =f"{minutes}м"

                        premium_users_list .append ({
                        'user_id':user_id ,
                        'name':user_name ,
                        'expires_at':expires_at ,
                        'expires_str':expires_str ,
                        'time_left':time_left
                        })
                        premium_count +=1
                    except :
                        continue

        if premium_count ==0 :
            await m .answer (await get_text ("premium_no_users",m .from_user .id ,language =lang ),protect_content =True )
        else :
            text =f"{await get_text('premium_stats_title', m.from_user.id, language=lang)}\n\n"
            text +=f"{await get_text('premium_users_count', m.from_user.id, language=lang)} <code>{premium_count}</code>\n\n"
            premium_users_list .sort (key =lambda x :x ['expires_at'])

            for user_info in premium_users_list :
                # pass requester's id for language lookup, and include the target user's id
                # in kwargs so the locale formatting finds {user_id}
                premium_user_text = await get_text(
                    'premium_user_info',
                    user_id=m.from_user.id,
                    language=lang,
                    target_id=user_info['user_id'],
                    name=user_info['name'],
                    expires_str=user_info['expires_str'],
                    time_left=user_info['time_left'],
                )
                text +=f"{premium_user_text}\n\n"

            await m .answer (text ,protect_content =True )
        return

    if await has_active_premium (m .from_user .id ):
        expires_at =await get_premium_expires_at (m .from_user .id )
        if expires_at :
            expires_str =expires_at .strftime ("%d.%m.%Y %H:%M")

            now =datetime .now ()
            delta =expires_at -now
            days =delta .days
            hours =delta .seconds //3600
            minutes =(delta .seconds %3600 )//60

            if days >365 *30 :
                time_left ="∞"
            elif days >0 :
                time_left =f"{days}д {hours}ч {minutes}м"if lang =="ru"else f"{days}d {hours}h {minutes}m"
            elif hours >0 :
                time_left =f"{hours}ч {minutes}м"if lang =="ru"else f"{hours}h {minutes}m"
            else :
                time_left =f"{minutes}м"if lang =="ru"else f"{minutes}m"

            await m .answer (
            f"{await get_text('premium_already', m.from_user.id, language=lang)}\n\n"
            f"{await get_text('premium_expires', m.from_user.id, language=lang, expires_str=expires_str)}\n"
            f"{await get_text('premium_time_left', m.from_user.id, language=lang)}\n"
            f"<code>{time_left}</code>",
            protect_content =True
            )
        else :
            await m .answer (await get_text ("premium_already",m .from_user .id ,language =lang ),protect_content =True )
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"💎 {await get_text('premium_24h', m.from_user.id, language=lang)} - 15 ⭐",
                callback_data="premium_24h"
            )],
            [InlineKeyboardButton(
                text=f"💎 {await get_text('premium_1month', m.from_user.id, language=lang)} - 25 ⭐",
                callback_data="premium_1month"
            )],
            [InlineKeyboardButton(
                text=f"💎 {await get_text('premium_3months', m.from_user.id, language=lang)} - 50 ⭐",
                callback_data="premium_3months"
            )],
            [InlineKeyboardButton(
                text=f"💎 {await get_text('premium_1year', m.from_user.id, language=lang)} - 100 ⭐",
                callback_data="premium_1year"
            )],
            [InlineKeyboardButton(
                text=await get_text("premium_close", m.from_user.id, language=lang),
                callback_data="premium_close"
            )]
        ]
    )

    await m .answer (
    f"{await get_text('premium_title', m.from_user.id, language=lang)}\n\n"
    f"{await get_text('premium_description', m.from_user.id, language=lang)}",
    reply_markup =keyboard ,
    protect_content =True
    )

@dp.message()
async def tools (m :types .Message ):
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return

    if await is_whitelisted (m .from_user .id )and m .from_user .id !=OWNER_ID :
        return

    await save_chat (m .chat )
    changes =await save_user (m .from_user )

    if changes and m .chat .type in ['group','supergroup']:
        if not await is_whitelisted (m .from_user .id )and m .from_user .id !=OWNER_ID :
            try :
                bot_member =await bot .get_chat_member (m .chat .id ,BOT_ID )
                if bot_member .status in ['administrator','creator']:
                    lang =await get_user_language (m .from_user .id )
                    user_name =html .escape (m .from_user .full_name or await get_text ("unavailable",m .from_user .id ,language =lang ))
                    changes_text =await get_text ('changes',m .from_user .id ,language =lang )
                    notification =f"<b>🔄 {changes_text}</b> <i>{user_name}</i>:\n"+"\n".join (changes )
                    await m .answer (notification ,protect_content =True )
            except :
                pass
        return

    if m .reply_to_message and m .reply_to_message .from_user :
        await save_user (m .reply_to_message .from_user )

    if m .forward_from :
        await save_user (m .forward_from )

    text =(m .text or m .caption or "").strip ()

    if m .chat .type in ['group','supergroup']:
        return

    if m .chat .type =='private':

        lang_doc =await user_languages .find_one ({"user_id":m .from_user .id })
        if not lang_doc :
            keyboard =InlineKeyboardMarkup ()
            keyboard .add (InlineKeyboardButton ("🇷🇺 Русский",callback_data ="lang_ru"))
            keyboard .add (InlineKeyboardButton ("🇬🇧 English",callback_data ="lang_en"))
            await m .answer (await get_text ("choose_lang",m .from_user .id ,language ="ru"),reply_markup =keyboard ,protect_content =True )
            return

        if text .startswith ("/broadcast"):
            if not await is_owner_or_pro (m .from_user .id ):
                return
            if m .reply_to_message :
                src =m .reply_to_message
                count =await chats .count_documents ({})
                success_count =0
                async for chat in chats .find ({}):
                    try :
                        await bot .copy_message (
                        chat_id =chat ["chat_id"],
                        from_chat_id =src .chat .id ,
                        message_id =src .message_id ,
                        protect_content =True ,
                        disable_notification =False ,
                        disable_web_page_preview =True
                        )
                        success_count +=1
                    except :
                        pass
                lang =await get_user_language (m .from_user .id )
                await m .answer (
                f"<b>{await get_text('broadcast_completed', m.from_user.id, language=lang)}</b>\n"
                f"{await get_text('delivered_to', m.from_user.id, language=lang, success_count=success_count, count=count)}",
                protect_content =True ,
                disable_web_page_preview =True
                )
                return
            parts =text .split (maxsplit =1 )
            btext =parts [1 ].strip ()if len (parts )>1 else ""
            if not btext :
                lang =await get_user_language (m .from_user .id )
                await m .answer (
                f"<b>{await get_text('broadcast_text_required', m.from_user.id, language=lang)}</b>",
                protect_content =True ,
                disable_web_page_preview =True
                )
                return
            entities =[]
            if m .entities :
                cmd_prefix_len =len (parts [0 ])+1
                for ent in m .entities :
                    if ent .offset +ent .length <=cmd_prefix_len :
                        continue
                    new_offset =max (ent .offset -cmd_prefix_len ,0 )
                    new_length =ent .length -max (cmd_prefix_len -ent .offset ,0 )
                    if new_length >0 :
                        ent .offset =new_offset
                        ent .length =new_length
                        entities .append (ent )
            count =await chats .count_documents ({})
            success_count =0
            async for chat in chats .find ({}):
                try :
                    await bot .send_message (
                    chat ["chat_id"],
                    btext ,
                    protect_content =True ,
                    disable_web_page_preview =True ,
                    entities =entities or None
                    )
                    success_count +=1
                except :
                    pass
            lang =await get_user_language (m .from_user .id )
            await m .answer (
            f"<b>{await get_text('broadcast_completed', m.from_user.id, language=lang)}</b>\n"
            f"{await get_text('delivered_to', m.from_user.id, language=lang, success_count=success_count, count=count)}",
            protect_content =True ,
            disable_web_page_preview =True
            )
            return

        if text :
            if text .isdigit ()or text .startswith ("@"):
                # Require subscription to the news channel to use search
                try:
                    member = await bot.get_chat_member("@NewsRetro", m.from_user.id)
                    subscribed = member.status in ["member", "administrator", "creator"]
                except Exception:
                    subscribed = False

                if not subscribed and m.from_user.id != OWNER_ID:
                    lang = await get_user_language(m.from_user.id)
                    kb = InlineKeyboardMarkup(row_width=1)
                    news_btn = await get_text('news_channel_button', m.from_user.id, language=lang)
                    check_btn = await get_text('check_sub_button', m.from_user.id, language=lang)
                    kb.add(InlineKeyboardButton(text=news_btn, url="https://t.me/NewsRetro"))
                    kb.add(InlineKeyboardButton(text=check_btn, callback_data="check_sub"))
                    # store pending text search to run after subscription check (persist in DB)
                    try:
                        await db["pending_searches"].update_one(
                            {"user_id": m.from_user.id},
                            {"$set": {"user_id": m.from_user.id, "type": "text", "value": text, "created_at": datetime.now()}},
                            upsert=True,
                        )
                    except Exception:
                        pass
                    await m.answer(await get_text('need_subscribe', m.from_user.id, language=lang), reply_markup=kb, protect_content=True)
                    return

                user_obj ,found =await resolve_user (text ,m .from_user .id )
                if found :
                    user_id_to_check =None
                    if user_obj :
                        user_id_to_check =user_obj .id
                    elif text .isdigit ():
                        user_id_to_check =int (text )
                    else :
                        username_query =text [1 :].lower ()if text .startswith ("@")else text .lower ()
                        user_doc =await users .find_one ({
                        "username":{"$regex":f"^{username_query}$","$options":"i"}
                        })
                        if user_doc :
                            user_id_to_check =user_doc ["user_id"]

                    was_in_db =await users .find_one ({"user_id":user_id_to_check })is not None if user_id_to_check else False

                    if user_obj :
                        await save_user (user_obj )
                        await m .answer (await get_history (user_obj .id ,m .from_user .id ,user_in_db =was_in_db ),protect_content =True )
                    elif user_id_to_check :
                        await m .answer (await get_history (user_id_to_check ,m .from_user .id ,user_in_db =True ),protect_content =True )
                    else :
                        lang =await get_user_language (m .from_user .id )
                        found_text ="Пользователь найден:"if lang =="ru"else "User found:"
                        await m .answer (f"<b>❌ {found_text}</b>\n<code>{text}</code>",protect_content =True )
                else :
                    lang =await get_user_language (m .from_user .id )
                    not_found_text ="Пользователь не найден:"if lang =="ru"else "User not found:"
                    await m .answer (f"<b>❌ {not_found_text}</b>\n<code>{text}</code>",protect_content =True )
                return

        if m .forward_from :
            try:
                member = await bot.get_chat_member("@NewsRetro", m.from_user.id)
                subscribed = member.status in ["member", "administrator", "creator"]
            except Exception:
                subscribed = False

            u =m .forward_from
            if not subscribed and m.from_user.id != OWNER_ID:
                lang = await get_user_language(m.from_user.id)
                kb = InlineKeyboardMarkup(row_width=1)
                news_btn = await get_text('news_channel_button', m.from_user.id, language=lang)
                check_btn = await get_text('check_sub_button', m.from_user.id, language=lang)
                kb.add(InlineKeyboardButton(text=news_btn, url="https://t.me/NewsRetro"))
                kb.add(InlineKeyboardButton(text=check_btn, callback_data="check_sub"))
                # store pending forward to run after subscription check (persist in DB)
                try:
                    await db["pending_searches"].update_one(
                        {"user_id": m.from_user.id},
                        {"$set": {"user_id": m.from_user.id, "type": "forward", "value": u.id, "created_at": datetime.now()}},
                        upsert=True,
                    )
                except Exception:
                    pass
                await m.answer(await get_text('need_subscribe', m.from_user.id, language=lang), reply_markup=kb, protect_content=True)
                return

            lang =await get_user_language (m .from_user .id )
            was_in_db =await users .find_one ({"user_id":u .id })is not None
            header =f"<b>{await get_text('forwarded_from', m.from_user.id, language=lang)}</b>"
            sender_name =html .escape (u .full_name or await get_text ("unavailable",m .from_user .id ,language =lang ))
            header +=f"<b>{sender_name}</b>\n\n"
            await m .answer (
            header +await get_history (u .id ,m .from_user .id ,user_in_db =was_in_db ),
            protect_content =True
            )
            return

@dp.my_chat_member()
async def on_bot_join (upd :ChatMemberUpdated ):
    """Обработчик добавления бота в чат"""
    await save_chat (upd .chat )
    old =upd .old_chat_member
    new =upd .new_chat_member
    me =await bot .get_me ()

    if new .user .id !=me .id :
        return

    if old and old .status in ['left','kicked','restricted']and new and new .status in ['member','administrator','creator']:
        asyncio .create_task (collect_chat_members (upd .chat .id ))

        chat_lang ="ru"
        try :
            admins =await bot .get_chat_administrators (upd .chat .id )
            if admins :
                first_admin_id =admins [0 ].user .id
                lang_doc =await user_languages .find_one ({"user_id":first_admin_id })
                if lang_doc :
                    chat_lang =lang_doc .get ("language","ru")
        except :
            pass

        keyboard =InlineKeyboardMarkup ()
        keyboard .add (InlineKeyboardButton ("🇷🇺 Русский",callback_data =f"chat_lang_ru_{upd.chat.id}"))
        keyboard .add (InlineKeyboardButton ("🇬🇧 English",callback_data =f"chat_lang_en_{upd.chat.id}"))

        try :
            lang_msg =await bot .send_message (
            upd .chat .id ,
            await get_text ("choose_lang",language =chat_lang ),
            reply_markup =keyboard ,
            protect_content =True
            )
            asyncio .create_task (handle_chat_language_selection (upd .chat .id ,lang_msg .message_id ,chat_lang ))
        except :
            pass

async def handle_chat_language_selection (chat_id :int ,message_id :int ,default_lang :str ):
    """Обработка выбора языка для чата"""
    await asyncio .sleep (30 )
    try :
        await bot .delete_message (chat_id ,message_id )
    except :
        pass

@dp.callback_query(lambda c: c.data.startswith('chat_lang_'))
async def set_chat_language (callback_query :types .CallbackQuery ):
    """Обработчик выбора языка для чата"""
    if hasattr (callback_query .from_user ,'is_bot')and callback_query .from_user .is_bot :
        return

    parts =callback_query .data .split ('_')
    lang =parts [2 ]
    chat_id =int (parts [3 ])

    await set_user_language (callback_query .from_user .id ,lang )
    try :
        await chat_languages .update_one (
        {"chat_id":chat_id },
        {"$set":{"chat_id":chat_id ,"language":lang }},
        upsert =True
        )
    except :
        pass

    try :
        await bot .delete_message (callback_query .message .chat .id ,callback_query .message .message_id )
    except :
        pass

    has_admin_rights =False
    try :
        bot_member =await bot .get_chat_member (chat_id ,BOT_ID )
        if bot_member .status in ['administrator','creator']:
            has_admin_rights =True
    except :
        pass

    welcome_message =f"""{await get_text('welcome_title', language=lang)}
{await get_text('welcome_capabilities', language=lang)}
{await get_text('welcome_track', language=lang)}
{await get_text('welcome_monitor', language=lang)}
{await get_text('welcome_protect', language=lang)}

{await get_text('welcome_commands', language=lang)}
{await get_text('welcome_chatid', language=lang)}

{await get_text('welcome_chat_id', language=lang)} <code>{chat_id}</code>"""

    if not has_admin_rights :
        welcome_message +=f"\n\n{await get_text('welcome_admin_warning', language=lang)}"

    bot_username = (await bot.get_me()).username
    add_button = InlineKeyboardButton(
        text=await get_text("add_to_chats", language=lang),
        url=f"https://t.me/{bot_username}?startgroup=true"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[add_button]])

    try :
        await bot .send_message (chat_id ,welcome_message ,reply_markup =keyboard ,protect_content =True )
    except Exception :
        try :
            await bot .send_message (
            chat_id ,
            f"{await get_text('welcome_title', language=lang)}\n\n{await get_text('welcome_chat_id', language=lang)} <code>{chat_id}</code>\n\n<i>",
            protect_content =True
            )
        except :
            pass

    await callback_query .answer (await get_text ("lang_set",language =lang ))

@dp.callback_query(lambda c: c.data.startswith('premium_'))
async def premium_callback (callback_query :types .CallbackQuery ):
    """Обработчик кнопок Premium"""
    if hasattr (callback_query .from_user ,'is_bot')and callback_query .from_user .is_bot :
        return

    if callback_query .data =="premium_close":
        try :
            await bot .delete_message (callback_query .message .chat .id ,callback_query .message .message_id )
        except :
            await callback_query .answer ("✅",show_alert =False )
        return

    lang =await get_user_language (callback_query .from_user .id )

    tariff_map ={
    "premium_24h":{"duration_hours":24 ,"price":15 ,"name":await get_text ("premium_24h",callback_query .from_user .id ,language =lang )},
    "premium_1month":{"duration_hours":720 ,"price":25 ,"name":await get_text ("premium_1month",callback_query .from_user .id ,language =lang )},
    "premium_3months":{"duration_hours":2160 ,"price":50 ,"name":await get_text ("premium_3months",callback_query .from_user .id ,language =lang )},
    "premium_1year":{"duration_hours":8760 ,"price":100 ,"name":await get_text ("premium_1year",callback_query .from_user .id ,language =lang )},
    }

    if callback_query .data not in tariff_map :
        await callback_query .answer ("❌",show_alert =False )
        return

    tariff =tariff_map [callback_query .data ]

    try :
        await bot .send_invoice (
        callback_query .from_user .id ,
        title =f"⭐ Premium: {tariff['name']}",
        description =f"Premium подписка на {tariff['name']}",
        payload =f"premium_{callback_query.from_user.id}_{tariff['duration_hours']}",
        provider_token ="",
        currency ="XTR",
        prices =[types .LabeledPrice (label =tariff ['name'],amount =tariff ['price'])],
        start_parameter =f"premium_{callback_query.data}",
        protect_content =True
        )
        await callback_query .answer ()
    except Exception as e :
        logging .error (f"Ошибка при создании инвойса: {e}")
        await callback_query .answer ("❌ Ошибка при создании платежа. Попробуйте позже.",show_alert =True )

@dp.pre_checkout_query()
async def pre_checkout (pre_checkout_query :types .PreCheckoutQuery ):
    try:
        await bot .answer_pre_checkout_query (pre_checkout_query .id ,ok =True )
    except Exception:
        pass

@dp.callback_query(lambda c: c.data == 'check_sub')
async def check_subscription (callback_query :types .CallbackQuery ):
    """Проверка подписки на канал NewsRetro"""
    if hasattr (callback_query .from_user ,'is_bot')and callback_query .from_user .is_bot :
        return

    lang = await get_user_language(callback_query.from_user.id)
    try:
        member = await bot.get_chat_member("@NewsRetro", callback_query.from_user.id)
        subscribed = member.status in ["member", "administrator", "creator"]
    except Exception:
        subscribed = False

    if subscribed:
        await callback_query.answer(await get_text('check_sub_ok', callback_query.from_user.id, language=lang), show_alert=True)
        try:
            await bot.send_message(callback_query.from_user.id, await get_text('check_sub_ok', callback_query.from_user.id, language=lang), protect_content=True)
        except:
            pass
        try:
            pending = await db["pending_searches"].find_one_and_delete({"user_id": callback_query.from_user.id})
        except Exception:
            pending = None
        if pending:
            try:
                if pending.get('type') == 'text':
                    text = pending.get('value')
                    user_obj, found = await resolve_user(text, callback_query.from_user.id)
                    if found:
                        user_id_to_check = None
                        if user_obj:
                            user_id_to_check = user_obj.id
                        elif text.isdigit():
                            user_id_to_check = int(text)
                        else:
                            username_query = text[1:].lower() if text.startswith("@") else text.lower()
                            user_doc = await users.find_one({"username": {"$regex": f"^{username_query}$", "$options": "i"}})
                            if user_doc:
                                user_id_to_check = user_doc["user_id"]

                        was_in_db = await users.find_one({"user_id": user_id_to_check}) is not None if user_id_to_check else False
                        if user_obj:
                            await save_user(user_obj)
                            await bot.send_message(callback_query.from_user.id, await get_history(user_obj.id, callback_query.from_user.id, user_in_db=was_in_db), protect_content=True)
                        elif user_id_to_check:
                            await bot.send_message(callback_query.from_user.id, await get_history(user_id_to_check, callback_query.from_user.id, user_in_db=True), protect_content=True)
                        else:
                            not_found_text = "Пользователь найден:" if lang == "ru" else "User found:"
                            await bot.send_message(callback_query.from_user.id, f"<b>❌ {not_found_text}</b>\n<code>{text}</code>", protect_content=True)

                elif pending.get('type') == 'forward':
                    uid = pending.get('value')
                    was_in_db = await users.find_one({"user_id": uid}) is not None
                    header = f"<b>{await get_text('forwarded_from', callback_query.from_user.id, language=lang)}</b>"
                    sender_name = html.escape((await bot.get_chat(uid)).full_name or await get_text("unavailable", callback_query.from_user.id, language=lang))
                    header += f"<b>{sender_name}</b>\n\n"
                    await bot.send_message(callback_query.from_user.id, header + await get_history(uid, callback_query.from_user.id, user_in_db=was_in_db), protect_content=True)
            except Exception:
                pass
    else:
        kb = InlineKeyboardMarkup(row_width=1)
        news_btn = await get_text('news_channel_button', callback_query.from_user.id, language=lang)
        check_btn = await get_text('check_sub_button', callback_query.from_user.id, language=lang)
        kb.add(InlineKeyboardButton(text=news_btn, url="https://t.me/NewsRetro"))
        kb.add(InlineKeyboardButton(text=check_btn, callback_data="check_sub"))
        await callback_query.answer(await get_text('check_sub_not', callback_query.from_user.id, language=lang), show_alert=True)
        try:
            await bot.send_message(callback_query.from_user.id, await get_text('need_subscribe', callback_query.from_user.id, language=lang), reply_markup=kb, protect_content=True)
        except:
            pass
    

@dp.message(F.successful_payment)
async def successful_payment_handler (m :types .Message ):
    if hasattr (m .from_user ,'is_bot')and m .from_user .is_bot :
        return

    payment =m .successful_payment
    payload =payment .invoice_payload

    if not payload .startswith ("premium_"):
        return

    try :
        parts =payload .split ("_")
        if len (parts )<3 :
            return

        user_id =int (parts [1 ])
        duration_hours =int (parts [2 ])

        if user_id !=m .from_user .id :
            return

        expires_at =datetime .now ()+timedelta (hours =duration_hours )

        current_premium =await premium_subscriptions .find_one ({"user_id":user_id })

        if current_premium and current_premium .get ("expires_at")>datetime .now ():
            new_expires_at =current_premium .get ("expires_at")+timedelta (hours =duration_hours )
            await premium_subscriptions .update_one (
            {"user_id":user_id },
            {"$set":{"expires_at":new_expires_at ,"last_payment":datetime .now ()}}
            )
            expires_at =new_expires_at
        else :
            await premium_subscriptions .update_one (
            {"user_id":user_id },
            {
            "$set":{
            "user_id":user_id ,
            "expires_at":expires_at ,
            "created_at":datetime .now (),
            "last_payment":datetime .now ()
            }
            },
            upsert =True
            )

        await users .update_one (
        {"user_id":user_id },
        {"$set":{"is_pro":True }},
        upsert =True
        )

        lang =await get_user_language (user_id )
        expires_str =expires_at .strftime ("%d.%m.%Y %H:%M")
        await m .answer (
        f"{await get_text('premium_success', user_id, language=lang)}\n\n"
        f"{await get_text('premium_expires', user_id, language=lang, expires_str=expires_str)}",
        protect_content =True
        )

        tariff_names ={
        24 :await get_text ("premium_24h",user_id ,language =lang ),
        720 :await get_text ("premium_1month",user_id ,language =lang ),
        2160 :await get_text ("premium_3months",user_id ,language =lang ),
        8760 :await get_text ("premium_1year",user_id ,language =lang ),
        }
        tariff_name =tariff_names .get (duration_hours ,f"{duration_hours} часов")

        await send_receipt_to_pro_users (user_id ,tariff_name ,expires_str )

    except Exception as e :
        logging .error (f"Ошибка при обработке платежа: {e}")
        await m .answer ("❌ Произошла ошибка при активации подписки. Обратитесь к администратору.",protect_content =True )

async def send_receipt_to_pro_users (buyer_id :int ,tariff_name :str ,expires_str :str ):
    try :
        buyer_info =await bot .get_chat (buyer_id )
        buyer_name =html .escape (buyer_info .full_name or f"ID: {buyer_id}")
        buyer_username =f"@{buyer_info.username}"if buyer_info .username else f"<code>{buyer_id}</code>"
        async for pro_user in whitelist .find ({}):
            pro_user_id =pro_user .get ("user_id")
            if pro_user_id ==OWNER_ID or pro_user_id ==buyer_id :
                continue

            try :
                lang =await get_user_language (pro_user_id )
                receipt_text =await get_text ("premium_purchase_receipt",pro_user_id ,language =lang )
                receipt_msg =receipt_text .format (buyer_name =buyer_name ,buyer_username =buyer_username ,buyer_id =buyer_id ,tariff_name =tariff_name ,expires_str =expires_str )
                await bot .send_message (
                pro_user_id ,
                receipt_msg ,
                protect_content =True
                )
            except Exception as e :
                logging .warning (f"Не удалось отправить чек пользователю {pro_user_id}: {e}")
                pass
    except Exception as e :
        logging .error (f"Ошибка при отправке чеков: {e}")

@dp.chat_member()
async def member_upd (upd :ChatMemberUpdated ):
    await save_chat (upd .chat )
    old =upd .old_chat_member
    new =upd .new_chat_member
    user =new .user if new else old .user

    if hasattr (user ,'is_bot')and user .is_bot :
        return

    if await is_whitelisted (user .id ):
        return

    await save_user (user )

    if hasattr (upd ,'invite_link')and upd .invite_link :
        try :
            if upd .invite_link .creator :
                await save_user (upd .invite_link .creator )
        except :
            pass

    if hasattr (user ,'is_deleted')and user .is_deleted :
        try :
            await bot .send_message (
            upd .chat .id ,
            f"<b>👻 Удалённый аккаунт</b>\n<code>{user.id}</code>",
            protect_content =True
            )
        except :
            pass
        return

    user_name =html .escape (user .full_name or 'Неизвестно')

    try :
        chat_lang ="ru"
        try :

            chat_lang_doc =await chat_languages .find_one ({"chat_id":upd .chat .id })
            if chat_lang_doc :
                chat_lang =chat_lang_doc .get ("language","ru")
            else :

                admins =await bot .get_chat_administrators (upd .chat .id )
                if admins :
                    first_admin_id =admins [0 ].user .id
                    lang_doc =await user_languages .find_one ({"user_id":first_admin_id })
                    if lang_doc :
                        chat_lang =lang_doc .get ("language","ru")
        except :
            pass

        if old and old .status in ['left','kicked']and new .status =='member':
            returned_text =await get_text ("returned",language =chat_lang )
            await bot .send_message (upd .chat .id ,f"✨ <b>{user_name}</b> {returned_text}",protect_content =True )
        elif old and old .status =='member'and new .status in ['left','kicked']:
            left_text =await get_text ("left",language =chat_lang )
            await bot .send_message (upd .chat .id ,f"👋 <b>{user_name}</b> {left_text}",protect_content =True )
    except :
        pass

@dp.callback_query(lambda c: c.data == 'show_users_html')
async def show_users_html (callback_query :types .CallbackQuery ):
    """Генерация HTML таблицы пользователей"""
    if hasattr (callback_query .from_user ,'is_bot')and callback_query .from_user .is_bot :
        return
    if not await is_owner_or_pro (callback_query .from_user .id ):
        await callback_query .answer ("У вас нет доступа к этой функции / You don't have access to this function",show_alert =True )
        return

    lang =await get_user_language (callback_query .from_user .id )
    generating_text ="Генерирую таблицу пользователей..."if lang =="ru"else "Generating users table..."
    await callback_query .answer (generating_text )

    now =datetime .now ()

    active_premium ={}
    async for premium_doc in premium_subscriptions .find ({"expires_at":{"$gt":now }}):
        user_id =premium_doc .get ("user_id")
        active_premium [user_id ]=premium_doc

    users_list =[]
    premium_count =0

    async for user_doc in users .find ({}):
        user_id =user_doc .get ("user_id")
        if not user_id or user_id ==OWNER_ID :
            continue
        if await is_whitelisted (user_id ):
            continue

        name =f"{user_doc.get('first_name', '')} {user_doc.get('last_name', '')}".strip ()
        username =user_doc .get ('username','')

        expires_at =None
        time_left =""
        if user_id in active_premium :
            premium_doc =active_premium [user_id ]
            expires_at =premium_doc .get ("expires_at")
            if expires_at and expires_at >now :
                delta =expires_at -now
                days =delta .days
                hours =delta .seconds //3600
                minutes =(delta .seconds %3600 )//60

                if days >365 *30 :
                    time_left ="∞"
                elif days >0 :
                    time_left =f"{days}д {hours}ч {minutes}м"
                elif hours >0 :
                    time_left =f"{hours}ч {minutes}м"
                else :
                    time_left =f"{minutes}м"
                premium_count +=1

        is_premium =bool (time_left )

        users_list .append ({
        'id':user_id ,
        'name':html .escape (name or 'Неизвестно'),
        'username':f"@{username}"if username else '',
        'expires_at':expires_at ,
        'time_left':time_left or "—",
        'is_premium':is_premium ,
        'status':"⭐ Premium"if is_premium else "👤 Basic"
        })

    users_list .sort (
    key =lambda x :(
    0 if x ['expires_at']else 1 ,
    x ['expires_at']if x ['expires_at']else datetime .max
    )
    )

    now =datetime .now ()
    user_ids =await users .distinct ("user_id")
    premium_ids =await premium_subscriptions .distinct ("user_id",{"expires_at":{"$gt":now }})
    total_users =len (set (user_ids )|set (premium_ids ))

    try :
        me =await bot .get_me ()
        bot_username =me .username or "RetroTagBot"
    except :
        bot_username ="RetroTagBot"

    html_content =f"""<!DOCTYPE html>
<html lang="en" id="htmlLang">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <meta name="description" content="Users Database - RetroTag Info Bot">
    <meta name="mobile-web-app-capable" content="yes">
    <title>✨ Premium Dashboard - RetroTag</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html {{
            width: 100%;
            overflow-x: hidden;
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }}

        :root {{
            --bg-primary: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            --bg-secondary: #ffffff;
            --text-primary: #1a202c;
            --text-secondary: #718096;
            --border-color: #e2e8f0;
            --header-bg: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            --header-bg-animated: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
            --stats-bg: rgba(255,255,255,0.3);
            --hover-bg: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            --pro-color: #e53e3e;
            --pro-gradient: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
            --premium-color: #d69e2e;
            --premium-gradient: linear-gradient(135deg, #f6e05e 0%, #d69e2e 50%, #b7791f 100%);
            --normal-color: #38a169;
            --normal-gradient: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            --shadow-sm: 0 2px 4px rgba(0,0,0,0.06);
            --shadow-md: 0 4px 12px rgba(0,0,0,0.1);
            --shadow-lg: 0 10px 30px rgba(0,0,0,0.12);
            --shadow-xl: 0 20px 60px rgba(0,0,0,0.15);
            --shadow-2xl: 0 25px 70px rgba(0,0,0,0.18);
            --glow-pro: 0 0 25px rgba(245, 101, 101, 0.5);
            --glow-premium: 0 0 30px rgba(214, 158, 46, 0.6);
            --glow-normal: 0 0 20px rgba(72, 187, 120, 0.4);
        }}

        [data-theme="dark"] {{
            --bg-primary: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            --bg-secondary: #1e293b;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --border-color: #334155;
            --stats-bg: rgba(255,255,255,0.08);
            --hover-bg: linear-gradient(135deg, #334155 0%, #475569 100%);
            --header-bg: linear-gradient(135deg, #1e293b 0%, #334155 50%, #475569 100%);
            --header-bg-animated: linear-gradient(-45deg, #1e293b, #334155, #475569, #64748b);
            --shadow-sm: 0 2px 4px rgba(0,0,0,0.4);
            --shadow-md: 0 4px 12px rgba(0,0,0,0.5);
            --shadow-lg: 0 10px 30px rgba(0,0,0,0.6);
            --shadow-xl: 0 20px 60px rgba(0,0,0,0.7);
            --shadow-2xl: 0 25px 70px rgba(0,0,0,0.8);
            --glow-pro: 0 0 30px rgba(245, 101, 101, 0.7);
            --glow-premium: 0 0 35px rgba(214, 158, 46, 0.8);
            --glow-normal: 0 0 25px rgba(72, 187, 120, 0.6);
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg-primary);
            background-attachment: fixed;
            margin: 0;
            padding: 20px;
            color: var(--text-primary);
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            line-height: 1.7;
            min-height: 100vh;
            overflow-x: hidden;
            width: 100%;
            max-width: 100vw;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: var(--bg-secondary);
            border-radius: 32px;
            box-shadow: var(--shadow-2xl);
            overflow: hidden;
            animation: fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(15px);
            border: 2px solid rgba(255,255,255,0.3);
            width: 100%;
            box-sizing: border-box;
            position: relative;
        }}

        .container::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #4facfe);
            background-size: 200% 100%;
            animation: gradientShift 3s ease infinite;
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px) scale(0.95);
            }}
            to {{
                opacity: 1;
                transform: translateY(0) scale(1);
            }}
        }}

        .header {{
            background: var(--header-bg);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            color: white;
            padding: 60px 40px 50px 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
            width: 100%;
            box-sizing: border-box;
        }}

        @keyframes gradientShift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}

        .header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 60%);
            animation: rotate 25s linear infinite;
            pointer-events: none;
            z-index: 0;
        }}

        .header-sparkle {{
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 2em;
            opacity: 0.3;
            animation: sparkle 2s ease-in-out infinite;
            z-index: 1;
            pointer-events: none;
        }}

        .header::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
        }}

        @keyframes rotate {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}

        .header h1 {{
            position: relative;
            z-index: 1;
            font-size: 3.2em;
            font-weight: 900;
            margin-bottom: 20px;
            text-shadow: 0 4px 20px rgba(0,0,0,0.3), 0 2px 5px rgba(0,0,0,0.2);
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 50%, #ffffff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: shimmer 3s ease-in-out infinite;
        }}

        @keyframes shimmer {{
            0%, 100% {{ filter: brightness(1); }}
            50% {{ filter: brightness(1.2); }}
        }}

        .logo {{
            font-size: 4em;
            margin-bottom: 10px;
            filter: drop-shadow(0 4px 15px rgba(0,0,0,0.3));
            animation: float 3s ease-in-out infinite;
        }}

        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
        }}

        .orb {{
            position: absolute;
            border-radius: 50%;
            filter: blur(30px);
            opacity: 0.5;
            animation: float 12s ease-in-out infinite;
        }}
        .orb.one {{
            width: 220px;
            height: 220px;
            top: -40px;
            left: -30px;
            background: radial-gradient(circle, rgba(255,255,255,0.4), rgba(102,126,234,0.2));
            animation-duration: 14s;
        }}
        .orb.two {{
            width: 180px;
            height: 180px;
            bottom: -30px;
            right: 0;
            background: radial-gradient(circle, rgba(255,255,255,0.35), rgba(118,75,162,0.25));
            animation-duration: 12s;
        }}

        .header-controls {{
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            z-index: 2;
        }}

        .theme-toggle, .lang-toggle {{
            background: rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 12px;
            padding: 10px 18px;
            color: white;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}

        .theme-toggle:hover, .lang-toggle:hover {{
            background: rgba(255,255,255,0.3);
            transform: scale(1.05);
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
            position: relative;
            z-index: 1;
        }}

        .stat-box {{
            background: var(--stats-bg);
            backdrop-filter: blur(20px);
            padding: 28px 24px;
            border-radius: 20px;
            text-align: center;
            border: 2px solid rgba(255,255,255,0.3);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}

        .stat-box::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }}

        .stat-box:hover::before {{
            left: 100%;
        }}

        .stat-box:hover {{
            transform: translateY(-10px) scale(1.05);
            box-shadow: 0 20px 45px rgba(0,0,0,0.3);
            border-color: rgba(255,255,255,0.6);
            z-index: 10;
        }}

        .stat-box:nth-child(1) {{
            animation-delay: 0.1s;
        }}

        .stat-box:nth-child(2) {{
            animation-delay: 0.2s;
        }}

        .stat-box:nth-child(3) {{
            animation-delay: 0.3s;
        }}

        @keyframes pulse {{
            0%, 100% {{
                transform: scale(1);
            }}
            50% {{
                transform: scale(1.05);
            }}
        }}

        .stat-box:first-child {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
        }}

        .stat-box:nth-child(2) {{
            background: linear-gradient(135deg, rgba(245, 101, 101, 0.3) 0%, rgba(229, 62, 62, 0.3) 100%);
        }}

        .stat-box:nth-child(3) {{
            background: linear-gradient(135deg, rgba(214, 158, 46, 0.3) 0%, rgba(183, 121, 31, 0.3) 100%);
        }}

        .stat-number {{
            font-size: 3.2em;
            font-weight: 900;
            display: block;
            margin-bottom: 8px;
            text-shadow: 0 3px 10px rgba(0,0,0,0.2), 0 0 20px rgba(255,255,255,0.3);
            background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 50%, #ffffff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.03em;
            animation: pulse-glow 2s ease-in-out infinite;
        }}

        @keyframes pulse-glow {{
            0%, 100% {{ filter: brightness(1); }}
            50% {{ filter: brightness(1.1); }}
        }}

        .stat-label {{
            font-size: 0.9em;
            opacity: 0.95;
            font-weight: 500;
        }}

        .table-container {{
            padding: 40px;
            width: 100%;
            box-sizing: border-box;
        }}

        .search-box {{
            margin-bottom: 30px;
            text-align: center;
            width: 100%;
            box-sizing: border-box;
        }}

        .search-input {{
            padding: 18px 28px;
            width: 100%;
            max-width: 600px;
            border: 2px solid var(--border-color);
            border-radius: 20px;
            font-size: 16px;
            outline: none;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            background: var(--bg-secondary);
            color: var(--text-primary);
            box-shadow: var(--shadow-sm);
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
        }}

        .search-input::placeholder {{
            color: var(--text-secondary);
            opacity: 0.6;
        }}

        .search-input:focus {{
            border-color: #667eea;
            box-shadow: 0 0 0 5px rgba(102, 126, 234, 0.15), var(--shadow-lg);
            transform: translateY(-3px) scale(1.02);
            background: var(--bg-secondary);
        }}

        .search-box {{
            position: relative;
        }}

        .table-wrapper {{
            width: 100%;
            overflow-x: auto;
            overflow-y: visible;
            -webkit-overflow-scrolling: touch;
            margin-top: 30px;
            box-shadow: var(--shadow-lg);
            border-radius: 20px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
        }}

        table {{
            width: 100%;
            min-width: 100%;
            max-width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            box-shadow: none;
            border-radius: 16px;
            overflow: hidden;
            background: var(--bg-secondary);
        }}

        thead {{
            background: var(--header-bg);
            color: white;
        }}

        th, td {{
            padding: 18px 24px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}

        th {{
            font-weight: 600;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 1px;
            cursor: pointer;
            user-select: none;
            transition: all 0.2s ease;
            position: relative;
        }}

        th:hover {{
            background: rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }}

        th:active {{
            transform: translateY(0);
        }}

        th::after {{
            content: ' ↕';
            opacity: 0;
            transition: opacity 0.2s;
        }}

        th:hover::after {{
            opacity: 0.5;
        }}

        tbody tr {{
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border-bottom: 1px solid var(--border-color);
        }}

        tbody tr:last-child td {{
            border-bottom: none;
        }}

        tbody tr {{
            animation: fadeInRow 0.3s ease-out;
            animation-fill-mode: both;
        }}

        @keyframes fadeInRow {{
            from {{
                opacity: 0;
                transform: translateX(-10px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}

        tbody tr:nth-child(even) {{
            background: rgba(0,0,0,0.02);
        }}

        [data-theme="dark"] tbody tr:nth-child(even) {{
            background: rgba(255,255,255,0.02);
        }}

        tbody tr:hover {{
            background: var(--hover-bg) !important;
            transform: translateX(5px) scale(1.005);
            box-shadow: var(--shadow-md);
            z-index: 1;
            position: relative;
        }}

        .user-id {{
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            font-weight: 600;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 0.95em;
            letter-spacing: 0.5px;
        }}

        .username {{
            background: linear-gradient(135deg, #764ba2 0%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 600;
            letter-spacing: 0.3px;
        }}

        .pro-status {{
            background: var(--pro-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
            text-shadow: var(--glow-pro);
            position: relative;
            padding: 4px 12px;
            border-radius: 8px;
            display: inline-block;
            background-color: rgba(245, 101, 101, 0.1);
        }}

        .normal-status {{
            background: var(--normal-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 600;
            text-shadow: var(--glow-normal);
            position: relative;
            padding: 4px 12px;
            border-radius: 8px;
            display: inline-block;
            background-color: rgba(72, 187, 120, 0.1);
        }}

        .premium-status {{
            background: var(--premium-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
            text-shadow: var(--glow-premium);
            font-family: 'JetBrains Mono', monospace;
        }}

        .premium-status code {{
            background: linear-gradient(135deg, rgba(214, 158, 46, 0.15) 0%, rgba(183, 121, 31, 0.15) 100%);
            padding: 6px 12px;
            border-radius: 8px;
            border: 1px solid rgba(214, 158, 46, 0.3);
        }}

        .no-data {{
            text-align: center;
            padding: 60px 20px;
            color: var(--text-secondary);
            font-style: italic;
            font-size: 1.1em;
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 8px;
                overflow-x: hidden;
                -webkit-overflow-scrolling: touch;
            }}

            .container {{
                border-radius: 20px;
                margin: 0;
                width: 100%;
            }}

            .header {{
                padding: 25px 15px;
            }}

            .header h1 {{
                font-size: 1.6em;
                line-height: 1.2;
                word-wrap: break-word;
            }}

            .header-controls {{
                top: 8px;
                right: 8px;
                flex-direction: column;
                gap: 8px;
            }}

            .theme-toggle, .lang-toggle {{
                padding: 8px 12px;
                font-size: 11px;
                border-radius: 10px;
            }}

            .stats {{
                grid-template-columns: repeat(2, 1fr);
                gap: 12px;
                margin-top: 20px;
            }}

            .table-container {{
                padding: 12px;
            }}

            .table-wrapper {{
                margin-top: 12px;
                border-radius: 12px;
                -webkit-overflow-scrolling: touch;
                scrollbar-width: thin;
            }}

            .table-wrapper::-webkit-scrollbar {{
                height: 8px;
            }}

            .table-wrapper::-webkit-scrollbar-track {{
                background: var(--border-color);
                border-radius: 4px;
            }}

            .table-wrapper::-webkit-scrollbar-thumb {{
                background: #667eea;
                border-radius: 4px;
            }}

            table {{
                min-width: 100%;
            }}

            th, td {{
                padding: 10px 12px;
                font-size: 0.8em;
                word-wrap: break-word;
            }}

            .search-input {{
                max-width: 100%;
                padding: 12px 16px;
                font-size: 14px;
                border-radius: 12px;
            }}

            .stat-box {{
                padding: 12px;
                border-radius: 16px;
            }}

            .stat-number {{
                font-size: 1.8em;
            }}

            .stat-label {{
                font-size: 0.8em;
            }}
        }}

        @media (max-width: 480px) {{
            body {{
                padding: 5px;
                overflow-x: hidden;
            }}

            .container {{
                border-radius: 16px;
            }}

            .header {{
                padding: 20px 12px;
            }}

            .header h1 {{
                font-size: 1.3em;
                margin-bottom: 8px;
            }}

            .header-controls {{
                top: 5px;
                right: 5px;
                flex-direction: column;
                gap: 6px;
            }}

            .theme-toggle, .lang-toggle {{
                padding: 6px 10px;
                font-size: 10px;
            }}

            .stats {{
                grid-template-columns: 1fr;
                gap: 10px;
                margin-top: 15px;
            }}

            .table-container {{
                padding: 10px;
            }}

            .table-wrapper {{
                margin-top: 10px;
                border-radius: 10px;
            }}

            table {{
                min-width: 100%;
            }}

            .search-input {{
                padding: 10px 14px;
                font-size: 13px;
            }}

            th, td {{
                padding: 8px 10px;
                font-size: 0.75em;
            }}

            th {{
                font-size: 0.7em;
                padding: 8px 8px;
            }}

            .stat-box {{
                padding: 10px;
            }}

            .stat-number {{
                font-size: 1.6em;
            }}

            .stat-label {{
                font-size: 0.75em;
            }}
        }}

        @media (max-width: 360px) {{
            body {{
                padding: 4px;
            }}

            .header {{
                padding: 15px 10px;
            }}

            .header h1 {{
                font-size: 1.1em;
            }}

            table {{
                min-width: 100%;
            }}

            th, td {{
                padding: 6px 8px;
                font-size: 0.7em;
            }}

            th {{
                font-size: 0.65em;
            }}
        }}

        @media (orientation: landscape) and (max-height: 500px) {{
            .header {{
                padding: 15px 20px;
            }}

            .header h1 {{
                font-size: 1.2em;
                margin-bottom: 5px;
            }}

            .stats {{
                margin-top: 10px;
                gap: 8px;
            }}

            .stat-box {{
                padding: 8px;
            }}

            .stat-number {{
                font-size: 1.4em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="orb one"></div>
            <div class="orb two"></div>
            <a href="https://t.me/{bot_username}" class="theme-toggle" style="position:absolute; top:20px; left:20px; text-decoration:none; z-index:3; pointer-events:auto;">🤖 RetroTag</a>
            <div class="header-controls">
                <button class="lang-toggle" onclick="toggleLanguage()" id="langBtn">Русский</button>
                <button class="theme-toggle" onclick="toggleTheme()" id="themeBtn">🌙 Dark Theme</button>
            </div>
            <div class="logo">🎯</div>
            <h1 data-lang="en">✨ Users Database</h1>
            <h1 data-lang="ru" style="display:none;">✨ База данных</h1>
            <div class="stats">
                <div class="stat-box">
                    <span class="stat-number">{total_users}</span>
                    <span class="stat-label" data-lang="en">👥 Total Users</span>
                    <span class="stat-label" data-lang="ru" style="display:none;">👥 Все </span>
                </div>
                <div class="stat-box">
                    <span class="stat-number">{premium_count}</span>
                    <span class="stat-label" data-lang="en">⭐ Premium Users</span>
                    <span class="stat-label" data-lang="ru" style="display:none;">⭐ Premium </span>
                </div>
            </div>
        </div>
        <div class="table-container">
            <div class="search-box">
                <input type="text" class="search-input" id="searchInput"
                       data-placeholder-en="🔍 Search by ID, name or username..."
                       data-placeholder-ru="🔍 Поиск по ID, имени или username..."
                       placeholder="🔍 Search by ID, name or username..."
                       onkeyup="searchUsers(this.value)">
            </div>
            <div class="table-wrapper">
                <table id="usersTable">
                    <thead>
                        <tr>
                            <th onclick="sortTable(0)">
                                <span data-lang="en">🆔 User ID</span>
                                <span data-lang="ru" style="display:none;">🆔 ID пользователя</span>
                            </th>
                            <th onclick="sortTable(1)">
                                <span data-lang="en">👤 Name</span>
                                <span data-lang="ru" style="display:none;">👥 Имя</span>
                            </th>
                            <th onclick="sortTable(2)">
                                <span data-lang="en">👤 Username</span>
                                <span data-lang="ru" style="display:none;">👤 Username</span>
                            </th>
                            <th onclick="sortTable(3)">
                                <span data-lang="en">⭐ Status</span>
                                <span data-lang="ru" style="display:none;">⭐ Статус</span>
                            </th>
                            <th onclick="sortTable(4)">
                                <span data-lang="en">📊 Time Left</span>
                                <span data-lang="ru" style="display:none;">📊 Осталось</span>
                            </th>
                        </tr>
                    </thead>
                    <tbody>"""

    if users_list :
        for user in users_list :
            html_content +=f"""
                    <tr>
                        <td class="user-id">{user['id']}</td>
                        <td>{user['name']}</td>
                        <td class="username">{user['username']}</td>
                        <td>"""+("<span class='premium-status'>"if user ['is_premium']else "<span class='normal-status'>")+f"""{user['status']}</span></td>
                        <td class="premium-status"><code>{user['time_left']}</code></td>
                    </tr>"""
    else :
        html_content +="""
                    <tr>
                        <td colspan="5" class="no-data">
                            <span data-lang="en">No users found</span>
                            <span data-lang="ru" style="display:none;">Пользователи не найдены</span>
                        </td>
                    </tr>"""

    html_content +="""
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <script>
        function toggleLanguage() {{
            const html = document.documentElement;
            const langBtn = document.getElementById('langBtn');
            const searchInput = document.getElementById('searchInput');
            const themeBtn = document.getElementById('themeBtn');
            const currentLang = html.lang;
            const newLang = currentLang === 'en' ? 'ru' : 'en';

            html.lang = newLang;
            html.id = 'htmlLang';
            localStorage.setItem('language', newLang);

            document.querySelectorAll('[data-lang]').forEach(el => {{
                if (el.getAttribute('data-lang') === newLang) {{
                    el.style.display = '';
                }} else {{
                    el.style.display = 'none';
                }}
            }});

            if (newLang === 'ru') {{
                langBtn.textContent = 'Русский';
                if (searchInput) {{
                    searchInput.placeholder = searchInput.getAttribute('data-placeholder-ru');
                }}
                if (themeBtn) {{
                    const isDark = document.body.getAttribute('data-theme') === 'dark';
                    themeBtn.textContent = isDark ? '☀️ Светлая тема' : '🌙 Тёмная тема';
                }}
            }} else {{
                langBtn.textContent = 'English';
                if (searchInput) {{
                    searchInput.placeholder = searchInput.getAttribute('data-placeholder-en');
                }}
                if (themeBtn) {{
                    const isDark = document.body.getAttribute('data-theme') === 'dark';
                    themeBtn.textContent = isDark ? '☀️ Light Theme' : '🌙 Dark Theme';
                }}
            }}
        }}

        function toggleTheme() {{
            const body = document.body;
            const button = document.getElementById('themeBtn');
            const isDark = body.getAttribute('data-theme') === 'dark';
            const lang = document.documentElement.lang;

            if (isDark) {{
                body.removeAttribute('data-theme');
                button.textContent = lang === 'ru' ? '🌙 Тёмная тема' : '🌙 Dark Theme';
                localStorage.setItem('theme', 'light');
            }} else {{
                body.setAttribute('data-theme', 'dark');
                button.textContent = lang === 'ru' ? '☀️ Светлая тема' : '☀️ Light Theme';
                localStorage.setItem('theme', 'dark');
            }}
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            const savedLang = localStorage.getItem('language') || 'en';
            document.documentElement.lang = savedLang;
            document.documentElement.id = 'htmlLang';

            document.querySelectorAll('[data-lang]').forEach(el => {{
                if (el.getAttribute('data-lang') === savedLang) {{
                    el.style.display = '';
                }} else {{
                    el.style.display = 'none';
                }}
            }});

            const langBtn = document.getElementById('langBtn');
            const searchInput = document.getElementById('searchInput');
            if (savedLang === 'ru') {{
                langBtn.textContent = 'Русский';
                if (searchInput) {{
                    searchInput.placeholder = searchInput.getAttribute('data-placeholder-ru');
                }}
            }} else {{
                langBtn.textContent = 'English';
                if (searchInput) {{
                    searchInput.placeholder = searchInput.getAttribute('data-placeholder-en');
                }}
            }}

            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'dark') {{
                document.body.setAttribute('data-theme', 'dark');
                const themeBtn = document.getElementById('themeBtn');
                if (themeBtn) {{
                    themeBtn.textContent = savedLang === 'ru' ? '☀️ Светлая тема' : '☀️ Light Theme';
                }}
            }} else {{
                const themeBtn = document.getElementById('themeBtn');
                if (themeBtn) {{
                    themeBtn.textContent = savedLang === 'ru' ? '🌙 Тёмная тема' : '🌙 Dark Theme';
                }}
            }}
        }});

        function searchUsers(query) {
            const rows = document.querySelectorAll('#usersTable tbody tr');
            const searchTerm = query.toLowerCase();
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                let found = false;
                cells.forEach(cell => {
                    if (cell.textContent.toLowerCase().includes(searchTerm)) {
                        found = true;
                    }
                });
                row.style.display = found ? '' : 'none';
            });
        }

        function sortTable(columnIndex) {
            const table = document.getElementById('usersTable');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const isAscending = table.getAttribute('data-sort-order') !== 'asc';

            rows.sort((a, b) => {
                const aText = a.cells[columnIndex].textContent.trim();
                const bText = b.cells[columnIndex].textContent.trim();

                // Для числовых значений
                if (!isNaN(aText) && !isNaN(bText)) {
                    return isAscending ? aText - bText : bText - aText;
                }

                // Для текстовых значений
                return isAscending ?
                    aText.localeCompare(bText, 'ru') :
                    bText.localeCompare(aText, 'ru');
            });

            // Очистка и добавление отсортированных строк
            tbody.innerHTML = '';
            rows.forEach(row => tbody.appendChild(row));

            // Обновление атрибута сортировки
            table.setAttribute('data-sort-order', isAscending ? 'asc' : 'desc');
        }
    </script>
</body>
</html>"""

    with open ('db.html','w',encoding ='utf-8')as f :
        f .write (html_content )

    try :
        with open ('db.html','rb')as f :
            caption_text ="<b>📋 Таблица пользователей</b>"if lang =="ru"else "<b>📋 Users table</b>"
            await bot .send_document (
            callback_query .from_user .id ,
            f ,
            caption =caption_text ,
            protect_content =True
            )
    except Exception as e :
        error_prefix ="<b>❌ Ошибка при отправке файла:</b>\n"if lang =="ru"else "<b>❌ Error sending file:</b>\n"
        await bot .send_message (
        callback_query .from_user .id ,
        f"{error_prefix}<code>{str(e)}</code>",
        protect_content =True
        )

@dp.inline_query()
async def inline_query_handler (query :types .InlineQuery ):
    """Обработчик inline-запросов для автозаполнения"""
    if hasattr (query .from_user ,'is_bot')and query .from_user .is_bot :
        return

    query_text =query .query .strip ().lower ()
    results =[]

    if len (query_text )>=2 :
        try :
            cursor =users .find ({
            "$or":[
            {"username":{"$regex":query_text ,"$options":"i"}},
            {"first_name":{"$regex":query_text ,"$options":"i"}},
            {"last_name":{"$regex":query_text ,"$options":"i"}}
            ]
            }).limit (10 )

            async for user_doc in cursor :
                user_id =user_doc .get ("user_id")
                username =user_doc .get ("username","")
                first_name =user_doc .get ("first_name","")
                last_name =user_doc .get ("last_name","")
                full_name =f"{first_name} {last_name}".strip ()or "Unknown"

                title =f"@{username}"if username else f"{full_name} ({user_id})"
                description =f"ID: {user_id}"if username else f"Username: @{username}"if username else f"ID: {user_id}"

                results .append (
                InlineQueryResultArticle (
                id =str (user_id ),
                title =title ,
                description =description ,
                input_message_content =InputTextMessageContent (
                message_text =f"@{username}"if username else str (user_id )
                )
                )
                )
        except Exception as e :
            logging .error (f"Ошибка в inline query: {e}")

    await query .answer (results ,cache_time =60 )

async def main ():
    global client ,db ,users ,history ,chats ,whitelist ,privacy_log ,user_languages ,premium_subscriptions ,promo_codes ,chat_languages ,api_queue

    client =AsyncIOMotorClient (MONGODB_URI )
    db =client [DB_NAME ]

    users =db ["users"]
    history =db ["history"]
    chats =db ["chats"]
    whitelist =db ["whitelist"]
    privacy_log =db ["privacy_log"]
    user_languages =db ["user_languages"]
    premium_subscriptions =db ["premium_subscriptions"]
    promo_codes =db ["promo_codes"]
    chat_languages =db ["chat_languages"]

    api_queue =asyncio .Queue (maxsize =25 )

    await init_db ()
    global BOT_USERNAME
    try:
        me = await bot.get_me()
        BOT_USERNAME = me.username
    except Exception:
        BOT_USERNAME = None
    try:
        group_commands = [
            types.BotCommand(command='chatid', description='Show this chat ID')
        ]
        private_commands = [
            types.BotCommand(command='start', description='Start | Старт'),
            types.BotCommand(command='me', description='Show history | Показать историю'),
            types.BotCommand(command='id', description='Show ID | Показать ID'),
            types.BotCommand(command='lang', description='Language | Язык'),
            types.BotCommand(command='premium', description='Premium | Премиум')
        ]

        await bot.set_my_commands(group_commands, scope=types.BotCommandScopeAllGroupChats())
        await bot.set_my_commands(private_commands, scope=types.BotCommandScopeAllPrivateChats())
    except Exception as e:
        logging.warning(f"Failed to set bot commands: {e}")
    print ("🎯 RetroTag запущен!")
    print ("🔄 Собираю информацию...")
    try:
        mem_pending = globals().get('pending_searches')
        if isinstance(mem_pending, dict) and mem_pending:
            for uid, item in mem_pending.items():
                try:
                    await db["pending_searches"].update_one(
                        {"user_id": int(uid)},
                        {"$set": {"user_id": int(uid), "type": item.get('type'), "value": item.get('value'), "created_at": datetime.now()}},
                        upsert=True,
                    )
                except Exception:
                    pass
            try:
                mem_pending.clear()
            except Exception:
                pass
    except Exception:
        pass

    asyncio .create_task (api_rate_limiter ())

    async for chat_doc in chats .find ({}):
        if chat_doc ["chat_id"]<0 :
            asyncio .create_task (collect_chat_members (chat_doc ["chat_id"]))

    asyncio .create_task (update_all_users ())

    await dp .start_polling (bot )

if __name__ =="__main__":
    asyncio .run (main ())
