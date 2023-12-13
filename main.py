import psycopg2
import tornado.web
import tornado.ioloop
from tornado.web import authenticated
import os

db_params = {
    'dbname': 'authentication',
    'user': 'oumy',
    'password': 'kh2001',
    'host': 'localhost',
    'port': '5432',
}


# Connection to db
def connect_db():
    return psycopg2.connect(**db_params)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")


class IndexHandler(BaseHandler):

    @authenticated
    def get(self):
        self.render("index.html")


class RegisterHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("register.html")

    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")

        with connect_db() as conn, conn.cursor() as cur:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()

        self.redirect("login")

    def create_users_table(self):
        with connect_db() as conn, conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    password VARCHAR(255) NOT NULL
                );
            """)
            conn.commit()


class LoginHandler(BaseHandler):

    def get(self):
        incorrect = self.get_secure_cookie("incorrect")
        if incorrect and int(incorrect) > 3:
            self.write('<center>blocked</center>')
            return

        self.render("login.html")

    def post(self):
        incorrect = self.get_secure_cookie("incorrect")
        if incorrect and int(incorrect) > 3:
            self.write('<center>blocked</center>')
            return

        username = self.get_argument("username")
        password = self.get_argument("password")

        with connect_db() as conn, conn.cursor() as cur:
            cur.execute("SELECT password FROM users WHERE username = %s", (username,))
            result = cur.fetchone()
            print(result)
            if result:
                stored_password = result[0]
                print("test")
                if password == stored_password:
                    print(stored_password)
                    #self.set_secure_cookie("incorrect", "0")
                    #next_url = self.get_argument("next", None)
                    #self.render("index.html")
                    #print(next_url)
                    self.redirect("/index")
                else:
                    incorrect = self.get_secure_cookie("incorrect") or 0
                    increased = str(int(incorrect) + 1)
                    self.set_secure_cookie("incorrect", increased)
                    self.write("Login Failed")
            else:
                self.write("Failed")


if __name__ == "__main__":
    settings = {
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "login_url": "/login",
        "template_path": os.path.join(os.path.dirname(__file__), "templates")
    }
    app = tornado.web.Application([
        (r"/register", RegisterHandler),
        (r"/login", LoginHandler),
        (r"/index", IndexHandler)
    ], **settings)

    app.listen(8881)
    print("I'm listening on port 8881")
    tornado.ioloop.IOLoop.current().start()
