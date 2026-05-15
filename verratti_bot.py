import logging
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = [int(os.environ.get("ADMIN_ID", "0"))]

pronos = []
abonnes = set()

def is_admin(user_id):
    return user_id in ADMIN_IDS

def sport_emoji(sport):
    emojis = {"football": "⚽", "basketball": "🏀", "tennis": "🎾", "autres": "🏆"}
    return emojis.get(sport.lower(), "🏆")

def format_prono(p):
    emoji = sport_emoji(p["sport"])
    statut_map = {"en_cours": "🟡 En cours", "gagnant": "✅ Gagnant", "perdant": "❌ Perdant"}
    statut = statut_map.get(p["statut"], "🟡 En cours")
    return f"#{p['id']} {emoji} *{p['sport'].upper()}*\n🆚 {p['match']}\n📌 Prono : *{p['prono']}*\n📈 Cote : *{p['cote']}*\n📅 Date : {p['date']}\n🔖 Statut : {statut}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    abonnes.add(user.id)
    clavier = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚽ Football", callback_data="sport_football"), InlineKeyboardButton("🏀 Basketball", callback_data="sport_basketball")],
        [InlineKeyboardButton("🎾 Tennis", callback_data="sport_tennis"), InlineKeyboardButton("🏆 Autres", callback_data="sport_autres")],
        [InlineKeyboardButton("📋 Tous les pronos", callback_data="tous_pronos")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
    ])
    await update.message.reply_text(f"👋 Bienvenue *{user.first_name}* sur *VERRATTI PRONO PRO* !\n\n🔥 Les meilleurs pronos sportifs, gratuits.\n\nChoisis​​​​​​​​​​​​​​​​
