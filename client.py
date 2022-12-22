from PyQt5.Qt import *
import sys
import socket
from threading import Thread


class Game(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tic Tac Toe")
        self.setFixedSize(800, 800)
        self.setObjectName('main')
        self.setStyleSheet('#main {background: rgb(82, 82, 82)}')
        self.main_label = None
        self.role = None
        self.is_my_turn = False
        self.game_field = [['' for k in range(4)] for i in range(4)]
        self.disabled_cells = []
        self.socket = socket.socket()
        self.socket.connect(('localhost', 2000))
        self.UiComponents()

    def UiComponents(self):
        x = 120
        y = 150
        cell_size = 130
        margin = 10
        for row in range(len(self.game_field)):
            for cell in range(len(self.game_field[row])):
                button = QPushButton(self)
                button.setGeometry(x + (cell_size + margin) * cell, y + (cell_size + margin) * row, cell_size, cell_size)
                button.setObjectName('cell')
                button.setStyleSheet('#cell {background: rgb(189, 189, 189);}')
                button.setFont(QFont('Calibri', 56))
                button.setEnabled(False)
                button.clicked.connect(self._make_move)
                self.game_field[row][cell] = button
        self.main_label = QLabel(self)
        self.main_label.setText('Ожидаем второго игрока...')
        self.main_label.setAlignment(Qt.AlignCenter)
        self.main_label.setFont(QFont('Calibri', 18))
        self.main_label.setObjectName('label')
        self.main_label.setStyleSheet('#label {color: #fff}')
        self.main_label.setGeometry(0, 40, self.width(), 50)

    def _append_disabled(self, button: QPushButton):
        self.disabled_cells.append(button)

    def _get_button_coordinates(self, button: QPushButton):
        for i in range(len(self.game_field)):
            try:
                return f"{i}{self.game_field[i].index(button)}"
            except ValueError:
                pass

    def _make_move(self):
        button = self.sender()
        self._append_disabled(button)
        if self.role == 'cross':
            button.setText('x')
        elif self.role == 'zero':
            button.setText('o')
        self._disable_cells()
        coordinates = self._get_button_coordinates(button)
        self.socket.sendall(coordinates.encode('utf-8'))
        self.is_my_turn = False
        self._change_turn()

    def _show_enemy_move(self, coordinates: str):
        button = self.game_field[int(coordinates[0])][int(coordinates[1])]
        self._append_disabled(button)
        if self.role == 'zero':
            button.setText('x')
        elif self.role == 'cross':
            button.setText('o')

    def _enable_cells(self):
        for i in self.game_field:
            for k in i:
                if k not in self.disabled_cells:
                    k.setEnabled(True)

    def _disable_cells(self):
        for i in self.game_field:
            for k in i:
                k.setEnabled(False)

    def _set_text_to_main_label(self, text: str):
        self.main_label.setText(text)

    def _change_turn(self):
        if self.is_my_turn:
            self._set_text_to_main_label('Сейчас ваш ход')
            self._enable_cells()
        else:
            self._set_text_to_main_label('Сейчас ход противника')
            self._disable_cells()

    def _receiver(self):
        while True:
            data = self.socket.recv(1024).decode('utf-8')
            if not data:
                break
            elif data == 'cross':
                self.role = 'cross'
                self.is_my_turn = True
                self._change_turn()
            elif data == 'zero':
                self.role = 'zero'
                self.is_my_turn = False
                self._change_turn()
            elif data == 'win':
                self._disable_cells()
                self._set_text_to_main_label('Вы выиграли')
            elif data == 'lose':
                self._disable_cells()
                self._set_text_to_main_label('Вы проиграли')
            elif data == 'draw':
                self._set_text_to_main_label('Ничья')
            else:
                self._show_enemy_move(data)
                self.is_my_turn = True
                self._change_turn()

    def run(self):
        thread = Thread(target=self._receiver)
        thread.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = Game()
    game.show()
    game.run()
    sys.exit(app.exec())






