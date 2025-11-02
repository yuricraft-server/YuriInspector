import discord
from discord.ext import commands
import asyncio
import auth
import seedloaf
import json

class server_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group()
    async def server(self, ctx):
        return

    async def startCheck(bot, channel: discord.TextChannel, startTime):
        statusChannel = await bot.fetch_channel(auth.STATUS_CHANNEL)

        started = False
        async for message in statusChannel.history(after=startTime):
            if message.author.id == bot.user.id and message.content == "**Server started!**":
                started = True
        
        if not started:
            embed = discord.Embed(
                colour = 0xed766a,
                description = "We're currently at max capacity,\nplease try again later."
            )
            embed.set_author(
                name = "Seedloaf",
                url = "https://seedloaf.com/",
                icon_url = "https://seedloaf.com/_next/image?url=%2Fimages%2Flogo.webp&w=64&q=75"
            )
            embed.set_thumbnail(
                url = "https://github.com/yuricraft-server/YuriInspector/blob/main/images/error_zzz_2.png?raw=true"
            )

            await channel.send(embed=embed, view=server_cog.retryView(bot=bot))

    class retryView(discord.ui.View):
        def __init__(self, bot):
            super().__init__()
            self.bot = bot

        @discord.ui.button(
            label = "Try Again",
            style = discord.ButtonStyle.primary
        )

        async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):
            seedloaf.server_interact("true")

            button.label = "server starting..."
            button.style = discord.ButtonStyle.secondary
            button.disabled = True
            await interaction.response.edit_message(view=self)

            await asyncio.sleep(120)
            await server_cog.startCheck(self.bot, interaction.channel, interaction.created_at)

    @server.command(help="it starts thge server")
    async def start(self, ctx):
        seedloaf.server_interact("true")
        starting = await ctx.reply("server starting...")

        await asyncio.sleep(120)
        await server_cog.startCheck(self.bot, ctx.channel, starting.created_at)

    @server.command()
    @commands.has_permissions(administrator=True)
    async def stop(self, ctx):
        seedloaf.server_interact("false")
        await ctx.reply("server stoping...")