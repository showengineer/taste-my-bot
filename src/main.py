# Alles met interwebs ofzo
import server
import requests

# Loggen met kleur!
import log 

# Zodat ik met 100 requests tegelijk kan inschrijven!
import threading

# Tijd enz
import datetime

# Tijd maar dan voor thread blocking
import time as stime

# HTML parser 
from lxml import etree
from io import StringIO

# Globals, vooral voor de threads
success = False
kill = False
thread_list = None

# "Ik heb hier een pakketje voor ene Neo Naz-"
# "Leuke naam"
logging = log.init_logger("Taste my bott", True)

# Als we naar /confirm posten. 
# Schijnbaar moet je een Referer header meegeven. 
# What a sissy... (zeg met nifterig stemmetje...
# voor de ultieme mood).
def post_confirm(session, url, csrf_token):
    headers = {
        "Referer" : url
    }
    r = session.post(url, data={"csrf_token":csrf_token}, headers=headers)
    return r


# We moeten eerst naar /join
# Want daar zit een CSRF token in die we weer nodig hebben
# Om /confirm te laten werken. Gezellig!
# Nu maar hopen dat we geen extra shit moeten invullen.
# Want anders is het allemaal een beetje J A M M E R!
def initiate_join_event(session, event_url):
    url = f"{event_url}/join"
    r = session.get(url)
    return r

# Main join functie
def join(session, koekjes, event_url) -> bool:
    logging.info("Proberen aan te melden...")

    # GET request naar /join
    join_request = ses.get(f"{event_url}/join", cookies=interessante_koekjes)

    # Ja dit is dus kut.
    if join_request.status_code != 200:
        logging.error("Join request denied!")
        return 
        
    # Verkrijg de HTML
    join_html = join_request.content.decode("utf-8")

    # XPATH naar de form.
    ie = "/html/body/main/div/section[1]/div/div/section/form"

    # Parse, parse, parse
    treep = etree.HTMLParser()
    tree = etree.parse(StringIO(join_html), parser=treep)
    form = tree.xpath(ie)

    # Verkrijg alle hrefs/action attribute waardes
    links = [link.get('action', '') for link in form]

    # Hier zou /confirm tussen moeten zitten
    links = [l for l in links if l.endswith('/confirm')]

    # TODO: Invullen van shit.
    if len(links) == 0:
        logging.critical("Could not find form!")
        return -1
    
    # Dit moet er maar één zijn maar ja, je weet maar nooit.
    confirm_url = links[0]

    logging.debug(f"Found action url: {confirm_url}")

    # Verkrijg de hidden inputs
    elem = tree.xpath(f"{ie}/input")

    # In de value attribute zou een CSRF token moeten zitten.
    tokens = [e.get('value', '') for e in elem]

    # Wat?!
    if len(tokens) == 0:
        logging.critical("Could not find CSRF token!")
        return -1

    # Ook hier hoort maar één token in te zitten, maar ja.
    token = tokens[0]

    logging.debug(f"Found CSRF token: {token}")
    logging.debug("Attempting to confirm event attendance")

    # Confirm met alle info die we hebben gekregen!
    confirm_r = post_confirm(ses, confirm_url, token)

    # PROFIT!
    if confirm_r.status_code == 200:
        logging.success("It seems that signup was success! Check your email")
        return True

    # Dit gebeurt VAAK. 
    # Ik snap niet waarom hier niet over is nagedacht.
    # "Mhm, er gaat een kroegavond komen, de registratie is om 12 uur 
    # en IEDEREEN WIL KOMEN! Hoe zou het komen dat de website platligt?"
    elif confirm_r.status_code == 500 or confirm_r.status_code == 502:
        logging.warn("Server is overloaded!")
        return False
    # Iets anders waar ik te lui voor was om rekening mee te houden.
    # Deal with it.
    else:
        logging.error("Something went wrong")
        logging.debug(confirm_r.text)
        return False



def threadloop(session, koek, event_url):
    global success
    global kill
    
    # ga in een inifinite loop zitten
    while True:
        try:
            # Kill commando, break
            if kill:
                break

            # Commit werk
            r = join(session, koek, event_url)

            # Pak resultaat
            # Kill commando, set and break.
            if r == -1:
                kill = True
                break
            # We did it, set and break!
            elif r:
                success = True
                break
        # negeer
        except Exception:
            pass

# Maakt een lijst van thread workers
# Ze zijn nog niet actief tho.
def gen_threads(session, koek, event_url, c = 8):
    l = []

    for _ in range(c):
        l.append(threading.Thread(target=threadloop, args=[session, koek, event_url]))
    return l


# Blokkeer main thread totdat tijd is verstreken.
# Zit een seconde 'speeltijd' in want update is niet snel.
def wait_loop(start_time):
    print(f"Waiting till {start_time.strftime('%X')}\n")

    while True:
        ct = datetime.datetime.now()
        diff = start_time - ct
        print(f"Time left: {str(diff)}", end='\r')
        if diff.seconds < 1:
            break
        stime.sleep(0.166666)
    

# Main functie.
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
    


    

    
