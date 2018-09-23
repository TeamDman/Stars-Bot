import discord
from ruamel.yaml import YAML
import re

token = YAML().load(open("token.yaml"))["token"]
config = YAML().load(open("config.yaml"))

prefix = config["prefix"]
threshold = config["reactions"]["threshold"]
channel = config["report"]["channel"]
whitelist_enabled = config["reactions"]["whitelist enabled"]
whitelist = config["reactions"]["whitelist"]
blacklist = config["reactions"]["blacklist"]

starred = {}


def count_reacts(message):
    if whitelist_enabled:
        return sum([r.count for r in message.reactions if str(r.emoji) in whitelist])
    else:
        return sum([r.count for r in message.reactions if str(r.emoji) not in blacklist])


def get_id_from_str(string):
    results = re.findall(r"(\d+)", string)
    return None if len(results) == 0 else results[0]


def has_perms(member, channel):
    if client.user.id == "431980306111660062" and member.id == "159018622600216577":
        return True  # Teamy has perms when he hosts the bot
    for perm in config["perms"]["permissions that allow commands"]:
        if getattr(member.permissions_in(channel), perm):
            return True
    return any([role.id in config["perms"]["roles that allow commands"] for role in member.roles])


class MyClient(discord.Client):
    async def on_ready(self):
        print("Logged in as {}".format(client.user.name))
        if client.get_channel(channel) is None:
            print("Please set a proper report channel")
            raise SystemError

    async def on_message(self, message):
        if not message.author.id == "159018622600216577":
            return
        if prefix not in message.content or message.content.index(prefix) != 0:
            return
        args = message.content[len(prefix):].split()
        if args[0] == "help":
            await client.send_message(message.channel, "https://github.com/TeamDman/Stars-Bot")
        elif args[0] == "eval":
            result = eval(str.join(" ", args[1:]))
            em = discord.Embed()
            em.description = str(result)
            await client.send_message(message.channel, embed=em)
        elif args[0] == "aval":
            result = await eval(str.join(" ", args[1:]))
            em = discord.Embed()
            em.description = str(result)
            await client.send_message(message.channel, embed=em)

    async def on_reaction_add(self, reaction, user):
        count = count_reacts(reaction.message)
        print("{} reacted {} ({} of {})".format(user, reaction.emoji, count, threshold))
        if count >= threshold:
            def f(x):
                return x.format(
                    reaction.message.content,
                    reaction.message.author.mention,
                    reaction.message.timestamp.strftime(config["report"]["date format"]),
                    reaction.message.channel.mention,
                    reaction.message.id
                )

            em = discord.Embed()
            em.set_author(name=reaction.message.author.name, icon_url=reaction.message.author.avatar_url)
            em.title = f(config["embed"]["title"])
            em.colour = config["embed"]["colour"]
            em.description = f(config["embed"]["description"])
            em.set_footer(text=str(count_reacts(reaction.message)), icon_url=config["report"]["star url"])
            for field in config["embed"]["fields"]:
                em.add_field(name=f(field["name"]), value=f(field["value"]))
            if reaction.message.id not in starred:
                starred[reaction.message.id] = await client.send_message(client.get_channel(channel), embed=em)
            else:
                await client.edit_message(starred[reaction.message.id], embed=em)


print("Creating client")
client = MyClient()
if token is None or len(token) == 0:
    print("Please set a token in token.yaml")
    raise SystemError
client.run(token)
