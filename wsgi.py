from bottle import (route, static_file, default_app, error, request,
				redirect)
import leancloud
import storage
from jinja2 import Environment, FileSystemLoader
from leancloud import Engine

loader = FileSystemLoader("./views")
env = Environment(loader=loader)
VERSION = 'v2.1'

@route("/<filepath:path>")
def assets(filepath):
	return static_file(filepath, root="./static")

@error(404)
def page404(error):
	template = env.get_template("404.html")
	content = template.render()
	return content

@route("/")
def main():
	page = request.query.page or "1"
	page = int(page)
	skip = (page - 1) * 60
	limit = page * 60
	query = storage.Query()
	template = env.get_template("home.html")

	try:
		datas = query.datas[skip:limit]
	except IndexError:
		return redirect("/")

	content = template.render(datas=datas, version=VERSION)
	return content

@route('/mobile')
def mobile():
	page = request.query.page or "1"
	page = int(page)
	skip = (page - 1) * 60
	limit = page * 60
	query = storage.Query()
	template = env.get_template("mobile.html")

	try:
		datas = query.datas[skip:limit]
	except IndexError:
		return redirect("/mobile")

	content = template.render(datas=datas)
	return content

application = Engine(default_app())

@application.define
def update(**kwargs):
	fetcher = storage.Fetch()
	query = storage.Query()
	query.cleanData()
	fetcher.fetch_all()
	storage.Fetch.Live.save_all(fetcher.lives)

@application.define
def change_version(version, **kwargs):
	global VERSION
	VERSION = version

if __name__ == '__main__':
	from leancloud import cloudfunc
	cloudfunc.run("change_version", version='v1.1')
