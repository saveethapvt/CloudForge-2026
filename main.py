import time
import random
from collections import deque

# Simulated task queue
task_queue = deque()

# Number of workers currently running
workers = 1
MAX_WORKERS = 5

print("🚀 CloudForge Queue-Depth Worker Scaling")
print("-" * 42)

for cycle in range(10):
    # New tasks arrive
    new_tasks = random.randint(2,8)
    for _ in range(new_tasks):
        task_queue.append("task")

    # Scale workers based on queue depth
    if len(task_queue) > 10 and workers < MAX_WORKERS:
        workers += 1
        print("⬆️ Scaling UP: Added a worker")

    elif len(task_queue) < 4 and workers > 1:
        workers -= 1
        print("⬇️ Scaling DOWN: Removed a worker")

    # Workers process tasks
    processed = min(len(task_queue), workers * 3)

    for _ in range(processed):
        task_queue.popleft()

    print(
        f"Cycle {cycle + 1}: "
        f"New tasks={new_tasks}, "
        f"Processed={processed}, "
        f"Queue={len(task_queue)}, "
        f"Workers={workers}"
    )

    time.sleep(1)

print("-" * 42)
print("✅ Demo completed!")
print("\n📊 FINAL QUEUE SUMMARY")
print(f"Remaining tasks: {len(task_queue)}")
print(f"Final worker count: {workers}")
print("Autoscaling simulation finished successfully!")