import discord
from discord.ext import commands
from controllers import search

async def setup(bot: commands.Bot):
    await bot.add_cog(Search(bot))

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command()
    @commands.guild_only()
    async def search(self, ctx: commands.Context, *, song_name: str):
        """ Search for a song on YouTube """
        await ctx.defer()

        results = await search.search(song_name)
        if not results:
            await ctx.send("No results found.")
            return

        embeds = []
        for i, r in enumerate(results, 1):
            embed = discord.Embed(
                title=r['title'],
                url=r['url'],
                description=r['description'] or '*No description*',
                color=discord.Color.red()
            )
            embed.set_author(name=f"Result {i}")
            if r['thumbnail']:
                embed.set_thumbnail(url=r['thumbnail'])
            embed.add_field(name="Channel", value=r['channel'] or 'Unknown')
            if r['duration']:
                mins, secs = divmod(r['duration'], 60)
                embed.add_field(name="Duration", value=f"{mins}:{secs:02d}")
            embeds.append(embed)

        await ctx.send(embeds=embeds)