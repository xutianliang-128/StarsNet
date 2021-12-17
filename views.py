from flask import Flask, render_template, request, Blueprint, redirect
import json
import requests
from secret import base_url, headers, movie_detail_url, actor_detail_url, actor_filmography_url
from bs4 import BeautifulSoup
import base64
import matplotlib
from matplotlib import pyplot as plt
from io import BytesIO
import networkx as nx



'''
Cache is declared over here. MOVIES and STARS store the id of movies and stars that have been in the static json files.
'''
MOVIES = []
STARS = []
TEMP_ACTOR_1 = []
TEMP_ACTOR_2 = []

view = Blueprint('view', __name__)

class Image:
    '''
    Store some basic information about image
    '''
    def __init__(self, height, width, url):
        self.height = height
        self.width = width
        self.url = url

    def get_info(self):
        return {"height": self.height, "width": self.width, "imageUrl": self.url}

class Movie:
    '''
    Store some basic information about movie
    '''
    def __init__(self, m_id, name, img_info, rank, actors=None):
        self.id = m_id
        self.name = name
        self.rank = rank
        try:
            self.actors = actors.split(",")
        except:
            pass

        try:
            self.image = Image(img_info["height"], img_info["width"], img_info["imageUrl"])
        except:
            self.image = None

class MovieDetail(Movie):
    '''
    Input: Movie_id

    This class is inherited from Movie. Basically stores some detail information of certain movies.
    '''
    def __init__(self, id):
        global MOVIES
        if id in MOVIES:
            with open("static/movies.json", "r") as f:
                json_dict = json.load(f)
                this_movie = json_dict[id]
                self.status = False
                id = this_movie["id"]
                name = this_movie["name"]
                img_info = this_movie["img"]
                rank = this_movie["rank"]
                actors = this_movie["actors"]
                super().__init__(id, name, img_info, rank, actors)

                querystring = {"tconst": self.id}
                response = requests.request("GET", movie_detail_url, headers=headers, params=querystring)
                json_dict = json.loads(response.text)

                if "id" not in json_dict:
                    self.status = True
                else:
                    self.status = False
                    if "ratings" in json_dict:
                        self.rating = json_dict["ratings"]["rating"] if "rating" in json_dict["ratings"] else "Unknown"
                        self.rating_cnt = json_dict["ratings"]["ratingCount"] \
                            if "ratingCount" in json_dict["ratings"] else "Unknown"
                    else:
                        self.rating = "Unknown"
                        self.rating_cnt = "Unknown"
                    self.genre = json_dict["genres"]
                    if "releaseDate" in json_dict:
                        self.release_date = json_dict["releaseDate"]
                    else:
                        self.release_date = "Unknown"
                    if "plotSummary" in json_dict:
                        self.plot = json_dict["plotSummary"]["text"]
                    else:
                        self.plot = "Unknown"
        else:
            querystring = {"q": id}
            response = requests.request("GET", base_url, headers=headers, params=querystring)
            json_dict = json.loads(response.text)
            if "d" not in json_dict:
                self.status = True
            else:
                self.status = False
                item = json_dict["d"][0]
                name = item["l"]
                querystring = {"q": name}
                response = requests.request("GET", base_url, headers=headers, params=querystring)
                json_dict = json.loads(response.text)
                item = json_dict["d"][0]
                if "i" not in item:
                    item["i"] = None
                if "s" not in item:
                    item["s"] = "Unknown"
                super().__init__(item['id'], item["l"], item["i"], item["rank"], item["s"])


                querystring = {"tconst": id}
                response = requests.request("GET", movie_detail_url, headers=headers, params=querystring)
                json_dict = json.loads(response.text)
                if "id" not in json_dict:
                    self.status = True
                else:
                    self.status = False
                    if "ratings" in json_dict:
                        self.rating = json_dict["ratings"]["rating"] if "rating" in json_dict["ratings"] else "Unknown"
                        self.rating_cnt = json_dict["ratings"]["ratingCount"] \
                            if "ratingCount" in json_dict["ratings"] else "Unknown"
                    else:
                        self.rating = "Unknown"
                        self.rating_cnt = "Unknown"
                    self.genre = json_dict["genres"]
                    if "releaseDate" in json_dict:
                        self.release_date = json_dict["releaseDate"]
                    else:
                        self.release_date = "Unknown"
                    if "plotSummary" in json_dict:
                        self.plot = json_dict["plotSummary"]["text"]
                    else:
                        self.plot = "Unknown"
                    MOVIES.append(self.id)
                    with open("static/movies.json", "r") as f:
                        cont = f.read()
                        json_dict = json.loads(cont)
                    with open("static/movies.json", "w") as ff:
                        if self.id not in json_dict:
                            this_dic = {}
                            this_dic["id"] = self.id
                            this_dic["name"] = self.name
                            try:
                                this_dic["img"] = self.image.get_info()
                            except:
                                this_dic["img"] = None
                            this_dic["rank"] = self.rank
                            this_dic["actors"] = self.actors
                            json_dict[self.id] = this_dic
                            json.dump(json_dict, ff)

    def get_status(self):
        return self.status


class Actors:
    '''
    Store some basic information about movie
    '''
    def __init__(self, a_id, name, img_info, rank, relate=None):
        self.id = a_id
        self.name = name
        self.rank = rank
        try:
            temp = relate.split(",")
            self.gender = temp[0]
            self.product = temp[1]
        except:
            pass

        try:
            self.image = Image(img_info["height"], img_info["width"], img_info["imageUrl"])
        except:
            self.image = None


class ActorDetail(Actors):
    '''
    Input: Actor_id

    This class is inherited from Actors. Basically stores some detail information of certain stars.
    '''
    def __init__(self, id):
        global STARS
        if id in STARS:
            with open("static/actors.json", "r") as f:
                json_dict = json.load(f)
                this_movie = json_dict[id]
                self.status = False
                id = this_movie["id"]
                name = this_movie["name"]
                img_info = this_movie["img"]
                rank = this_movie["rank"]
                relate = this_movie["relate"]

                super().__init__(id, name, img_info, rank, relate)

                querystring = {"nconst": self.id}
                response = requests.request("GET", actor_detail_url, headers=headers, params=querystring)
                json_dict = json.loads(response.text)

                if "id" not in json_dict:
                    self.status = True
                else:
                    self.status = False
                    self.birthday = json_dict["birthDate"] if "birthData" in json_dict else "Unknown"

                    self.birthplace = json_dict["birthPlace"] if "birthPlace" in json_dict else "Unknown"

                response = requests.request("GET", actor_filmography_url, headers=headers, params=querystring)
                json_dict = json.loads(response.text)

                films = json_dict["filmography"]
                self.film_dict = {}
                self.out = {}

                for i in films:
                    temp_id = i["id"]
                    if len(self.out) <= 10:
                        self.out[temp_id] = i['title']
                    self.film_dict[temp_id] = i["title"]


        else:
            querystring = {"q": id}
            response = requests.request("GET", base_url, headers=headers, params=querystring)
            json_dict = json.loads(response.text)
            if "d" not in json_dict:
                self.status = True
            else:
                self.status = False
                item = json_dict["d"][0]
                name = item["l"]
                querystring = {"q": name}
                response = requests.request("GET", base_url, headers=headers, params=querystring)
                json_dict = json.loads(response.text)
                item = json_dict["d"][0]
                if "i" not in item:
                    item["i"] = None
                if "s" not in item:
                    item["s"] = "Unknown"
                super().__init__(item['id'], item["l"], item["i"], item["rank"], item["s"])


                querystring = {"nconst": id}
                response = requests.request("GET", actor_detail_url, headers=headers, params=querystring)
                json_dict = json.loads(response.text)
                if "id" not in json_dict:
                    self.status = True
                else:
                    self.status = False
                    if "birthDate" in json_dict:
                        self.birthday = json_dict["birthDate"]
                    else:
                        self.birthday = "Unknown"
                    if "birthPlace" in json_dict:
                        self.birthplace = json_dict["birthPlace"]
                    else:
                        self.birthplace = "Unknown"

                response = requests.request("GET", actor_filmography_url, headers=headers, params=querystring)
                json_dict = json.loads(response.text)

                films = json_dict["filmography"]
                self.film_dict = {}
                self.out = {}
                for i in films:
                    temp_id = i["id"]
                    if len(self.out) <= 10:
                        self.out[temp_id] = i['title']
                    self.film_dict[temp_id] = i["title"]
                    STARS.append(self.id)
                    with open("static/actors.json", "r") as f:
                        cont = f.read()
                        json_dict = json.loads(cont)
                    with open("static/actors.json", "w") as ff:
                        if self.id not in json_dict:
                            this_dic = {}
                            this_dic["id"] = self.id
                            this_dic["name"] = self.name
                            try:
                                this_dic["img"] = self.image.get_info()
                            except:
                                this_dic["img"] = None
                            this_dic["rank"] = self.rank
                            this_dic["relate"] = item["s"]
                            json_dict[self.id] = this_dic
                            json.dump(json_dict, ff)

        adding = False
        with open("static/movie-actor_graph.json", "r") as f:
            cont = json.loads(f.read())
            if id not in cont["actor"]:
                adding = True

        if adding:
            with open("static/movie-actor_graph.json", "w") as ff:
                cont["actor"][id] = self.film_dict
                for i in films:
                    if i['id'] not in cont["movie"]:
                        cont["movie"][i["id"]] = {"title": i["title"], "actor": [id]}
                    else:
                        if id not in cont["movie"][i["id"]]["actor"]:
                            cont["movie"][i["id"]]["actor"].append(id)
                json.dump(cont, ff)





    def get_status(self):
        return self.status


class JsonRetriever:
    '''
    Retrieve information from API and store it into Movies object or Actors object.
    '''
    def __init__(self, name, movie_or_actors):
        self.querystring = {"q": name}
        self.response = requests.request("GET", base_url, headers=headers, params=self.querystring)
        self.json_dict = json.loads(self.response.text)

        if "d" not in self.json_dict:
            self.status = True
        else:
            self.maximum = 5
            self.status = False
            self.outcome = []

            if movie_or_actors == 1:
                global MOVIES
                with open("static/movies.json", "r") as f:
                    cont = f.read()
                    json_dict = json.loads(cont)
                for item in self.json_dict["d"]:
                    if "tt" in item["id"]:
                        if "i" not in item:
                            item["i"] = None
                        if "s" not in item:
                            item["s"] = "Unknown"
                        self.outcome.append(Movie(item['id'], item["l"], item["i"], item["rank"], item["s"]))
                        if item['id'] not in json_dict:
                            MOVIES.append(item['id'])
                            this_dic = {}
                            this_dic["id"] = item['id']
                            this_dic["name"] = item["l"]
                            this_dic["img"] = item["i"]
                            this_dic["rank"] = item["rank"]
                            this_dic["actors"] = item["s"]
                            json_dict[item['id']] = this_dic

                        if len(self.outcome) > self.maximum:
                            break
                with open("static/movies.json", "w") as ff:
                    wrap = json.dumps(json_dict)
                    ff.write(wrap)
            else:
                global STARS
                with open("static/actors.json", "r") as f:
                    cont = f.read()
                    json_dict = json.loads(cont)
                for item in self.json_dict["d"]:
                    if "nm" in item["id"]:
                        if "i" not in item:
                            item["i"] = None
                        if "s" not in item:
                            item["s"] = "Unknown"
                        self.outcome.append(Actors(item['id'], item["l"], item["i"], item["rank"], item["s"]))
                        if item['id'] not in json_dict:
                            STARS.append(item['id'])
                            this_dic = {}
                            this_dic["id"] = item['id']
                            this_dic["name"] = item["l"]
                            this_dic["img"] = item["i"]
                            this_dic["rank"] = item["rank"]
                            this_dic["relate"] = item["s"]
                            json_dict[item['id']] = this_dic
                        if len(self.outcome) > self.maximum:
                            break

                with open("static/actors.json", "w") as ff:
                    wrap = json.dumps(json_dict)
                    ff.write(wrap)

    def get_status(self):
        return self.status

    def get_outcome(self):
        return self.outcome

@view.route("/")
def index():
    global MOVIES
    global STARS
    with open("static/movies.json", "r") as f:
        json_dict = json.loads(f.read())
        MOVIES = MOVIES + list(json_dict.keys())
        MOVIES = list(set(MOVIES))
    with open("static/actors.json", "r") as f:
        json_dict = json.loads(f.read())
        STARS = STARS + list(json_dict.keys())
        STARS = list(set(STARS))
    return render_template("index.html")

@view.route("/movie_search/", methods=["GET", "POST"])
def search_selection_movie():
    return render_template("movie_search.html")

@view.route("/handle_movie/", methods=["POST"])
def handle_movie():
    movie_name = request.form.get("movie_name")
    detail = JsonRetriever(movie_name, 1)
    if detail.get_status():
        return render_template("notFound.html", name=movie_name)
    outcome = detail.get_outcome()
    return render_template("movie_list.html", outcome=outcome)

@view.route("/to_index/", methods=["POST"])
def to_index():
    return redirect("/")

@view.route("/actor_search/", methods=["POST"])
def search_selection_actor():
    return render_template("actor_search.html")

@view.route("/handle_actor/", methods=["POST"])
def handle_actor():
    actor_name = request.form.get("actor_name")
    detail = JsonRetriever(actor_name, 0)
    if detail.get_status():
        return render_template("notFound.html", name=actor_name)
    outcome = detail.get_outcome()
    return render_template("actor_list.html", outcome=outcome)

@view.route("/movie/<m_id>", methods=["GET", "POST"])
def show_movie_detail(m_id):
    detail = MovieDetail(m_id)
    if detail.get_status():
        return render_template("notFound.html", name=m_id)
    return render_template("movie_detail.html", outcome=detail)

@view.route("/actor/<a_id>", methods=["GET", "POST"])
def show_actor_detail(a_id):
    detail = ActorDetail(a_id)
    if detail.get_status():
        return render_template("notFound.html", name=a_id)
    return render_template("actor_detail.html", outcome=detail)

@view.route("/ratings/<m_id>", methods=["GET", "POST"])
def crawling(m_id):
    '''
    :param m_id:
    :return:
        int total_num: It is the number of users on IMDb who rate the certain movie
        list[int] num_list: It is the list which contain the number of people who rated the movie from 10 to 1.

    This function crawls and parses data from IMDb ratings page.
    '''
    find_img = False
    with open("static/ratings.txt", "r") as f:
        line = f.readline()
        while line:
            line = line.split()
            if m_id in line[0]:
                total_num = line[1]
                num_list = line[2:]
                num_list = list(map(int, num_list))
                find_img = True
                break
            line = f.readline()
    if find_img:
        from PIL import Image
        try:
            img = Image.open(view.root_path + "\static\img\\" + m_id + ".png")
        except:
            return render_template("notFound.html", name=m_id)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_stream = base64.b64encode(buffered.getvalue())
        img_stream = str(img_stream)

        try:
            img = Image.open(view.root_path + "\static\img\\" + m_id + "_pie.png")
        except:
            return render_template("notFound.html", name=m_id)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_stream2 = base64.b64encode(buffered.getvalue())
        img_stream2 = str(img_stream)

        return render_template("ratings_detail.html",
                               total_num=total_num,
                               num_list=num_list,
                               img_stream=img_stream[2:-1],
                               img_stream2=img_stream2[2:-1])

    response = requests.get("https://www.imdb.com/title/" + m_id + "/ratings")
    soup = BeautifulSoup(response.text, 'html.parser')

    total = soup.find_all("a", href=True)
    total_num = 0
    for i in total:
        if "ratings?demo=imdb_users" in i["href"]:
            total_num = i.string.split()
            total_num = total_num[0]
            total_num = total_num.split(",")
            total_num = ''.join(total_num)
            total_num = int(total_num)
            break
    each = soup.find_all("div", class_="leftAligned")
    num_list = []
    for i in each:
        if i.string[0].isnumeric():
            temp = i.string
            num = i.string.split()
            num = num[0]
            num = num.split(",")
            num = ''.join(num)
            num = int(num)
            num_list.append(num)
    store_line = ""
    temp_total = str(total_num)
    temp_list = list(map(str, num_list))
    temp_list = [m_id, temp_total] + temp_list
    store_line = " ".join(temp_list)
    with open("static/ratings.txt", "a") as f:
        f.write(store_line + "\n")


    plt.figure()
    x = [*range(10, 0, -1)]
    try:
        plt.barh(x, num_list, tick_label=x)
    except:
        return render_template("notFound.html", name=m_id)
    for a, b in zip(x, num_list):
        plt.text(b,a,'%.0f' %b, ha='left', va='center', fontsize=7)

    plt.savefig("static/img/" + m_id + ".png")
    buffered = BytesIO()
    plt.savefig(buffered, format="PNG")
    img_stream = base64.b64encode(buffered.getvalue())
    img_stream = str(img_stream)
    print("lalala")
    plt.figure()
    try:
        plt.pie(num_list, autopct="%0.2f%%", labels=x)
    except:
        return render_template("notFound.html", name=m_id)

    plt.savefig("static/img/" + m_id + "_pie.png")

    buffered = BytesIO()
    plt.savefig(buffered, format="PNG")
    img_stream2 = base64.b64encode(buffered.getvalue())

    img_stream2 = str(img_stream2)

    return render_template("ratings_detail.html",
                           total_num=total_num,
                           num_list=num_list,
                           img_stream=img_stream[2:-1],
                           img_stream2=img_stream2[2:-1])

@view.route("/compare/", methods=["GET", "POST"])
def compare():
    return render_template("comparing.html")

@view.route("/coActGraph/", methods=["GET", "POST"])
def make_co_graph():
    name1 = request.form["name1"]
    name2 = request.form["name2"]
    try:
        detail = JsonRetriever(name1, 0)
        if detail.get_status():
            return render_template("notFound.html", name=name1)
        outcome1 = detail.get_outcome()
        detail = JsonRetriever(name2, 0)
        if detail.get_status():
            return render_template("notFound.html", name=name2)
        outcome2 = detail.get_outcome()
        global TEMP_ACTOR_1
        global TEMP_ACTOR_2
        TEMP_ACTOR_1 = outcome1
        TEMP_ACTOR_2 = outcome2
        return render_template("two_list.html", outcome1=outcome1, outcome2=outcome2)
    except:
        return render_template("notFound.html", name=name1 + " or " + name2)

@view.route("/handle_actors_list/", methods=["GET", "POST"])
def handle_two_actors_list():
    index_1 = request.form.get("index1")
    index_2 = request.form.get("index2")
    global TEMP_ACTOR_1
    global TEMP_ACTOR_2
    try:
        actor1 = TEMP_ACTOR_1[int(index_1)-1]
    except:
        return render_template("notFound.html", name="You should proceed with the normal procedure")
    try:
        actor2 = TEMP_ACTOR_2[int(index_2)-1]
    except:
        return render_template("notFound.html", name="You should proceed with the normal procedure")

    with open("static/movie-actor_graph.json", "r") as f:
        cont = json.loads(f.read())
        if actor1.id not in cont["actor"]:
            detail1 = ActorDetail(actor1.id)
            dict1 = detail1.film_dict
        else:
            dict1 = cont["actor"][actor1.id]
        if actor2.id not in cont["actor"]:
            detail2 = ActorDetail(actor2.id)
            dict2 = detail2.film_dict
        else:
            dict2 = cont["actor"][actor2.id]


        G = nx.Graph()
        G.add_node(actor1.name)

        for i in dict1:
            G.add_edge(actor1.name, dict1[i])
        G.add_node(actor2.name)
        for i in dict2:
            G.add_edge(actor2.name, dict2[i])
        top_nodes = {actor1.name, actor2.name}
        pos = nx.bipartite_layout(G, top_nodes)
        bottom_nodes = set(G) - top_nodes
        deg = nx.degree(G)
        colist = []
        for node in bottom_nodes:
            if deg[node] >= 2:
                colist.append(node)
        mono_nodes = bottom_nodes - set(colist)
        plt.figure(figsize=(12.8, 9.6))
        nx.draw_networkx_nodes(G, nodelist=top_nodes, pos=pos, node_shape="d", node_size=5, linewidths=0.05)
        nx.draw_networkx_nodes(G, nodelist=mono_nodes, pos=pos, node_shape="o", node_size=5, linewidths=0.05)
        nx.draw_networkx_nodes(G, nodelist=set(colist), pos=pos, node_color="r" , node_shape="o", node_size=5, linewidths=0.05)
        nx.draw_networkx_edges(G, pos=pos, width=0.1)

        labels = {n: n for n in colist}
        labels.update({n: n for n in top_nodes})
        nx.draw_networkx_labels(G, pos=pos, labels=labels, font_color='r', font_size=10)


        buffered = BytesIO()
        plt.savefig(buffered, format="PNG")
        img_stream = base64.b64encode(buffered.getvalue())

        img_stream = str(img_stream)

    return render_template("show_graph.html", img_stream=img_stream[2:-1], colist=colist)
