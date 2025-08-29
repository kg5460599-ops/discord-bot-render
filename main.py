import discord
from discord.ext import commands, tasks
import os
import asyncio
import datetime
import json

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix='!@', intents=intents)

# Bot statistics storage
bot_stats = {
    'start_time': None,
    'messages_sent': 0,
    'commands_used': 0,
    'servers_joined': 0,
    'members_served': 0
}

@bot.event
async def on_ready():
    bot_stats['start_time'] = datetime.datetime.now()
    print(f'🟢 {bot.user} is now ONLINE!')
    print(f'Bot ID: {bot.user.id}')
    print(f'Connected to {len(bot.guilds)} servers')
    print(f'Serving {len(bot.users)} users')
    
    # Start status update loop
    update_status.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Count messages for stats
    bot_stats['messages_sent'] += 1
    
    # Process commands
    await bot.process_commands(message)

@bot.event
async def on_guild_join(guild):
    bot_stats['servers_joined'] += 1
    print(f"Joined new server: {guild.name}")

@bot.event
async def on_command(ctx):
    bot_stats['commands_used'] += 1

# Status update task
@tasks.loop(minutes=5)
async def update_status():
    status_messages = [
        f"👀 Watching {len(bot.guilds)} servers",
        f"💬 {bot_stats['messages_sent']} messages processed",
        f"🎯 {bot_stats['commands_used']} commands used",
        "🔥 Always Online!"
    ]
    
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name=status_messages[bot_stats['commands_used'] % len(status_messages)]
    )
    await bot.change_presence(activity=activity, status=discord.Status.online)

@bot.command(name='ping')
async def ping(ctx):
    """Complete bot status and statistics"""
    
    # Calculate uptime
    if bot_stats['start_time']:
        uptime = datetime.datetime.now() - bot_stats['start_time']
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
    else:
        uptime_str = "Unknown"
    
    # Bot latency
    latency = round(bot.latency * 1000)
    
    # Status emoji based on latency
    if latency < 100:
        status_emoji = "🟢"
        status_text = "Excellent"
    elif latency < 200:
        status_emoji = "🟡"
        status_text = "Good"
    elif latency < 300:
        status_emoji = "🟠"
        status_text = "Average"
    else:
        status_emoji = "🔴"
        status_text = "Poor"
    
    # Create invite link
    invite_link = discord.utils.oauth_url(
        bot.user.id,
        permissions=discord.Permissions(administrator=True)
    )
    
    # Calculate total members across all servers
    total_members = sum(guild.member_count for guild in bot.guilds)
    
    # Create rich embed
    embed = discord.Embed(
        title=f"{status_emoji} Bot Status Report",
        description=f"**Status:** {status_text} ({latency}ms)",
        color=0x00ff00 if latency < 200 else 0xff0000,
        timestamp=datetime.datetime.now()
    )
    
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    
    # Bot Info Section
    embed.add_field(
        name="🤖 Bot Information",
        value=f"**Name:** {bot.user.name}\n"
              f"**ID:** {bot.user.id}\n"
              f"**Status:** 🟢 Online\n"
              f"**Uptime:** {uptime_str}",
        inline=True
    )
    
    # Server Stats Section
    embed.add_field(
        name="📊 Server Statistics",
        value=f"**Servers:** {len(bot.guilds)}\n"
              f"**Total Members:** {total_members:,}\n"
              f"**Channels:** {sum(len(guild.channels) for guild in bot.guilds)}\n"
              f"**Roles:** {sum(len(guild.roles) for guild in bot.guilds)}",
        inline=True
    )
    
    # Performance Stats
    embed.add_field(
        name="⚡ Performance",
        value=f"**Latency:** {latency}ms\n"
              f"**Messages:** {bot_stats['messages_sent']:,}\n"
              f"**Commands:** {bot_stats['commands_used']:,}\n"
              f"**Memory:** Active",
        inline=True
    )
    
    # System Info
    embed.add_field(
        name="🔧 System Information",
        value=f"**Python:** {discord.__version__}\n"
              f"**Discord.py:** {discord.__version__}\n"
              f"**Prefix:** `!@`\n"
              f"**Shards:** 1",
        inline=True
    )
    
    # Current Server Info
    embed.add_field(
        name="🏠 Current Server",
        value=f"**Name:** {ctx.guild.name}\n"
              f"**Members:** {ctx.guild.member_count:,}\n"
              f"**Owner:** {ctx.guild.owner.mention}\n"
              f"**Region:** {ctx.guild.preferred_locale}",
        inline=True
    )
    
    # Quick Links
    embed.add_field(
        name="🔗 Quick Links",
        value=f"[📨 Invite Bot]({invite_link})\n"
              f"[🆘 Support](https://discord.com)\n"
              f"[📚 Commands](https://discord.com)\n"
              f"[🌐 Website](https://discord.com)",
        inline=True
    )
    
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    await ctx.send(embed=embed)

@bot.command(name='invite')
async def invite(ctx):
    """Generate bot invite link"""
    invite_link = discord.utils.oauth_url(
        bot.user.id,
        permissions=discord.Permissions(administrator=True)
    )
    
    embed = discord.Embed(
        title="📨 Invite Me to Your Server!",
        description=f"Click [HERE]({invite_link}) to add me to your server!",
        color=0x7289da
    )
    
    embed.add_field(
        name="✨ Features:",
        value="• Real-time status monitoring\n"
              "• Server statistics\n"
              "• Performance metrics\n"
              "• 24/7 online presence",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='stats')
async def stats(ctx):
    """Detailed bot statistics"""
    embed = discord.Embed(
        title="📈 Detailed Statistics",
        color=0x00ff00
    )
    
    embed.add_field(
        name="📊 Usage Stats",
        value=f"Messages Processed: {bot_stats['messages_sent']:,}\n"
              f"Commands Used: {bot_stats['commands_used']:,}\n"
              f"Servers Joined: {bot_stats['servers_joined']:,}",
        inline=True
    )
    
    embed.add_field(
        name="🌐 Network Stats",
        value=f"Total Servers: {len(bot.guilds)}\n"
              f"Total Users: {len(bot.users):,}\n"
              f"Avg Latency: {round(bot.latency * 1000)}ms",
        inline=True
    )
    
    await ctx.send(embed=embed)

@bot.command(name='uptime')
async def uptime(ctx):
    """Check bot uptime"""
    if bot_stats['start_time']:
        uptime = datetime.datetime.now() - bot_stats['start_time']
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        embed = discord.Embed(
            title="⏰ Bot Uptime",
            description=f"🟢 **{days}** days, **{hours}** hours, **{minutes}** minutes, **{seconds}** seconds",
            color=0x00ff00
        )
        
        embed.add_field(name="Started At", value=bot_stats['start_time'].strftime("%Y-%m-%d %H:%M:%S UTC"))
        
        await ctx.send(embed=embed)

@bot.command(name='help')
async def help_command(ctx):
    """Show all available commands"""
    embed = discord.Embed(
        title="🆘 Bot Commands",
        description="Here are all available commands:",
        color=0x7289da
    )
    
    commands_list = {
        "!@ping": "Complete bot status and server stats",
        "!@invite": "Get bot invite link",
        "!@stats": "Detailed bot statistics",
        "!@uptime": "Check bot uptime",
        "!@help": "Show this help menu"
    }
    
    for cmd, desc in commands_list.items():
        embed.add_field(name=cmd, value=desc, inline=False)
    
    await ctx.send(embed=embed)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="❌ Command Not Found",
            description=f"Use `!@help` to see all available commands.",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=10)
    else:
        embed = discord.Embed(
            title="⚠️ Error Occurred",
            description=f"```{str(error)}```",
            color=0xff0000
        )
        await ctx.send(embed=embed)

# Keep bot alive
async def keep_alive():
    while True:
        print(f"🔄 Bot is running... Servers: {len(bot.guilds)} | Users: {len(bot.users)}")
        await asyncio.sleep(300)

# Run bot
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if not TOKEN:
        print("❌ Error: DISCORD_TOKEN environment variable not found!")
        print("Please set your bot token as an environment variable.")
    else:
        print("🚀 Starting Discord Bot...")
        bot.loop.create_task(keep_alive())
        bot.run(TOKEN)
