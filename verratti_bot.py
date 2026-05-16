import os
from telegram.ext import Application

TOKEN = os.environ.get("TOKEN").strip()

print(repr(TOKEN))

app = Application.builder().token(TOKEN).build()

app.run_polling()