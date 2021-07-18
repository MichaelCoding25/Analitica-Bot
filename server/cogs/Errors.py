import sys
import traceback

from discord.ext import commands
import discord

from server.cogs.info_send import StatCommands

from datetime import datetime


class Errors(commands.Cog):
    """
    A cog designed to handle discord related errors.
    """

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Errors cog is ready")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        The event triggered when an error is raised while invoking a command.

        :param ctx: Context
        :param error: Exception
        """

        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound, commands.UserInputError)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'```css\n [ERROR] {ctx.command} has been disabled. ```')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'```css\n [ERROR] {ctx.command} can not be used in Private'
                                             f' Messages. ```')
            except:
                pass
        elif isinstance(error, discord.errors.Forbidden):
            try:
                return await ctx.author.send(f'```css\n [ERROR] {ctx.command} can not be used'
                                             f' in Private Messages. ```')
            except:
                pass
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':
                return await ctx.send('```css\n [ERROR} I could not find that member. Please try again. ```')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @StatCommands.get_user_stats.error
    async def get_user_stats_handler(self, ctx, error):
        """
        The error handler for the get_user_stats command
        :param ctx: From what location in discord was the error raised.
        :param error: The discord error that was raised.
        """
        author = ctx.message.author.mention
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'stat_type':
                await ctx.send(f"{author} ```css\n [ERROR] You Forgot to provide the statistic type you would like "
                               f"sent. ```")
            elif error.param.name == 'num_of_days':
                await ctx.send(f"{author} ```css\n [ERROR] You forgot to provide the number of days that you would "
                               f"like to see the statistics for. ```")
            elif error.param.name == 'graph_type':
                await ctx.send(f"{author} ```css\n [ERROR] You forgot to provide the graph type you would like the "
                               f"statistics to be shown by.```")
            elif error.param.name == 'display_public':
                await ctx.send(f"{author} ```css\n [ERROR] You forgot to provide a statement of Yes or No, if you "
                               f"want the statistics shown publicly.```")
            elif error.param.name == 'member':
                await ctx.send(f"{author} ```css\n [ERROR] You forgot to provide the member that you would like to "
                               f"check the statistics of. ```")
            else:
                await ctx.send(f"{author} ```css\n [ERROR] You forgot to enter one of the parameters for the"
                               f" {ctx.command} command.```")
        elif isinstance(error, commands.BadArgument):
            if error.param.name == 'stat_type':
                await ctx.send(
                    f"{author} ```css\n [ERROR] You failed to provide a valid stat type, try again with one of the "
                    f"following: statuses, activities```")
            elif error.param.name == 'num_of_days':
                await ctx.send(f"{author} ```css\n You failed to provide a valid number of days, try again with a "
                               f"number between 1 and 20.```")
            elif error.param.name == 'graph_type':
                await ctx.send(f"{author} ```css\n [ERROR] You failed to provide a valid graph type, try again with "
                               f"one of the following: *pie, bar*.```")
            elif error.param.name == 'display_public':
                await ctx.send(f"{author} ```css\n [ERROR] You failed to provide a valid argument for display_public, "
                               f"try again with either: yes or no.```")
            elif error.param.name == 'member':
                await ctx.send(f"{author} ```css\n [ERROR] You failed to provide a valid member, please try again "
                               f"with either the member's *discord id* or their *name and discriminator*. Eg: "
                               f"Example#0000.```")
        print(f'{error} was raised for {ctx.command}, at {datetime.today().strftime("%b %d %Y %H:%M")}')

    @StatCommands.get_user_last_stat.error
    async def get_user_last_stat_handler(self, ctx, error):
        """
        The error handler for the get_user_last_stat command
        :param ctx: From what location in discord was the error raised.
        :param error: The discord error that was raised.
        """
        author = ctx.message.author.mention
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'stat_type':
                await ctx.send(f"{author} ```css\n [ERROR] You Forgot to provide the statistic type you would like "
                               f"sent. ```")
            elif error.param.name == 'stat_name':
                await ctx.send(f"{author} ```css\n [ERROR] You forgot to provide the statistic name that you are "
                               f"searching for. ```")
            elif error.param.name == 'display_public':
                await ctx.send(f"{author} ```css\n [ERROR] You forgot to provide a statement of Yes or No, if you "
                               f"want the statistics shown publicly.```")
            elif error.param.name == 'member':
                await ctx.send(f"{author} ```css\n [ERROR] You Forgot to provide the member that you would like to "
                               f"check the statistic of. ```")
            else:
                await ctx.send(f"{author} ```css\n [ERROR] You forgot to enter one of the parameters for the"
                               f" {ctx.command} command.```")
        elif isinstance(error, commands.BadArgument):
            if error.param.name == 'stat_type':
                await ctx.send(
                    f"{author} ```css\n [ERROR] You failed to provide a valid stat type, try again with one of the "
                    f"following: status, activity.```")
            elif error.param.name == 'stat_name':
                await ctx.send(f"{author} ```css\n [ERROR] You failed to provide a valid stat type, try again. ```")
            elif error.param.name == 'display_public':
                await ctx.send(f"{author} ```css\n [ERROR] You failed to provide a valid argument for display_public, "
                               f"try again with either: yes or no.```")
            elif error.param.name == 'member':
                await ctx.send(f"{author} ```css\n [ERROR] You failed to provide a valid member, please try again "
                               f"with either the member's discord id or their name and discriminator. Eg: "
                               f"Example#0000.```")
        print(f'{error} was raised for {ctx.command}, at {datetime.today().strftime("%b %d %Y %H:%M")}')


def setup(client):
    """Adds the above cog to the cog list."""
    client.add_cog(Errors(client))
