import asyncio

from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import run_async, run_js

chat_msgs = []
online_users = set()

MAX_MESSAGES_COUNT = 100

async def main():
    global chat_msgs

    put_markdown("##привет всем в этом чатике")

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)

    nickname = await input("Войти", required=True, placeholder="Никнейм", validate=lambda n: "Этот никнейм занят" if n in online_users or n == '' else None)

    online_users.add(nickname)

    chat_msgs.append(('!',f"{nickname} вошёл в чат"))
    msg_box.append(put_markdown(f"{nickname} вошёл в чат"))

    refresh_task = run_async(refresh_msg(nickname, msg_box))

    while True:
        data = await input_group("Сообщение", [
            input(placeholder='Текст', name ="msg"),
            actions(name='cmd', buttons=['Отправить', {'label':'Выйти из чата', 'type':'cancel'}])
        ], validate=lambda m: ('msg', 'Введите сообщение') if m['cmd'] == 'Отправить' and not m["msg"] else None)

        if data is None:
            break

        msg_box.append(put_markdown(f"{nickname}: {data['msg']}"))
        chat_msgs.append((nickname, data['msg']))

    #Выход из чата
    refresh_task.close()

    online_users.remove(nickname)
    toast("Вы вышли из чата")
    msg_box.append(put_markdown(f"Пользователь '{nickname}' вышел из чата"))
    chat_msgs.append(('!', f"Пользователь '{nickname}' вышел из чата"))



async def refresh_msg(nickname, msg_box):
    global  chat_msgs
    last_idx = len(chat_msgs)

    while True:
        await asyncio.sleep(1)

        for m in chat_msgs[last_idx:]:
            if m[0] != nickname:
                msg_box.append(put_markdown(f"'{m[0]}': {m[1]}"))

            if len(chat_msgs) > MAX_MESSAGES_COUNT:
                chat_msgs = chat_msgs[len(chat_msgs) // 2:]

            last_idx = len(chat_msgs)

if __name__ == "__main__":
    start_server(main, debug=True, port=8000, cdn=False)