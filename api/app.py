from flask import Flask, jsonify, make_response, request
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
from logging.config import dictConfig
from collections import deque
import psycopg2
import psycopg2.extras
import os

load_dotenv()

DATABASE=os.getenv('DATABASE')
DATABASE_HOST=os.getenv('POSTGRES_HOST')
DATABASE_PORT=os.getenv('POSTGRES_PORT')
DATABASE_USERNAME=os.getenv('DATABASE_USERNAME')
DATABASE_PASSWORD=os.getenv('DATABASE_PASSWORD')


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


app = Flask(__name__, static_folder='../client/build')
CORS(app)


try:
    con = psycopg2.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        dbname=DATABASE,
        user=DATABASE_USERNAME,
        password=DATABASE_PASSWORD)

    cur = con.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

    @app.route('/movies', methods=['POST'])
    def fetch_all_movies():
        cur.execute('SELECT * FROM title_basics LIMIT 5')
        rows = cur.fetchall()
        app.logger.info(rows)

        return make_response(jsonify(rows))


    @app.route('/getMovie', methods=['POST'])
    def getMovie():
        params = request.get_json(force=True)
        app.logger.info("PARAMS=", params)
        term = params[0]
        query_type = params[1]
        if query_type == "movie":
            return getMoviesByTitle(term)
        elif query_type == "genre":
            return getMoviesByGenre(term)
        elif query_type == "bacon":
            return getBaconNumber(term)
        return "Error - Invalid query"

    def getMoviesByTitle(term):
        cmd = f"""
            SELECT basics.tconst, basics.primarytitle, basics.startyear, prin.category AS role, names.primaryname as NAME
            FROM title_basics basics
            JOIN title_principals prin ON basics.tconst = prin.tconst
            JOIN name_basics names ON prin.nconst=names.nconst
            WHERE basics.primarytitle iLIKE '%{term}%'
            OR basics.originaltitle iLIKE '%{term}%';
            """
        cur.execute(cmd)
        rows = cur.fetchall()
        app.logger.info(rows)

        response = make_response(jsonify(rows))
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        return response

    def getMoviesByGenre(term):
        cmd = f"""
            SELECT basics.primarytitle, basics.startyear, basics.genres, ratings.averagerating, ratings.numvotes
            FROM title_basics basics
            JOIN title_ratings ratings ON basics.tconst=ratings.tconst
            WHERE ratings.numvotes > 1000 AND basics.genres iLIKE '%{term}%'
            ORDER BY ratings.averagerating DESC
            LIMIT 10;
            """
        cur.execute(cmd)
        rows = cur.fetchall()
        app.logger.info(rows)

        response = make_response(jsonify(rows))
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        return response

    def getBaconNumber(term):
        cmd = f"""
            SELECT basics.tconst,  prin.category AS role, names.primaryname as name
            FROM title_basics basics
            JOIN title_principals prin ON basics.tconst = prin.tconst
            JOIN name_basics names ON prin.nconst=names.nconst
            WHERE names.primaryname='{term}'
            """
        cur.execute(cmd)
        rows = cur.fetchall()

        rows = list(dict(r) for r in rows)
        movies = [rows[i]['tconst'] for i in range(len(rows))]
        queue = deque([(0, m) for m in movies])
        seen = set()
        baconNum = -1

        while queue:
            num, movie = queue.popleft()
            cmd = f"""
                SELECT basics.tconst,  prin.category AS role, names.primaryname as name
                FROM title_basics basics
                JOIN title_principals prin ON basics.tconst = prin.tconst
                JOIN name_basics names ON prin.nconst=names.nconst
                WHERE basics.tconst='{movie}'
                """
            cur.execute(cmd)
            rows = cur.fetchall()
            rows = list(dict(r) for r in rows)
            cast = set([rows[i]['name'] for i in range(len(rows))])
            app.logger.info(cast)

            if 'Kevin Bacon' in cast:
                baconNum = num
                break

            seen.add(movie)

            for c in cast:
                cmd = f"""
                    SELECT basics.tconst,  prin.category AS role, names.primaryname as name
                    FROM title_basics basics
                    JOIN title_principals prin ON basics.tconst = prin.tconst
                    JOIN name_basics names ON prin.nconst=names.nconst
                    WHERE names.primaryname='{c}'
                    """
                cur.execute(cmd)
                rows = cur.fetchall()

                rows = list(dict(r) for r in rows)
                movies = [rows[i]['tconst'] for i in range(len(rows))]
                for m in movies:
                    if m not in seen:
                        queue.append((num+1, m))


        response = make_response(jsonify(baconNum))
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        return response


except:
    app.logger.error('Error connecting to database')


@app.route('/test', methods=['GET'])
def test_response():
    sample_response = {
        "items": [
            { "id": 1, "name": "Apples",  "price": "$2" },
            { "id": 2, "name": "Peaches", "price": "$5" }
        ]
    }
    # JSONify response
    response = make_response(jsonify(sample_response))

    # Add Access-Control-Allow-Origin header to allow cross-site request
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'

    return response
