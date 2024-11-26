import datetime
from multiprocessing import Pool

def collatz_sequence(n):
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
    return True

def count_collatz_up_to_number(to_number):
    count = 0
    for i in range(1, to_number):
        if collatz_sequence(i):
            count += 1
    return count

# завд для кожного процесу
def worker_task(number):
    return collatz_sequence(number)

if __name__ == '__main__':
    num_processes = 4
    range_limit = 1000000
    chunk_size = range_limit // num_processes

    print("Counting ...")
    print("Please wait ...")

    start_time = datetime.datetime.now()

    with Pool(processes=num_processes) as pool:
        results = pool.map(worker_task, range(1, range_limit))

    total_count = sum(results)

    end_time = datetime.datetime.now()
    print("Total time: ", end_time - start_time)

    print(f"Total numbers that passed Collatz hypothesis: {total_count}")







