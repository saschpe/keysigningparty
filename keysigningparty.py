#!/usr/bin/env python
#
# Copyright (c) 2010 Sascha Peilicke <sasch.pe@gmx.de>

import re
import sys
import subprocess


def parse_cmdline():
    from optparse import OptionParser

    parser = OptionParser(usage="usage: %prog [options] FILE")
    parser.add_option("-e", "--event", dest="eventName", help="name of the keysigning event", metavar="EVENT")
    parser.add_option("-m", "--message", dest="emailMessage", help="mail message content", metavar="EMAIL")
    parser.set_defaults(eventName = "keysigning party")
    parser.set_defaults(emailMessage = 
"""Hello!

It was nice meeting you at '%s'! If I can make it to the next one, perhaps I'll see you there again?

Anyway, thanks for signing my key (and you've not done so yet, hopefully you will soon...). I've signed your key to which you provided the fingerprint and have attached it to this e-mail.

Take care!
""")
    global options
    global args
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("please provide a valid keyfile (one key ID per line)!")


def sign_keys():
    # Read keys from file (format: one key ID per line)
    keys = [key.splitlines()[0] for key in sys.stdin.readlines()]
    for key in keys:
        print '='*10, 'Processing %s' % key, '='*30

        subprocess.call('gpg --recv-keys %s' % key, shell=True)
        subprocess.call('gpg --sign-key %s' % key, shell=True)

        # Extract primary UID e-mail address from fingerprint
        p = subprocess.Popen('gpg --fingerprint %s' % key, shell=True, stdout=subprocess.PIPE)
        p.wait()
        fingerprintOutput = p.stdout.readlines()

        for line in fingerprintOutput:
            if line.startswith("uid"):
                matches = re.compile("<(.*)>").search(line)
                if matches is not None:
                    emailAddress = matches.group(1)
                    break

        # Export
        subprocess.call('gpg --export -a %s > %s/%s.asc' % (key, tempDir, key), shell=True)
        print


def send_keys():
    # Send e-mail via KMail's dbus interface
    for key in keys:
        subprocess.call('qdbus org.kde.kmail /KMail org.kde.kmail.kmail.openComposer "%s" "" "" "Your signed key from %s" "%s" 0 "" "%s/%s.asc"' % (emailAddress, eventName, emailMessage, tempDir, key), shell=True)



if __name__ == "__main__":
    parse_cmdline()