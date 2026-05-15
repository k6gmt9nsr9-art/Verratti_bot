# -*- coding: utf-8 -*-
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
ADMINS = [int(os.environ.get("ADMIN_ID", "0"))]
pronos = []
abonnes = set()

def is_admin(uid): return uid in ADMINS

def fmt(p):
	st = {"en_cours":"En cours","gagnant":"GAGNANT","perdant":"PERDANT"}.get(p["statut"],"?")
	return "#"+str(p["id"])+" "+p["sport"]+"\n"+p["match"]+"\nProno:"+p["prono"]+"\nCote:"+p["cote"]+"\nDate:"+p["date"]+"\nStatut:"+st

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
	abonnes.add(u.effective_user.id)
	kb = InlineKeyboardMarkup([[InlineKeyboardButton("Football",callback_data="s_football"),InlineKeyboardButton("Basketball",callback_data="s_basketball")],[InlineKeyboardButton("Tennis",callback_data="s_tennis"),InlineKeyboardButton("Autres",callback_data="s_autres")],[InlineKeyboardButton("Tous les pronos",callback_data="tous")],[InlineKeyboardButton("Stats",callback_data="stats")]])
	await u.message.reply_text("Bienvenue "+u.effective_user.first_name+" sur VERRATTI PRONO PRO ! Choisis un sport :",reply_markup=kb)

async def cmd_pronos(u: Update, c: ContextTypes.DEFAULT_TYPE):
	if not pronos: await u.message.reply_text("Aucun prono."); return
	for p in pronos: await u.message.reply_text(fmt(p))

async def cmd_stats(u: Update, c: ContextTypes.DEFAULT_TYPE):
	g=sum(1 for p in pronos if p["statut"]=="gagnant"); pe=sum(1 for p in pronos if p["statut"]=="perdant"); t=round((g/(g+pe))*100,1) if (g+pe)>0 else 0
	await u.message.reply_text("Total="+str(len(pronos))+" G="+str(g)+" P="+str(pe)+" Taux="+str(t)+"%")

async def cmd_ajouter(u: Update, c: ContextTypes.DEFAULT_TYPE):
	if not is_admin(u.effective_user.id): await u.message.reply_text("Interdit."); return
	a=c.args
	if len(a)<4: await u.message.reply_text("Usage: /ajouter sport match prono cote"); return
	p={"id":len(pronos)+1,"sport":a[0],"match":a[1].replace("-"," "),"prono":a[2].replace("-"," "),"cote":a[3],"date":datetime.now().strftime("%d/%m/%Y %H:%M"),"statut":"en_cours"}
	pronos.append(p)
	for uid in abonnes:
		try: await c.bot.send_message(chat_id=uid,text="Nouveau prono!\n\n"+fmt(p))
		except: pass
	await u.message.reply_text("Prono ajoute!")

async def cmd_modifier(u: Update, c: ContextTypes.DEFAULT_TYPE):
	if not is_admin(u.effective_user.id): await u.message.reply_text("Interdit."); return
	a=c.args
	if len(a)<2: await u.message.reply_text("Usage: /modifier id statut"); return
	for p in pronos:
		if p["id"]==int(a[0]):
			p["statut"]=a[1]
			for uid in abonnes:
				try: await c.bot.send_message(chat_id=uid,text="Resultat!\n\n"+fmt(p))
				except: pass
			await u.message.reply_text("Mis a jour!"); return
	await u.message.reply_text("Introuvable.")

async def cmd_broadcast(u: Update, c: ContextTypes.DEFAULT_TYPE):
	if not is_admin(u.effective_user.id): await u.message.reply_text("Interdit."); return
	msg=" ".join(c.args); n=0
	for uid in abonnes:
		try: await c.bot.send_message(chat_id=uid,text=msg); n+=1
		except: pass
	await u.message.reply_text("Envoye a "+str(n)+" personnes.")

async def bouton(u: Update, c: ContextTypes.DEFAULT_TYPE):
	q=u.callback_query; await q.answer(); d=q.data
	if d=="tous":
		if not pronos: await q.message.reply_text("Aucun prono."); return
		for p in pronos: await q.message.reply_text(fmt(p))
	elif d=="stats":
		g=sum(1 for p in pronos if p["statut"]=="gagnant"); pe=sum(1 for p in pronos if p["statut"]=="perdant"); t=round((g/(g+pe))*100,1) if (g+pe)>0 else 0
		await q.message.reply_text("Total="+str(len(pronos))+" G="+str(g)+" P="+str(pe)+" Taux="+str(t)+"%")
	elif d.startswith("s_"):
		sport=d[2:]; fl=[p for p in pronos if p["sport"].lower()==sport]
		if not fl: await q.message.reply_text("Aucun prono pour "+sport); return
		for p in fl: await q.message.reply_text(fmt(p))

def main():
	app=Application.builder().token(TOKEN).build()
	app.add_handler(CommandHandler("start",start))
	app.add_handler(CommandHandler("pronos",cmd_pronos))
	app.add_handler(CommandHandler("stats",cmd_stats))
	app.add_handler(CommandHandler("ajouter",cmd_ajouter))
	app.add_handler(CommandHandler("modifier",cmd_modifier))
	app.add_handler(CommandHandler("broadcast",cmd_broadcast))
	app.add_handler(CallbackQueryHandler(bouton))
	print("Bot demarre!")
	app.run_polling()

main()