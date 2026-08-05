from flask import abort
import pymysql
from util.DB import DB



db_pool = DB.init_db_pool()


# ユーザークラス
class User:
    @classmethod
    def create(cls, username, password):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO users (name, email, password, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW());"
                cur.execute(sql,(name, emaill, password))
                conn.commit()
                return cur.lastrowid
        except Exception as e:
            print(f'システムエラーが発生しました: {e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def find_by_email(cls, email):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM users WHERE email = %s;"
                cur.execute(sql,(email,))
                user = cur.fetchone()
            return user
        except Exception as e:
            print(f'システムエラーが発生しました: {e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def get_name_by_id(cls, user_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT name FROM users WHERE id = %s;"
                cur.execute(sql,(user_id,))
                user = cur.fetchone()
            return user['name'] if user else None
        except Exception as e:
            print(f'システムエラーが発生しました: {e}')
            abort(500)
        finally:
            db_pool.release(conn)

        
        