from hoshino import Service, priv
from nonebot import *
import json
import pytz
import asyncio
from random import randint

sv_help = '''
私聊[塔罗牌]
'''.strip()

sv = Service(
    name = '塔罗牌',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '娱乐', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助塔罗牌"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    
    

bot = get_bot()

#初始化自定义信息
fn = "./hoshino/modules/tarot/"
with open(fn + 'settings.json') as f:
	s = json.load(f)
me = s['机器人自称']
u = s['对用户称呼']
g = s['回应的群聊']
t = s['每日限用次数']
h = s['次数更新时间（24小时）']


#快速读取
def q_l(filename):
	with open(filename) as f:
		return json.load(f)

#快速覆盖写入
def q_d(data,filename):
	with open(filename,'w') as f:
		json.dump(data,f)


#塔罗牌指令主体
@on_command('占卜', aliases=('塔罗牌'))
async def tarot(session: CommandSession):
	if not session.ctx['message_type'] == 'private':
		if session.ctx['group_id'] in g:
			session.finish(f'请私聊{me}使用时间胶囊哦！')
		else:
			session.finish()
	else:
		user = session.ctx['user_id']	
		#检查使用次数
		if not 'record' in session.state and not t == 0:
			record = q_l(fn + 'today_record.json')
			if str(user) in record.keys():
				if record[str(user)] >= t:
					session.finish(f'每天只能占卜{t}次哦!')
				else :
					record[str(user)] += 1
			else:
				record[str(user)] = 1
			session.state['record'] = record
				
		#确定占卜
		if not 'sure' in session.state:
			msg = ''
			if t != 0:
				msg += '注意，每人每天只能占卜%d次' % t
				msg += '\n（%d:00 更新）\n' % h
			msg += '占卜时若没按提示输入，会被视为放弃，千万注意哦'
			msg += '\n确定现在占卜的话,请输入 好'
			the_choice = session.get('0', prompt=msg)
			if the_choice == '好':
				q_d(session.state['record'],fn+'today_record.json')
				session.state['sure'] = True
			else:
				session.finish(f'{u}已取消占卜')
			await asyncio.sleep(0.3)
	
		#交代规则
		if not 'rule1' in session.state:
			msg = f'{me}利用程序尽可能还原了塔罗牌占卜过程'
			msg += '\n包括洗牌、切牌、抽取、翻牌'
			await session.send(msg)
			await asyncio.sleep(1.2)
			session.state['rule1'] = True
		if not 'rule2' in session.state:
			msg = '我们应用22张大阿卡纳与56张小阿卡纳'
			msg += '\n每张大阿卡纳分正位与逆位，代表不同的意思'
			msg += '\n小阿卡纳每张分别有特定的意思'
			msg += f'\n开始时，使用简化的"疑难牌阵"，抽取4张牌({me}会教你使用哦)'
			msg += '\n抽取完成后，会按顺序翻开'
			msg += '\n输入 好 可以进入下一步哦！'
			#等待用户的正确输入
			cnt = 0
			reply = session.get(f'r_decide{cnt}',prompt=msg)
			while True:
				if reply == '好':
					session.state['rule2'] = True
					break
				else: 
					cnt += 1
					msg = '想进入下一步的话...需要按要求回复哦！'
					reply = session.get(f'r_decide{cnt}',prompt=msg)
			await asyncio.sleep(0.3)
			
		#忠告
		if not 'tip' in session.state:
			msg = '注意了哦，\n塔罗牌功能仅供娱乐，有些重要的事情需要自己做决定'
			msg += '\n请勿过度参考结果或信以为真'
			await session.send(msg)
			session.state['tip'] = True
			await asyncio.sleep(1.5)
			
		#准备
		if not 'ready' in session.state:
			msg = f'嗯嗯，那么现在，请再默想一遍困扰{u}的问题'
			msg += '如果准备好了，就对我说 好'
			#等待用户的正确输入
			cnt = 0
			reply = session.get(f'ready{cnt}',prompt=msg)
			while True:
				if reply == '好':
					session.state['ready'] = True
					break
				else: 
					cnt += 1
					msg = '想进入下一步的话...要按要求回复哦！'
					reply = session.get(f'ready{cnt}',prompt=msg)
				
		#洗牌
		if not 'cards' in session.state:
			await session.send('开始随机打乱卡片')
			all_cards = []
			#加入大阿卡纳
			big_cards_names = ['愚者','魔术师','女教皇','皇帝','女皇','教皇',
				'恋人','战车','力量','隐士','命运之轮','正义','吊人','死神',
				'节制','恶魔','塔','星星','月亮','太阳','审判','世界']
			for big_card_name in big_cards_names:
				direction = randint(1,2)
				if direction == 1:
					direction = '正位'
				else :
					direction = '逆位'
				card_name = big_card_name + ' ' + direction
				all_cards.append(card_name)
			await asyncio.sleep(1)
			#加入小阿卡纳
			small_cards_names = ['SWORDS宝剑','CUP圣杯','WANDS权杖','PENTACES钱币']
			small_cards_types = ['1','2','3','4','5','6','7','8','9','10','侍者','骑士','王后','国王']
			for small_cards_name in small_cards_names:
				for small_cards_type in small_cards_types: 
					card_name = small_cards_name + ' ' + small_cards_type
					all_cards.append(card_name)
			await asyncio.sleep(1)
			#打乱牌库
			cards = []
			while all_cards:
				moved_card = all_cards.pop(randint(0,len(all_cards)-1))
				cards.append(moved_card)
			#完成洗牌
			await session.send('洗牌finish！')
			await asyncio.sleep(0.8)
			
			#切牌
			await session.send('开始切牌!')
			a = randint(25,35) #中间数
			b = randint(5,20) #最小数
			c = randint(40,50) #最大数
			moved_cards = cards[randint(b,a):randint(a,c)]
			await asyncio.sleep(0.8)
			for moved_card in moved_cards:
				cards.remove(moved_card)
				cards.append(moved_card)
			await session.send('切牌也完成了')
			session.state['cards'] = cards
			await asyncio.sleep(0.6)
			
		#抽牌	
		if not 'start_choose' in session.state:
			msg = f'接下来是选牌阶段，准备好了的话，请对{me}说 开始选牌'
			#等待用户的正确输入
			cnt = 0
			reply = session.get(f'start_choose{cnt}',prompt=msg)
			while True:
				if reply == '开始选牌':
					session.state['start_choose'] = True
					break
				else: 
					cnt += 1
					msg = '想进入下一步的话...要按要求回复哦！'
					reply = session.get(f'start_choose{cnt}',prompt=msg)
		if not 'choose_card' in session.state:
			session.state['c_cards'] = []
			msg = '牌阵需要4张牌，分别是1,2,3和切牌'
			msg += '\n一共有78张牌，请输入想要选取的牌的序号(正整数)'
			msg += '\n每个数字之间，请输入 和\n例如： \n1和16和34和78'
			msg += '\n警告：若选卡格式错误，将直接退出占卜！！！'
			choose_cards = session.get('cc', prompt=msg)
			get_cards = choose_cards.split('和')
			if len(get_cards) == 4:
				try:
					get_cards = map(int,get_cards)
				except ValueError:
					session.finish('序号必须是数字')
				for get_card in get_cards:
					if isinstance(get_card,float):
						session.finish('序号必须是整数')
					elif get_card > 78:
						session.finish('序号不能超过78呢')
					elif get_card < 1:
						session.finish('必须是正数哦!')
					#符合要求
					else:
						get_card_name = session.state['cards'][get_card-1]
						session.state['c_cards'].append(get_card_name)
			else:
				session.finish('格式有误')
			#完成选牌
			await session.send('正在将这些卡挑出...')
			await asyncio.sleep(1.1)
			del session.state['cards'] #删掉cards以节省空间（鸡肋）
			session.state['choose_cards'] = True
			await session.send('选牌已经完成!')
			await asyncio.sleep(1.2)

		
		
		#翻牌
		msg = f'下面就要开始翻牌咯，{u}!'
		msg += '\n每10秒会翻开一张牌哦'
		await session.send(msg)
		await asyncio.sleep(1.6)
		
		
		#读取
		big = q_l(fn + 'big.json')
		small = q_l(fn + 'small.json')
		meanings = q_l(fn + 'meanings.json')
		#告知结果
		needs = ['1','2','3','切']
		for need in needs:
			seeing = session.state['c_cards'].pop(0)
			
			msg = '准备翻开'
			if need == '切':
				message = '切牌'
			else:
				message = '第' + need +'张牌'
			msg += message
			await session.send(msg)
			await asyncio.sleep(0.9)
			msg = message + ' 结果是:\n'
			msg += seeing
			msg += '\n这张牌'
			msg += meanings[need]
			msg += '\n\n这张牌的内涵：\n'
			card_info = seeing.split()
			#小阿卡纳
			if card_info[0] in small.keys():
				card_meaning = small[card_info[0]][str(card_info[1])]
			#大阿卡纳
			else :
				card_meaning = big[card_info[0]][card_info[1]]
			msg+= card_meaning
			await session.send(msg)
			await asyncio.sleep(9.2)
		msg = f'根据每张牌的意思，{u}应该可以解决疑惑了吧'
		msg += '\n但是注意哦，不可以完全将其信以为真，自己也得做出适当判断'
		msg += f'\n辣么，祝{u}happy every day!'
		await session.send(msg)
	
	
#每天更新记录		
@scheduler.scheduled_job('cron',hour = h)
async def _():
	new = {}
	q_d({},fn + 'today_record.json')
