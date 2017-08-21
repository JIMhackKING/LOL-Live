from bottle import route, static_file, default_app, error
import leancloud
import storage
from jinja2 import Environment, FileSystemLoader
from leancloud import Engine

loader = FileSystemLoader("./views")
env = Environment(loader=loader)

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
	query = storage.Query()
	template = env.get_template("home.html")

	datas = query.datas
	content = template.render(datas = datas)
	return content

application = Engine(default_app())

@application.define
def update(**kwargs):
	fetcher = storage.Fetch()
	query = storage.Query()
	query.cleanData()
	fetcher.fetch_all()
	storage.Fetch.Live.save_all(fetcher.lives)
