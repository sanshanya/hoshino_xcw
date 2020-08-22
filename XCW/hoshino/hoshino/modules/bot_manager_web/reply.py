import nonebot
from hoshino.config.bot_manager_web import PUBLIC_ADDRESS

bot = nonebot.get_bot()


@bot.on_message('private')
async def setting(ctx):
    message = ctx['raw_message']
    if message == 'bot设置':
        await bot.send(ctx, f'{PUBLIC_ADDRESS}/manage', at_sender=False)
