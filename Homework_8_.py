import datetime
from multiprocessing import Queue
from multiprocessing import Process


def collatz_sequence(n):
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
    return True


def part_count(from_number, to_number, queue_object):
    count = 0
    for i in range(from_number, to_number):
        if collatz_sequence(i):
            count += 1
    queue_object.put(count)


if __name__ == '__main__':
    numbers_queue = Queue()
    num_processes = 4
    range_limit = 1000000000

    t1 = Process(target=part_count, args=(1, range_limit // num_processes, numbers_queue))
    t2 = Process(target=part_count,
                 args=(range_limit // num_processes, 2 * range_limit // num_processes, numbers_queue))
    t3 = Process(target=part_count,
                 args=(2 * range_limit // num_processes, 3 * range_limit // num_processes, numbers_queue))
    t4 = Process(target=part_count, args=(3 * range_limit // num_processes, range_limit, numbers_queue))

    print("Counting ...")
    print("Please wait ...")

    start_time = datetime.datetime.now()

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()

    end_time = datetime.datetime.now()
    print("Total time: ", end_time - start_time)

    total_count = 0
    while not numbers_queue.empty():
        total_count += numbers_queue.get()  

    print(f"Total numbers that passed the Collatz hypothesis check: {total_count}")






