import redis
from redis import connection
from rq import Queue

import time

r = redis.Redis()
q = Queue(connection=r)

from bg_task import bg_task
from temp import myfunc



def main():
    for i in range(20):
        job = q.enqueue(myfunc, args=('amin', 3))
        # q.enqueue(commit_db, depends_on=j)
        # job = q.enqueue(bg_task, 5)
        print(f"Task ({job.id}) added to queue at {job.enqueued_at}")
        print(f'{job.result = }')
    print(len(q.jobs))


if __name__ == '__main__':
    main()