# Imports

import json
import numpy as np
from flask import Flask, jsonify, render_template, request
from deep_reinforcement_learning import *

app = Flask(__name__)

# Abrindo sessão
sess = tf.InteractiveSession()

# Previsões
x , prediction, _ = createNetwork()

# Carregando o modelo treinado
saver = tf.train.Saver()
checkpoint = tf.train.get_checkpoint_state("model")

if checkpoint and checkpoint.model_checkpoint_path:
    s = saver.restore(sess,checkpoint.model_checkpoint_path)
    print("Modelo carregado com sucesso:", checkpoint.model_checkpoint_path)
else:
    print("Não foi possível carregar o modelo")
graph = tf.get_default_graph()

@app.route('/')
def index():
    return render_template('index.html')

def  bestmove(input):
    global graph
    with graph.as_default():
        data = (sess.run(tf.argmax(prediction.eval(session = sess,feed_dict={x:[input]}),1)))
    return data

@app.route('/api/ticky', methods=['POST'])
def ticky_api():
    data = request.get_json()
    data = np.array(data['data'])
    data = data.tolist()
    return jsonify(np.asscalar(bestmove(data)[0]))

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=81)

