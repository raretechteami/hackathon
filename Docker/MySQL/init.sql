DROP DATABASE IF EXISTS oyatsuapp;

DROP USER IF EXISTS 'testuser'@'%';


CREATE USER 'testuser'@'%' IDENTIFIED BY 'testuser';

CREATE DATABASE IF NOT EXISTS oyatsuapp
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;


GRANT ALL PRIVILEGES ON oyatsuapp.* TO 'testuser'@'%';

FLUSH PRIVILEGES;

USE oyatsuapp;

CREATE TABLE
    users (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        name VARCHAR(50) NOT NULL,
        email VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
        PRIMARY KEY (id),
        UNIQUE KEY uq_users_email (email)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    convenience_stores (
        id TINYINT UNSIGNED NOT NULL,
        name VARCHAR(80) NOT NULL,
        created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
        PRIMARY KEY (id),
        UNIQUE KEY uq_cs_name (name)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    posts (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        user_id BIGINT UNSIGNED NOT NULL,
        store_id TINYINT UNSIGNED NOT NULL,
        product_name VARCHAR(120) NOT NULL,
        price_yen INT UNSIGNED NULL,
        calories_kcal DECIMAL(5,1) UNSIGNED NOT NULL,
        sugar_g DECIMAL(5,1) UNSIGNED NOT NULL,
        image_path VARCHAR(255) NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
        delete_flag BOOLEAN  DEFAULT 0 NOT NULL,
        PRIMARY KEY (id),
        KEY idx_posts_user_id (user_id),
        KEY idx_posts_store_id (store_id),
        CONSTRAINT fk_posts_user FOREIGN KEY (user_id) REFERENCES users (id),
        CONSTRAINT fk_posts_store FOREIGN KEY (store_id) REFERENCES convenience_stores (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    comments (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        user_id BIGINT UNSIGNED NOT NULL,
        post_id BIGINT UNSIGNED NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
        PRIMARY KEY (id),
        KEY idx_comments_user_id (user_id),
        KEY idx_comments_post_id (post_id),
        CONSTRAINT fk_comments_user FOREIGN KEY (user_id) REFERENCES users (id),
        CONSTRAINT fk_comments_post FOREIGN KEY (post_id) REFERENCES posts (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;


INSERT INTO users (name, email, password)
VALUES
  ('羽花尊', 'hack@example.com', '3584b4056308d03f33938298679d1762756d1493c69efc4e73dedc517240ebf7'),
  ('餅月餡奈', 'mochi@example.com', '3584b4056308d03f33938298679d1762756d1493c69efc4e73dedc517240ebf7'),
  ('オニギリジョー', 'onigiri@example.com', '3584b4056308d03f33938298679d1762756d1493c69efc4e73dedc517240ebf7');

INSERT INTO convenience_stores (id, name)
VALUES
  (1, 'ローソン'),
  (2, 'ナチュラルローソン'),
  (3, 'ファミリーマート'),
  (4, 'セブンイレブン'),
  (5, 'ミニストップ'),
  (6, 'デイリーヤマザキ'),
  (7, 'まいばすけっと');

INSERT INTO posts (user_id, store_id, product_name, price_yen, calories_kcal, sugar_g, image_path, content, delete_flag)
VALUES
  (1, 1, 'こんにゃくチップスのりしお', 100, 58.0, 5.0, './static/uploads/sample_chips.png', 'こんにゃく素材とは思えないサクサク軽くて、のりしおの風味がしっかり効いていて大満足！！
  1袋あたりの糖質が5g、食物繊維も豊富でヘルシーで嬉しいです。', 0 ),
  (3, 3, '無限バリリ', 180, 110.0, 5.0, './static/uploads/sample_bariri.png', 'かりんとうの食感でクセになります！ついつい食べ続けてしまいます。', 0),
  (1, 4, '全粒粉食パン3枚入', 116, 168.0, 28.4, './static/uploads/sample_bread.png', 'クセがなくて食べやすい！しかも添加物が少なめで食物繊維が多め！健康志向の私にはぴったりでした。リピ確定です！', 0);

INSERT INTO comments (user_id, post_id, content)
VALUES
    (2, 1, 'こんなのあったんですねー！！これなら自分も食べられそうです♫'),
    (2, 2, 'こんなのあったんですねー！！これなら自分も食べられそうです♫教えていただきありがとうございます。'),
    (3, 3, '全粒粉のパンは身近なところで売っていないので今まで通販で買っていました。それがセブンイレブンで売っているなんてありがたい発見です。早速買いに行ってみます。');