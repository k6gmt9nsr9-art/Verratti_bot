import logging
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

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
    return (f"#{p['id']} {emoji} *{p['sport'].upper()}*\n🆚 {p['match']}\n📌 Prono : *{p['prono']}*\n📈 Cote : *{p['cote']}*\n📅 Date : {p['date']}\n🔖 Statut : {statut}")

def start(update, context):
    user = update.effective_user
    abonnes.add(user.id)
    clavier = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚽ Football", callback_data="sport_football"), InlineKeyboardButton("🏀 Basketball", callback_data="sport_basketball")],
        [InlineKeyboardButton("🎾 Tennis", callback_data="sport_tennis"), InlineKeyboardButton("🏆 Autres", callback_data="sport_autres")],
        [InlineKeyboardButton("📋 Tous les pronos", callback_data="tous_pronos")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
    ])
    update.message.reply_text(f"👋 Bienvenue *{user.first_name}* sur *VERRATTI PRONO PRO* !\n\n🔥 Les meilleurs pronos sportifs, gratuits.\n\nChoisis un sport :", parse_mode="Markdown", reply_markup=clavier)

def pronos_command(update, context):
    if not pronos:
        update.message.reply_text("😴 Aucun prono disponible pour l'instant.")
        return
    for p in pronos:
        update.message.reply_text(format_prono(p), parse_mode="Markdown")

def stats_command(update, context):
    total = len(pronos)
    gagnants = sum(1 for p in pronos if p["statut"] == "gagnant")
    perdants = sum(1 for p in pronos if p["statut"] == "perdant")
    taux = round((gagnants / (gagnants + perdants)) * 100, 1) if (gagnants + perdants) > 0 else 0
    update.message.reply_text(f"📊 *Stats VERRATTI PRONO PRO*\n\n📝 Total : {total}\n✅ Gagnants : {gagnants}\n❌ Perdants : {perdants}\n🎯 Taux : *{taux}%*", parse_mode="Markdown")

def ajouter_command(update, context):
    if not is_admin(update.effective_user.id):
        update.message.reply_text("❌ Réservé aux admins.")
        return
    args = context.args
    if len(args) < 4:
        update.message.reply_text("⚠️ Usage : `/ajouter [sport] [match] [prono] [cote]`", parse_mode="Markdown")
        return
    sport, match, prono_val, cote = args[0], args[1].replace("-", " "), args[2].replace("-", " "), args[3]
    nouveau = {"id": len(pronos) + 1, "sport": sport, "match": match, "prono": prono_val, "cote": cote, "date": datetime.now().strftime("%d/%m/%Y %H:%M"), "statut": "en_cours"}
    pronos.append(nouveau)
    msg = f"🔔 *Nouveau prono !*\n\n{format_prono(nouveau)}"
    for uid in abonnes:
        try:
            context.bot.send_message(chat_id=uid, text=msg, parse_mode="Markdown")
        except:
            pass
    update.message.reply_text(f"✅ Prono #{nouveau['id']} ajouté et envoyé à {len(abonnes)} abonné(s) !")

def modifier_command(update, context):
    if not is_admin(update.effective_user.id):
        update.message.reply_text("❌ Réservé aux admins.")
        return
    args = context.args
    if len(args) < 2:
        update.message.reply_text("⚠️ Usage : `/modifier [id] [gagnant|perdant|en_cours]`", parse_mode="Markdown")
        return
    prono_id, nouveau_statut = int(args[0]), args[1].lower()
    for p in pronos:
        if p["id"] == prono_id:
            p["statut"] = nouveau_statut
            msg = f"🔔 *Résultat mis à jour !*\n\n{format_prono(p)}"
            for uid in abonnes:
                try:
                    context.bot.send_message(chat_id=uid, text=msg, parse_mode="Markdown")
                except:
                    pass
            update.message.reply_text(f"✅ Prono #{prono_id} → {nouveau_statut}")
            return
    update.message.reply_text(f"❌ Prono #{prono_id} introuvable.")

def broadcast_command(update, context):
    if not is_admin(update.effective_user.id):
        update.message.reply_text("❌ Réservé aux admins.")
        return
    message = " ".join(context.args)
    count = 0
    for uid in abonnes:
        try:
            context.bot.send_message(chat_id=uid, text=f"📢 *Annonce*\n\n{message}", parse_mode="Markdown")
            count += 1
        except:
            pass
    update.message.reply_text(f"✅ Envoyé à {count} abonné(s).")

def button_handler(update, context):
    query = update.callback_query
    query.answer()
    data = query.data
    if data == "tous_pronos":
        if not pronos:
            query.message.reply_text("😴 Aucun prono disponible.")
            return
        for p in pronos:
            query.message.reply_text(format_prono(p), parse_mode="Markdown")
    elif data == "stats":
        total = len(pronos)
        gagnants = sum(1 for p in pronos if p["statut"] == "gagnant")
        perdants = sum(1 for p in pronos if p["statut"] == "perdant")
        taux = round((gagnants / (gagnants + perdants)) * 100, 1) if (gagnants + perdants) > 0 else 0
        query.message.reply_text(f"📊 Total: {total} | ✅ {gagnants} | ❌ {perdants} | 🎯 {taux}%", parse_mode="Markdown")
    elif data.startswith("sport_"):
        sport = data.replace("sport_", "")
        filtres = [p for p in pronos if p["sport"].lower() == sport]
        if not filtres:
            query.message.reply_text(f"{sport_emoji(sport)} Aucun prono {sport} disponible.")
            return
        for p in filtres:
            query.message.reply_text(format_prono(p), parse_mode="Markdown")

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("pronos", pronos_command))
    dp.add_handler(CommandHandler("stats", stats_command))
    dp.add_handler(CommandHandler("ajouter", ajouter_command))
    dp.add_handler(CommandHandler("modifier", modifier_command))
    dp.add_handler(CommandHandler("broadcast", broadcast_command))
    dp.add_handler(CallbackQueryHandler(button_handler))
    logger.info("🚀 Bot démarré !")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
