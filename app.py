from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:masterpassword@localhost/champ_manager'
db = SQLAlchemy(app)

# Modelo de Jogador
class Player(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  points =  db.Column(db.Integer, default = 0)

# Modelo de Partida
class Match(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  player_1 = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
  player_2 = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
  winner_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
  points_won = db.Column(db.Integer, default = 0)

# Modelo Visão de Tabela Classificação
class TableClass(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  player_id = db.Column(db.Integer, nullable=False)
  player_nome = db.Column(db.String(100), nullable=False)
  total_points = db.Column(db.Integer, default = 0)

# Código para criação da visão com a tabela
#
# CREATE VIEW TABLECLASS AS
# SELECT player.id AS player_id,
#    player.name AS player_nome,
#    ( SELECT sum(match_1.points_won) AS sum
#           FROM match match_1
#          WHERE match_1.winner_id = player.id) AS total_points
#   FROM player,
#    match
#  WHERE match.winner_id = player.id
#  GROUP BY player.id;

# Criação do Banco de Dados
db.create_all()

# Rotas
@app.route('/')
def index():
  players = Player.query.all()
  matches = Match.query.all()
  return render_template('index.html', players=players, matches=matches)

@app.route('/add_player', methods=['POST'])
def add_player():
  name = request.form['name']
  new_player = Player(name=name)
  db.session.add(new_player)
  db.session.commit()
  return redirect(url_for('index'))

@app.route('/remove_player/<int:id>')
def remove_player(id):
  player = Player.query.get(id)
  db.session.delete(player)
  db.session.commit()
  return redirect(url_for('index'))

@app.route('/add_match', methods=['POST'])
def add_match():
  player_1 = request.form['player1']
  player_2 = request.form['player2']
  winner_id = request.form['winner']
  points = request.form['points']

  new_match = Match(player_1=player_1, player_2=player_2, winner_id=winner_id, points_won=points)
  db.session.add(new_match)
  db.session.commit()

  return redirect(url_for('index'))

@app.route('/remove_match/<int:id>')
def remove_match(id):
  match = Match.query.get(id)
  db.session.delete(match)
  db.session.commit()
  return redirect(url_for('index'))

@app.route('/update_score')
def update_score():
  winners = (
        db.session.query(TableClass.player_nome, TableClass.total_points)
        .from_statement(text("SELECT * FROM tableclass"))
        .all()
    )
  return render_template('classification.html', winners=winners)

if __name__ == '__main__':
  app.run(debug=True)