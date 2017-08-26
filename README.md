> 嗨，我是LOL-Live，被创造于 2017-8-21，在 2017-8-25 停工，经历了两个版本的迭代，创作者是 JIMhackKING(DHC_King) 。这篇文档，在介绍我的同时，还将向大家展示创造我的过程。

![](http://dhc.pythonanywhere.com/images/leo_cat-48.png)

# LOL-Live #

## 目录 ##

- [简介](#简介)
- [项目初始化](#项目初始化)
- [开始创作](#开始创作)
- [测试](#测试)
- [部署](#部署)
- [许可](#许可)
- [邀请函](#邀请函)

## 简介 ##

LOL-Live是一个集国内绝大多数直播平台的直播视频聚合平台。当初创建这个项目的目的是为了看游戏直播能够方便一点，国内知名的LOL游戏主播大多数都不在同一个直播平台，有时候想看不同主播的时候要不断切换网址，切换直播平台，这种操作是在是太麻烦，于是就想着做个直播视频聚合网，方便观看直播。项目开发中历经两个版本的迭代，并且在开发 V2.1 版本时保留了 V1.1 版本的使用。

大家可以浏览我的网址：[http://lol-live.leanapp.cn/](http://lol-live.leanapp.cn/)，项目部署在了leancloud上，有一定的免费额度（如果显示超出限制，需要晚一些来访问，免费的开发版每天有6个小时的限制）

----------

### requirements.txt ###

文件里列出了项目所需要的库和环境

- python2.7
- bottle
- bs4
- lxml
- jinja2
- leancloud

用 python2.7 是因为我习惯于使用 python2.7 版本，建议使用 python3.x 版本，以上列出的所有库都已适用于 python3。运行环境建议使用虚拟的 python 环境，项目需要借助 leancloud 平台的云引擎挂载该 webapp 以及存储项目的数据。

我会在下面的内容中说明项目代码的作用以及简单介绍 leancloud 中 python api 的使用方法及作用。

## 项目初始化 ##

步骤：

1. 通过 `$ git clone git@github.com:JIMhackKING/LOL-Live.git` 将项目源代码克隆到本地
2. 新建虚拟环境
3. 安装依赖库： `$ pip install -r requirements.txt`

## 开始创作 ##

*这一部分是项目制作过程详解，供学习用，可以略过*

项目中使用 leancloud 数据库作为数据存储工具，有两个原因，一是因为该 webapp 挂载在 leancloud 上，二是他的数据操作命令相对于大多数关系型数据库的 SQL 命令简单一些，下面举个例子来创建一个表和插入数据：

	import leancloud

	# 可以用继承的方式定义 leancloud.Object 的子类
	class Todo(leancloud.Object):
	    pass
	# 或者用以下的方式定义子类
	# Todo = leancloud.Object.extend('Todo')
	todo = Todo()
	todo.set('title', '工程师周会')
	todo.set('content', '每周工程师会议，周一下午2点')
	todo.save()

用上面的代码就可以实现表的创建和数据的插入，只需要定义一个子类，参数是你要创建的表的名称，然后定义一个实例（todo），用 set 方法就可以插入一条数据，不需要先创建一个表结构，他会自己创建一个字段并插入数据。详细教程可以查阅官网资料 [数据存储开发指南·Python](https://leancloud.cn/docs/leanstorage_guide-python.html)。

我们先把网站后端实现了，看代码一点点分析。

### wsgi.py ###

leancloud 规定在项目根目录下必须有 `wsgi.py` 与 `requirements.txt` 文件，云引擎运行时会首先加载 `wsgi.py` 这个模块，并将此模块的全局变量 `application` 做为 WSGI 函数进行调用,所以 `wsgi.py` 文件里必须包含一个 `application` 的全局变量／函数／类，并且符合 WSGI 规范。

首先导入要用到的模块

	from bottle import (route, static_file, default_app, error, request,
				redirect)
	import leancloud
	import storage
	from jinja2 import Environment, FileSystemLoader
	from leancloud import Engine

然后定义一个 `jinja2` 的 `Environment` （项目使用 jinja2 模板引擎渲染 html）。

	loader = FileSystemLoader("./views")  # 文件系统的 loader
	env = Environment(loader=loader)  # jinja2 的环境
	VERSION = 'v2.1'  # 网站的版本，用于后面网站版本的切换

环境会把编译的模块像 Python 的 `sys.modules` 一样保持在内存中。与 `sys.models` 不同，无论如何这个 缓存默认有大小限制，且模板会自动重新加载。 所有的加载器都是 `jinja2.BaseLoader` 的子类。如果你想要创建自己的加载器，继 承 BaseLoader 并重载 `get_source`。 

代码中间部分所有用 `route` 装饰器装饰的函数都是 `bottle` 绑定路由的函数，`route` 的参数是要绑定的 url，return 返回的内容是显示在网页上的内容（HTML），不需要带头信息。

使用 `get_template` 方法获取上面定义的 jinja2 环境 `env` 加载的文件系统目录下的指定模板

	template = env.get_template("404.html")

如果不想用 `env` 的方法，可以使用 `loader.load(env, "404.html")` 加载模板，极力不推荐此方法。

之后调用 `template` 的 `render` 方法渲染模板：

	content = template.render()

`render` 方法传入的参数是模板里面定义的变量。关于 jinja2 模板的使用方法本篇不再讲述，可以参阅官方文档：[jinja2官方文档](http://jinja.pocoo.org/) 或 [jinja2中文文档](http://docs.jinkan.org/docs/jinja2/index.html)

文件中第24行

	page = request.query.page or "1"

我在网页中添加了分页功能，以URL参数 page 作为页码，`request.query` 是 url 参数的存储对象，通过属性名称获取对应的值。

	query = storage.Query()

这一行是查询数据库的代码，是 `storage.py` 文件中的一个类，我将在讲解下一个文件的时候介绍。

    application = Engine(default_app())

上面这一个变量是 wsgi 规范的 app 实例对象。

最后有两个函数被 application.define 装饰器装饰，这两个函数是定义的云函数，也就是 leancloud 云引擎上的云函数，该函数可以实现一些诸如更新数据库，操作 webapp 后端的功能，两个函数的操作对象是远端的服务器。

### storage.py ###

首先导入模块

	import leancloud
	import os
	from bs4 import BeautifulSoup
	import requests

	ID = os.environ["LEANCLOUD_ID"]
	KEY = os.environ["LEANCLOUD_KEY"]

	leancloud.init(ID, KEY)

调用 leancloud 的存储接口必须要初始化 leancloud，参数是你在 leancloud 创建的应用的应用 Key。

`Fetch` 类有许多的方法，每个方法都是用来获取不同直播平台的直播间信息的，除了最后一个方法 `fetch_all`，`fetch_all` 方法用来调用类中所有的 api ，类变量 `Live` 是云存储里创建 Class 的对象（leancloud 里的 Class 相当于一个数据表），之后我们获取到数据后用上面说到的方法插入直播间数据到数据库中

文件里定义的另一个类 `Query` 与 `Fetch` 类的作用相反，`Query` 类的作用是从数据库中获取数据，datas 属性是类的一个属性，是云存储中一个 Class 的所有数据，cleanData 方法是删除 Class 中的所有数据。

### ./views ###

该目录里面保存的是所有需要用到的模板，网页前端和后端在整个项目里面各占一半，编写代码所用的时间也最多（因为我对前端不熟悉）

### ./static ###

该目录保存 html 所需要用到的静态文件

## 测试 ##

在项目发布之前，需要不断的进行测试，测试方法如下：

在 `wsgi.py` 文件的最后添加代码：

    from bottle import run
	run()

之后在命令行运行 `$ python wsgi.py`，然后打开浏览器，输入 http://localhost:8080 就可以看到运行结果

## 部署 ##

将项目部署在 leancloud 的云引擎上也比较简单，当然也可以部署在其他的服务器，我就只介绍如何部署在 leancloud。

首先将你的项目代码发布到一个开源代码平台上，然后在控制台进入你创建的应用，点击左边菜单的云引擎，之后再点击设置，在代码库里面填写你发布的代码库网址，点击保存之后再到最下面填写 web 主机域名，点击保存，一切完成之后点击侧边栏的部署，选择部署目标以及填写分支或版本号之后点击部署既可完成整个项目的发布和部署，最后访问你在设置里面填写的 web 主机域名就可以访问你的网站。完整的网站托管开发指南可查阅官方文档，文档很详细地引导大家一步步创建自己的网站，。文档地址：[网站托管开发指南·Python](https://leancloud.cn/docs/leanengine_webhosting_guide-python.html)

![侧边栏](http://dhc.pythonanywhere.com/images/snipaste20170826_161147.png)

## 许可 ##

这个项目使用的是 [GNU通用公共许可证](https://github.com/JIMhackKING/LOL-Live/blob/master/LICENSE) 

## 邀请函 ##

当前项目的最大缺陷是网页前端的展现做的不尽人意，其中还有一个适应手机端的网页，因做的太难看最终放弃了，代码仍在项目中，我本人诚恳地邀请各位开发者能够对项目优化做出贡献，提出问题或者改进的方案和方法。

如果大家发现项目有 BUG ，欢迎提交 issues 到 [https://github.com/JIMhackKING/LOL-Live/issues](https://github.com/JIMhackKING/LOL-Live/issues)，如果你能提出改进的方案或者对项目进行了优化，我将不胜感激，如果你有新的想法并对代码进行了改进，欢迎 Pull request。