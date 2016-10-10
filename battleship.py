# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.phonon import Phonon
import sys
import random

import designShip

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

class Key(QtCore.QObject):

    def __init__(self, soundFile, parent=None):
        super(Key, self).__init__(parent)

        self.soundFile = soundFile

        self.mediaObject = Phonon.MediaObject(self)
        self._audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self._path = Phonon.createPath(self.mediaObject, self._audioOutput)
        self.mediaSource = Phonon.MediaSource(soundFile)
        self.mediaObject.setCurrentSource(self.mediaSource)

    def play(self):
        self.mediaObject.stop()
        self.mediaObject.seek(0)
        self.mediaObject.play()

class BattleShipApp(QtGui.QMainWindow, designShip.Ui_MainWindow):

    _layout = list()
    for j in range(15):
        _layout.append(15 * [0])

    _shipList = list()

    _buttonClicked = list() # list of indices of clicked button -> information for saving/loading

    _destroyedShipsCounter = 0

    _nmbOfHits = [0, 0, 0, 0, 0] # number of times each ship was hit

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
        self._buttonClicked = list()
        for i in range(5):
            self._nmbOfHits[i] = 0
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
        self.msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)

        # definition of error box
        self.errMsg = QtGui.QErrorMessage()
        self.errMsg.setWindowTitle("Error")

        # setup of new game
        self.new_game()

        # click even for each button is the same
        self.buttonGroup.buttonClicked.connect(self.handleButtonClicked)
        self.actionNew_Game.triggered.connect(self.set_new_game)
        self.actionSave_Game.triggered.connect(self.file_save)
        self.actionLoad_Game.triggered.connect(self.file_load)
        self.actionQuit.triggered.connect(QtGui.qApp.quit)  # QtGui.qApp.quit closes main window

    def click_all_buttons(self):
        for button in self.centralwidget.findChildren(QtGui.QAbstractButton):
            if button.isEnabled():
                self.handleButtonClicked(button)
                self._buttonClicked.append(self.buttonGroup.id(button))

    def set_new_game(self):
        for btn_id in self._buttonClicked:
            self.buttonGroup.button(btn_id).setEnabled(True)
            self.buttonGroup.button(btn_id).setStyleSheet(designShip._fromUtf8("")) # reset button background-color
        self.new_game()

    def file_save(self):
        export_dialog = QtGui.QFileDialog()
        export_dialog.setWindowTitle("Save Game")
        export_dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        export_dialog.setNameFilter("SAV files (*.sav)")
        export_dialog.setDefaultSuffix("sav")
        if export_dialog.exec_() == QtGui.QFileDialog.Accepted:
            file = open(export_dialog.selectedFiles()[0], 'w')
            file.write(str(self._layout) + "\n")
            file.write(str(self._shipList) + "\n")
            file.write(str(self._buttonClicked) + "\n")
            file.write(str(self._nmbOfHits) + "\n")
            file.write(str(self._destroyedShipsCounter))
            file.close()

    def file_load(self):
        open_dialog = QtGui.QFileDialog()
        open_dialog.setWindowTitle("Load Game")
        open_dialog.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        open_dialog.setNameFilter("SAV files (*.sav)")
        open_dialog.setDefaultSuffix("sav")
        if open_dialog.exec_() == QtGui.QFileDialog.Accepted:
            try:
                file = open(open_dialog.selectedFiles()[0], "r")
                content = file.readlines()
                try:
                    layout = eval(content[0])
                    shiplist = eval(content[1])
                    buttons = eval(content[2])
                    nmbHits = eval(content[3])
                    counter = eval(content[4])
                    # check if objects are appropriate type
                    if not isinstance(layout, list) or not isinstance(shiplist, list) or not isinstance(buttons, list) or not isinstance(nmbHits, list) or not isinstance(counter, int):
                        self.errMsg.showMessage("Wrong file opened. At least one object is not appropriate type.")
                        self.errMsg.show()
                        return
                    if len(layout) != 15 or len(shiplist) != 5 or len(nmbHits) != 5 or counter < 0 or counter > 5:
                        self.errMsg.showMessage("Wrong file opened. At least one object is out of range.")
                        self.errMsg.show()
                        return
                    for i in range(15):
                        # layout must be 2-dimensional list
                        if not isinstance(layout[i], list):
                            self.errMsg.showMessage("Wrong file opened. Layout list must be 2-dimensional.")
                            self.errMsg.show()
                            return
                        # layout must be 2-dimensional list 15x15
                        if len(layout[i]) != 15:
                            self.errMsg.showMessage("Wrong file opened. Layout list must be 2-dimensional 15 x 15.")
                            self.errMsg.show()
                            return
                        for j in range(15):
                            # layout must contain 0 or 1
                            if layout[i][j] != 0 and layout[i][j] != 1:
                                self.errMsg.showMessage("Wrong file opened. Layout values must be between 0 or 1.")
                                self.errMsg.show()
                                return
                    for i in range(5):
                        # shiplist must contain objects of type Ship
                        if not isinstance(shiplist[i], Ship):
                            self.errMsg.showMessage("Wrong file opened. Object of type Ship cannot be found.")
                            self.errMsg.show()
                            return
                    for i in range(len(buttons)):
                        # buttonlist must contain indices between -226 and -2
                        if buttons[i] < -226 or buttons[i] > -2:
                            self.errMsg.showMessage("Wrong file opened. Button index is out of range.")
                            self.errMsg.show()
                            return
                    # number of hits must be integers between 0 and 5
                    for i in range(5):
                        if not isinstance(nmbHits[i], int):
                            self.errMsg.showMessage("Wrong file opened. Number of hits must be integers between 0 and 5.")
                            self.errMsg.show()
                            return
                        if nmbHits[i] < 0 or nmbHits[i] > 5:
                            self.errMsg.showMessage("Wrong file opened. Number of hits must be integers between 0 and 5.")
                            self.errMsg.show()
                            return
                    # first we need to reset buttons that were clicked in current game
                    for btn_id in self._buttonClicked:
                        self.buttonGroup.button(btn_id).setEnabled(True)
                        self.buttonGroup.button(btn_id).setStyleSheet(designShip._fromUtf8(""))
                    self._layout = layout
                    self._shipList = shiplist
                    self._buttonClicked = buttons
                    self._nmbOfHits = nmbHits
                    for i in range(5):
                        self._shipList[i]._hit = self._nmbOfHits[i]
                    self._destroyedShipsCounter = counter
                    for btn_id in self._buttonClicked:
                        self.buttonGroup.button(btn_id).setEnabled(False)
                        btn_number = btn_id * (-1) - 2
                        if self._layout[btn_number / 15][btn_number % 15] == 1:
                            self.buttonGroup.button(btn_id).setStyleSheet(
                                designShip._fromUtf8("background-color: rgb(0, 85, 0);"))
                        else:
                            self.buttonGroup.button(btn_id).setStyleSheet(
                                designShip._fromUtf8("background-color: rgb(10, 105, 148);"))
                except:
                    self.errMsg.showMessage("Wrong file opened. Cannot evaluate appropriate objects.")
                    self.errMsg.show()
                    return
            except:
                self.errMsg.showMessage("Cannot open selected file.")
                self.errMsg.show()
                return

    def handleButtonClicked(self, button):
        button.setEnabled(False)
        self._buttonClicked.append(self.buttonGroup.id(button))
        btn_number = self.buttonGroup.id(button)*(-1) - 2 # received index from -2 to -226 -> from 0 to 224
        xx = btn_number / 15
        yy = btn_number % 15
        if self._layout[xx][yy] == 1:
            button.setStyleSheet(designShip._fromUtf8("background-color: rgb(0, 85, 0);"))
            for i in range(5):
                if self._shipList[i].is_hit(yy, xx):
                    self._nmbOfHits[i] += 1
                    if self._shipList[i].sink():
                        self._destroyedShipsCounter += 1
                        if self._destroyedShipsCounter == 5:
                            self.msg.setText("Congratulations! You destroyed all ships.")
                            self.msg.setWindowTitle("Hit and sunk!")
                            iconMsg = QtGui.QPixmap("h-bomb.jpg")
                            iconMsg = iconMsg.scaled(100, 100, QtCore.Qt.KeepAspectRatio,
                                                     transformMode = QtCore.Qt.SmoothTransformation)
                            self.msg.setIconPixmap(iconMsg)
                            self.msg.show()
                            Key("explosion.wav", self.msg).play()
                            self.click_all_buttons()
                        else:
                            self.msg.setText("Congratulations! The ship of length " + str(self._shipList[i].l) + " was sunk.")
                            self.msg.setWindowTitle("Hit and sunk!")
                            iconMsg = QtGui.QPixmap("sinking-ship.jpg")
                            iconMsg = iconMsg.scaled(100, 100, QtCore.Qt.KeepAspectRatio,
                                                     transformMode = QtCore.Qt.SmoothTransformation)
                            self.msg.setIconPixmap(iconMsg)
                            self.msg.show()
                            Key("ship_sink.mp3", self.msg).play()
                    else:
                        self.msg.setText("You hit the ship.")
                        self.msg.setWindowTitle("Hit!")
                        iconMsg = QtGui.QPixmap("bomb.png")
                        iconMsg = iconMsg.scaled(100, 100, QtCore.Qt.KeepAspectRatio,
                                                 transformMode = QtCore.Qt.SmoothTransformation)
                        self.msg.setIconPixmap(iconMsg)
                        self.msg.show()
                        Key("blast.wav", self.msg).play()
        else:
            button.setStyleSheet(designShip._fromUtf8("background-color: rgb(10, 105, 148);"))

def main():
    app = QtGui.QApplication(sys.argv)
    form = BattleShipApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()