import discord


async def send_discord_message(token, channel_id, message, image_path=None):
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    async def on_ready():
        print(f'Logged in as {client.user} (ID: {client.user.id})')
        print('------')

        channel = client.get_channel(channel_id)

        if channel:
            if isinstance(message, list):
                for msg in message:
                    await channel.send(msg)
            else:
                await channel.send(message)

            if image_path:
                await send_image(channel, image_path)
        else:
            print(f"Could not find channel with ID: {channel_id}")

        await client.close()

    async def send_image(channel, image_path):
        with open(image_path, 'rb') as image_file:
            await channel.send(file=discord.File(image_file, filename=image_path))

    client.on_ready = on_ready

    async with client:
        await client.start(token)
