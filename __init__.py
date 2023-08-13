import breadcord


class NebulusCustomiser(breadcord.module.ModuleCog):
    def __init__(self, module_id: str, /):
        super().__init__(module_id)


async def setup(bot: breadcord.Bot):
    await bot.add_cog(NebulusCustomiser("nebulus_customiser"))
