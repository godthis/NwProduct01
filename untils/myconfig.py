# -*- coding: utf-8 -*-
from untils.searchDB import initmysqlparm


def choiceEnv(envname):
    if envname == '巴龙':
        username = 'BL0001'
        password = 'qs8888'
        baseurl = 'http://issx.bl.test2.qs.com'

        host = "1.1.2.50"
        port = 33337
        user = "root"
        passwd = "sniMSI234Nmi"

        initmysqlparm(host, port, user, passwd)

        return (username, password, baseurl)
    elif envname == '七匹狼':
        username = 'QPL001'
        password = 'qs8888'
        baseurl = 'http://issx.bl.test2.qs.com'

        host = "1.1.2.50",
        port = 33337,
        user = "root",
        passwd = "sniMSI234Nmi"
        initmysqlparm(host, port, user, passwd)
        return (username, password, baseurl)