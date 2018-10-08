# Um Programa Python para implementar o Aprendizado de Máquina para o Jogo Tic Tac Toe (3x3) 
# usando Aprendizado por Reforço (técnica de aprendizado Q) e tensorflow.

# Imports
import time
import tensorflow as tf
import random
import numpy as np
from pathlib import Path
import os
import sys

# Variáveis
game_rows = rows = 3
game_cols = cols = 3
winning_length = 3
boardSize = rows * cols
actions = rows * cols
won_games = 0
lost_games = 0
draw_games = 0
layer_1_w = 750
layer_2_w = 750
layer_3_w = 750


def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev = 0.01)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.01, shape = shape)
    return tf.Variable(initial)


# Política gananciosa (greedy policy) para selecionar uma ação
# Quanto maior o valor de e, maior a probabilidade de uma ação ser aleatória.
epsilon = 1.0

# Discount factor -- determina a importância de recompensas futuras
GAMMA = 0.9


# troca X's por O's e vice-versa
def InverseBoard(board):
    temp_board = np.copy(board)
    rows, cols = temp_board.shape
    for r in range(rows):
        for c in range(cols):
            temp_board[r,c] *= -1
    return temp_board.reshape([-1])

def isGameOver(board):
    temp = None
    rows , cols = board.shape

    ## Linhas
    for i in range(rows):
        temp = getRowSum(board, i)
        if checkValue(temp):
            return True
    ## Colunas
    for i in range(cols):
        temp = getColSum(board, i)
        if checkValue(temp):
            return True

    ## Diagonais
    temp = getRightDig(board)
    if checkValue(temp):
        return True

    temp = getLeftDig(board)
    if checkValue(temp):
        return True

    return False

def getRowSum(board , r):
    rows , cols = board.shape
    sum = 0
    for c in range(cols):
        sum = sum + board[r,c]
    return sum

def getColSum(board , c):
    rows , cols = board.shape
    sum = 0
    for r in range(rows):
        sum = sum + board[r,c]
    return sum

def getLeftDig(board):
    rows , cols = board.shape
    sum = 0
    for i in range(rows):
        sum = sum + board[i,i]
    return sum

def getRightDig(board):
    rows , cols = board.shape
    sum = 0
    i = rows - 1
    j = 0
    while i >= 0:
        sum += board[i,j]
        i = i - 1
        j = j + 1
    return sum

def checkValue(sum):
    if sum == -3 or sum == 3:
        return True


# Cria a rede
def createNetwork():

    W_layer1 = weight_variable([boardSize, layer_1_w])
    b_layer1 = bias_variable([layer_1_w])

    W_layer2 = weight_variable([layer_1_w, layer_2_w])
    b_layer2 = bias_variable([layer_2_w])

    W_layer3 = weight_variable([layer_2_w, layer_3_w])
    b_layer3 = bias_variable([layer_3_w])

    o_layer = weight_variable([layer_3_w, actions])
    o_bais  = bias_variable([actions])

    # Input Layer
    x = tf.placeholder("float", [None, boardSize])

    # hidden layers
    h_layer1 = tf.nn.relu(tf.matmul(x,W_layer1) + b_layer1)
    h_layer2 = tf.nn.relu(tf.matmul(h_layer1,W_layer2) + b_layer2)
    h_layer3 = tf.nn.relu(tf.matmul(h_layer2,W_layer3) + b_layer3)

    # Output layer
    y = tf.matmul(h_layer3,o_layer) + o_bais
    prediction = tf.argmax(y[0])

    return x,y, prediction


def tainNetwork():
    print()

    # Cria a rede
    inputState , Qoutputs, prediction = createNetwork()

    # Calcula a perda
    targetQOutputs = tf.placeholder("float",[None,actions])
    loss =  tf.reduce_mean(tf.square(tf.subtract(targetQOutputs, Qoutputs)))

    # Treina o modelo e minimiza a perda
    train_step = tf.train.AdamOptimizer(1e-4).minimize(loss)

    # Cria a sessão
    sess = tf.InteractiveSession()

    # Salva a rede e inicializa as variáveis
    saver = tf.train.Saver()
    sess.run(tf.global_variables_initializer())

    # Carrega o modelo salvo
    step = 0
    iterations = 0

    checkpoint = tf.train.get_checkpoint_state("model")
    if checkpoint and checkpoint.model_checkpoint_path:
        s = saver.restore(sess,checkpoint.model_checkpoint_path)
        print("Modelo carregado com sucesso:", checkpoint.model_checkpoint_path)
        step = int(os.path.basename(checkpoint.model_checkpoint_path).split('-')[1])
    else:
        print("Não foi possível carregar a rede")
    iterations += step

    print(time.ctime())

    ## Define número máximo de correspondências para interação inicial
    tot_matches = 60000
    number_of_matches_each_episode = 500
    max_iterations = tot_matches / number_of_matches_each_episode
    
    e_downrate = 0.9 / max_iterations

    e = epsilon

    print("Iteração Máxima = {}".format(max_iterations))
    print()
    
    run_time = 0
    while "ticky" != "tacky":
        sys.stdout.flush()
        start_time = time.time()
        episodes = number_of_matches_each_episode
        global won_games
        global lost_games
        global draw_games

        total_loss = 0

        epchos = 100
        GamesList = []

        for i in range(episodes):
            completeGame, victory = playaGame(e,sess,inputState, prediction,Qoutputs)
            GamesList.append(completeGame)
            

        for k in range(epchos):
            random.shuffle(GamesList)
            for i in GamesList:
                len_complete_game = len(i)
                loop_in = 0
                game_reward = 0
                while loop_in < len_complete_game:
                    j = i.pop()
                    currentState = j[0]
                    action = j[1][0]
                    reward = j[2][0]
                    nextState = j[3]

                    ## Game e reward
                    if loop_in == 0:
                        game_reward = reward
                    else:
                        # Obter q valores para o próximo estado usando a rede
                        nextQ = sess.run(Qoutputs,feed_dict={inputState:[nextState]})
                        maxNextQ = np.max(nextQ)
                        game_reward = GAMMA * ( maxNextQ )

                    
                    targetQ = sess.run(Qoutputs,feed_dict={inputState:[currentState]})

                    # Uma vez que calculamos a recompensa para a ação em particular, devemos também adicionar a recompensa -1 
                    # para todos os movimentos ilegais no valor q 
                    for index,item in enumerate(currentState):
                        if item != 0:
                            targetQ[0,index] = -1

                    targetQ[0,action] = game_reward

                    loop_in += 1
                    t_loss = 0

                    
                    t_loss=sess.run([train_step,Qoutputs,loss],feed_dict={inputState:[currentState], targetQOutputs:targetQ})
                    total_loss += t_loss[2]

        iterations += 1
        time_diff = time.time()-start_time
        run_time += time_diff
        print("Iteração {} completada com {} wins, {} losses {} draws, out of {} games played, e is {} \ncost is {} , current_time is {}, time taken is {} , total time = {} hours \n".format(iterations,
        won_games,lost_games,draw_games,episodes,e*100,total_loss,time.ctime(),time_diff,(run_time)/3600))
        start_time = time.time()
        total_loss = 0
        won_games = 0
        lost_games = 0
        draw_games = 0

        if e > -0.2:
            e -= e_downrate
        else:
             e = random.choice([0.1,0.05,0.06,0.07,0.15,0.03,0.20,0.25,0.5,0.4])

        saver.save(sess, "./model/model.ckpt",global_step=iterations)




# Joga um jogo e retorna uma lista com todos os estados, ações e recompensa final.
def playaGame(e,sess,inputState, prediction, Qoutputs):
    global won_games
    global lost_games
    global draw_games

    win_reward = 10
    loss_reward = -1
    draw_reward = 3

    ## Cria o objeto de memória de jogo inteiro que contém as memórias para o jogo e um tabuleiro vazio
    completeGameMemory = []
    myList = np.array([0]*(rows*cols)).reshape(3,3)

    turn = random.choice([1,-1])

    if(turn == -1):
        initial_index = random.choice(range(9))
        best_index, _= sess.run([prediction,Qoutputs], feed_dict={inputState : [np.array(np.copy(myList).reshape(-1))]})
        initial_index = random.choice([best_index,initial_index,best_index])
        myList[int(initial_index/3),initial_index%3] = -1
        turn = turn * -1

    while(True):

        ## Criar uma memória que mantenha o estado inicial atual, a ação tomada, a recompensa recebida, o próximo estado
        memory = []

        ## Criar uma cópia do board que é linear
        temp_copy = np.array(np.copy(myList).reshape(-1))

        ## Buscar todos os índices que estão livres ou zero para que eles possam ser usados para jogar o próximo movimento
        zero_indexes = []
        for index,item in enumerate(temp_copy):
            if item == 0:
                zero_indexes.append(index)

        if len(zero_indexes) == 0:
            reward = draw_reward
            completeGameMemory[-1][2][0] = reward
            draw_games += 1
            break

        selectedRandomIndex = random.choice(zero_indexes)

        ## Calcular a previsão da rede que pode ser usada posteriormente como uma ação com alguma probabilidade
        pred, _ = sess.run([prediction,Qoutputs], feed_dict={inputState : [temp_copy]})

        ## Como a rede pode ser confusa e imprecisa, verifique se a previsão está correta primeiro.
        isFalsePrediction = False if temp_copy[pred] == 0 else True

        ## Vamos adicionar o estado inicial à memória atual
        memory.append(np.copy(myList).reshape(-1))

        ## Vamos escolher uma ação com alguma probabilidade e exploração
        if random.random() > e: 
            action = pred
        else: 
            random_action = random.choice(range(9))
            action = selectedRandomIndex

        memory.append([action])

        if action not in zero_indexes:
            reward = loss_reward
            memory.append([reward])
            memory.append(np.copy(myList.reshape(-1)))
            completeGameMemory.append(memory)
            lost_games +=1
            break

        ## Atualizar o board com a ação tomada
        myList[int(action/game_rows),action%game_cols] = 1

        ## Agora calcule a recompensa.
        reward = 0

        ## Se escolhermos uma ação inválida, não recebemos nenhuma recompensa e o oponente ganha
        if isFalsePrediction == True and action == pred:
            reward = loss_reward
            memory.append([reward])
            memory.append(np.copy(myList.reshape(-1)))
            completeGameMemory.append(memory)
            lost_games +=1
            break

        ## Se depois de jogarmos o nosso jogo o jogo estiver completo, então merecemos uma recompensa e é o estado final
        if(isGameOver(myList)):
            reward = win_reward
            memory.append([reward])
            memory.append(np.copy(myList.reshape(-1)))
            completeGameMemory.append(memory)
            won_games +=1
            break



        temp_copy_inverse = np.array(np.copy(InverseBoard(myList)).reshape(-1))
        temp_copy = np.array(np.copy(myList).reshape(-1))
        zero_indexes = []
        for index,item in enumerate(temp_copy):
            if item == 0:
                zero_indexes.append(index)

        if len(zero_indexes) == 0:
            reward = draw_reward
            memory.append([reward])
            memory.append(np.copy(myList.reshape(-1)))
            completeGameMemory.append(memory)
            draw_games+=1
            break

        selectedRandomIndex = random.choice(zero_indexes)
        pred, _ = sess.run([prediction,Qoutputs], feed_dict={inputState : [temp_copy_inverse]})
        isFalsePrediction = False if temp_copy[pred] == 0 else True

        action = None

        if(isFalsePrediction == True):
            action = random.choice([selectedRandomIndex])
        else:
            action = random.choice([selectedRandomIndex,pred,pred,pred,pred])

        temp_copy2 = np.copy(myList).reshape(-1)
        if temp_copy2[action] != 0:
            print("Erro ",temp_copy2 , action)
            return

        myList[int(action/game_rows),action%game_cols] = -1

        if isGameOver(myList) == True:
            reward = loss_reward
            memory.append([reward])
            memory.append(np.copy(myList.reshape(-1)))
            completeGameMemory.append(memory)
            lost_games +=1
            break

        ## Se ninguém ganhou e o jogo ainda não terminou, então vamos continuar o jogo
        memory.append([0])
        memory.append(np.copy(myList.reshape(-1)))

        completeGameMemory.append(memory)

    return completeGameMemory,reward



if __name__ == "__main__":
    tainNetwork()
