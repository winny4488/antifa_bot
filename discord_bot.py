import discord
import asyncio
import os
from main import rag_query
from main import refine
from helpers.chat_memory import ChatMemory

# Discord shit
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

# Replace this with your real token
# Go to (https://discord.com/developers/applications)
# Create bot, get token
# Replace "os.getenv()" with "your_token"
DISCORD_TOKEN = os.getenv("KOMUNA_TOKEN")
DISCORD_USER = int(os.getenv("KOMUNA_USER")) # Replace with your User ID integer

# Keep memory for context
memory = ChatMemory(max_messages = 8)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Talking to the bot
    query_cmd = message.content.startswith("!komuna")
    query_cmd_mention = client.user in message.mentions
    clear_cmd = message.content.startswith("!komuna clear")
    dump_cmd = message.content.startswith("!komuna dump")
    ref_cmd = message.content.startswith("!komuna refine")
    help_cmd = message.content.startswith("!komuna help")
    quit_cmd = message.content.startswith("!komuna quit")

    # Retrieve message history for ai
    recent_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in memory.get_history()
    ]

    if clear_cmd:
        memory.clear()
        await message.channel.send("Memory wiped")
        return
    elif dump_cmd:
        dump = str(memory.get_history())

        # Discord hard limit = 2000 chars
        max_len = 1900  # safe margin
        if len(dump) <= max_len:
            await message.channel.send(dump)
        else:
            # Split into chunks
            chunks = [dump[i:i+max_len] for i in range(0, len(dump), max_len)]
            for chunk in chunks:
                await message.channel.send(chunk)
        return
    elif ref_cmd:
        await message.channel.send("Reanalyzing chat history.")
        await message.channel.typing()
        new_response = refine(recent_messages)
        memory.add_message(role = "Komuna", content = new_response)
        await message.channel.send(new_response)
        return
    elif help_cmd:
        help_txt = f"""
            Hello! In order to get started using the AI, you can use the following commands:

            !komuna <query> - where <query> is what you want to ask the AI
            !komuna clear - clears the AI's memory in case the AI stops functioning properly
            !komuna dump - pastes the AI's memory to the chat, useful for debugging
            !komuna refine - if the AI misses your query or question, or just doesn't answer you correctly, you can ask the bot to redo the query, and hopefully receive a better answer. Only works if the AI remembers the chat
            !komuna quit - admin only, closes the cli python program

            Important note: Komuna will occasionally run into errors while typing into discord. This is almost always because of the 2000 character discord message limit. The discord bot adds a sneaky "(in 2000 characters or less)" to your query automatically to mitigate this, but it doesn't always work.
        """
        await message.channel.send(help_txt)
        return
    elif quit_cmd:
        if not message.author.id == DISCORD_USER: return
        await message.channel.send("Goodbye.")
        await client.close()
        return
    elif query_cmd:
        query = message.content[len("!komuna"):].strip()
    elif query_cmd_mention:
        # Remove bot mention(s) from the message
        query = message.clean_content.replace(f"@{client.user.name}", "").strip()
    else:
        return  # Ignore unrelated messages

    if not query:
        await message.channel.send("Komuna needs a query or message to formulate a response. Empty message detected.")
        return

    await message.channel.typing()
    try:
        # Store the message in memory
        memory.add_message(role = str(message.author.id), content = message.content)

        # Add character limit silently
        query = query + " (In 2000 characters or less)"

        # Get ai response
        response = await asyncio.to_thread(rag_query, query, recent_messages)
        cleaned_response = response.strip(' "\'')

        # Store ai response in memory
        memory.add_message(role = "Komuna", content = cleaned_response)

        # Send ai response
        await message.channel.send(cleaned_response)
    except Exception as e:
        await message.channel.send("Komuna encountered an issue. Admin: Check console.")
        print("Error:", e)


client.run(DISCORD_TOKEN)
