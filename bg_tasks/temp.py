# 
from typing import Dict
import pydnsbl
import json
import psycopg2
from psycopg2.extras import DictCursor, DictRow
import ipaddress
from datetime import datetime, timezone
import time


# import redis stuff
import redis
from redis import connection
from rq.decorators import job
from rq import get_current_job, Retry


# create connection to redis
redis_conn = redis.Redis()

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


# conn = create_connection('blm_main_db')


# function to get IPv4adresses from a cidr netblock
def get_single_ip_range(nblock):
    return [ip.compressed for ip in ipaddress.IPv4Network(nblock)]


def dnsbl_check(ip):
    ip_checker = pydnsbl.DNSBLIpChecker()
    res = ip_checker.check(ip)
    listed = res.blacklisted
    providers = {i.host:'Not listed' for i in res.providers}
    context = {}
    if listed:
        listed_by = json.dumps(list(res.detected_by.keys()))
        return {'ip_addr': ip, 'listed': listed, 'listed_by': listed_by}
    
    return {'ip_addr': ip, 'listed': False, 'listed_by': ''}
    # return context



@job('scQueue', connection=redis_conn, timeout=6*3600, retry=Retry(max=5))
def dnsbl_checklist(parent_id, ip_range):
    conn = create_connection('blm_main_db')
    # Python RQ job related code
    job = get_current_job()
    start_ip_idx = job.meta.get('last_ip_idx', 0)
    print(f'{start_ip_idx = }')


    total_listed_ip = 0
    prev_total_listed_ip = 0
    # geting parent IP objcect of this ip_range
    cur = conn.cursor()
    cur1 = conn.cursor(cursor_factory=DictCursor)
    cur2 = conn.cursor(cursor_factory=DictCursor)
    cur3 = conn.cursor(cursor_factory=DictCursor)
    cur4 = conn.cursor(cursor_factory=DictCursor)

    cur.execute(f'SELECT total_listed_ip FROM blacklist_netblock WHERE id={parent_id}')
    # cur1.close()
    for row in cur:
        prev_total_listed_ip = int(row[0])


    ip_changes_insert_query = 'INSERT INTO blacklist_ipupdates (parent_id, ip_addr, listed, iphistory_id, update_time, created_at) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *'

    ip_hist_insert_query = "INSERT INTO blacklist_iphistory (parent_id, ip_addr, listed, listed_by, check_datetime) VALUES (%s, %s, %s, %s, %s) RETURNING listed, listed_by"
    
    # update the parent netblock with updated listed entries
    nblock_update_query = "UPDATE blacklist_netblock SET total_listed_ip=%s WHERE id=%s"

    # update or create iptable rows
    iptable_insert_query = '''
    INSERT INTO blacklist_iptable (parent_id, ip_addr, listed, listed_by, last_checked_at, updated_at, created_at) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''

    # select the old row of this ip from IPtable
    iptable_select_query = 'SELECT listed, listed_by FROM blacklist_iptable WHERE parent_id=%s and ip_addr=%s'

    iptable_update_query1 = '''
    UPDATE blacklist_iptable SET last_checked_at = %s WHERE parent_id=%s and ip_addr=%s
    '''

    iptable_update_query2 = '''
    UPDATE blacklist_iptable SET listed = %s, listed_by = %s, last_checked_at = %s, updated_at = %s WHERE parent_id=%s and ip_addr=%s
    '''

    job.save_meta()
    for idx, ip in enumerate(ip_range[start_ip_idx:]):
        job.meta['last_ip_idx'] = start_ip_idx + idx
        job.save_meta()
        res = dnsbl_check(ip) # updated result.
        print(res)
        if res['listed']:
            total_listed_ip += 1

        dt = datetime.now(timezone.utc)
        # inserting into IPhistory table on each scan.
        cur1.execute(ip_hist_insert_query, (parent_id, res['ip_addr'], res['listed'], res['listed_by'], dt))
        cmpr_data_dict = cur1.fetchone()

        # get previous data of this ip
        cur2.execute(iptable_select_query, (parent_id, res['ip_addr']))
        prev_data_dict = cur2.fetchone()
        

        if not prev_data_dict:
            print('########## LISTED 1ST TIME ############')
            cur2.execute(iptable_insert_query, (parent_id, res['ip_addr'], res['listed'], res['listed_by'], dt, dt, dt))

            # if res['listed']:
            #     print('########## LISTED 1ST TIME ############')
            #     cur4.execute(ip_changes_insert_query, (parent_id, res['ip_addr'], res['listed'], iphistory_id, dt, dt))
            #     print(cur4.fetchone())

        if prev_data_dict:
            if prev_data_dict == cmpr_data_dict:
                # just update the last_checked_at 
                cur3.execute(iptable_update_query1, (dt, parent_id, res['ip_addr']))
            if prev_data_dict != cmpr_data_dict:
                print('############## CHANGE FOUND ##############')
                cur4.execute(iptable_update_query2, (res['listed'], res['listed_by'], dt, dt, parent_id, res['ip_addr']))
                # print(cur4.fetchone())

        conn.commit()
    
    cur1.execute(nblock_update_query, (total_listed_ip, parent_id))
    
    cur.close()
    cur1.close()
    cur2.close()
    cur3.close()
    cur4.close()

    # commit all the changes to db
    conn.commit()
    conn.close()



def get_nblock_info():

    cur = conn.cursor()

    cur.execute('SELECT * FROM blacklist_netblock ORDER BY cidr')
    # get the job queue
    # q = get_job_queue()
    for row in cur:
        nblock = f'{row[1]}/{row[2]}'
        print(nblock)
        print(dnsbl_checklist.delay(row[0], get_single_ip_range(nblock)))
        print('--------------\n')

    cur.close()
    conn.commit()
    conn.close()



# @job('scQueue', connection=redis_conn)
# def func():
#     print('---------- START -----------')
#     time.sleep(5)
#     print('---------- ENDDD -----------')


