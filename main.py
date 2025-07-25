# main.py

import discord
from discord.ext import commands
import datetime
import os

# Railwayの環境変数からトークンを取得（.envは不要）
TOKEN = os.environ.get("DISCORD_TOKEN")
print("読み込んだDISCORD_TOKEN:", repr(TOKEN))  # 確認用

if TOKEN is None:
    raise ValueError("DISCORD_TOKEN が設定されていません")

# インテントの設定
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

pretime_dict = {}

@bot.event
async def on_ready():
    print(f"✅ ログイン成功: {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    print("🎧 ボイスチャンネルの状態が更新されました")

    if before.self_mute != after.self_mute or before.self_deaf != after.self_deaf:
        print("🔇 ミュート設定の変更のため、無視されました")
        return

    if before.channel is None and after.channel is not None:
        await handle_join(member)
    elif before.channel is not None and after.channel is None:
        await handle_leave(member, before.channel)

async def handle_join(member):
    pretime_dict[member.name] = datetime.datetime.now()
    print(f"{member.name} が {member.voice.channel.name} に参加しました")

    text = f"{member.display_name} さんが学習開始しました"
    await send_to_log_channel(member.guild, text)

async def handle_leave(member, channel_left):
    join_time = pretime_dict.pop(member.name, None)

    if join_time:
        elapsed = datetime.datetime.now() - join_time
        seconds = int(elapsed.total_seconds())
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds %= 60

        duration_str = f"{hours}時間{minutes}分{seconds}秒" if hours > 0 else (
            f"{minutes}分{seconds}秒" if minutes > 0 else f"{seconds}秒"
        )

        text = f"{member.display_name} さんが {channel_left.name} から抜けました。学習時間：{duration_str}"
        await send_to_log_channel(member.guild, text)

async def send_to_log_channel(guild, message):
    for channel in guild.text_channels:
        if channel.name == "学習記録（仮）":
            await channel.send(message)
            break

# ボット起動
bot.run(TOKEN)
