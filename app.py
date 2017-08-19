from bottle import route, run

@route("/")
def main():
	return "hello,world!"