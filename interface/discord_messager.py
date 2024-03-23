import discord


class DiscordMessager(discord.Client):
    def __init__(self, channel_id, message, image_path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_id = channel_id
        self.message = message
        self.image_path = image_path

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

        channel = self.get_channel(self.channel_id)

        if channel:
            if self.message:
                await channel.send(self.message)
            if self.image_path:
                await self.send_image(channel, self.image_path)
        else:
            print(f"Could not find channel with ID: {self.channel_id}")

        await self.close()

    async def send_image(self, channel, image_path):
        with open(image_path, 'rb') as image_file:
            await channel.send(file=discord.File(image_file, filename=image_path))


async def send_discord_message(token, channel_id, message='Hello, Discord!', image_path=None):
    intents = discord.Intents.default()
    client = DiscordMessager(channel_id, message, image_path, intents=intents)

    async with client:
        await client.start(token)
        await client.wait_until_ready()
        await client.close()

