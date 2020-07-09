class Game:
    def __init__(self, id):

        # Total de rounds, empates, victorias del jugador 0 y del jugador 1
        self._rounds_played_info = {"total": 0, "ties": 0, "0": 0, "1": 0}
        # Y si fue consultado o no
        self._round_info_was_refreshed = False
        self.gameOver = self.isGameOver()

        # Info de las partidas jugadas
        self._games_played_info = {"total": 0, "0": 0, "1": 0}
        # Y si fue refrescado las stats de las partidas jugadas o nel
        self.games_played_info_was_refreshed = False

        self.p1Went = False
        self.p2Went = False
        self.ready = False
        self.id = id
        self.moves = [None, None]

    def get_player_move(self, p):
        """
        :param p: [0,1]
        :return: Move
        """
        return self.moves[p]

    def play(self, player, move):
        self.moves[player] = move
        if player == 0:
            self.p1Went = True
        else:
            self.p2Went = True

    def connected(self):
        return self.ready

    def bothWent(self):

        return self.p1Went and self.p2Went

    def winner(self):

        p1 = self.moves[0].upper()[0]
        p2 = self.moves[1].upper()[0]

        key = p1 + p2
        keymap = {'PP': -1, 'PR': 0, 'PS': 1, 'RR': -1, 'RS': 0, 'RP': 1, 'SS': -1, 'SP': 0, 'SR': 1, 'NN': -1}

        # A veces el modelo manda None si no escoges
        if p1 == 'N' and p2 != 'N':
            result = 1
        elif p2 == 'N' and p1 != 'N':
            result = 0
        else:
            result = keymap[key]

        return result

    def resetWent(self):
        self.p1Went = False
        self.p2Went = False

    def getRoundsInfo(self):
        return self._rounds_played_info

    def refreshRoundInfo(self):
        round_info = self._rounds_played_info
        winner = self.winner()

        # Checamos si no fue consultado por algún cliente antes,
        # y si sí, hacemos las stats.
        # Como los dos clientes piden el reset, esto para que no haga dos veces los stats.
        if not self._round_info_was_refreshed:
            # Ponemos nuestra bandera en true para avisar que ya fue revisada
            self._round_info_was_refreshed = True
            # Contamos en uno las rondas totales
            round_info["total"] += 1
            if winner == -1:
                round_info["ties"] += 1
            else:
                round_info[str(winner)] += 1


        # Si ya fue consultado pues seteamos de nuevo al valor predeterminado
        else:
            self._round_info_was_refreshed = False

    # Revisa que el juego no haya terminado.
    # Si no hay ganador, retornar falso hasta que haya ganador, de ser así, retorna el ganador.
    def isGameOver(self):
        rounds_info = self._rounds_played_info
        p1 = rounds_info["0"]
        p2 = rounds_info["1"]
        winner = (0 if p1 > 2 else (1 if p2 > 2 else False))

        return winner

    # Para terminar ahora sí el juego y reiniciar los valores necesarios
    # Como los stats de los rounds y así
    def finishGame(self):
        self._rounds_played_info = {}
        self._rounds_played_info = {"total": 0, "ties": 0, "0": 0, "1": 0}
        return None
    # Lo que ocurre cuando el juego acabó, refrescar las stats de los juegos jugados
    def refreshGamesPlayedInfo(self):
        # Comprobación que no se haya refrescado dos veces
        # if not self.games_played_info_was_refreshed:
        self.games_played_info_was_refreshed = True
        games_info = self._games_played_info
        games_info["total"] += 1
        winner = self.isGameOver()
        games_info[str(winner)] += 1


        return self._games_played_info

    def getGamesPlayedInfo(self):
        return self._games_played_info
