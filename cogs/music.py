import discord
from discord.ext import commands
from controllers import music

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))

class MusicControls(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    def _vc(self, interaction: discord.Interaction):
        return interaction.guild.voice_client

    @discord.ui.button(label="⏸", style=discord.ButtonStyle.secondary)
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self._vc(interaction)
        if not vc:
            return await interaction.response.send_message("Not in a voice channel.", ephemeral=True)

        if vc.is_paused():
            music.resume(vc)
            button.label = "⏸"
        elif vc.is_playing():
            music.pause(vc)
            button.label = "▶"
        else:
            return await interaction.response.send_message("Nothing is playing.", ephemeral=True)

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="⏭", style=discord.ButtonStyle.primary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self._vc(interaction)
        if not vc:
            return await interaction.response.send_message("Not in a voice channel.", ephemeral=True)

        skipped = music.skip(self.guild_id, vc)
        await interaction.response.send_message("Skipped." if skipped else "Nothing to skip.", ephemeral=True, delete_after=3)

    @discord.ui.button(label="⏹", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self._vc(interaction)
        if not vc:
            return await interaction.response.send_message("Not in a voice channel.", ephemeral=True)

        music.stop(self.guild_id, vc)
        await interaction.response.edit_message(embed=stopped_embed(), view=None)


def now_playing_embed(track: dict) -> discord.Embed:
    embed = discord.Embed(title="▶ Now Playing", description=f"**{track['title']}**", color=discord.Color.red())
    if track.get("thumbnail"):
        embed.set_image(url=track["thumbnail"])
    if track.get("duration"):
        mins, secs = divmod(track["duration"], 60)
        embed.add_field(name="Duration", value=f"`{mins}:{secs:02d}`")
    if track.get("webpage_url"):
        embed.add_field(name="Link", value=f"[YouTube]({track['webpage_url']})")
    return embed

def queued_embed(track: dict, pos: int) -> discord.Embed:
    return discord.Embed(
        title="Added to Queue",
        description=f"**{track['title']}** — position #{pos}",
        color=discord.Color.blurple()
    )

def stopped_embed() -> discord.Embed:
    return discord.Embed(title="⏹ Stopped", description="Queue cleared.", color=discord.Color.dark_gray())


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    @commands.guild_only()
    async def arise(self, ctx: commands.Context):
        """ Join the voice channel """
        await ctx.defer()
        if not ctx.author.voice:
            return await ctx.send("Please join a voice channel first.")

        vc = ctx.guild.voice_client
        if vc is None:
            await ctx.author.voice.channel.connect()
            await ctx.send("I've been summoned.")
        elif vc.channel != ctx.author.voice.channel:
            await vc.move_to(ctx.author.voice.channel)
            await ctx.send("Moved to your channel.")
        else:
            await ctx.send("Already in your channel.")

    @commands.hybrid_command()
    @commands.guild_only()
    async def release(self, ctx: commands.Context):
        """ Leave the voice channel """
        await ctx.defer()
        vc = ctx.guild.voice_client
        if vc:
            await vc.disconnect()
            await ctx.send("See you on the other side.")
        else:
            await ctx.send("Not in a voice channel.")

    @commands.hybrid_command()
    @commands.guild_only()
    async def play(self, ctx: commands.Context, *, song_name: str):
        """ Play a song or add it to the queue """
        await ctx.defer()
        if not ctx.author.voice:
            return await ctx.send("Please join a voice channel first.")

        vc = ctx.guild.voice_client or await ctx.author.voice.channel.connect()
        
        state = music.get_state(ctx.guild.id)
        channel = ctx.channel

        async def on_track_start(track: dict):
            await channel.send(embed=now_playing_embed(track), view=MusicControls(ctx.guild.id))

        state.on_track_start = on_track_start

        track = await music.play(ctx.guild.id, vc, song_name)
        if not track:
            return await ctx.send("Couldn't find or play that song.")

        if state.current == track and not state.queue:
            pass
        else:
            pos = len(state.queue)
            await ctx.send(embed=queued_embed(track, pos))

    @commands.hybrid_command()
    @commands.guild_only()
    async def pause(self, ctx: commands.Context):
        """ Pause or resume the current song """
        await ctx.defer()
        vc = ctx.guild.voice_client
        if not vc:
            return await ctx.send("Not in a voice channel.")
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
            return await ctx.send("Not in a voice channel.")
        music.stop(ctx.guild.id, vc)
        await ctx.send(embed=stopped_embed())

    @commands.hybrid_command()
    @commands.guild_only()
    async def skip(self, ctx: commands.Context):
        """ Skip the current song """
        await ctx.defer()
        vc = ctx.guild.voice_client
        if not vc:
            return await ctx.send("Not in a voice channel.")
        skipped = music.skip(ctx.guild.id, vc)
        await ctx.send("Skipped." if skipped else "Nothing to skip.")