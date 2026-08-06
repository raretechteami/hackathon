from flask import abort
import pymysql
from util.DB import DB



db_pool = DB.init_db_pool()


# ユーザークラス
class User:
    @classmethod
    def create(cls, name, email, password):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO users (name, email, password, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW());"
                cur.execute(sql,(name, email, password))
                conn.commit()
                return cur.lastrowid
        except pymysql.Error as e:
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
        except pymysql.Error as e:
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
        except pymysql.Error as e:
            print(f'システムエラーが発生しました: {e}')
            abort(500)
        finally:
            db_pool.release(conn)

class Post:
    @classmethod
    def get_all_posts(cls):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                    SELECT posts.*, user_posts.user_id 
                    FROM posts 
                    JOIN user_posts ON posts.id = user_posts.post_id 
                    WHERE posts.delete_flag = FALSE 
                    ORDER BY posts.created_at DESC;
                """
                cur.execute(sql)
                posts = cur.fetchall()
            
            return posts
        except pymysql.Error as e:
            print(f'システムエラーが発生しました: {e}')
            abort(500)
        finally:
            db_pool.release(conn)

    # createメソッド追加

























    @classmethod
    def delete(cls, post_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "UPDATE posts SET delete_flag = TRUE, updated_at = NOW() WHERE id = %s;"
                cur.execute(sql,(post_id,))
                conn.commit()
        except pymysql.Error as e:
            print(f'システムエラーが発生しました: {e}')
            abort(500)
        finally:
            db_pool.release(conn)

    
    @classmethod
    def find_by_id(cls, post_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                    SELECT posts.*, user_posts.user_id
                    FROM  posts
                    JOIN user_posts ON posts.id = user_posts.post_id
                    WHERE posts.id = %s AND posts.delete_flag = FALSE;
                """
                cur.execute(sql,(post_id,))
                post = cur.fetchone()
            return post
        except pymysql.Error as e:
            print(f'システムエラーが発生しました: {e}')
            abort(500)
        finally:
            db_pool.release(conn)

    
    @classmethod
    def update(cls, post_id, store_id, product_name,price_yen, calories_kcal, sugar_g, image_path, content):
        conn = db_pool.get_conn() 
        try:
            with conn.cursor() as cur:
                sql = """
                    UPDATE posts
                    SET store_id = %s, product_name = %s, price_yen = %s, calories_kcal = %s, sugar_g = %s, image_path = %s, content = %s, created_at = NOW(), updated_at = NOW()
                    WHERE id = %s;
                """
                cur.execute(sql,(store_id, product_name, price_yen, calories_kcal, sugar_g, image_path, content, post_id))
                conn.commit()
        except pymysql.Error as e:
            print(f'システムエラーが発生しました: {e}')
            abort(500)
        finally:
            db_pool.release(conn)



class Comment:
    @classmethod
    def create(cls, user_id, post_id, comment_text):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO comments (user_id, post_id, content, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW());"
                cur.execute(sql,(user_id, post_id, comment_text))
                conn.commit()
        except pymysql.Error as e:
            print(f'システムエラーが発生しました: {e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def get_by_post_id(cls, post_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                    SELECT comments.*, users.name AS user_name
                    FROM comments
                    JOIN users ON comments.user_id = users.id
                    WHERE comments.post_id = %s
                    ORDER BY comments.created_at DESC;
                """
                cur.execute(sql,(post_id,))
                Comments = cur.fetchall()
            return Comments
        except pymysql.Error as e:
            print(f'システムエラーが発生しました: {e}')
            abort(500)
        finally:
            db_pool.release(conn)
