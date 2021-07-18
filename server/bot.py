# Main bot file, starts the bot and everything else from here
import os

import discord
from discord.ext import commands, tasks

from server.database.database_sqlite import *

from datetime import datetime

# The prefix of the commands that the bot uses
BOT_PREFIX = '.'
client = commands.Bot(command_prefix=BOT_PREFIX)
client.remove_command('help')

HAS_STARTED_DATABASE = False


@client.event
async def on_ready():
    """
    Whenever the bot is loaded and ready for action, it writes to the console.
    Checks if the databases and tables inside of it exist, and if they don't, calls functions to create them.
    :return:
    """
    global HAS_STARTED_DATABASE
    print("Bot is ready")
    delete_extra_db_logs.start()
    if not HAS_STARTED_DATABASE:
        create_members_info_table()
        create_activities_table()
        create_statuses_table()
        # create_perms_tables() 'It is not being used yet so it is not being created.'
        HAS_STARTED_DATABASE = True
        print("Database is ready")


@client.command(pass_context=True, aliases=['Help', 'HELP'])
async def help(ctx, *cog):
    """
    Help command: gathers all cogs and commands that the bot has and sends them via Private Message to the user using
    the help command.
    :param ctx: Context
    """
    global halp
    global BOT_PREFIX
    try:
        if not cog:
            """Cog listing."""
            halp = discord.Embed(title='Cog Listing and Uncatergorized Commands',
                                 description=f'Use `{BOT_PREFIX}help *cog*` to find out more about them!\n(BTW, '
                                             f'the Cog Name Must Be in Title Case, Just Like this Sentence.)')
            cogs_desc = ''
            for x in client.cogs:
                cogs_desc += ('{} - {}'.format(x, client.cogs[x].__doc__) + '\n')
            halp.add_field(name='Cogs', value=cogs_desc[0:len(cogs_desc) - 1], inline=False)
            cmds_desc = ''
            for y in client.walk_commands():
                if not y.cog_name and not y.hidden:
                    cmds_desc += ('{} - {}'.format(y.name, y.help) + '\n')
            halp.add_field(name='Uncatergorized Commands', value=cmds_desc[0:len(cmds_desc) - 1], inline=False)
            await ctx.message.add_reaction(emoji='✉')
            await ctx.message.author.send('', embed=halp)
        else:
            """Helps me remind you if you pass too many args."""
            if len(cog) > 1:
                halp = discord.Embed(title='Error!', description='That is way too many cogs!',
                                     color=discord.Color.red())
                await ctx.message.author.send('', embed=halp)
            else:
                """Command listing within a cog."""
                found = False
                for x in client.cogs:
                    for y in cog:
                        if x == y:
                            halp = discord.Embed(title=cog[0] + ' Command Listing',
                                                 description=client.cogs[cog[0]].__doc__)
                            for c in client.get_cog(y).get_commands():
                                if not c.hidden:
                                    halp.add_field(name=c.name, value=c.help, inline=False)
                            found = True
                if not found:
                    """Reminds you if that cog doesn't exist."""
                    halp = discord.Embed(title='Error!', description='How do you even use "' + cog[0] + '"?',
                                         color=discord.Color.red())
                else:
                    await ctx.message.add_reaction(emoji='✉')
                await ctx.message.author.send('', embed=halp)
    except:
        await ctx.send("Excuse me, I can't send embeds.")


@tasks.loop(seconds=24)
async def delete_extra_db_logs():
    handle_database_overdraft()
    print(f'Purged Database || {datetime.today().strftime("%b %d %Y %H:%M")}')


def launch(token):
    """
    Loads all of the cogs and starts the bot with the discord application.
    :param token: The token provided by Discord Application in order to authenticate the bot
     (Required in order to connect the bot to the Discord servers).
    """
    # Load all the cogs from the files in the cogs folder on startup of bot.
    for filename in os.listdir('./server/cogs'):
        if filename.endswith('.py'):
            try:
                client.load_extension(f'server.cogs.{filename[:-3]}')
            except:
                print(f"Was unable to load {filename} cog")

    # Attempt to start the bot.
    try:
        client.run(token)
    except discord.errors.LoginFailure:
        print("You have entered an improper token.")
