import asyncio

async def start_countdown():
    for i in range(600):
        remaining = 600 - i
        minutes = str(remaining // 60).zfill(2)
        seconds = str(remaining % 60).zfill(2)
        with open('output/countdown.txt', 'w') as file:
            file.write(f"{minutes}:{seconds}")
        await asyncio.sleep(1)

# Function to run the countdown
def run_countdown():
    asyncio.run(start_countdown())
