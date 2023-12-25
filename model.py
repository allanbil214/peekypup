from email.mime import image
import mysql.connector

db = mysql.connector.connect (
    host = "localhost",
    user = "root",
    password = "",
    database = "picturefy" 
)

class Model():
    def __init__(self):
        pass

    #memilih splash screen text dari database
    def funnyLine():
        cur = db.cursor()
        cur.execute("""SELECT * FROM funnyline
                        ORDER BY RAND()
                        LIMIT 1;""")
        return cur.fetchone()[1]

    #mengambil data dari table image_tags 
    def get_imagetags():
        cur = db.cursor()
        cur.execute("""SELECT tags.id, image.id, tags.tag_name, image.filename, COUNT(image.id) AS image_count FROM image_tags
                        left JOIN image ON image_tags.image_id = image.id
                        left JOIN tags ON image_tags.tag_id = tags.id 
                        GROUP BY tags.id ORDER BY RAND() limit 15""")
        return cur.fetchall()

    #mengambil gambar sorting tanggal terbaru
    def get_images_newest(userId):
        cur = db.cursor()
        cur.execute("""SELECT
                            tags.id AS tag_id,
                            image.id AS image_id,
                            tags.tag_name,
                            image.filename,
                            image.title,
                            image.desc,
                            image.input_date,
                            users.username,
                            COALESCE(SUM(iv.view_count), 0) AS total_views, 
                            image.score,
                            CASE WHEN image_like.user_id IS NOT NULL THEN 1 ELSE 0 END AS liked_by_user,
                            COALESCE(COUNT(DISTINCT img_comments.cmnt_id), 0) AS total_comments
                        FROM
                            image_tags
                        LEFT JOIN
                            image ON image_tags.image_id = image.id
                        LEFT JOIN
                            users ON users.id = image.user_id
                        LEFT JOIN
                            tags ON image_tags.tag_id = tags.id
                        LEFT JOIN
                            image_views iv ON image.id = iv.image_id
                        LEFT JOIN
                            image_like ON image.id = image_like.image_id
                            AND (image_like.user_id = %s OR %s IS NULL)     
                        LEFT JOIN
                            img_comments ON image.id = img_comments.image_id                       
                        GROUP BY
                            tags.id, image.id, tags.tag_name, image.filename, image.title, image.desc, image.input_date, users.username
                        ORDER BY
                            image.input_date DESC;
                        """, (userId, userId))
        return cur.fetchall()

    #mengambil gambar sorting random
    def get_images_random(userId):
        cur = db.cursor()
        cur.execute("""SELECT
                        tags.id AS tag_id,
                        image.id AS image_id,
                        tags.tag_name,
                        image.filename,
                        image.title,
                        image.desc,
                        image.input_date,
                        users.username,
                        COALESCE(SUM(iv.view_count), 0) AS total_views, 
                        image.score,
                        CASE WHEN image_like.user_id IS NOT NULL THEN 1 ELSE 0 END AS liked_by_user,
                        COALESCE(COUNT(DISTINCT img_comments.cmnt_id), 0) AS total_comments
                    FROM
                        image_tags
                    LEFT JOIN
                        image ON image_tags.image_id = image.id
                    LEFT JOIN
                        users ON users.id = image.user_id
                    LEFT JOIN
                        tags ON image_tags.tag_id = tags.id
                    LEFT JOIN
                        image_views iv ON image.id = iv.image_id
                    LEFT JOIN
                        image_like ON image.id = image_like.image_id
                        AND (image_like.user_id = %s OR %s IS NULL) 
                    LEFT JOIN
                        img_comments ON image.id = img_comments.image_id                                                    
                    GROUP BY
                        tags.id, image.id, tags.tag_name, image.filename, image.title, image.desc, image.input_date, users.username
                    ORDER BY
                        rand();
                    """, (userId, userId))
        return cur.fetchall()

    #mengambil gambar sorting tanggal terlama
    def get_images_oldest(userId):
        cur = db.cursor()
        cur.execute("""SELECT
                        tags.id AS tag_id,
                        image.id AS image_id,
                        tags.tag_name,
                        image.filename,
                        image.title,
                        image.desc,
                        image.input_date,
                        users.username,
                        COALESCE(SUM(iv.view_count), 0) AS total_views, 
                        image.score,
                        CASE WHEN image_like.user_id IS NOT NULL THEN 1 ELSE 0 END AS liked_by_user,
                        COALESCE(COUNT(DISTINCT img_comments.cmnt_id), 0) AS total_comments
                    FROM
                        image_tags
                    LEFT JOIN
                        image ON image_tags.image_id = image.id
                    LEFT JOIN
                        users ON users.id = image.user_id
                    LEFT JOIN
                        tags ON image_tags.tag_id = tags.id
                    LEFT JOIN
                        image_views iv ON image.id = iv.image_id
                    LEFT JOIN
                        image_like ON image.id = image_like.image_id
                        AND (image_like.user_id = %s OR %s IS NULL)    
                    LEFT JOIN
                        img_comments ON image.id = img_comments.image_id                                            
                    GROUP BY
                        tags.id, image.id, tags.tag_name, image.filename, image.title, image.desc, image.input_date, users.username
                    ORDER BY
                        image.input_date asc;
                    """, (userId, userId))
        return cur.fetchall()

    def get_images_trending(userId): # trending by views on 1 month interval
        cur = db.cursor() 
        cur.execute("""SELECT
                            tags.id AS tag_id,
                            image.id AS image_id,
                            tags.tag_name,
                            image.filename,
                            image.title,
                            image.desc,
                            image.input_date,
                            users.username,
                            COALESCE(SUM(iv.view_count), 0) AS total_views, 
                            image.score,
                            CASE WHEN image_like.user_id IS NOT NULL THEN 1 ELSE 0 END AS liked_by_user,
                            COALESCE(COUNT(DISTINCT img_comments.cmnt_id), 0) AS total_comments
                        FROM
                            image_tags
                        LEFT JOIN
                            image ON image_tags.image_id = image.id
                        LEFT JOIN
                            users ON users.id = image.user_id
                        LEFT JOIN
                            tags ON image_tags.tag_id = tags.id
                        LEFT JOIN
                            image_views iv ON image.id = iv.image_id
                            
                        LEFT JOIN
                            image_like ON image.id = image_like.image_id
                            AND (image_like.user_id = %s OR %s IS NULL)     
                        LEFT JOIN
                            img_comments ON image.id = img_comments.image_id                       
                        GROUP BY
                            tags.id, image.id, tags.tag_name, image.filename, image.title, image.desc, image.input_date, users.username
                        ORDER BY
                            total_views DESC;
                        """, (userId, userId)) #AND iv.view_date >= NOW() - INTERVAL 1 MONTH
        return cur.fetchall()

    # Inside your mdl module
    def get_images_hot(userId):
        cur = db.cursor()
        cur.execute("""SELECT
                        tags.id AS tag_id,
                        image.id AS image_id,
                        tags.tag_name,
                        image.filename,
                        image.title,
                        image.desc,
                        image.input_date,
                        users.username,
                        COALESCE(SUM(iv.view_count), 0) AS total_views, 
                        image.score,
                        CASE WHEN image_like.user_id IS NOT NULL THEN 1 ELSE 0 END AS liked_by_user,
                        COALESCE(COUNT(DISTINCT img_comments.cmnt_id), 0) AS total_comments
                    FROM
                        image_tags
                    LEFT JOIN
                        image ON image_tags.image_id = image.id
                    LEFT JOIN
                        users ON users.id = image.user_id
                    LEFT JOIN
                        tags ON image_tags.tag_id = tags.id
                    LEFT JOIN
                        image_views iv ON image.id = iv.image_id
                    LEFT JOIN
                        image_like ON image.id = image_like.image_id
                        AND (image_like.user_id = %s OR %s IS NULL)    
                    LEFT JOIN
                        img_comments ON image.id = img_comments.image_id                                            
                    GROUP BY
                        tags.id, image.id, tags.tag_name, image.filename, image.title, image.desc, image.input_date, users.username
                    ORDER BY
                        COUNT(image_like.image_id) DESC;
                    """, (userId, userId))
        return cur.fetchall()

    def get_images_fav(userId):
        cur = db.cursor()
        cur.execute("""SELECT
                            tags.id AS tag_id,
                            image.id AS image_id,
                            tags.tag_name,
                            image.filename,
                            image.title,
                            image.desc,
                            image.input_date,
                            users.username,
                            COALESCE(SUM(iv.view_count), 0) AS total_views, 
                            image.score,
                            CASE WHEN image_like.user_id IS NOT NULL THEN 1 ELSE 0 END AS liked_by_user,
                            COALESCE(COUNT(DISTINCT img_comments.cmnt_id), 0) AS total_comments
                        FROM
                            image_tags
                        LEFT JOIN
                            image ON image_tags.image_id = image.id
                        LEFT JOIN
                            users ON users.id = image.user_id
                        LEFT JOIN
                            tags ON image_tags.tag_id = tags.id
                        LEFT JOIN
                            image_views iv ON image.id = iv.image_id
                        LEFT JOIN
                            image_like ON image.id = image_like.image_id
                            AND (image_like.user_id = %s OR %s IS NULL)     
                        LEFT JOIN
                            img_comments ON image.id = img_comments.image_id                       
                        GROUP BY
                            tags.id, image.id, tags.tag_name, image.filename, image.title, image.desc, image.input_date, users.username
                        HAVING
                            liked_by_user = 1
                        ORDER BY
                            image.input_date DESC;
                        """, (userId, userId))
        return cur.fetchall()


    #mengambil gambar secara specific
    def get_images_specific(title, userId):
        cur = db.cursor()
        if not title.strip():  
            cur.execute("""SELECT
                                tags.id AS tag_id,
                                image.id AS image_id,
                                tags.tag_name,
                                image.filename,
                                image.title,
                                image.desc,
                                image.input_date,
                                users.username,
                                COALESCE(SUM(iv.view_count), 0) AS total_views, 
                                image.score,
                                CASE WHEN image_like.user_id IS NOT NULL THEN 1 ELSE 0 END AS liked_by_user,
                                COALESCE(COUNT(DISTINCT img_comments.cmnt_id), 0) AS total_comments
                            FROM
                                image_tags
                            LEFT JOIN
                                image ON image_tags.image_id = image.id
                            LEFT JOIN
                                users ON users.id = image.user_id
                            LEFT JOIN
                                tags ON image_tags.tag_id = tags.id
                            LEFT JOIN
                                image_views iv ON image.id = iv.image_id
                            LEFT JOIN
                                image_like ON image.id = image_like.image_id
                                    AND (image_like.user_id = %s OR %s IS NULL)  
                            LEFT JOIN
                                img_comments ON image.id = img_comments.image_id        
                            WHERE
                                COALESCE(image.user_id, 'dummy_value') = 'dummy_value'
                            GROUP BY
                                tags.id, image.id, tags.tag_name, image.filename, image.title, image.desc, image.input_date, users.username
                            ORDER BY
                                image.input_date DESC""", (userId, userId)) 
            print("SQL Query:", cur.statement)
            print("userId:", userId)
            print("title:", title)

        elif "#" in title:
            x = title.replace("#", "")
            cur.execute("""SELECT
                                tags.id AS tag_id,
                                image.id AS image_id,
                                tags.tag_name,
                                image.filename,
                                image.title,
                                image.desc,
                                image.input_date,
                                users.username,
                                COALESCE(SUM(iv.view_count), 0) AS total_views, 
                                image.score,
                                CASE WHEN image_like.user_id IS NOT NULL THEN 1 ELSE 0 END AS liked_by_user,
                                COALESCE(COUNT(DISTINCT img_comments.cmnt_id), 0) AS total_comments
                            FROM
                                image_tags
                            LEFT JOIN
                                image ON image_tags.image_id = image.id
                            LEFT JOIN
                                users ON users.id = image.user_id
                            LEFT JOIN
                                tags ON image_tags.tag_id = tags.id
                            LEFT JOIN
                                image_views iv ON image.id = iv.image_id
                            LEFT JOIN
                                image_like ON image.id = image_like.image_id
                                AND (image_like.user_id = %s OR %s IS NULL)  
                            LEFT JOIN
                                img_comments ON image.id = img_comments.image_id                                
                            WHERE
                                tags.tag_name LIKE %s
                            GROUP BY
                                tags.id, image.id, tags.tag_name, image.filename, image.title, image.desc, image.input_date, users.username
                            ORDER BY
                                image.input_date DESC""", (userId, userId, f"%{x}%"))

        elif "@" in title:
            y = title.replace("@", "")
            cur.execute("""SELECT
                                tags.id AS tag_id,
                                image.id AS image_id,
                                tags.tag_name,
                                image.filename,
                                image.title,
                                image.desc,
                                image.input_date,
                                users.username,
                                COALESCE(SUM(iv.view_count), 0) AS total_views, 
                                image.score,
                                CASE WHEN image_like.user_id IS NOT NULL THEN 1 ELSE 0 END AS liked_by_user,
                                COALESCE(COUNT(DISTINCT img_comments.cmnt_id), 0) AS total_comments
                            FROM
                                image_tags
                            LEFT JOIN
                                image ON image_tags.image_id = image.id
                            LEFT JOIN
                                users ON users.id = image.user_id
                            LEFT JOIN
                                tags ON image_tags.tag_id = tags.id
                            LEFT JOIN
                                image_views iv ON image.id = iv.image_id
                            LEFT JOIN
                                image_like ON image.id = image_like.image_id
                                AND (image_like.user_id = %s OR %s IS NULL)  
                            LEFT JOIN
                                img_comments ON image.id = img_comments.image_id                                    
                        WHERE
                            users.username LIKE %s
                        GROUP BY
                            tags.id, image.id, tags.tag_name, image.filename, image.title, image.desc, image.input_date, users.username
                        ORDER BY
                            image.input_date DESC""", (userId, userId, f"%{y}%"))

        else:
            cur.execute("""SELECT
                                tags.id AS tag_id,
                                image.id AS image_id,
                                tags.tag_name,
                                image.filename,
                                image.title,
                                image.desc,
                                image.input_date,
                                users.username,
                                COALESCE(SUM(iv.view_count), 0) AS total_views, 
                                image.score,
                                CASE WHEN image_like.user_id IS NOT NULL THEN 1 ELSE 0 END AS liked_by_user,
                                COALESCE(COUNT(DISTINCT img_comments.cmnt_id), 0) AS total_comments
                            FROM
                                image_tags
                            LEFT JOIN
                                image ON image_tags.image_id = image.id
                            LEFT JOIN
                                users ON users.id = image.user_id
                            LEFT JOIN
                                tags ON image_tags.tag_id = tags.id
                            LEFT JOIN
                                image_views iv ON image.id = iv.image_id
                            LEFT JOIN
                                image_like ON image.id = image_like.image_id
                                AND (image_like.user_id = %s OR %s IS NULL)  
                            LEFT JOIN
                                img_comments ON image.id = img_comments.image_id                                    
                            WHERE
                                image.title LIKE %s
                            GROUP BY
                                tags.id, image.id, tags.tag_name, image.filename, image.title, image.desc, image.input_date, users.username
                            ORDER BY
                                image.input_date DESC""", (userId, userId, f"%{title}%"))
        
        return cur.fetchall()


    def get_user_based_image(uname, userId):
        cur = db.cursor()
        y = uname.replace("@", "")
        query = """SELECT
                    tags.id AS tag_id,
                    image.id AS image_id,
                    tags.tag_name,
                    image.filename,
                    image.title,
                    image.desc,
                    image.input_date,
                    users.username,
                    COALESCE(SUM(iv.view_count), 0) AS total_views, 
                    image.score,
                    CASE WHEN image_like.user_id IS NOT NULL THEN 1 ELSE 0 END AS liked_by_user,
                    COALESCE(COUNT(DISTINCT img_comments.cmnt_id), 0) AS total_comments
                FROM
                    image_tags
                LEFT JOIN
                    image ON image_tags.image_id = image.id
                LEFT JOIN
                    users ON users.id = image.user_id
                LEFT JOIN
                    tags ON image_tags.tag_id = tags.id
                LEFT JOIN
                    image_views iv ON image.id = iv.image_id
                LEFT JOIN
                    image_like ON image.id = image_like.image_id
                        AND (image_like.user_id = %s OR %s IS NULL)  
                LEFT JOIN
                    img_comments ON image.id = img_comments.image_id                                    
                WHERE
                    users.username LIKE %s
                GROUP BY
                    tags.id, image.id, tags.tag_name, image.filename, image.title, image.desc, image.input_date, users.username
                ORDER BY
                    image.input_date DESC"""

        params = (userId, userId, f'%{y}%')
        print("Executing query:", query % params)
        cur.execute(query, params)
        result = cur.fetchall()
        print("Query result:", result)
        return result

    def get_tags_based_image(title, userId):
        cur = db.cursor()           
        cur.execute("""SELECT 
                                tags.id AS tag_id,
                                image.id AS image_id,
                                tags.tag_name,
                                image.filename,
                                image.title,
                                image.desc,
                                image.input_date,
                                users.username,
                                COALESCE(SUM(iv.view_count), 0) AS total_views, 
                                image.score,
                                CASE WHEN image_like.user_id IS NOT NULL THEN 1 ELSE 0 END AS liked_by_user,
                            COALESCE(COUNT(DISTINCT img_comments.cmnt_id), 0) AS total_comments
                            FROM
                                image_tags
                            LEFT JOIN
                                image ON image_tags.image_id = image.id
                            LEFT JOIN
                                users ON users.id = image.user_id
                            LEFT JOIN
                                tags ON image_tags.tag_id = tags.id
                            LEFT JOIN
                                image_views iv ON image.id = iv.image_id
                            LEFT JOIN
                                image_like ON image.id = image_like.image_id
                                AND (image_like.user_id = %s OR %s IS NULL)  
                            LEFT JOIN
                                img_comments ON image.id = img_comments.image_id                                    
                            WHERE tags.id = "%s"
                            GROUP BY
                                tags.id, image.id, tags.tag_name, image.filename, image.title, image.desc, image.input_date, users.username
                            order by image.input_date desc""", (userId, userId, title))

        return cur.fetchall()

    def get_id_based_image(image_id):
        cur = db.cursor()           
        cur.execute(f"""SELECT
                            tags.id AS tag_id,
                            image.id AS image_id,
                            tags.tag_name,
                            image.filename,
                            image.title,
                            image.desc,
                            image.input_date,
                            users.username,
                            COALESCE(SUM(iv.view_count), 0) AS total_views, 
                            image.score,
                            CASE WHEN image_like.user_id IS NOT NULL THEN 1 ELSE 0 END AS liked_by_user,
                            COALESCE(COUNT(DISTINCT img_comments.cmnt_id), 0) AS total_comments
                        FROM
                            image_tags
                        LEFT JOIN
                            image ON image_tags.image_id = image.id
                        LEFT JOIN
                            users ON users.id = image.user_id
                        LEFT JOIN
                            tags ON image_tags.tag_id = tags.id
                        LEFT JOIN
                            image_views iv ON image.id = iv.image_id
                        LEFT JOIN
                            image_like ON image.id = image_like.image_id
                        LEFT JOIN
                            img_comments ON image.id = img_comments.image_id                                
                        WHERE
                            image.id = {image_id}
                        GROUP BY
                            tags.id, image.id, tags.tag_name, image.filename, image.title, image.desc, image.input_date, users.username
                        ORDER BY
                            image.input_date DESC""") 

        return cur.fetchall()


    def insert_recent_opened_image(userId, imageId, recent):
        cur = db.cursor()

        # Insert new activity, ignoring if there's a duplicate key
        insert_query = """
            INSERT IGNORE INTO activity (user_id, image_id, activity_date)
            VALUES (%s, %s, %s)
        """

        # If there's a duplicate key, update the timestamp
        update_query = """
            UPDATE activity
            SET activity_date = %s
            WHERE user_id = %s AND image_id = %s
        """

        # Execute the INSERT query
        cur.execute(insert_query, (userId, imageId, recent))

        # Execute the UPDATE query
        cur.execute(update_query, (recent, userId, imageId))

        db.commit()

    def get_recent_opened_image(userId, limit=10):
        print(userId)
        cur = db.cursor()
        cur.execute("""SELECT
                            tags.id AS tag_id,
                            image.id AS image_id,
                            tags.tag_name,
                            image.filename,
                            image.title,
                            image.desc,
                            image.input_date,
                            users.username,
                            COALESCE(SUM(iv.view_count), 0) AS total_views, 
                            image.score,
                            CASE WHEN image_like.user_id IS NOT NULL THEN 1 ELSE 0 END AS liked_by_user,
                            COALESCE(COUNT(DISTINCT img_comments.cmnt_id), 0) AS total_comments
                        FROM
                            image_tags
                        LEFT JOIN
                            image ON image_tags.image_id = image.id
                        LEFT JOIN
                            users ON users.id = image.user_id
                        LEFT JOIN
                            tags ON image_tags.tag_id = tags.id
                        LEFT JOIN
                            image_views iv ON image.id = iv.image_id
                        LEFT JOIN
                            image_like ON image.id = image_like.image_id
                            AND (image_like.user_id = %s OR %s IS NULL)
                        LEFT JOIN
                            img_comments ON image.id = img_comments.image_id
                        LEFT JOIN
                            activity ON image.id = activity.image_id  -- Assuming user_activity has content_id column
                        WHERE
                            activity.user_id = %s  -- Filter by the specific user's activity
                        GROUP BY
                            tags.id, image.id, tags.tag_name, image.filename, image.title, image.desc, image.input_date, users.username
                        ORDER BY
                            activity.activity_date DESC    -- Order by the timestamp of the user activity
                        LIMIT %s;
                        """, (userId, userId, userId, limit))
        return cur.fetchall()


    #mengambil data dari table tags
    def get_tags():
        cur = db.cursor()
        cur.execute("select * from tags")
        return cur.fetchall()
    
    #melakukan register
    def check_username(username):
        cur = db.cursor()
        cur.execute(f"select count(*) from users where username like '%{username}'")
        return cur.fetchall()

    def check_email(email):
        cur = db.cursor()
        cur.execute(f"select count(*) from users where username like '%{email}'")
        return cur.fetchall()

    def registering(username, password, reg_time, isadmin, email):
        cur = db.cursor()
        cur.execute("""INSERT INTO users (`username`, `password`, `reg_time`, `isadmin`, `email`) 
                    VALUES (%s, %s, %s, %s, %s);""",(username, password, reg_time, isadmin, email,))
        db.commit()
        return True

    def update_user_profile(user_id, new_username, new_password):
        cur = db.cursor()
        cur.execute("""
            UPDATE users
            SET `username` = %s, `password` = %s
            WHERE `id` = %s;
        """, (new_username, new_password, user_id))
        db.commit()
        return True

    #mengambil 1 data dari table users
    def loggin_in(self, uname):
        cur = db.cursor()
        cur.execute(f"SELECT * FROM users WHERE username='{uname}'")
        return cur.fetchone()

    ## < aio image process
    def check_tags(tag_name):
        cur = db.cursor()
        cur.execute(f"select COUNT(*) from tags where tag_name LIKE '%{tag_name}%'")
        return cur.fetchone()

    def get_tags_specific(tag_name):
        cur = db.cursor()
        cur.execute(f"select * from tags where tag_name LIKE '%{tag_name}%'")
        return cur.fetchone()

    def get_tags_latest_id():
        cur = db.cursor()
        cur.execute(f"SELECT * FROM tags ORDER BY id desc LIMIT 0, 1")
        return cur.fetchone()

    def get_images_latest_id():
        cur = db.cursor()
        cur.execute(f"SELECT * FROM image ORDER BY id desc LIMIT 0, 1")
        return cur.fetchone()
    ## end aio>
    

    ## adding new image comments
    def add_comment(image_id, user_id, comment_text, comment_date):
        cur = db.cursor()
        cur.execute("INSERT INTO `img_comments` (`image_id`, `user_id`, `comment_text`, `comment_date`) VALUES (%s, %s, %s, %s)", 
                    (image_id, user_id, comment_text, comment_date))
        db.commit()

    def get_comments(image_id):
        cur = db.cursor()
        #cur.execute(f"""SELECT * FROM img_comments WHERE image_id={image_id} AND user_id={user_id}""")
        cur.execute(f"""SELECT img_comments.*, users.username
                    FROM img_comments
                    JOIN users ON img_comments.user_id = users.id
                    WHERE img_comments.image_id = {image_id};
                    """)
        return cur.fetchall()

    def sum_comments(image_id):
        cur = db.cursor()
        cur.execute(f""" SELECT COUNT(*) as comment_count
                        FROM img_comments
                        WHERE image_id={image_id}""")
        return cur.fetchall()


    def get_comments_user(uid):
        cur = db.cursor()
        #cur.execute(f"""SELECT * FROM img_comments WHERE image_id={image_id} AND user_id={user_id}""")
        cur.execute(f"""SELECT img_comments.*, users.username, image.title
                    FROM img_comments
                    JOIN users ON img_comments.user_id = users.id
                    JOIN image ON img_comments.image_id = image.id
                    WHERE img_comments.user_id = {uid};
                    """)
        return cur.fetchall()

    def sum_comments_user(uid):
        cur = db.cursor()
        cur.execute(f""" SELECT COUNT(*) as comment_count
                        FROM img_comments
                        WHERE img_comments.user_id = {uid}""")
        return cur.fetchall()

    ## adding new image view counts
    def add_viewcounts(image_ids, view_date):
        cur = db.cursor()
        view_counts = [(image_id, 1, view_date) for image_id in image_ids]
        cur.executemany("INSERT INTO `image_views` (`image_id`, `view_count`, `view_date`) VALUES (%s, %s, %s)", view_counts)
        db.commit()

    # def get_liked(image_ids, user_id):
    #     cur = db.cursor()
    #     cur.execute(f"SELECT COUNT(*) AS liked FROM image_like WHERE user_id={user_id} AND image_id={image_ids};")

    def insert_liked(image_ids, user_id, datetime):
        cur = db.cursor()
        cur.execute("INSERT INTO image_like(image_id, user_id, when_liked) VALUES(%s, %s, %s);", (image_ids, user_id, datetime))
        db.commit()

    def update_score_plus(image_ids):
        cur = db.cursor()
        cur.execute(f"UPDATE image SET score = score + 1 WHERE id = {image_ids};")
        db.commit()

    def remove_liked(image_id, user_id):
        cur = db.cursor()
        cur.execute("DELETE FROM image_like WHERE image_id = %s AND user_id = %s;", (image_id, user_id))
        db.commit()

    def update_score_minus(image_ids):
        cur = db.cursor()
        cur.execute(f"UPDATE image SET score = score - 1 WHERE id = {image_ids};")
        db.commit()

    def get_like_count(image_id):
        cur = db.cursor()
        cur.execute("""
            SELECT COUNT(*) AS like_count
            FROM image_like
            WHERE image_id = %s """, (image_id,))
        result = cur.fetchone()
        print(f"image id: {image_id}")
        print(result[0])

        return result[0]


    ## < adding an image process
    def add_newTags(id, value):
        cur = db.cursor()
        cur.execute(f"INSERT INTO tags(id, tag_name) VALUES({id}, '{value}')")
        db.commit()

    def add_newImages(id, title, desc, user_id, filename, input_date):
        cur = db.cursor()
        cur.execute("""INSERT INTO `image` (`id`, `title`, `desc`, `user_id`, `filename`, `input_date`) 
                        VALUES (%s,%s,%s,%s,%s,%s)""", (id, title, desc, user_id, filename, input_date,))
        db.commit()

    def add_newImgTgs(image_id, tag_id):
        cur = db.cursor()
        cur.execute("INSERT INTO image_tags (image_id, tag_id) VALUES (%s, %s);", (image_id, tag_id,))
        db.commit()
        return True
    ## end adding an image process >

    ## < delete an image process
    def delete_imageTag(id):
        cur = db.cursor()
        cur.execute(f"DELETE FROM image_tags WHERE image_id={id}")
        db.commit()

    def delete_image(id):
        cur = db.cursor()
        cur.execute(f"DELETE FROM image WHERE id={id}")
        db.commit()
    ## end delete>

    ## < edit an image process
    def edit_newImages(id, title, desc):
        cur = db.cursor()
        cur.execute("UPDATE image SET title=%s, `desc`=%s WHERE id = %s;", (title, desc, id,))
        db.commit()
        return True

    def edit_newImgTgs(image_id, tag_id):
        cur = db.cursor()
        cur.execute("UPDATE image_tags SET tag_id=%s WHERE image_id = %s;", (tag_id, image_id,))
        db.commit()
        return True
    ## end edit>

    ## < get total post
    def count_images():
        cur = db.cursor()
        cur.execute("SELECT COUNT(*) FROM image")
        return cur.fetchone()

    def count_tags():
        cur = db.cursor()
        cur.execute("SELECT COUNT(*) FROM tags")
        return cur.fetchone()

    def count_tags_based_images(title):
        cur = db.cursor()
        cur.execute(f"SELECT COUNT(*) FROM image_tags WHERE tag_id='{title}'")
        return cur.fetchone()     

    def count_user_based_images(title):
        cur = db.cursor()
        cur.execute(f"SELECT COUNT(*) FROM image WHERE user_id='1'='{title}'")
        return cur.fetchone()     

    def count_search_based_images(title):
        cur = db.cursor()

        if("#" in title):
            x = title.replace("#","")            
            cur.execute(f"""SELECT COUNT(tags.id) FROM image_tags
                            left JOIN image ON image_tags.image_id = image.id
                            left JOIN tags ON image_tags.tag_id = tags.id 
                            LEFT JOIN users ON users.id = image.user_id
                                    WHERE tags.tag_name LIKE "%{x}%"
                                    order by image.input_date desc""")
        elif("@" in title):
            y = title.replace("@","")            
            cur.execute(f"""SELECT COUNT(tags.id) FROM image_tags
                            left JOIN image ON image_tags.image_id = image.id
                            left JOIN tags ON image_tags.tag_id = tags.id
                            LEFT JOIN users ON users.id = image.user_id 
                                    WHERE users.username LIKE "%{y}%"
                                    order by image.input_date desc""")
        else:
            cur.execute(f"""SELECT COUNT(tags.id) FROM image_tags
                            left JOIN image ON image_tags.image_id = image.id
                            left JOIN tags ON image_tags.tag_id = tags.id
                            LEFT JOIN users ON users.id = image.user_id 
                                    WHERE image.title LIKE "%{title}%"
                                    order by image.input_date desc""")

        return cur.fetchone()   
    ## end get total post >


#############################################################################################################
#DASHBOARD
#############################################################################################################
    
    def get_user_data():
        cur = db.cursor()
        cur.execute("select * from users")
        return cur.fetchall()

    def sayonara_user(id):
        cur = db.cursor()
        cur.execute(f"DELETE FROM users WHERE id={id}")
        db.commit()

    #mengambil gambar sorting tanggal terbaru
    def get_images_id_order():
        cur = db.cursor()
        cur.execute("""SELECT tags.id, image.id, tags.tag_name, image.filename, 
                        image.title, image.desc, image.input_date, users.username FROM image_tags
                        left JOIN image ON image_tags.image_id = image.id
                        LEFT JOIN users ON users.id = image.user_id
                        left JOIN tags ON image_tags.tag_id = tags.id ORDER BY image.id asc""")
        return cur.fetchall()