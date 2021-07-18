from server import bot
import os

CURRENT_DIR = os.getcwd().replace('\\', '/')  # The current directory the bot is sitting in.


def main():
    """
    Requests the token that is needed to start the bot and then calls the function in the bot.py module to start it.
    """
    print('')
    print("Hi, you are about to launch the Analitica Discord Bot.")
    print("Before you do, there are a couple of thing you need to input:")
    print('')
    token = input("Please input the Authentication Token for the bot, as provided by Discord: ")
    print('')
    bot.launch(token)


if __name__ == '__main__':
    main()
