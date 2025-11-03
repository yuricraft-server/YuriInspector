import discord
import random
import auth
import seedloaf
import asyncio
import serverCog
import uhh
import typing
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

    print("loading cogs...")
    await bot.add_cog(serverCog.server_cog(bot=bot))

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

    embeds = [[]]
    for feed_view in feed_views:
        embed = feed_view.post.embed
        urls = []

        if isinstance(embed, AppBskyEmbedImagesView):
            for image in embed.images:
                urls.append(image.fullsize)

        dembed = discord.Embed(color=0x9BB6A7)
        dembed.set_image(url=urls[0])
        if len(embeds[len(embeds)-1]) == 10: embeds.append([])
        embeds[len(embeds)-1].append(dembed)
    for embeds_object in embeds:
        reply = await channel.send(embeds=embeds_object)
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
async def textures(ctx):
    return

@textures.command()
@commands.has_role(1427690676635570238)
async def release(ctx, repository: typing.Literal["MintyTex", "SimpleMintyTex"], *, title: str):
    uhh.create_release(
        repo = repository,
        title = title
    )

    await ctx.reply(f"created release `{repository} {title}`.")

bot.run(auth.TOKEN)
