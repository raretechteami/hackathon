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
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
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
# サインアップ処理
@app.route('/userRegist', methods=['POST'])
def signup_process():
    nickname = request.form.get('nickname', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    password_confirm = request.form.get('password_confirm', '').strip()

    # 未入力チェック
    if not nickname or not email or not password or not password_confirm:
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

    # User 作成
    user_id = User.create(nickname, email, hashed_password)

    # ログイン状態にしてリダイレクト
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
@app.route('/logout', methods=['GET','POST'])
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
# 新規投稿画面の表示
@app.route('/posts/newPost', methods=['GET'])
def new_post_view():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    
    stores = ConvenienceStore.get_all()
    return render_template('post/new_post.html', stores=stores, user_id=user_id)

@app.route('/posts', methods=['POST'])
def create_post():
    user_id = session.get('user_id')
    stores = ConvenienceStore.get_all()
    
    if user_id is None:
        return redirect(url_for('login_view'))
    product_name = request.form.get('product_name', '').strip()
    store_id = request.form.get('store_id', '').strip()
    calories_kcal = request.form.get('calories_kcal', '').strip()
    sugar_g= request.form.get('sugar_g', '').strip()
    price_yen = request.form.get('price_yen', '').strip()
    content = request.form.get('content', '').strip()

    form_data={
        'product_name': product_name,
        'store_id':store_id,
        'calories_kcal': calories_kcal,
        'sugar_g': sugar_g,
        'price_yen': price_yen,
        'content': content
    }

    if product_name == '':
        flash('商品名が空です', 'error')
        return render_template('post/new_post.html', stores=stores, user_id=user_id, form_data=form_data)
    if store_id == '':
        flash('店舗名が空です', 'error')
        return render_template('post/new_post.html', stores=stores, user_id=user_id, form_data=form_data)
    if calories_kcal == '':
        flash('カロリーが空です', 'error')
        return render_template('post/new_post.html', stores=stores, user_id=user_id, form_data=form_data)
    if sugar_g == '':
        flash('糖質が空です', 'error')
        return render_template('post/new_post.html', stores=stores, user_id=user_id, form_data=form_data)
    if price_yen == '':
        flash('価格が空です', 'error')
        return render_template('post/new_post.html', stores=stores, user_id=user_id, form_data=form_data)
    
    file = request.files.get('file')
    if not file or file.filename == '':
        flash('画像ファイルがありません', 'error')
        return render_template('post/new_post.html', stores=stores, user_id=user_id, form_data=form_data)

    
    if content == '':
        flash('投稿内容が空です', 'error')
        return render_template('post/new_post.html', stores=stores, user_id=user_id, form_data=form_data)

    if allowed_file(file.filename):
            unique_id = uuid.uuid4().hex[:6]
            image_name =  unique_id + str(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER,image_name))
            image_path = 'uploads/' + image_name
    else:
        flash('画像ファイルを選んでください','error')
        return redirect(url_for('new_post_view'))
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

    post['user_name'] = User.get_name_by_id(post['user_id'])
    post['created_at'] = post['created_at'].strftime('%Y-%m-%d %H:%M')
    
    stores = ConvenienceStore.get_all()
    store_dict = {store['id']: store['name'] for store in stores}
    post['store_name'] = store_dict.get(post['store_id'], '')

    comments = Comment.get_by_post_id(post_id)
    for c in comments:
        if c.get('created_at'):
            c['created_at'] = c['created_at'].strftime('%Y-%m-%d %H:%M')


    if int(post['user_id']) == int(user_id):
        return render_template(
            'post/post_detail.html',
            post=post,
            stores=stores,
            comments=comments,
            user_id=user_id
        )

    return render_template(
        'post/follow_post_detail.html',
        post=post,
        stores=stores,
        comments=comments,
        user_id=user_id
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
    
    stores = ConvenienceStore.get_all()
    comments = Comment.get_by_post_id(post_id)
    for c in comments:
        if c.get('created_at'):
            c['created_at'] = c['created_at'].strftime('%Y-%m-%d %H:%M')

    product_name = request.form.get('product_name', '').strip()
    store_id = request.form.get('store_id', '').strip()
    calories_kcal = request.form.get('calories_kcal', '').strip()
    sugar_g = request.form.get('sugar_g', '').strip()
    price_yen = request.form.get('price_yen', '').strip()
    content = request.form.get('content', '').strip()

    form_data = {
        'product_name': product_name,
        'store_id': store_id,
        'calories_kcal': calories_kcal,
        'sugar_g': sugar_g,
        'price_yen': price_yen,
        'content': content
    }

    # 各フィールドの未入力バリデーション
    if product_name == '':
        flash('商品名が空です', 'error')
        return render_template('post/post_detail.html', post=post, stores=stores, comments=comments, user_id=user_id, form_data=form_data)
    if store_id == '':
        flash('店舗名が空です', 'error')
        return render_template('post/post_detail.html', post=post, stores=stores, comments=comments, user_id=user_id, form_data=form_data)
    if calories_kcal == '':
        flash('カロリーが空です', 'error')
        return render_template('post/post_detail.html', post=post, stores=stores, comments=comments, user_id=user_id, form_data=form_data)
    if sugar_g == '':
        flash('糖質が空です', 'error')
        return render_template('post/post_detail.html', post=post, stores=stores, comments=comments, user_id=user_id, form_data=form_data)
    if price_yen == '':
        flash('価格が空です', 'error')
        return render_template('post/post_detail.html', post=post, stores=stores, comments=comments, user_id=user_id, form_data=form_data)
    if content == '':
        flash('投稿内容が空です', 'error')
        return render_template('post/post_detail.html', post=post, stores=stores, comments=comments, user_id=user_id, form_data=form_data)

    image_file = request.files.get('image')
    image_path = post['image_path']
    if image_file and image_file.filename != '':
        if allowed_file(image_file.filename):
            unique_id = uuid.uuid4().hex[:6]
            image_name = unique_id + str(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_name))
            image_path = 'uploads/' + image_name
        else:
            flash('画像ファイルを選んでください', 'error')
            return render_template('post/post_detail.html', post=post, stores=stores, comments=comments, user_id=user_id, form_data=form_data)
    
    Post.update(
        post_id=post_id,
        store_id=int(store_id),
        product_name=product_name,
        price_yen=int(price_yen),
        calories_kcal=float(calories_kcal),
        sugar_g=float(sugar_g),
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