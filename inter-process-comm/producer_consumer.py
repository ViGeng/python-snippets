
from multiprocessing import Process, Queue
import time,os

def hard_work(load):
    for i in range(load):
        for _ in range(10000000):
            a = 99999 * 99999

def producer(queue):
    os.sched_setaffinity(0, {0})  # Set CPU affinity to CPU 0
    for i in range(10):
        item = f"Item {i}"
        hard_work(1)
        queue.put(item)
        print(f"Produced: {item}")
    queue.put(None)  # Signal the consumer that production is done
    print(f"Producer running on CPUs: {os.sched_getaffinity(0)}")


def consumer(queue):
    os.sched_setaffinity(0, {1})  # Set CPU affinity to CPU 1
    while True:
        item = queue.get()
        if item is None:
            break
        hard_work(10)
        print(f"Consumed: {item}")
    print(f"Consumer running on CPUs: {os.sched_getaffinity(0)}")

if __name__ == "__main__":
    queue = Queue()

    # Create and start producer process
    producer_process = Process(target=producer, args=(queue,))
    producer_process.start()

    # Create and start consumer process
    consumer_process = Process(target=consumer, args=(queue,))
    consumer_process.start()

    # Wait for the producer process to finish
    producer_process.join()

    # Wait for the consumer process to finish
    consumer_process.join()
