import nonebot
from nonebot import RequestSession, on_request
from hoshino import util


@on_request('group.invite')
async def handle_group_invite(session: RequestSession):
	await session.approve()
