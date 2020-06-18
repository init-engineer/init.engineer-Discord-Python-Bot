import os

from utils import default
from utils.data import Bot, HelpFormat
from multiprocessing import Process

def main():
    config = default.get("config.json")
    print("機器人登入中 ...")

    bot = Bot(
        command_prefix=config.prefix,
        prefix=config.prefix,
        command_attrs=dict(hidden=True),
        help_command=HelpFormat()
    )

    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            name = file[:-3]
            bot.load_extension(f"cogs.{name}")

    bot.run(config.token)


if __name__ == '__main__':
    while True:
        p = Process(target=main)
        p.start()
        p.join()
        if p.exitcode == 100:
            print('準備重啟 ...')
            continue
        else:
            break
