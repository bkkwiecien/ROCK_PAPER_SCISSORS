import random
from flask import Flask, render_template, request
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

app = Flask(__name__)
score = 10
user = None
nick = ''
start_time = datetime.now()

Base = declarative_base()
engine = create_engine('sqlite:///users.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(bind=engine)


class User(Base):
    __tablename__ = 'users'

    nick = Column(String, primary_key=True)
    start_time = Column(String)
    end_time = Column(String)
    total_time = Column(String)
    score = Column(String)
    results = Column(String)

    def __repr__(self):
        return f'database created'


def add_user(nick):
    user = User(nick=nick, start_time=str([]), end_time=str([]), total_time=str([]), score=str([]), results=str([]))
    session.add(user)
    session.commit()

    return user


def if_none(element, update):
    if not list(element).append(update):
        return str([update])
    else:
        return list(element).append(update)


def safe_statistics(nick, start_time_data, end_time_data, total_time_data, score_data, results_data):
    user = session.get(User, nick)

    session.execute(update(User).where(User.nick == nick).values(
        end_time=str(if_none(user.end_time, start_time_data)),
        start_time=str(if_none(user.start_time, end_time_data)),
        total_time=str(if_none(user.total_time, total_time_data)),
        score=str(if_none(user.score, score_data)),
        results=str(if_none(user.results, results_data))
    ))


def convert_statistics(stat):
    new_statistics = []

    for i in range(len(stat['start_time'])):
        new_statistics.append(
            {
                "start_time": stat['start_time'][i],
                "end_time": stat['end_time'][i],
                "total_time": stat['total_time'][i],
                "score": stat['score'][i],
                "results": stat['results'][i]
            }
        )

    return new_statistics


def open_statistics(nick):
    user = session.get(User, nick)
    statistics = {
        "start_time": list(user.start_time),
        "end_time": list(user.end_time),
        "total_time": list(user.total_time),
        "score": list(user.score),
        "results": list(user.results)
    }

    return convert_statistics(statistics)


def computer_choice():
    options = ['paper', 'paper','paper','paper','paper', 'scissors', 'scissors', 'scissors', 'rock', 'rock']
    choice = random.choice(options)

    return choice


def winner(player, bot):

    posible_results = {
        'paper': {
            'paper': 0,
            'scissors': -1,
            'rock': 1
        },
        'scissors': {
            'paper': 1,
            'scissors': 0,
            'rock': -1
        },
        'rock': {
            'paper': -1,
            'scissors': 1,
            'rock': 0
        }
    }

    result = posible_results[player][bot]

    return result


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/main_menu", methods=["POST"])
def register():
    global nick, score, user
    if nick == '':
        nick = request.form.get("nick")

        if not nick:
            return render_template("no_nickname.html")

    add_user(nick)

    return render_template("play_button.html", nick=nick.upper(), score=score)


@app.route("/game")
def display_game():
    global nick, score, start_time

    start_time = datetime.now()

    return render_template("the_game.html", nick=nick.upper(), score=score)


@app.route("/results")
def display_winner():
    global nick, score, start_time

    human_choice = request.args.get("option")
    result = winner(human_choice, computer_choice())
    end_time = datetime.now()
    total_time = (end_time - start_time).strftime("%H:%M:%S")
    start_time = start_time.strftime("%H:%M:%S")
    end_time = end_time.strftime("%H:%M:%S")

    safe_statistics(nick, start_time, end_time, total_time, score, result)

    if result == -1:
        score -= 3
        return render_template("results.html", nick=nick.upper(), score=score, first_word="YOU", second_word="LOSE")
    elif result == 1:
        score += 4
        return render_template("results.html", nick=nick.upper(), score=score, first_word="YOU", second_word="WON")
    else:
        return render_template("results.html", nick=nick.upper(), score=score, first_word="", second_word="TIE")


@app.route("/statistics")
def statistics():
    global nick
    statistics = open_statistics(nick)

    return render_template("statistics.html", nick=nick.upper(), statistics=statistics)


def __del__():
    session.close()


if __name__ == '__main__':
    app.run()
