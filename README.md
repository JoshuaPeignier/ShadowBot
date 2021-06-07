# ShadowBot
A Discord bot for Shadow Hunters

# Requirements
Before running the bot, make sure that Python3 is installed on your computer: https://realpython.com/installing-python/
To see which version of Python3 you have, open a terminal (look for cmd.exe if you run on Windows) and just type

```bash
python3
```

If your version of Python is at least 3.7.X, everything should work fine. Just in case, though, be sure to download the latest version of Python.


Then, you need to install the Python library discord.py. A tutorial is available here: https://discordpy.readthedocs.io/en/latest/intro.html

# Download

The simplest way is to use the "Download ZIP" button on top of this page, and then extract it somewhere on your computer, but this means that you will have redownload manually each time there is an update.
If you know how to use git, just clone the repository, and you should be able to update everything with a pull each time an update is available.

# Token and security measures

The file bot\_LPDA.py on this repository (and on the archive that you download) is incomplete: for security reasons, I removed the token associated to the account of the Discord bot.
Just ask me for the token in private if you need ; else, it may be available in a pinned message on Discord.
Once you have the token, open the file bot\_LPDA.py in a notepad, look for the following line:

```python3
client.run('XXXXXXXXXX')
```
and replace the XXXXXXXX by the token. DO NOT send or show the token to ANYONE outside our group, and DO NOT put it anywhere on the internet, besides our Discord server. If someone else gets that token, it means they have access to the account of the Discord bot. I would still be the owner of the account, but they could use it for another program which could, for example, spy on our server. That would be bad.


# Run the bot

Simpler solution: double click the bot.bat file.

Other solution: open a terminal, use the cd command to go in the directory where you cloned/extracted the repo, and then:
```python
python3 bot_LPDA.py
```

If you have done everything correctly, a terminal should appear with a message saying
```bash
We have logged in as ShadowBot X.X.X#1011
```


