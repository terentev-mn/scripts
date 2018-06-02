#!/usr/bin/env python
#-*- coding: utf-8 -*-
# Send message by xmpp

import sys

try:
    import xmpp
except:
    print('Please install xmpp module!')
    print('aptitude install python-xmpp')
    sys.exit


if len(sys.argv)<2:
    print("Usage: JID text")
    sys.exit
else:
    to = sys.argv[1]
    msg = sys.argv[2]
    try:
        xmpp_jid = 'nagios@domain.com'
        xmpp_pwd = 'password'
        jid = xmpp.protocol.JID(xmpp_jid)
        client = xmpp.Client(jid.getDomain(),debug=[])
        client.connect()
        client.auth(jid.getNode(),str(xmpp_pwd),resource=to)
        client.send(xmpp.protocol.Message(to,msg))
        client.disconnect()
    except:
        print('error connect'); response = ''
