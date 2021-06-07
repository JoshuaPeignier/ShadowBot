import bot_code
import discord
intents = discord.Intents.default()
intents.reactions = True
intents.members = True

############################# Actually running the bot
client=bot_code.ShadowClient(intents=intents)
client.run('Njk0MjcwODgyMDQ2MDE3NTg4.XoMX_Q.Rmz-5qRP3dzskCrKUzgb-d7TowI')
