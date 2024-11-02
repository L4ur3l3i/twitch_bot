# main.py
import concurrent.futures
from chat_bot import run_chat_bot
from countdown import run_countdown

def main():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Start both the chat bot and countdown in separate processes
        executor.submit(run_chat_bot)
        executor.submit(run_countdown)

if __name__ == "__main__":
    main()
