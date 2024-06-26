import time
import redis
from flask import Flask, render_template
from flask import url_for
import pandas as pd
import matplotlib.pyplot as plt
from decouple import config


app = Flask(__name__)

REDIS_HOST = config('REDIS_HOST') 
REDIS_PASSWORD = config('REDIS_PASSWORD')

cache = redis.Redis(host=REDIS_HOST, port=6379, password=REDIS_PASSWORD)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return render_template('hello.html', name= "BIPM", count = count)

@app.route('/titanic')
def new_page():
    df = pd.read_csv('static/titanic.csv') 
    table = df.to_html()

    
    df_surrvived = df[df['survived'] == 1]
    counts = df_surrvived['sex'].value_counts()

    counts.plot(kind='bar')
    plt.title('Distribution of Sex')
    plt.xlabel('Sex')
    plt.ylabel('Count')
    plt.savefig('static/plot.png')  # save the plot to a file
    plt.close()
    return render_template('titanic.html', table=table)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)