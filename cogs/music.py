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
            
    @commands.hybrid_command()
    @commands.guild_only()
    async def play(self, ctx: commands.Context, *, song_name: str):
        """ Play a song or add it to the queue """
        await ctx.defer()

        if not ctx.author.voice:
            await ctx.send("Please join a voice channel first.")
            return

        voice_client = ctx.guild.voice_client
        if voice_client is None:
            voice_client = await ctx.author.voice.channel.connect()

        track = await music.play(ctx.guild.id, voice_client, song_name)
        if not track:
            await ctx.send("Couldn't find or play that song.")
            return

        state = music.get_state(ctx.guild.id)
        if len(state.queue) == 0 and state.current == track:
            await ctx.send(f"Now playing: **{track['title']}**")
        else:
            await ctx.send(f"Added to queue: **{track['title']}**")

    @commands.hybrid_command()
    @commands.guild_only()
    async def pause(self, ctx: commands.Context):
        """ Pause or resume the current song """
        await ctx.defer()
        vc = ctx.guild.voice_client
        if not vc:
            await ctx.send("I'm not in a voice channel.")
            return

        if vc.is_paused():
            music.resume(vc)
            await ctx.send("Resumed.")
        elif vc.is_playing():
            music.pause(vc)
            await ctx.send("Paused.")
        else:
            await ctx.send("Nothing is playing.")

    @commands.hybrid_command()
    @commands.guild_only()
    async def stop(self, ctx: commands.Context):
        """ Stop playback and clear the queue """
        await ctx.defer()
        vc = ctx.guild.voice_client
        if not vc:
            await ctx.send("I'm not in a voice channel.")
            return

        music.stop(ctx.guild.id, vc)
        await ctx.send("Stopped and queue cleared.")

    @commands.hybrid_command()
    @commands.guild_only()
    async def skip(self, ctx: commands.Context):
        """ Skip the current song """
        await ctx.defer()
        vc = ctx.guild.voice_client
        if not vc:
            await ctx.send("I'm not in a voice channel.")
            return

        skipped = music.skip(ctx.guild.id, vc)
        await ctx.send("Skipped." if skipped else "Nothing to skip.")
    