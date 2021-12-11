import pydnsbl
import json
import psycopg2
import ipaddress
from datetime import datetime, timezone

from redis import connection
from rq.decorators import job


# function to get IPv4adresses from a cidr netblock
def get_single_ip_range(nblock):
    return [ip.compressed for ip in ipaddress.IPv4Network(nblock)]




# function to check blacklist status of a single IP
def dnsbl_check(ip):
    ip_checker = pydnsbl.DNSBLIpChecker()
    res = ip_checker.check(ip)
    listed = res.blacklisted
    providers = {i.host:'Not listed' for i in res.providers}
    context = {}
    if listed:
        listed_by = json.dumps(list(res.detected_by.keys()))
        return {'ip': ip, 'listed': listed, 'listed_by': listed_by}
    
    return {'ip': ip, 'listed': False, 'listed_by': ''}
    # return context


# function to check blacklist status of a netblock/ ip range
def dnsbl_checklist(conn, ip_range):
    cur = conn.cursor()
    sql = "INSERT INTO blacklist_iphistory (ip_addr, listed, listed_by, check_datetime) VALUES (%s, %s, %s, %s)"
    dt = datetime.now(timezone.utc)
    for ip in ip_range:
        res = dnsbl_check(ip)
        print(res)
        cur.execute(sql, (res['ip'], res['listed'], res['listed_by'], dt))
    cur.close()

# create a database connection
def create_connection(db_name):
    conn = None
    try:
        conn = psycopg2.connect(
                host = "127.0.0.1",
                database = db_name,
                user = 'alamin',
                password = 'Qwerty123',
                port = 5432
        )
 
    except:
        print('Cannot create db connection')
    return conn


# def get_job_queue():
#     import redis
#     from redis import connection
#     from rq import Queue

#     r = redis.Redis()
#     q = Queue(connection=r)
#     return q


def get_nblock_info():
    conn = create_connection('blm_main_db')
    cur = conn.cursor()

    cur.execute('SELECT * FROM blacklist_netblock')
    # get the job queue
    # q = get_job_queue()
    for row in cur:
        nblock = row[1] + '/' + row[2]
        # print(nblock)
        dnsbl_checklist.delay(conn, get_single_ip_range(nblock))
        print('--------------\n')

    cur.close()
    conn.commit()
    conn.close()

if __name__ == '__main__':
    get_nblock_info()
