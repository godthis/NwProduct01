
#访问数据库
import re
import pymysql


def searchmysql(sql, pattern):
    connect = pymysql.connect(host="1.1.2.50",
                              port=33337,
                              user="root",
                              passwd="sniMSI234Nmi")
    cursor = connect.cursor()
    cursor.execute(sql)
    sqlresults = cursor.fetchall()
    #sqlresults = cursor.fetchone()
    connect.close()
    #print(str(sqlresults))
    # pattern ='[0-9]{3,}'
    regex = re.compile(pattern)
    #resutlt = re.search(regex, str(sqlresults)).group()
    resutlt=regex.findall(str(sqlresults))
    if resutlt:
        #print("resutlt " + str(resutlt))
        return str(resutlt)