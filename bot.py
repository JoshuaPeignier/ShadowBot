import discord

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')

client.run('Njk0MjcwODgyMDQ2MDE3NTg4.XoMX_Q.Rmz-5qRP3dzskCrKUzgb-d7TowI')
