import settings
import asyncio
import discord
import traceback
from discord.ext import commands
from typing import Set

logger = settings.logging.getLogger("bot")
cogs_logger = settings.logging.getLogger("cogs")
tree_logger = settings.logging.getLogger("tree")

class Client(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.presences = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix="+",
            intents=intents,
            help_command=None,
            case_insensitive=True,
            chunk_guilds_at_startup=False,
            status=discord.Status.do_not_disturb
        )
        
        self.client = self
        
        self._loaded_extensions: Set[str] = set()
        
    async def setup_hook(self):
        logger.info(f"Initializing....Refering myself as {self.user} (ID: {self.user.id})")
        
        try:
            await self.load_cogs()
            
            tree_logger.info("I'm Ready!")
        except Exception as exception:
            logger.error(f'Failed to initialize bot! : {exception}')
            logger.error(traceback.format_exc())

    async def load_cogs(self):
        cogs_logger.info("Loading cogs...")

        loaded_count = 0
        failed_loads = []
        
        for cog_file in settings.COGS_DIR.glob("*.py"):
            if cog_file.name == "__init__.py" : 
                continue
            
            extension_name = f'cogs.{cog_file.name[:-3]}'

            try :
                # skip if already loaded
                if extension_name in self._loaded_extensions:
                    cogs_logger.info(f"Extension {extension_name} exist! Skipping this")
                    continue
                
                await self.load_extension(extension_name)
                self._loaded_extensions.add(extension_name)

                loaded_count += 1
                cogs_logger.info(f'Loaded {cog_file.name}')
            except Exception as exception:
                error_msg = f"Failed to load {extension_name} : {exception}"
                cogs_logger.error(error_msg)
                failed_loads.append((extension_name, str(exception)))
            
        # log summary
        cogs_logger.info(f"Loaded {loaded_count} cogs successfully")
        if failed_loads:
            cogs_logger.warning(f"Failed to load {len(failed_loads)} cogs:")
            for ext, error in failed_loads:
                cogs_logger.warning(f"  - {ext} : {error}")
                
    async def reload_extension(self, extension_name: str) -> tuple[bool, str]:
        try:
            if extension_name in self._loaded_extensions:
                await self.unload_extension(extension_name)
            
            await self.load_extension(extension_name)

            if extension_name not in self._loaded_extensions:
                self._loaded_extensions.add(extension_name)
            
            return True, f"Successfully reloaded {extension_name}"
        except Exception as exception:
            error_msg = f"Failed to reload {extension_name} : {str(exception)}"
            cogs_logger.error(error_msg)
            
    async def sync_commands(self):
        try:
            tree_logger.info("Syncing all commands...")
            synced = await client.tree.sync()
            tree_logger.info(f"Synced {len(synced)} commands to global")

            await asyncio.sleep(5)
        except Exception as exception:
            error_msg = f"Error syncing commands : {str(exception)}"
            tree_logger.error(error_msg)
    
    async def on_command_error(self, ctx: commands.Context, error):
        command_name = str(ctx.command) if ctx.command else "unknown"
        
        logger.error(f"Command error in {command_name} : {error}")

        try:
            await ctx.send(f"An error occurred while executing the command. Please try again later...", ephemeral=True)
        except:
            pass
    
    async def close(self):
        logger.info("Shutting down bot...")

        await super().close()
        
client = Client()

@client.command(name="reload", description="Reload all commands")        
async def reload_commands(interaction: commands.Context):
    try:
        reloaded_cogs = 0
        reload_result = []
        
        for cog_file in settings.COGS_DIR.glob("*.py"):
            if cog_file.name == "__init__.py":
                continue
            
            extension_name = f'cogs.{cog_file.name[:-3]}'
            success = await client.reload_extension(extension_name=extension_name)
            
            if success:
                reloaded_cogs += 1
                cogs_logger.info(f"Reloaded {cog_file.name}")
                reload_result.append(f"SUCCESS : {cog_file.name}")
            else:
                reload_result.append(f"FAILED : {cog_file.name}")

        await interaction.send(f"Successfully reloaded {len(reload_result)} cogs!")
        
        await asyncio.sleep(3)
    except Exception as exception:
        error_msg = f"Error reloading cogs: {str(exception)}"
        cogs_logger.error(error_msg)
        cogs_logger.error(traceback.format_exc())

        await interaction.send(f"Error: {str(exception)}", ephemeral=True)

@client.command(name="sync", description="Sync all commands")
async def sync_commands(interaction: commands.Context):
    try:
        tree_logger.info("Syncing all commands...")
        synced = await client.tree.sync()
        tree_logger.info(f"Synced {len(synced)} commands to global")

        await interaction.send(f"Sycned {len(synced)} commands.")

        await asyncio.sleep(5)
    except Exception as exception:
        error_msg = f"Error syncing commands : {str(exception)}"
        tree_logger.error(error_msg)
        
        await interaction.send(f"Error: {str(exception)}")
        
@client.event
async def on_ready():
    try:
        logger.info(f'Bot ready : {client.user} (ID: {client.user.id})')
        logger.info(f'Connected to {len(client.guilds)} guilds')

        activity = discord.Activity(
            type=discord.ActivityType.playing,
            name=f"Playing Music and Vibing"
        )
        await client.change_presence(
            activity=activity,
            status=discord.Status.online
        )
    except Exception as exception:
        logger.error(f"Error in on_ready: {exception}")
        
if __name__ == "__main__":
    try:
        logger.info("Starting BOT...")
        client.run(settings.DISCORD_API_SECRET, root_logger=True, reconnect=True)
    except KeyboardInterrupt:
        logger.info("Bot shutting down requested by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        logger.error(traceback.format_exc())
    finally:
        logger.info("Bot process ended")