from flask import Flask, request, redirect, render_template, session, flash, abort, url_for
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
import hashlib
import os
import re
import uuid



from models import User, Post, Comment, ConvenienceStore




# 定数定義
EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
SESSION_DAYS = 30

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', uuid.uuid4().hex)
app.permanent_session_lifetime = timedelta(days=SESSION_DAYS)

csrf = CSRFProtect(app)

UPLOAD_FOLDER = './static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ルートページのリダイレクト処理
@app.route('/', methods=['GET'])
def index():
    user_id=session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    return redirect(url_for('posts_view'))


# サインアップページの表示
@app.route('/userRegist', methods=['GET'])
def sign_up_view():
    if session.get('user_id') is not None:
        return redirect(url_for('posts_view'))
    return render_template('auth/signup.html')






# サインアップ処理
@app.route('/userRegist', methods=['POST'])
def signup_process():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    password_confirm = request.form.get('password_confirm', '').strip()

    # 空チェック
    if not name or not email or not password or not password_confirm:
        flash("すべての項目を入力してください。", "error")
        return redirect(url_for('sign_up_view'))
    
    # パスワード一致チェック
    if password != password_confirm:
        flash("パスワードが一致しません。", "error")
        return redirect(url_for('sign_up_view'))
    
    # メール形式チェック
    if re.match(EMAIL_PATTERN, email) is None:
        flash('メールアドレスは正しい形式で入力してください。', 'error')
        return redirect(url_for('sign_up_view'))
    
    # 既存ユーザーチェック
    registered_user = User.find_by_email(email)
    if registered_user is not None:
        flash('既に登録されているメールアドレスです。', 'error')
        return redirect(url_for('sign_up_view'))
    
    # パスワードのハッシュ化
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    # Userのcreateメソッドを呼び出してユーザーを作成し、user_idを取得
    user_id = User.create(name, email, hashed_password)

    # セッションにuser_idをキー名user_idで保存
    session['user_id'] = user_id

    return redirect(url_for('posts_view'))





#  ログインページの表示
@app.route('/login', methods=['GET'])
def login_view():
    if session.get('user_id') is not None:
        return redirect(url_for('posts_view'))
    return render_template('auth/login.html')    




# ログイン処理
@app.route('/login', methods=['POST'])
def login_process():
    email = request.form.get('email','').strip()
    password = request.form.get('password', '')

    if email == '' or password == '':
        flash('メールアドレスかパスワードが入力されていません。', 'error')
    else:
        user = User.find_by_email(email)
        if user is None:
            flash('メールアドレスかパスワードが間違っています。', 'error')
        
        else:
            hashPassword = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if hashPassword != user["password"]:
                flash('メールアドレスかパスワードが間違っています。', 'error')
            else:
                session['user_id'] = user["id"]
                return redirect(url_for('posts_view'))
    return redirect(url_for('login_view'))





# ログアウト
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login_view'))



# 投稿一覧ページの表示
@app.route('/posts', methods=['GET'])
def posts_view():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    else:
        posts = Post.get_all_posts()
        for post in posts:
            post['created_at'] = post['created_at'].strftime('%Y-%m-%d %H:%M')
            post['user_name'] = User.get_name_by_id(post['user_id'])
            post['comment_count'] = Comment.get_count_by_post_id(post['id'])

        return render_template('post/posts.html',posts=posts,user_id=user_id)





# 投稿処理

@app.route('/posts', methods=['POST'])
def create_post():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    product_name = request.form.get('product_name', '').strip()
    store_id = request.form.get('store_id', '').strip()
    calories_kcal = request.form.get('calories_kcal', '').strip()
    sugar_g= request.form.get('sugar_g', '').strip()
    price_yen = request.form.get('price_yen', '').strip()
    content = request.form.get('content', '').strip()
    if product_name == '':
        flash('商品名が空です','error')
        return redirect(url_for('posts_view'))
    if store_id == '':
        flash('店舗名が空です','error')
        return redirect(url_for('posts_view'))
    if calories_kcal == '':
            flash('カロリーが空です','error')
            return redirect(url_for('posts_view'))
    if sugar_g == '':
        flash('糖質が空です','error')
        return redirect(url_for('posts_view'))
    if price_yen == '':
        flash('価格が空です','error')
        return redirect(url_for('posts_view'))
    if content == '':
        flash('投稿内容が空です','error')
        return redirect(url_for('posts_view'))
    file = request.files['file']
    if (not file):
        flash('画像ファイルがありません','error')
        return redirect(url_for('posts_view'))
    if allowed_file(file.filename):
            unique_id = uuid.uuid4().hex[:6]
            image_name =  unique_id + str(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER,image_name))
            image_path = UPLOAD_FOLDER + image_name
    else:
        flash('画像ファイルを選んでください','error')
        return redirect(url_for('posts_view'))
    Post.create(user_id,product_name,store_id,calories_kcal,sugar_g,price_yen,image_path,content)
    flash('投稿が完了しました','success')
    return redirect(url_for('posts_view'))














# 投稿詳細ページの表示
@app.route('/posts/<int:post_id>', methods=['GET'])
def post_detail_view(post_id):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    
    post = Post.find_by_id(post_id)
    if post is None:
        abort(404)

    stores = ConvenienceStore.get_all()

    comments = Comment.get_by_post_id(post_id)

    return render_template(
        'post/post_detail.html',
        post=post,
        stores=stores,
        comments=comments
    )

# 編集内容の保存処理
@app.route('/posts/<int:post_id>', methods=['POST'])
def update_post(post_id):
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for('login_view'))
    
    post = Post.find_by_id(post_id)
    if post is None or post['user_id'] != user_id:
        flash('投稿の編集権限がありません。', 'error')
        return redirect(url_for('posts_view'))
    
    product_name = request.form.get('product_name', '').strip()
    store_id = request.form.get('store_id', '').strip()
    calories_kcal = request.form.get('calories_kcal', '').strip()
    sugar_g = request.form.get('sugar_g', '').strip()
    price_yen = request.form.get('price_yen', '').strip()
    content = request.form.get('content', '').strip()

   
    product_name = product_name if product_name else post['product_name']
    store_id = int(store_id) if store_id else post['store_id']
    price_yen = int(price_yen) if price_yen else post['price_yen']
    calories_kcal = float(calories_kcal) if calories_kcal else post['calories_kcal']
    sugar_g = float(sugar_g) if sugar_g else post['sugar_g']
    content = content if content else post['content']

    image_file = request.files.get('image')
    image_path = post['image_path']
    if image_file and image_file.filename != '':
        image_path = Post.save_image(image_file)
    
    Post.update(
        post_id=post_id,
        store_id=store_id,
        product_name=product_name,
        price_yen=price_yen,
        calories_kcal=calories_kcal,
        sugar_g=sugar_g,
        image_path=image_path,
        content=content  
    )

    flash('投稿が更新されました。', 'success')
    return redirect(url_for('posts_view'))







# コメント処理
@app.route('/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    
    comment_text = request.form.get('comment_text','').strip()
    if comment_text == '':
        flash('コメントを入力してください。', 'error')
        return redirect(url_for('post_detail_view', post_id=post_id))
    
    Comment.create(
        user_id=user_id,
        post_id=post_id,
        comment_text=comment_text
    )

    return redirect(url_for('post_detail_view', post_id=post_id))

# 投稿削除処理
@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    
    post = Post.find_by_id(post_id)
    if post is None:
        abort(404)

    if post['user_id'] != user_id:
        flash('投稿の削除権限がありません。', 'error')
        return redirect(url_for('posts_view'))
    
    Post.delete(post_id)
    flash('投稿が削除されました。','success')
    return redirect(url_for('posts_view'))




# エラーハンドリング
@app.errorhandler(400)
def bad_request(error):
    return render_template('error/400.html'), 400


@app.errorhandler(403)
def admin_error(error):
    return render_template('error/403.html'), 403

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('error/500.html'), 500




if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
