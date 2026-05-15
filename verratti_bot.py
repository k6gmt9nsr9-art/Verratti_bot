import logging
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = [int(os.environ.get("ADMIN_ID", "0"))]
pronos = []
abonnes = set()

def is_admin(user_id):
return user_id in ADMIN_IDS

def format_prono(p):
statut = {"en_cours": "En cours", "gagnant": "GAGNANT", "perdant": "PERDANT"}.get(p["statut"], "En cours")
return "#" + str(p["id"]) + " " + p["sport"].upper() + "\nMatch : " + p["match"] + "\nProno : " + p["prono"] + "\nCote : " + p["cote"] + "\nDate : " + p["date"] + "\nStatut : " + statut

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
user = update.effective_user
abonnes.add(user.id)
clavier = InlineKeyboardMarkup([
[InlineKeyboardButton("Football", callback_data="sport_football"), InlineKeyboardButton("Basketball", callback_data="sport_basketball")],
[InlineKeyboardButton("Tennis", callback_data="sport_tennis"), InlineKeyboardButton("Autres", callback_data="sport_autres")],
[InlineKeyboardButton("Tous les pronos", callback_data="tous_pronos")],
[InlineKeyboardButton("Stats", callback_data="stats")],
])
await update.message.reply_text("Bienvenue " + user.first_name + " sur VERRATTI PRONO PRO ! Les meilleurs pronos gratuits. Choisis un sport :", reply_markup=clavier)

async def pronos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not pronos:
await update.message.reply_text("Aucun prono disponible.")
return
for p in pronos:
await update.message.reply_text(format_prono(p))

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
total = len(pronos)
gagnants = sum(1 for p in pronos if p["statut"] == "gagnant")
perdants = sum(1 for p in pronos if p["statut"] == "perdant")
taux = round((gagnants / (gagnants + perdants)) * 100, 1) if (gagnants + perdants) > 0 else 0
await update.message.reply_text("Stats : Total=" + str(total) + " Gagnants=" + str(gagnants) + " Perdants=" + str(perdants) + " Taux=" + str(taux) + "%")

async def ajouter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not is_admin(update.effective_user.id):
await update.message.reply_text("Reserve aux admins.")
return
args = context.args
if len(args) < 4:
await update.message.reply_text("Usage : /ajouter sport match prono cote")
return
nouveau = {"id": len(pronos) + 1, "sport": args[0], "match": args[1].replace("-", " "), "prono": args[2].replace("-", " "), "cote": args[3], "date": datetime.now().strftime("%d/%m/%Y %H:%M"), "statut": "en_cours"}
pronos.append(nouveau)
for uid in abonnes:
try:
await context.bot.send_message(chat_id=uid, text="Nouveau prono !\n\n" + format_prono(nouveau))
except Exception:
pass
await update.message.reply_text("Prono ajoute !")

async def modifier_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not is_admin(update.effective_user.id):
await update.message.reply_text("Reserve aux admins.")
return
args = context.args
if len(args) < 2:
await update.message.reply_text("Usage : /modifier id statut")
return
prono_id = int(args[0])
for p in pronos:
if p["id"] == prono_id:
p["statut"] = args[1].lower()
for uid in abonnes:
try:
await context.bot.send_message(chat_id=uid, text="Resultat mis a jour !\n\n" + format_prono(p))
except Exception:
pass
await update.message.reply_text("Prono mis a jour !")
return
await update.message.reply_text("Prono introuvable.")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not is_admin(update.effective_user.id):
await update.message.reply_text("Reserve aux admins.")
return
message = " ".join(context.args)
count = 0
for uid in abonnes:
try:
await context.bot.send_message(chat_id=uid, text="Annonce : " + message)
count += 1
except Exception:
pass
await update.message.reply_text("Envoye a " + str(count) + " personnes.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()
data = query.data
if data == "tous_pronos":
if not pronos:
await query.message.reply_text("Aucun prono disponible.")
return
for p in pronos:
await query.message.reply_text(format_prono(p))
elif data == "stats":
total = len(pronos)
gagnants = sum(1 for p in pronos if p["statut"] == "gagnant")
perdants = sum(1 for p in pronos if p["statut"] == "perdant")
taux = round((gagnants / (gagnants + perdants)) * 100, 1) if (gagnants + perdants) > 0 else 0
await query.message.reply_text("Total=" + str(total) + " Gagnants=" + str(gagnants) + " Perdants=" + str(perdants) + " Taux=" + str(taux) + "%")
elif data.startswith("sport_"):
sport = data.replace("sport_", "")
filtres = [p for p in pronos if p["sport"].lower() == sport]
if not filtres:
await query.message.reply_text("Aucun prono " + sport + " disponible.")
return
for p in filtres:
await query.message.reply_text(format_prono(p))

def main():
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("pronos", pronos_command))
app.add_handler(CommandHandler("stats", stats_command))
app.add_handler(CommandHandler("ajouter", ajouter_command))
app.add_handler(CommandHandler("modifier", modifier_command))
app.add_handler(CommandHandler("broadcast", broadcast_command))
app.add_handler(CallbackQueryHandler(button_handler))
logger.info("Bot demarre !")
app.run_polling()

if **name** == "**main**":
main()