# -*- coding: utf-8 -*-

from PyQt4 import QtGui

import sys

import designShip

import random

class Ship:

    """
    horizontal: True/False
    length: ship length, possible values are 2, 3, 4, 5
    x_coord: x coordinate of board
    y_coord: y coordinate of board
    """
    def __init__(self, length, x_coord, y_coord, horizontal):
        self._hit = 0
        self._length = length
        self._x_coord = x_coord
        self._y_coord = y_coord
        self._horizontal = horizontal

    def getHorizontal(self):
        return self._horizontal

    horizontal = property(fget = getHorizontal)

    def get_x_coord(self):
        return self._x_coord

    x = property(fget = get_x_coord)

    def get_y_coord(self):
        return self._y_coord

    y = property(fget = get_y_coord)

    def get_length(self):
        return self._length

    l = property(fget = get_length)

    def sink(self):
        return self._hit == self._length

    def is_hit(self, x, y):
        if self._horizontal:
            if x >= self._x_coord and x < self._x_coord + self._length and self._y_coord == y:
                self._hit += 1
                return True
        else:
            if y >= self._y_coord and y < self._y_coord + self._length and self._x_coord == x:
                self._hit += 1
                return True
        return False

    def __str__(self):
        if self._horizontal:
            hor = "horizontal"
        else:
            hor = "vertical"
        return "Ship: board at (" + str(self._x_coord) + ", " + str(self._y_coord) + "), length = " + str(self._length) + ", position = " + hor

    def __repr__(self):
        return "Ship(" + str(self._length) + ", " + str(self._x_coord) + ", " + str(self._y_coord) + ", " + str(self._horizontal) + ")"

    """
    Needs for comparing equality of two objects of type Ship
    """
    def __eq__(self, ship_object):
        return self._length == ship_object._length and self._x_coord == ship_object._x_coord and self._y_coord == ship_object._y_coord and self._horizontal == ship_object._horizontal

class BattleShipApp(QtGui.QMainWindow, designShip.Ui_MainWindow):

    _layout = list()
    for j in range(15):
        _layout.append(15 * [0])

    _shipList = list()

    _destroyedShipsCounter = 0

    """
    reset layout for new game
    """
    def set_layout(self):
        for i in range(len(self._shipList)):
            if self._shipList[i].horizontal:
                for j in range(self._shipList[i].l):
                    self._layout[self._shipList[i].y][self._shipList[i].x + j] = 0
            else:
                for j in range(self._shipList[i].l):
                    self._layout[self._shipList[i].y + j][self._shipList[i].x] = 0

    def new_game(self):
        xCoords = range(15)
        yCoords = range(15)
        self.set_layout()
        self._shipList = list()
        self._destroyedShipsCounter = 0

        pos = ["horizontal", "vertical"]

        def randomLocation(length):
            position = random.choice(pos)
            if position == "horizontal":
                rand_x = random.choice(xCoords[:(len(xCoords) - length + 1)])
                rand_y = random.choice(yCoords)

                for i in range(length):
                    if self._layout[rand_y][rand_x + i] == 1: # in this location ship already exists
                        for j in range(rand_x + i - 1, rand_x - 1, -1):
                            self._layout[rand_y][j] = 0
                        randomLocation(length)
                        return # must use to go out from current function
                    else:
                        self._layout[rand_y][rand_x + i] = 1

            else:
                rand_x = random.choice(xCoords)
                rand_y = random.choice(yCoords[:(len(xCoords) - length + 1)])
                for i in range(length):
                    if self._layout[rand_y + i][rand_x] == 1:
                        for j in range(rand_y + i - 1, rand_y - 1, -1):
                            self._layout[j][rand_x] = 0
                        randomLocation(length)
                        return # must use to go out from current function
                    else:
                        self._layout[rand_y + i][rand_x] = 1

            self._shipList.append(Ship(length, rand_x, rand_y, position == "horizontal"))

            xCoords.remove(rand_x) # already chosen
            yCoords.remove(rand_y)

        randomLocation(5)
        randomLocation(4)
        randomLocation(3)
        randomLocation(3)
        randomLocation(2)

    def __init__(self):
        # setup of main window
        super(self.__class__, self).__init__()
        self.setupUi(self)

        # definition of message box
        self.msg = QtGui.QMessageBox()
        self.msg.setIcon(QtGui.QMessageBox.Information)
        self.msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)

        # setup of new game
        self.new_game()

        # click even for each button is the same
        self.buttonGroup = QtGui.QButtonGroup(self)
        for button in self.centralwidget.findChildren(QtGui.QAbstractButton):
            self.buttonGroup.addButton(button)
        self.buttonGroup.buttonClicked.connect(self.handleButtonClicked)
        self.actionClose.triggered.connect(QtGui.qApp.quit) # QtGui.qApp.quit closes main window
        self.actionNew_Game.triggered.connect(self.set_new_game)

    def click_all_buttons(self):
        for button in self.centralwidget.findChildren(QtGui.QAbstractButton):
            if button.isEnabled():
                self.handleButtonClicked(button)

    def set_new_game(self):
        for button in self.centralwidget.findChildren(QtGui.QAbstractButton):
            button.setEnabled(True)
            button.setStyleSheet(designShip._fromUtf8("")) # reset button background-color
        self.new_game()

    def handleButtonClicked(self, button):
        button.setEnabled(False)
        btn_number = self.buttonGroup.id(button)*(-1) - 2 # received index from -2 to -226 -> from 0 to 224
        xx = btn_number / 15
        yy = btn_number % 15
        if self._layout[xx][yy] == 1:
            button.setStyleSheet(designShip._fromUtf8("background-color: rgb(0, 85, 0);"))
            for ship in self._shipList:
                if ship.is_hit(yy, xx):
                    if ship.sink():
                        self._destroyedShipsCounter += 1
                        if self._destroyedShipsCounter == 5:
                            self.msg.setText("Congratulations! You destroyed all ships.")
                            self.msg.setWindowTitle("Hit and sunk!")
                            self.msg.show()
                            self.click_all_buttons()
                        else:
                            self.msg.setText("Congratulations! The ship of length " + str(ship.l) + " was sunk.")
                            self.msg.setWindowTitle("Hit and sunk!")
                            self.msg.show()
                    else:
                        self.msg.setText("You hit the ship.")
                        self.msg.setWindowTitle("Hit!")
                        self.msg.show()
        else:
            button.setStyleSheet(designShip._fromUtf8("background-color: rgb(10, 105, 148);"))

def main():
    app = QtGui.QApplication(sys.argv)
    form = BattleShipApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()