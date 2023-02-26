import mysql.connector
import pymysql

def mysql_connector():

    # the same dictionary as the python file called passport
    file_loc = "./passport"

    ## read from passport
    try:
        with open(file_loc, encoding='utf_8') as f:
            data = f.read().split('\n')
    except:
        print("Error reading passport file")
        return

    ## connecting to the database using 'connect()' method
    ## it takes 3 required parameters 'host', 'user', 'password'
    db = mysql.connector.connect(
        host=data[0],
        user=data[1],
        password=data[2]
    )

    print(db) # it will print a connection object if everything is fine

    db.close()

def pymysql():
    # !/usr/bin/python3

    import pymysql

    # 打开数据库连接
    db = pymysql.connect(host='comp208-team16.ctw17gkeyu80.eu-west-2.rds.amazonaws.com',
                         user='root',
                         password='5hqYXX55sFnIirPD868G',
                         database='test')

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    # 使用 execute()  方法执行 SQL 查询
    cursor.execute("SELECT VERSION()")

    # 使用 fetchone() 方法获取单条数据.
    data = cursor.fetchone()

    print("Database version : %s " % data)

    # 关闭数据库连接
    db.close()


if __name__ == '__main__':
    pymysql()
