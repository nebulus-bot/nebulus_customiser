import breadcord


class ModuleCogClassName(breadcord.module.ModuleCog):
    def __init__(self, module_id: str, /):
        super().__init__(module_id)


async def setup(bot: breadcord.Bot):
    await bot.add_cog(ModuleCogClassName("module_id"))
