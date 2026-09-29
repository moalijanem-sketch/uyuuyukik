import mysql.connector
from config import DB_HOST,DB_PORT,DB_USER,DB_PASSWORD,DB_NAME

def server_connection():
    return mysql.connector.connect(host=DB_HOST,port=DB_PORT,user=DB_USER,password=DB_PASSWORD)

def connection():
    return mysql.connector.connect(host=DB_HOST,port=DB_PORT,user=DB_USER,password=DB_PASSWORD,database=DB_NAME)

def init_db():
    c=server_connection(); cur=c.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cur.close(); c.close()
    c=connection(); cur=c.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS people(
        id INT AUTO_INCREMENT PRIMARY KEY,
        national_no VARCHAR(30) UNIQUE,
        full_name VARCHAR(150) NOT NULL,
        age INT NOT NULL,
        gender ENUM('ذكر','أنثى') NOT NULL,
        family_members INT DEFAULT 1,
        governorate VARCHAR(50) NOT NULL,
        residence VARCHAR(150),
        employment VARCHAR(100),
        salary DECIMAL(12,2) DEFAULT 0,
        education VARCHAR(80),
        marital_status VARCHAR(50),
        phone VARCHAR(30),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX(full_name), INDEX(governorate), INDEX(age)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role ENUM('admin','viewer') DEFAULT 'viewer',
        active BOOLEAN DEFAULT TRUE)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS audit_log(
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(80), action VARCHAR(100), details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    c.commit(); cur.close(); c.close()

def query(sql,params=(),fetch=False):
    c=connection(); cur=c.cursor(dictionary=True)
    try:
        cur.execute(sql,params)
        result=cur.fetchall() if fetch else cur.lastrowid
        c.commit(); return result
    finally:
        cur.close(); c.close()
