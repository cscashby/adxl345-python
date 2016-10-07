#!/usr/bin/python
import client.webclient
import client.display
import datetime
import sys

##################################################################################
## Main running thread code
##################################################################################

if __name__ == "__main__":
    if len(sys.argv) == 1:
        gameName = datetime.date.today().isoformat()
    else:
        gameName = sys.argv[1]

    print "Starting game with name {}".format(gameName)

    sys.argv = [sys.argv[0]]
    client.webclient.startWeb()
    client.display.run(gameName)