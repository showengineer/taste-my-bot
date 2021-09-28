import server


if __name__ == "__main__":
    s = server.SessionStealer()

    s.login()
    s.selector()

