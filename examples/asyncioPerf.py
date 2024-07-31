import asyncio
import time

async def measure_sleep_precision(sleep_time, repetitions):
    total_diff = 0
    for _ in range(repetitions):
        start = time.perf_counter()
        await asyncio.sleep(sleep_time)
        end = time.perf_counter()
        total_diff += end - start - sleep_time
    avg_diff = total_diff / repetitions
    return avg_diff * 1000 # ms

async def main():
    sleep_time = 0.001  # 1 millisecond
    repetitions = 1000
    avg_diff = await measure_sleep_precision(sleep_time, repetitions)
    print(f"Average difference over {repetitions} repetitions: {avg_diff:.6f} ms")

asyncio.run(main())