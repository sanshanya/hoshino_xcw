from sqlitedict import SqliteDict

from hoshino import CanceledException, message_preprocessor, trigger, priv
from hoshino.typing import CQEvent
import hoshino

if hoshino.config.authMS.auth_config.ENABLE_COM:
    path_first = hoshino.config.authMS.auth_config.DB_PATH
else:
    path_first = './'
    
key_dict = SqliteDict(path_first+'key.sqlite', autocommit=True)
group_dict = SqliteDict(path_first+'group.sqlite', autocommit=True)
trial_list = SqliteDict(path_first+'trial.sqlite', autocommit=True) # 试用列表

@message_preprocessor
async def handle_message(bot, event: CQEvent, _):
    if event.detail_type != 'group':
        return
    if event.group_id not in group_dict:
        return
    for t in trigger.chain:
        sf = t.find_handler(event)
        if sf:
            trigger_name = t.__class__.__name__
            break

    if not sf:
        return  # triggered nothing.
    sf.sv.logger.info(f'Message {event.message_id} triggered {sf.__name__} by {trigger_name}.')

    if sf.only_to_me and not event['to_me']:
        return  # not to me, ignore.

    if not sf.sv._check_all(event):
        return  # permission denied.

    try:
        await sf.func(bot, event)
    except CanceledException:
        raise
    except Exception as e:
        sf.sv.logger.error(f'{type(e)} occured when {sf.__name__} handling message {event.message_id}.')
        sf.sv.logger.exception(e)
    raise CanceledException(f'Handled by {trigger_name} of Hoshino')
