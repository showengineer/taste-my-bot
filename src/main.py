import server
import requests
import log 

logging = log.init_logger("SessionStealer", True)

def post_confirm(session, base_url, csrf_token):
    url = f"{base_url}/confirm"
    r = session.post(url, data={"csrf_token":csrf_token})
    return r

def initiate_join_event(session, event_url):
    url = f"{event_url}/join"
    r = session.get(url)
    return r

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
        if ~(r == "y" or r == "Y" or r == "j" or r == "J" or r == "ja"):
            logging.critical("Afgebroken door gebruiker")
            s.bexit()
            exit(1)

    
    s.bexit()


    
