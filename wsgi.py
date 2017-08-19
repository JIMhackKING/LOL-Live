from bottle import route, run, default_app

@route("/")
def main():
	return "hello,world!"

application = default_app()