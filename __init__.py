import discord
from discord._types import ClientT
from discord.ext import commands
from discord import app_commands, Interaction
from psycopg2.extensions import connection, cursor

import breadcord
from data.modules.nebulus_manager.BaseCog import BaseModule


class NebulusCustomiser(
    BaseModule,
    commands.GroupCog,
    group_name="customise",
    group_description="Customise your Nebulus experience"
):
    def __init__(self, module_id: str, /):
        super().__init__(module_id)

        # TODO: This is a temporary way of getting a module. This will be changed once Breadcord is fixed.
        self.connection: connection = self.bot.cogs.get("NebulusManager").connection
        self.cursor: cursor = self.connection.cursor()

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS enabled_modules ("
            "    server_id  bigint NOT NULL,"
            "    modules    text[] NOT NULL,"
            "    PRIMARY KEY (server_id)"
            ");"
        )
        self.connection.commit()

        self.bot._before_invoke = self.before_invoke
        self.bot.tree.interaction_check = self.interaction_check

    async def interaction_check(self, interaction: Interaction[ClientT], /) -> bool:
        cog = interaction.command.extras["cog"]
        self.cursor.execute(
            "SELECT modules FROM enabled_modules WHERE server_id = %s",
            (interaction.guild.id,)
        )

        fail = True
        resp = self.cursor.fetchall()
        for module in resp[0][0]:
            if module == cog:
                fail = False

        if fail:
            raise Exception("Module not enabled")
        else:
            return True

    async def before_invoke(self, ctx: commands.Context):
        self.cursor.execute(
            "SELECT modules FROM enabled_modules WHERE server_id = %s",
            (ctx.guild.id, )
        )

        fail = True
        resp = self.cursor.fetchall()
        for module in resp[0][0]:
            if module == ctx.cog.qualified_name:
                fail = False

        if fail:
            raise Exception("Module not enabled")
        else:
            return True

    @app_commands.command()
    @app_commands.default_permissions(manage_guild=True)
    async def enable_module(self, interaction: discord.Interaction, module: str):
        if module not in self.bot.cogs:
            await interaction.response.send_message(f"`{module}` is not valid.")
            return True

        self.cursor.execute(
            "SELECT modules FROM enabled_modules WHERE server_id = %s",
            (interaction.guild.id, )
        )
        resp = list(self.cursor.fetchall()[0][0])
        print(resp)
        resp.append(module)

        self.cursor.execute(
            "UPDATE enabled_modules "
            "SET modules = %s "
            "WHERE server_id = %s",
            (resp, interaction.guild.id)
        )

        self.connection.commit()
        await interaction.response.send_message(f"Enabled `{module}`")

    @app_commands.command()
    @app_commands.default_permissions(manage_guild=True)
    async def disable_module(self, interaction: discord.Interaction, module: str):
        if module not in self.bot.cogs:
            await interaction.response.send_message(f"`{module}` is not valid.")
            return True

        self.cursor.execute(
            "SELECT modules FROM enabled_modules WHERE server_id = %s",
            (interaction.guild.id,)
        )
        resp = list(self.cursor.fetchall()[0][0])
        print(resp)
        resp.remove(module)

        self.cursor.execute(
            "UPDATE enabled_modules "
            "SET modules = %s "
            "WHERE server_id = %s",
            (resp, interaction.guild.id)
        )

        self.connection.commit()
        await interaction.response.send_message(f"Disabled `{module}`")

    @enable_module.autocomplete("module")
    async def module_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
        self.cursor.execute(
            "SELECT modules FROM enabled_modules WHERE server_id = %s",
            (interaction.guild.id,)
        )
        resp = list(self.cursor.fetchall()[0][0])

        cogs = [cog for cog in self.bot.cogs]
        cogs_new = list(cogs)
        for cog in cogs:
            if cog in ["Settings", "ModuleManager", "NebulusManager", "NebulusCustomiser"]:
                cogs_new.remove(cog)
            if cog in resp:
                try:
                    cogs_new.remove(cog)
                except ValueError:
                    pass
        cogs = cogs_new

        response = [
            app_commands.Choice(name=cog, value=cog)
            for cog in breadcord.helpers.search_for(current, cogs)
        ]

        if not response:
            response = [app_commands.Choice(name="⚠️ No module could be found!", value=current)]

        return response

    @disable_module.autocomplete("module")
    async def disable_module_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
        self.cursor.execute(
            "SELECT modules FROM enabled_modules WHERE server_id = %s",
            (interaction.guild.id,)
        )
        resp = list(self.cursor.fetchall()[0][0])
        cogs_new = list(resp)
        for cog in resp:
            if cog in ["Settings", "ModuleManager", "NebulusManager", "NebulusCustomiser"]:
                cogs_new.remove(cog)
        resp = cogs_new

        response = [
            app_commands.Choice(name=cog, value=cog)
            for cog in breadcord.helpers.search_for(current, resp)
        ]

        if not response:
            response = [app_commands.Choice(name="⚠️ No module could be found!", value=current)]

        return response


async def setup(bot: breadcord.Bot):
    await bot.add_cog(NebulusCustomiser("nebulus_customiser"))
