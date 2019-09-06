#访问数据库
import pymysql

def initmysqlparm(host,port,user,passwd):
    global hostparm, portparm, userparm, passwdparm
    hostparm = host
    portparm = port
    userparm = user
    passwdparm = passwd


def searchmysql(sql):
    global hostparm, portparm, userparm, passwdparm
    connect = pymysql.connect(host=hostparm,
                              port=portparm,
                              user=userparm,
                              passwd=passwdparm)
    cursor = connect.cursor()
    cursor.execute(sql)
    sqlresults = cursor.fetchall()
    #sqlresults = cursor.fetchone()
    connect.close()
    if sqlresults:
        return str(sqlresults)