from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from selenium.webdriver.support import expected_conditions as EC
import time
import log
import threading
import resolve

logging = log.init_logger("SessionStealer", True)

class SessionStealer:
    def __init__(self):
        driver_path = "../assets/geckodriver"
        self.t_url = "https://www.asvtaste.nl/login?next=https%3A%2F%2Fwww.asvtaste.nl%2Fmijn-asv-taste%2Fevenementen"
        options = webdriver.FirefoxOptions()
        self.browser = webdriver.Firefox(options=options, executable_path=driver_path)
        self.koekjes = None
        self.window = self.browser.current_window_handle
        self.logged_in = False

    def login(self):
        logging.debug("Navigating to login page!")
        self.browser.get(self.t_url)

        try:
            wait = WebDriverWait(self.browser, 60, 0.5)
        except exceptions.TimeoutException:
            logging.critical("Kon niet inloggen, timeout")
            return None

        logging.debug("Waiting for login")
        wait.until(lambda driver: "login" not in driver.current_url)
        
        logging.debug("Left login page, checking login status.")
        # check if actually logged in
        try:
            element = self.browser.find_element_by_xpath("/html/body/header/nav[1]/div/ul/li[1]/a")
            
            # Dit is niet hele goede validatie maar ja, alles is server-side rendered dus geen keus
            if element.text != "Inloggen":
                self.logged_in = True
                logging.info(f"Logged in as {element.text}")
                
            else:
                raise Exception("Not actually logged in")

        except Exception as e:
            logging.critical("Could not confirm login, exiting.")
            logging.debug(e)
            self.browser.quit()
            exit(1)

        logging.debug("Getting cookies. KOEKJES!!!!")

        self.koekjes = self.get_session()

    def get_current_location(self) -> str:
        return self.browser.current_url

    def get_session(self):
        koekjes = self.browser.get_cookies()
        
        # Mocht er nog iets leuks mee gebeuren

        return koekjes
        
    
    def selector(self):
        # Gebruiker moet wat gaan doen!
        self.browser.execute_script("alert(\"Volg de aanwijzingen op de terminal!\");")
        logging.warn("Volg de aanwijzingen op dit scherm!")

        print("\nDruk op ENTER om door te gaan")

        # Het boeit me echt niet wat je hier invult, druk gewoon op ENTER
        # Dit is alleen om de thread te blokken
        input()

        # Get rid of alert
        try:
            self.browser.switch_to.alert.dismiss()
        except Exception:
            pass
        

        print("\nNavigeer naar de pagina van het evenement waar je bij wilt inschrijven\nAls je klaar bent, druk je hier op de Enter toets\n")
        
        path = "/html/body/main/div/section[1]/div/div/section/h1"

        c_event = None

        def inp():
            input()

        t = threading.Thread(target=inp)
        t.start()
        
        while t.is_alive():
            try:
                if not "evenementen" in self.browser.current_url:
                    time.sleep(1)
                    continue
                # Probeer de titel te vinde
                element = self.browser.find_element_by_xpath(path)
                c_event = element.text
                if c_event == "Evenementen":
                    c_event = None

                print(f"\33[2K\rHuidig gekozen evenement: {c_event}", end="\r")
                time.sleep(0.5)
            except exceptions.NoSuchElementException:
                pass
        print("")

        if c_event == None:
            logging.critical("No event selected!")
            self.browser.quit()
            exit(1)

        url = self.browser.current_url
        logging.debug(f"Selected target URL: {url}")

        # Probeer uit te vogelen vanaf wanneer we kunnen aanmelden
        txpath = "/html/body/main/div/section[1]/div/div/nav/div[2]/dl/dd"
        vxpath = "/html/body/main/div/section[1]/div/div/nav/div[2]/dl/dt"

        
        try:
            te = self.browser.find_element_by_xpath(txpath)
            
            if te.text == "Aanmelden voor dit evenement is niet meer mogelijk":
                logging.error("Can't sign up for this event!")
                return None
            elif te.text == "Aangemeld":
                logging.error("Already signed up for this event!")
                return None

            # Nested try blocks fuck yes
            try:
                ve = self.browser.find_element_by_xpath(vxpath)
                if ve.text == "Aanmelden mogelijk tot":
                    logging.warn("Enrollment already possible!")
                    return (url, self.koekjes, -1)
            except exceptions.NoSuchElementException:
                pass

            tie = resolve.resolve_datetime(te.text)
            logging.debug(f"Resolved time: {tie}")

            return (url, self.koekjes, tie)


        except exceptions.NoSuchElementException:
            logging.warn("Could not find elements to figure out time")
            return (url, self.koekjes, None)

    def bexit(self):
        self.browser.quit()
