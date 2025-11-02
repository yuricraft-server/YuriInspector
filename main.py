import discord
import random
import auth
import seedloaf
import asyncio
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from atproto import AsyncClient
from atproto_client.models.app.bsky.embed.images import View as AppBskyEmbedImagesView

bsky = AsyncClient()

intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix="$",
    intents=intents
)

@bot.event
async def on_ready():

    print("logging into bluesky...")
    await bsky.login(
        login=auth.BLUESKY_LOGIN,
        password=auth.BLUESKY_PASSWORD
    )

    print(f'Logged in as {bot.user.name}\n')
    await bot.change_presence(activity=discord.CustomActivity(name="girls kissing"), status=discord.Status.online)

@bot.event
async def on_message(message):
    if random.randint(1,50) == 1: await message.add_reaction("<:osagebwaa:1427902721410732032>")

    if message.content.lower() == "$yuri" and message.webhook_id != None:
        await get_yuri(message.channel, 1)
        return

    await bot.process_commands(message)

async def get_yuri(channel: discord.TextChannel, count: int):
    profile_feed = await bsky.get_author_feed(actor=auth.BLUESKY_USER, limit=100)
    feed_views = random.choices(profile_feed.feed, k=count)

    for feed_view in feed_views:
        embed = feed_view.post.embed
        urls = []

        if isinstance(embed, AppBskyEmbedImagesView):
            for image in embed.images:
                urls.append(image.fullsize)

        dembed = discord.Embed(color=0x9BB6A7)
        dembed.set_image(url=urls[0])
        reply = await channel.send(embed=dembed)
        yuri_channel = bot.get_channel(auth.YURI_CHANNEL)
        if channel != yuri_channel: await reply.forward(destination=yuri_channel)

@bot.hybrid_command()
async def yuri(ctx, count: int = 1):
    await get_yuri(ctx.channel, count)

@bot.hybrid_command()
async def yaoi(ctx):
    await ctx.channel.send("no.")

@bot.command()
async def load_commands(ctx):
    await bot.tree.sync()
    await ctx.channel.send("commands loaded")

@bot.group()
async def server(ctx):
    return

async def startCheck(channel: discord.TextChannel, startTime):
    statusChannel = bot.fetch_channel(auth.STATUS_CHANNEL)

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
            url = "https://github.com/yuricraft-server/YuriInspector/blob/main/images/error.png?raw=true"
        )

        await channel.send(embed=embed, view=retryView())

class retryView(discord.ui.View):
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
        await startCheck(interaction.channel, interaction.created_at)

@server.command(help="it starts thge server")
async def start(ctx):
    seedloaf.server_interact("true")
    starting = await ctx.reply("server starting...")

    await asyncio.sleep(120)
    await startCheck(ctx.channel, starting.created_at)

@server.command()
@commands.has_permissions(administrator=True)
async def stop(ctx):
    seedloaf.server_interact("false")
    await ctx.reply("server stoping...")

bot.run(auth.TOKEN)
