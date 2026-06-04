from discord.ext import commands
import controllers.test as test

async def setup(bot : commands.Bot):
    await bot.add_cog(Test(bot=bot))

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.hybrid_command()
    async def test(self, ctx: commands.Context):
        """ Test """
        
        msg = await test.test()
        await ctx.send(msg)