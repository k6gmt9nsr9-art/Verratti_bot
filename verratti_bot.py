# -*- coding: utf-8 -*-

import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
ADMINS = [int(os.environ.get("ADMIN_ID", "0"))]
pronos = []
abonnes = set()

def is_admin(uid):
    return uid in ADMINS

def format_prono(p):
s = {"en_cours": "En cours", "gagnant": "GAGNANT", "perdant": "PERDANT"}.get(p["statut"], "?")
return "#" + str(p["id"]) + " " + p["sport"] + "\n" + p["match"] + "\nProno: " + p["prono"] + "\nCote: " + p["cote"] + "\nDate: " + p["date"] + "\nStatut: " + s

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
abonnes.add(update.effective_user.id)
nom = update.effective_user.first_name
kb = InlineKeyboardMarkup([
[InlineKeyboardButton("Football", callback_data="s_football"), InlineKeyboardButton("Basketball", callback_data="s_basketball")],
[InlineKeyboardButton("Tennis", callback_data="s_tennis"), InlineKeyboardButton("Autres", callback_data="s_autres")],
[InlineKeyboardButton("Tous les pronos", callback_data="tous")],
[InlineKeyboardButton("Stats", callback_data="stats")],
])
await update.message.reply_text("Bienvenue " + nom + " sur VERRATTI PRONO PRO ! Choisis un sport :", reply_markup=kb)

async def cmd_pronos(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not pronos:
await update.message.reply_text("Aucun prono disponible.")
return
for p in pronos:
await update.message.reply_text(format_prono(p))

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
total = len(pronos)
g = sum(1 for p in pronos if p["statut"] == "gagnant")
pe = sum(1 for p in pronos if p["statut"] == "perdant")
t = round((g / (g + pe)) * 100, 1) if (g + pe) > 0 else 0
await update.message.reply_text("Total=" + str(total) + " G=" + str(g) + " P=" + str(pe) + " Taux=" + str(t) + "%")

async def cmd_ajouter(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not is_admin(update.effective_user.id):
await update.message.reply_text("Interdit.")
return
a = context.args
if len(a) < 4:
await update.message.reply_text("Usage: /ajouter sport match prono cote")
return
p = {"id": len(pronos) + 1, "sport": a[0], "match": a[1].replace("-", " "), "prono": a[2].replace("-", " "), "cote": a[3], "date": datetime.now().strftime("%d/%m/%Y %H:%M"), "statut": "en_cours"}
pronos.append(p)
for uid in abonnes:
try:
await context.bot.send_message(chat_id=uid, text="Nouveau prono!\n\n" + format_prono(p))
except Exception:
pass
await update.message.reply_text("Prono ajoute!")

async def cmd_modifier(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not is_admin(update.effective_user.id):
await update.message.reply_text("Interdit.")
return
a = context.args
if len(a) < 2:
await update.message.reply_text("Usage: /modifier id statut")
return
pid = int(a[0])
for p in pronos:
if p["id"] == pid:
p["statut"] = a[1]
for uid in abonnes:
try:
await context.bot.send_message(chat_id=uid, text="Resultat!\n\n" + format_prono(p))
except Exception:
pass
await update.message.reply_text("Mis a jour!")
return
await update.message.reply_text("Introuvable.")

async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not is_admin(update.effective_user.id):
await update.message.reply_text("Interdit.")
return
msg = " ".join(context.args)
n = 0
for uid in abonnes:
try:
await context.bot.send_message(chat_id=uid, text=msg)
n += 1
except Exception:
pass
await update.message.reply_text("Envoye a " + str(n) + " personnes.")

async def bouton(update: Update, context: ContextTypes.DEFAULT_TYPE):
q = update.callback_query
await q.answer()
d = q.data
if d == "tous":
if not pronos:
await q.message.reply_text("Aucun prono.")
return
for p in pronos:
await q.message.reply_text(format_prono(p))
elif d == "stats":
total = len(pronos)
g = sum(1 for p in pronos if p["statut"] == "gagnant")
pe = sum(1 for p in pronos if p["statut"] == "perdant")
t = round((g / (g + pe)) * 100, 1) if (g + pe) > 0 else 0
await q.message.reply_text("Total=" + str(total) + " G=" + str(g) + " P=" + str(pe) + " Taux=" + str(t) + "%")
elif d.startswith("s_"):
sport = d[2:]
fl = [p for p in pronos if p["sport"].lower() == sport]
if not fl:
await q.message.reply_text("Aucun prono pour " + sport)
return
for p in fl:
await q.message.reply_text(format_prono(p))

def main():
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("pronos", cmd_pronos))
app.add_handler(CommandHandler("stats", cmd_stats))
app.add_handler(CommandHandler("ajouter", cmd_ajouter))
app.add_handler(CommandHandler("modifier", cmd_modifier))
app.add_handler(CommandHandler("broadcast", cmd_broadcast))
app.add_handler(CallbackQueryHandler(bouton))
print("Bot demarre!")
app.run_polling()

main()