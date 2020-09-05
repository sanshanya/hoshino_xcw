import os
from .__bot__ import HOST, PORT

ICP_CONTENT = os.environ.get('ICP_CONTENT') if os.environ.get('ICP_CONTENT') else ''
PUBLIC_ADDRESS = os.environ.get('PUBLIC_ADDRESS') if os.environ.get('PUBLIC_ADDRESS') else f"http://333.33.33.33:9222"
PASSWORD = os.environ.get('BOT_MANAGER_WEB_PASSWORD') if os.environ.get('BOT_MANAGER_WEB_PASSWORD') else 'xcw'

#PUBLIC_ADDRESS = os.environ.get('PUBLIC_ADDRESS') if os.environ.get('PUBLIC_ADDRESS') else f"http://{HOST}:{PORT}"，将{host}改为你的服务器ip
#PASSWORD = os.environ.get('BOT_MANAGER_WEB_PASSWORD') if os.environ.get('BOT_MANAGER_WEB_PASSWORD') else '987654321'，987654321就是密码可改
#登陆地址 XXX.XXX.XXX.XXX:xxxx/manage     ":"前是你服务器ip，后面是你的端口，本整合包默认9222