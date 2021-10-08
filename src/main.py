import server
import requests
import log 
import threading
import datetime

import time as stime

from lxml import etree
from io import StringIO

success = False
kill = False
thread_list = None

logging = log.init_logger("Taste my bott", True)

def post_confirm(session, url, csrf_token):
    headers = {
        "Referer" : url
    }
    r = session.post(url, data={"csrf_token":csrf_token}, headers=headers)
    return r

def initiate_join_event(session, event_url):
    url = f"{event_url}/join"
    r = session.get(url)
    return r


def join(session, koekjes, event_url) -> bool:
    logging.info("Proberen aan te melden...")
    join_request = ses.get(f"{event_url}/join", cookies=interessante_koekjes)

    if join_request.status_code != 200:
        logging.error("Join request denied!")
        return 
        
    join_html = join_request.content.decode("utf-8")

    ie = "/html/body/main/div/section[1]/div/div/section/form"

    treep = etree.HTMLParser()

    tree = etree.parse(StringIO(join_html), parser=treep)

    form = tree.xpath(ie)

    links = [link.get('action', '') for link in form]

    links = [l for l in links if l.endswith('/confirm')]

    if len(links) == 0:
        logging.critical("Could not find form!")
        return -1
    

    confirm_url = links[0]

    logging.debug(f"Found action url: {confirm_url}")

    elem = tree.xpath(f"{ie}/input")

    tokens = [e.get('value', '') for e in elem]

    if len(tokens) == 0:
        logging.critical("Could not find CSRF token!")
        return -1

    token = tokens[0]

    logging.debug(f"Found CSRF token: {token}")
    logging.debug("Attempting to confirm event attendance")

    confirm_r = post_confirm(ses, confirm_url, token)

    if confirm_r.status_code == 200:
        logging.success("It seems that signup was success! Check your email")
        return True
    elif confirm_r.status_code == 500 or confirm_r.status_code == 502:
        logging.warn("Server is overloaded!")
        return False
    else:
        logging.error("Something went wrong")
        logging.debug(confirm_r.text)
        return False



def threadloop(session, koek, event_url):
    global success
    global kill
    while True:
        try:
            if kill:
                break

            r = join(session, koek, event_url)
            if r == -1:
                kill = True
                break
            elif r:
                success = True
                break
            
        except Exception:
            pass


def gen_threads(session, koek, event_url, c = 8):
    l = []

    for _ in range(c):
        l.append(threading.Thread(target=threadloop, args=[session, koek, event_url]))
    return l



def wait_loop(start_time):
    print(f"Waiting till {start_time.strftime('%X')}\n")

    while True:
        ct = datetime.datetime.now()
        diff = start_time - ct
        print(f"Time left: {str(diff)}", end='\r')
        if diff.seconds < 1:
            break
        stime.sleep(0.166666)
    

if __name__ == "__main__":
    print("Taste Ticketbot v0.1")
  
    logging.debug("Initalizing sessionstealer")
    s = server.SessionStealer()
    logging.debug("Session stealer initalized")

    logging.debug("Initiating user selection")
    s.login()
    stealer = s.selector()
    
    if stealer == None:
        s.bexit()
        logging.critical("Aanmelden niet mogelijk")
        exit(1)

    # Switchen van user input
    event_url = stealer[0]
    koekjes = stealer[1]
    time = stealer[2]

    
    # TODO: Moet uiteindelijk zorgen dat user nog tijd kan aangeven
    if time == None:
        logging.critical("Kon tijd niet verkrijgen!")
        s.bexit()
        exit(1)

    # Aanmeldingen staan al open
    if time == -1:
        print("\nJe kan je al aanmelden voor dit evenement")
        r = input("Toch aanmelden? (y/N): ")
        if r != "y" and r != "Y" and r != "j" and r != "J" and r != "ja":
            logging.critical("Afgebroken door gebruiker")
            s.bexit()
            exit(1)

    
    
    s.bexit()

    ses = requests.Session()

    interessante_koekjes = {}

    # strip de koekjes
    for koekje in koekjes:
        interessante_koekjes[f"{koekje['name']}"] = f"{koekje['value']}"


    logging.info("Creating 8 workers...")
    thread_list = gen_threads(ses, interessante_koekjes, event_url)

    if time == -1:
        logging.info("Starting workers...")
        for t in thread_list:
            t.start()
    
    else:
        wait_loop(time)
        logging.info("Starting workers...")
        for t in thread_list:
            # Distribute requests
            stime.sleep(1)
            t.start()

    while not success and not kill:
        stime.sleep(0.1)


    if success:
        exit(0)
    else:
        exit(1)
    


    

    
