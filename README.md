# Stars-Bot
### Known limitations
The discord.py events only fire for messages that are in its cache. 
Messages that existed before the bot is loaded will not be starred/updated.
Additionally, if the server is moving super fast, then the message might be uncached and will no longer trigger events.
That _shouldn't_ be an issue that will be encountered.