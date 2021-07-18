import os
import re
import sqlite3
from datetime import datetime

import discord
from discord.ext import commands

import server.graphs.graph_creation as gc
from server.database.database_sqlite import MEMBERS_DATABASE_DIRECTORY
from server.graphs.graph_creation import GRAPHS_DIRECTORY

DAY_IN_SECONDS = 86400

DEVELOPER = 'HolyRidek#9770'


def member_security_check(ctx, member: str):
    """
    Checks to see if member is a part of the Discord server where the statistics were requested.
    :param ctx: Context
    :param member: The member we want to check.
    """
    reason = ''
    is_in_server = False
    try:
        for mem in ctx.guild.members:
            if re.search('[a-zA-Z]', member):  # If member was requested via name and discriminator
                if member == str(mem.name + '#' + mem.discriminator):
                    is_in_server = True
            else:  # If member was requested via discord ID
                if member == str(mem.id):
                    is_in_server = True
    except:
        return False, 'in_pm'

    if is_in_server:
        if re.search('[a-zA-Z]', str(member)):
            discord_member = ctx.guild.get_member_named(member)
        else:
            discord_member = ctx.guild.get_member(int(member))

        member_name = discord_member.name + '#' + discord_member.discriminator

        db_conn = sqlite3.connect(MEMBERS_DATABASE_DIRECTORY)
        cursor = db_conn.cursor()
        days_string = f'-20 days'
        cursor.execute("SELECT mem_id FROM members_info WHERE (mem_id = ? AND date_time >="
                       "strftime('%s',datetime('now',?))) OR (mem_id = ? AND date_time >=strftime"
                       "('%s',datetime('now',?)))", (discord_member.id, days_string, member_name, days_string))
        data = cursor.fetchall()
        if data[0] is None or data[0] == '':
            reason = 'not_in_db'
        else:
            return True, reason
    else:
        reason = 'not_in_guild'

    return False, reason


class StatCommands(commands.Cog):
    """
    User statistics commands.
    :param commands.Cog: Means it is a cog.
    """

    def __init__(self, client):
        """
        Receives and configures the Discord client for the commands.
        :param client: The bot
        """
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Starts the cog.
        :return:
        """
        print("StatCommands cog is ready")
        print('')

    @commands.command(pass_context=True, aliases=['GULS'])
    async def get_user_last_stat(self, ctx, stat_type, stat_name, display_public, *, member):
        """
        A command to receive the last time and date a member had a certain stat.
        :param ctx: Context (Not for users)
        :param stat_type: What type of statistic are you requesting? [statuses, activities]
        :param stat_name: What is the name of the statistic you would like to check.
        :param display_public: Do you want the statistic to be displayed in the channel you requested them in
         or do you want the bot to PM you the statistics? [Yes - Displayed in channel, No - Sent via private message]
        :param member: Which member are you requesting the statistics about? [discord_id, name+discriminator]
         [Eg: Example#0000, 000000000000000000]
        """
        passed_security_check, reason = member_security_check(ctx, member)
        # Check if member that was submitted is in the discord server and in the database.
        if passed_security_check:
            # Checks how the member was submitted: via name or via id.
            if re.search('[a-zA-Z]', str(member)):
                discord_member = ctx.guild.get_member_named(member)
            else:
                discord_member = ctx.guild.get_member(int(member))

            if str(stat_type).lower() == 'status':
                return_msg = self.member_last_status(ctx, stat_name, discord_member)
            elif str(stat_type).lower() == 'activity':
                return_msg = self.member_last_activity(ctx, stat_name, discord_member)
            else:
                return await ctx.send(f"{ctx.message.author.mention} ```css\n [ERROR] You failed to provide a valid"
                                      f" parameter for stat_type, try again with one of the following:"
                                      f" statuses / activities.```")
        else:
            if reason == 'not_in_guild':
                return await ctx.send(f"{ctx.message.author.mention} ```css\n [ERROR] {member} is not currently in "
                                      f"this server. If you would like to check his information, please make"
                                      f" sure he is a part of this Discord server and a day has passed.```")
            elif reason == 'not_in_db':
                return await ctx.send(
                    f"{ctx.message.author.mention} ```fix\n [Warning] {member} is not currently in my "
                    f"database, please allow at least a day to pass from when the member joins the server "
                    f"before requesting his stats.```")
            elif reason == 'in_pm':
                return await ctx.send(f'{ctx.message.author.mention} ```css\n [ERROR] You cannot use any of the'
                                      f' commands for Analitica Bot in PM, try again in a server.```')
            else:
                return

        if 'ERROR' in return_msg or 'WARNING' in return_msg:
            return await ctx.send(return_msg)

        # Check if the user wants the info displayed publicly or not
        if str(display_public).lower() == 'yes':
            await ctx.send(return_msg)
        elif str(display_public).lower() == 'no':
            await ctx.message.author.send(return_msg)
            await ctx.message.add_reaction(emoji='✉')
        else:
            return await ctx.send(f"{ctx.message.author.mention} ```css\n [ERROR] You failed to provide a valid "
                                  f"parameter for display_public, try again with one of the following: Yes / "
                                  f"No.```")

    def member_last_status(self, ctx, status_name, member: discord.Member):
        """
        Searches for the last instance of the specific status in the database related to the member and returns the
        date and time at which it was logged.
        :param ctx: Context (Not for users)
        :param status_name: The name of the status you want to check.
        :param member: The member of which you want to check the last instance.
        """
        member_name = member.name + '#' + member.discriminator
        statuses = {'online', 'idle', 'dnd', 'do not disturb', 'offline'}
        if str(status_name).lower() not in statuses:
            return f"{ctx.message.author.mention} ```css\n [ERROR] the stat_name you have entered is incorrect, " \
                   f"please try again with [online, offline, idle, do not disturb]``` "
        if status_name == 'do_not_disturb':
            status = 'dnd'
        conn = sqlite3.connect(MEMBERS_DATABASE_DIRECTORY)
        c = conn.cursor()
        c.execute("SELECT * FROM statuses")
        statuses = c.fetchall()
        c.execute("SELECT * FROM members_info WHERE mem_id = ? OR mem_id = ?", (member.id, member_name))
        instances = c.fetchall()
        c.close()

        for stat in statuses:
            if stat[1] == status_name:
                status_id = stat[0]

        for instance in reversed(instances):
            if instance[2] == status_id:
                if status_name == 'dnd':
                    return f"`{member} was last on Do Not Disturb at" \
                           f" {datetime.fromtimestamp(instance[1]).strftime('%Y-%m-%d %H:%M:%S')} ` "
                else:
                    return f"`{member} was last {status_name} at " \
                           f"{datetime.fromtimestamp(instance[1]).strftime('%Y-%m-%d %H:%M:%S')} `"

        if status_name == 'dnd':
            return f'`I am sorry but it seems that I was not able to find that `{member}` has ever been on `Do Not ' \
                   f'Disturb` in my database.`'
        else:
            return f'`I am sorry but it seems that I was not able to find that `{member}` has ever been `{status_name}`' \
                   f' in my database.` '

    def member_last_activity(self, ctx, activity_name, member: discord.Member):
        """
        Searches for the last instance of the specific activity in the database related to the member and returns the
        date and time at which it was logged.
        :param ctx: Context (Not for users)
        :param activity_name: The name of the activity you want to check.
        :param member: The member of which you want to check the last instance.
        """
        member_name = member.name + '#' + member.discriminator
        conn = sqlite3.connect(MEMBERS_DATABASE_DIRECTORY)
        c = conn.cursor()
        c.execute("SELECT act_name FROM activities")
        activities_tup = c.fetchall()
        is_found = False
        activities_list = []

        for act in activities_tup:
            activities_list.append(act[0])
            if str(act[0]).lower() == str(activity_name).lower():
                is_found = True

        if not is_found:
            c.close()
            return f"{ctx.message.author.mention} ```css\n [ERROR] the activity_name you have entered is incorrect, " \
                   f"please try again with {activities_list}``` "

        c.execute("SELECT * FROM activities")
        activities = c.fetchall()
        c.execute("SELECT * FROM members_info WHERE mem_id = ? OR mem_id = ?", (member.id, member_name))
        instances = c.fetchall()
        c.close()

        for act in activities:
            if str(act[1]).lower() == str(activity_name).lower():
                activity_id = act[0]

        for instance in reversed(instances):
            if instance[3] == activity_id:
                return f"`{member_name} has last done {activity_name} at " \
                       f"{datetime.fromtimestamp(instance[1]).strftime('%Y-%m-%d %H:%M:%S')}`"

        return f'`Unfortunately I was not able to find in my database that {member_name} has ever done {activity_name}`'

    @commands.command(pass_context=True, aliases=['GUS'])
    async def get_user_stats(self, ctx, stat_type, num_of_days, graph_type, display_public, *, member):
        """
        A command to receive a user's statistics from the last time period.
        :param ctx: Context (Not for users)
        :param stat_type: What type of statistic are you requesting? [statuses, activities]
        :param num_of_days: How many days do you want to go back with the statistics? [Max: 20]
        :param graph_type: What type of graph do you want the statistics to be displayed with? [pie, bar]
        :param display_public: Do you want the statistics to be displayed in the channel you requested them in
         or do you want the bot to PM you the statistics? [Yes - Displayed in channel, No - Sent via private message]
        :param member: Which member are you requesting the statistics about? [discord_id, name+discriminator]
         [Eg: Example#0000, 000000000000000000]
        """
        if int(num_of_days) > 20:  # Checks if the data that has been requested is from the last 20 days.
            return await ctx.send(
                f"{ctx.message.author.mention} You may only request data that is 20 days old, or less. "
                f"Please try again.")

        # Begins to make the embed
        return_embed = discord.Embed(title='User Statistics Graph', colour=discord.Color.blue())
        return_embed.timestamp = datetime.now()

        # The member requesting the stats
        return_embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        # The member the info of is being requested
        return_embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)

        return_embed.add_field(name='Statistic:', value=stat_type)
        return_embed.add_field(name='Graph Type:', value=graph_type)
        return_embed.add_field(name='Number Of Days:', value=num_of_days)

        passed_security_check, reason = member_security_check(ctx, member)
        # Check if member that was submitted is in the discord server and in the database.
        if passed_security_check:
            # Checks how the member was submitted: via name or via id.
            if re.search('[a-zA-Z]', str(member)):
                discord_member = ctx.guild.get_member_named(member)
            else:
                discord_member = ctx.guild.get_member(int(member))

            # Checks which type of graph the users wants his info displayed with.
            if str(graph_type).lower() == 'bar' or str(graph_type).lower() == 'pie':
                if str(stat_type).lower() == 'statuses':
                    return_msg, return_img = self.get_user_statuses(ctx, num_of_days, graph_type, discord_member)
                elif str(stat_type).lower() == 'activities':
                    return_msg, return_img = self.get_user_activities(ctx, num_of_days, graph_type, discord_member)
                else:
                    return await ctx.send(f"{ctx.message.author.mention} ```css\n [ERROR] You failed to provide a valid"
                                          f" parameter for stat_type, try again with one of the following:"
                                          f" statuses / activities.```")
            else:
                return await ctx.send(f"{ctx.message.author.mention} ```css\n [ERROR] You failed to provide a valid "
                                      f"graph type, try again with one of the following: pie /  bar.```")

            if return_msg == 'error':
                return await ctx.send(f"{ctx.message.author.mention} ```css\n [ERROR] An unexpected error occurred"
                                      f" with {commands.command()}. Try again later or contact the developer"
                                      f" on discord: {DEVELOPER}")

            return_embed.description = return_msg
            return_embed.set_image(url=f"attachment://{return_img.filename}")

            # Check if the user wants the info displayed publicly or not
            if str(display_public).lower() == 'yes':
                await ctx.send(embed=return_embed, file=return_img)
            elif str(display_public).lower() == 'no':
                await ctx.message.author.send(embed=return_embed, file=return_img)
                await ctx.message.add_reaction(emoji='✉')
            else:
                return await ctx.send(f"{ctx.message.author.mention} ```css\n [ERROR] You failed to provide a valid "
                                      f"parameter for display_public, try again with one of the following: Yes / "
                                      f"No.```")
        else:
            if reason == 'not_in_guild':
                return await ctx.send(f"{ctx.message.author.mention} ```css\n [ERROR] {member} is not currently in "
                                      f"this server. If you would like to check his information, please make"
                                      f" sure he is a part of this Discord server and a day has passed.```")
            elif reason == 'not_in_db':
                return await ctx.send(
                    f"{ctx.message.author.mention} ```fix\n [Warning] {member} is not currently in my "
                    f"database, please allow at least a day to pass from when the member joins the server "
                    f"before requesting his stats.```")
            elif reason == 'in_pm':
                return await ctx.send(f'{ctx.message.author.mention} ```css\n [ERROR] You cannot use any of the'
                                      f' commands for Analitica Bot in PM, try again in a server.```')
            else:
                return

        if os.path.exists(f"{GRAPHS_DIRECTORY}/{return_img.filename}"):
            os.remove(f"{GRAPHS_DIRECTORY}/{return_img.filename}")

    def get_user_statuses(self, ctx, num_of_days, graph_type, member: discord.Member):
        """
        Gathers all info about the statuses of the member, sends to a function to make a graph and returns the graph
        and the corresponding message.
        :param ctx: Context
        :param num_of_days: How many days are being requested.
        :param graph_type: Which graph is being requested? Bar or Pie.
        :param member: The member that the info is being requested about.
        """
        member_name = member.name + '#' + member.discriminator
        if graph_type == 'pie':
            db_conn = sqlite3.connect(MEMBERS_DATABASE_DIRECTORY)
            cursor = db_conn.cursor()
            days_string = f'-{num_of_days} days'
            cursor.execute("SELECT status_id FROM members_info WHERE (mem_id = ? AND date_time >="
                           "strftime('%s',datetime('now',?))) OR (mem_id = ? AND date_time >=strftime"
                           "('%s',datetime('now',?)))", (member.id, days_string, member_name, days_string))
            status_ids = cursor.fetchall()
            cursor.execute("SELECT * FROM statuses")
            all_statuses_db = cursor.fetchall()
            db_conn.close()

            # Makes a list with the number of times that each status was present.
            all_statuses = []
            for status_id in status_ids:
                for stat in all_statuses_db:
                    if stat[0] == status_id[0]:
                        all_statuses.append(stat[1])

            gc.create_status_pie_graph(all_statuses)
            try:
                return_img = discord.File(f"{GRAPHS_DIRECTORY}/status_pie_graph.png", filename="status_pie_graph.png")
                return_message = f"Graph of {member_name}'s statuses from the last {num_of_days}d.\nRequested by" \
                                 f" {ctx.message.author.mention}"
            except Exception as e:
                print(e)
                return_message = 'error'
                return_img = ''

        elif graph_type == 'bar':
            db_conn = sqlite3.connect(MEMBERS_DATABASE_DIRECTORY)
            cursor = db_conn.cursor()
            days_string = f'-{num_of_days} days'
            cursor.execute("SELECT status_id, date_time FROM members_info WHERE (mem_id = ? AND date_time >="
                           "strftime('%s',datetime('now',?))) OR (mem_id = ? AND date_time >=strftime"
                           "('%s',datetime('now',?)))", (member.id, days_string, member_name, days_string))
            statuses = cursor.fetchall()
            cursor.execute("SELECT * FROM statuses")
            all_statuses_db = cursor.fetchall()
            db_conn.close()

            day_week_statuses = []
            now = datetime.now()
            now_time = int(datetime.timestamp(now))
            # List withing a list with the number of each status displayed per day.
            for day in range(int(num_of_days)):
                day_statuses = []
                for status in statuses:
                    if now_time - (DAY_IN_SECONDS * (day + 1)) < status[1] <= now_time - (DAY_IN_SECONDS * day):
                        for stat in all_statuses_db:
                            if stat[0] == status[0]:
                                day_statuses.append(stat[1])
                day_week_statuses.append(day_statuses)

            gc.create_status_bar_graph(day_week_statuses)
            try:
                return_img = discord.File(f"{GRAPHS_DIRECTORY}/status_bar_graph.png", filename="status_bar_graph.png")
                return_message = f"Graph of {member_name}'s statuses from the last {num_of_days}d per day.\nRequested by" \
                                 f" {ctx.message.author.mention}"
            except Exception as e:
                print(e)
                return_message = 'error'
                return_img = ''

        return return_message, return_img

    def get_user_activities(self, ctx, num_of_days, graph_type, member: discord.Member):
        """
        Gathers all info about the activities of the member, sends to a function to make a graph and returns the graph
        and the corresponding message.
        :param ctx: Context
        :param num_of_days: How many days are being requested.
        :param graph_type: Which graph is being requested? Bar or Pie.
        :param member: The member that the info is being requested about.
        """
        member_name = member.name + '#' + member.discriminator
        if graph_type == 'pie':
            db_conn = sqlite3.connect(MEMBERS_DATABASE_DIRECTORY)
            cursor = db_conn.cursor()
            days_string = f'-{num_of_days} days'

            cursor.execute("SELECT activity_id FROM members_info WHERE (mem_id = ? AND date_time >="
                           "strftime('%s',datetime('now',?))) OR (mem_id = ? AND date_time >=strftime"
                           "('%s',datetime('now',?)))", (member.id, days_string, member_name, days_string))
            activity_ids = cursor.fetchall()
            cursor.execute("SELECT * FROM activities")
            all_activities_db = cursor.fetchall()
            db_conn.close()

            all_activities = []
            # Makes a list with the number of times each activity was present.
            for activity_id in activity_ids:
                for act in all_activities_db:
                    if act[0] == activity_id[0]:
                        all_activities.append(act[1])

            activities_names = []
            for activity in all_activities_db:
                activities_names.append(activity[1])

            gc.create_activity_pie_graph(all_activities, activities_names)
            try:
                return_img = discord.File(f"{GRAPHS_DIRECTORY}/activity_pie_graph.png",
                                          filename="activity_pie_graph.png")
                return_message = f"Graph of {member_name}'s activities from the last {num_of_days}d.\nRequested by" \
                                 f" {ctx.message.author.mention}"
            except Exception as e:
                print(e)
                return_message = 'error'
                return_img = ''

        elif graph_type == 'bar':
            db_conn = sqlite3.connect(MEMBERS_DATABASE_DIRECTORY)
            cursor = db_conn.cursor()
            days_string = f'-{num_of_days} days'
            cursor.execute("SELECT activity_id, date_time FROM members_info WHERE (mem_id = ? AND date_time >="
                           "strftime('%s',datetime('now',?))) OR (mem_id = ? AND date_time >=strftime"
                           "('%s',datetime('now',?)))", (member.id, days_string, member_name, days_string))
            activities = cursor.fetchall()
            cursor.execute("SELECT * FROM activities")
            all_activities_db = cursor.fetchall()
            db_conn.close()

            day_week_activities = []
            now = datetime.now()
            now_time = int(datetime.timestamp(now))
            # List withing a list with the number of each activity displayed per day.
            for day in range(int(num_of_days)):
                day_activities = []
                for activity in activities:
                    if now_time - (DAY_IN_SECONDS * (day + 1)) < activity[1] <= now_time - (DAY_IN_SECONDS * day):
                        for act in all_activities_db:
                            if act[0] == activity[0]:
                                day_activities.append(act[1])
                day_week_activities.append(day_activities)

            activities_names = []
            for activity in all_activities_db:
                activities_names.append(activity[1])

            gc.create_activity_bar_graph(day_week_activities, activities_names)
            try:
                return_img = discord.File(f"{GRAPHS_DIRECTORY}/activity_bar_graph.png", filename="activity_bar_graph"
                                                                                                 ".png")
                return_message = f"Graph of {member_name}'s activities from the last {num_of_days}d per " \
                                 f"day.\nRequested by {ctx.message.author.mention} "
            except Exception as e:
                print(e)
                return_message = 'error'
                return_img = ''

        return return_message, return_img


def setup(client):
    """
    Adds current class into cog list.
    :param client:
    :return:
    """
    client.add_cog(StatCommands(client))
