# main.py
import discord
from discord.ext import commands
import datetime
import os
from dotenv import load_dotenv
# from keep_alive import keep_alive  # 一番上の方で追加

# .envファイルからトークンを読み込む
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# インテントの設定（Voiceとメッセージ内容を扱うにはこれが必要）
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Botインスタンスの作成
bot = commands.Bot(command_prefix="!", intents=intents)

# 入退室の記録用辞書
pretime_dict = {}


@bot.event
async def on_ready():
    print(f"ログイン成功: {bot.user}")


@bot.event
async def on_voice_state_update(member, before, after):
    print("ボイスチャンネルで変化がありました")

    # ミュートやスピーカーミュートだけの変化ならスキップ
    if before.self_mute != after.self_mute or before.self_deaf != after.self_deaf:
        print("ミュート設定の変更です")
        return

    # 入室処理
    if before.channel is None and after.channel is not None:
        pretime_dict[member.name] = datetime.datetime.now()

        # 「学習記録」チャンネルに入室メッセージを送信
        for channel in member.guild.text_channels:
            if channel.name == "学習記録（仮）":
                await channel.send(f"{member.display_name} さんが学習開始しました")
                break

# 退室処理
    elif before.channel is not None and after.channel is None:
        if member.name in pretime_dict:
            duration = datetime.datetime.now() - pretime_dict[member.name]
            duration_sec = int(duration.total_seconds())

            # 時・分・秒に変換
            hours = duration_sec // 3600
            minutes = (duration_sec % 3600) // 60
            seconds = duration_sec % 60

            # 時間のフォーマット作成
            if hours > 0:
                duration_text = f"{hours}時間{minutes}分{seconds}秒"
            elif minutes > 0:
                duration_text = f"{minutes}分{seconds}秒"
            else:
                duration_text = f"{seconds}秒"

            text = f"{member.display_name} さんが {before.channel.name} から抜けました。学習時間：{duration_text}"

            # 「学習記録」チャンネルに送信
            for channel in member.guild.text_channels:
                if channel.name == "学習記録（仮）":
                    await channel.send(text)
                    break


# ボット起動
# keep_alive()  # bot.run() の前にこれを呼ぶ

bot.run(TOKEN)
