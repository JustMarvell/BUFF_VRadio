import discord
from discord.ext import commands
from controllers import music

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.hybrid_command()
    @commands.guild_only()
    async def arise(self, ctx: commands.Context):
        """ Join the voice channel """
        
        await ctx.defer()
        
        if not ctx.author.voice:
            await ctx.send("Please join a voice channel first")
            return
                
        if ctx.guild.voice_client is None:
            await ctx.author.voice.channel.connect()
            await ctx.send("I've been summoned")
        elif ctx.guild.voice_client.channel is not ctx.author.voice.channel:
            await ctx.guild.voice_client.move_to(ctx.author.voice.channel)
            await ctx.send(f"Moved to new channel")
        else:
            await ctx.send("I'm already in your voice channel")
        
    @commands.hybrid_command()
    @commands.guild_only()
    async def release(self, ctx: commands.Context):
        """ Leave the voice channel """

        client = ctx.guild.voice_client
        await ctx.defer()
        
        if client:
            await client.disconnect()
            
            await ctx.send("See you in the other side")
        else:
            await ctx.send("I'm not in a voice channel")
    