#!/usr/bin/python
import client.webclient
import client.display

##################################################################################
## Main running thread code
##################################################################################

if __name__ == "__main__":
    client.webclient.startWeb()
    client.display.run()
