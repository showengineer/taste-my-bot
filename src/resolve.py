# Ik snap niet waarom dit nodig is maar sure
# HERE COME THE MAGIC NUMBERS


# VB: 13 okt. 2021 12:00:00
import datetime

def resolve_datetime(datestring):
    # strip volledig van spaties en punten
    datestring = datestring.replace(' ', '')
    datestring = datestring.replace('.', '')

    appendone = 0

    # first up, de datumnummer
    dateday = datestring[:2]

    if not any(c.isalpha() for c in dateday):
        appendone = 1
    else:
        dateday = datestring[0]

    # dan de maand, nu maar hopen dat alles 3 letters heeft
    datemonth = datestring[1+appendone:4+appendone]

    # jaartal
    dateyear = datestring[4+appendone:8+appendone]

    # uur...HEHE 9/11!
    datehour = datestring[8+appendone:10+appendone]

    dateminute = datestring[11+appendone:13+appendone]

    datesecond = datestring[14+appendone:16+appendone]

    # converteer de hele meuk naar integers
    y = int(dateyear)
    
    # ik wou dat switch/case een ding was
    # py 3.10 ftw
    if datemonth == "jan":
        m = 1
    elif datemonth == "feb":
        m = 2
    elif datemonth == "mar":
        m = 3
    elif datemonth == "apr":
        m = 4
    elif datemonth == "mei":
        m = 5
    elif datemonth == "jun":
        m = 6
    elif datemonth == "jul":
        m = 7
    elif datemonth == "aug":
        m = 8
    elif datemonth == "sep":
        m = 9
    elif datemonth == "okt":
        m = 10
    elif datemonth == "nov":
        m = 11
    elif datemonth == "dec":
        m = 12
    else:
        raise ValueError(f"Could not resolve month '{datemonth}")
    

    d = int(dateday)

    H = int(datehour)
    M = int(dateminute)
    S = int(datesecond)

    # Return de zooi naar iets waar we iets mee kunnen
    return datetime.datetime(
        y, m, d, H, M, S
    )
