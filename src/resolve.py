# Ik snap niet waarom dit nodig is maar sure
# HERE COMES THE MAGIC NUMBERS


# VB: 13 okt. 2021 12:00:00
import datetime

def resolve_datetime(datestring):
    # strip volledig van spaties en punten
    datestring = datestring.replace(' ', '')
    datestring = datestring.replace('.', '')

    # first up, de datumnummer
    dateday = datestring[:2]

    # dan de maand, nu maar hopen dat alles 3 letters heeft
    datemonth = datestring[2:5]

    # jaartal
    dateyear = datestring[5:9]

    # uur...HEHE 9/11!
    datehour = datestring[9:11]

    dateminute = datestring[12:14]

    datesecond = datestring[15:17]

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
        raise ValueError("Could not resolve month")
    

    d = int(dateday)

    H = int(datehour)
    M = int(dateminute)
    S = int(datesecond)

    # Return de zooi naar iets waar we iets mee kunnen
    return datetime.datetime(
        y, m, d, H, M, S
    )
