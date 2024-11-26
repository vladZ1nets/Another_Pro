import datetime
from multiprocessing import Queue, Process
from multiprocessing import Pool


def collatz_sequence(n):
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
    return True


def part_count(from_number, to_number):
    count = 0
    for i in range(from_number, to_number):
        if collatz_sequence(i):
            count += 1
    return count


def worker_task(task_range):
    from_number, to_number = task_range
    return part_count(from_number, to_number)


if __name__ == '__main__':
    num_processes = 4
    range_limit = 1000000000
    chunk_size = range_limit // num_processes

    task_ranges = [(i * chunk_size, (i + 1) * chunk_size) for i in range(num_processes)]

    print("Counting ...")
    print("Please wait ...")

    start_time = datetime.datetime.now()

    with Pool(processes=num_processes) as pool:
        results = pool.map(worker_task, task_ranges)

    total_count = sum(results)

    end_time = datetime.datetime.now()
    print("Total time: ", end_time - start_time)

    print(f"Total numbers that passed Collatz hypothesis: {total_count}")






