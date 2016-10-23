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

    def was_hit(self, x, y):
        if self._horizontal:
            if x >= self._x_coord and x < self._x_coord + self._length and self._y_coord == y:
                return True
        else:
            if y >= self._y_coord and y < self._y_coord + self._length and self._x_coord == x:
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

    _buttonClicked = 225 * [False] # list of indices of clicked button -> information for saving/loading

    _destroyedShipsCounter = 0

    _nmbOfHits = [0, 0, 0, 0, 0] # number of times each ship was hit

    _layoutPlayer = list()
    for j in range(15):
        _layoutPlayer.append(15 * [0])

    _shipListPlayer = 5 * [None]
    _horizontal = True
    _currentLength = 0
    _currentIndex = -2
    _length_3_ind = [2, 3]

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
        for i in range(len(self._shipListPlayer)):
            if isinstance(self._shipListPlayer[i], Ship):
                if self._shipListPlayer[i].horizontal:
                    for j in range(self._shipListPlayer[i].l):
                        self._layoutPlayer[self._shipListPlayer[i].y][self._shipListPlayer[i].x + j] = 0
                else:
                    for j in range(self._shipListPlayer[i].l):
                        self._layoutPlayer[self._shipListPlayer[i].y + j][self._shipListPlayer[i].x] = 0

    def new_game(self):
        xCoords = range(15)
        yCoords = range(15)
        self.set_layout()
        self._shipList = list()
        for i in range(5):
            self._shipListPlayer[i] = None
        for i in range(225):
            if self._buttonClicked[i]:
                self._buttonClicked[i] = False
            if self._buttonClickedComputer[i]:
                self._buttonClickedComputer[i] = False
        for i in range(5):
            self._nmbOfHits[i] = 0
            self._nmbOfHitsComputer[i] = 0
        self._destroyedShipsCounter = 0
        self._destroyedShipsCounterComp = 0

        pos = ["horizontal", "vertical"]

        self._length_3_ind = [2, 3]
        self._horizontal = True
        self._currentLength = 0
        self._currentIndex = -2

        self._allPositions = range(-226, -1)
        self._prefferedPositions = list()
        self._shipHit = False
        self._indexHit = None
        # _indexPrevious = None
        self._shipOrientation = 0  # 0 - we don't know, 1 - horizontal, 2 - vertical
        self._destroyedShipsCounterComp = 0
        self._shipIndexWrong = list()
        self._curLen = 0  # current length of ship; if current length of ship is larger than the sinking ship then 2 ships are there

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

        # setup of new game
        self.new_game()

        # click even for each button is the same
        self.buttonGroup.buttonClicked.connect(self.handleButtonClicked)
        self.actionNew_Game.triggered.connect(self.set_new_game)
        self.actionSave_Game.triggered.connect(self.file_save)
        self.actionLoad_Game.triggered.connect(self.file_load)
        self.actionQuit.triggered.connect(QtGui.qApp.quit)  # QtGui.qApp.quit closes main window

        self.radioButton.toggled.connect(lambda: self.choosePosition(5))
        self.radioButton_2.toggled.connect(lambda: self.choosePosition(4))
        self.radioButton_3.toggled.connect(lambda: self.choosePosition(3))
        self.radioButton_4.toggled.connect(lambda: self.choosePosition(3))
        self.radioButton_5.toggled.connect(lambda: self.choosePosition(2))
        self.pushButton.clicked.connect(self.enableButton)

    def enableButton(self):
        for btn_id in range(-226, -1):
            self.buttonGroup.button(btn_id).setEnabled(True)
        self.actionSave_Game.setEnabled(True)
        self.pushButton.setEnabled(False)

    def keyPressEvent(self, event):
        if self._currentLength != 0:
            if event.key() == QtCore.Qt.Key_H:
                # if ship is not too close to right and bottom border
                if (self._currentIndex * (-1) - 2) % 15 < 16 - self._currentLength and self._currentIndex >= -241 + self._currentLength * 15:
                    if self._horizontal:
                        for i in range(self._currentLength):
                            xx = (self._currentIndex - i) * (-1) - 2
                            if self._layoutPlayer[xx / 15][xx % 15] == 0:
                                self.buttonGroupPlayer.button(self._currentIndex - i).setStyleSheet(designShip._fromUtf8(""))
                            else:
                                self.buttonGroupPlayer.button(self._currentIndex - i).setStyleSheet(designShip._fromUtf8("background-color: rgb(112, 128, 144);"))
                        self._horizontal = False
                        for i in range(self._currentLength):
                            self.buttonGroupPlayer.button(self._currentIndex - i * 15).setStyleSheet(designShip._fromUtf8("background-color: rgba(178, 34, 34, 100);"))
                    else:
                        for i in range(self._currentLength):
                            xx = (self._currentIndex - i * 15) * (-1) - 2
                            if self._layoutPlayer[xx / 15][xx % 15] == 0:
                                self.buttonGroupPlayer.button(self._currentIndex - i * 15).setStyleSheet(designShip._fromUtf8(""))
                            else:
                                self.buttonGroupPlayer.button(self._currentIndex - i * 15).setStyleSheet(designShip._fromUtf8("background-color: rgb(112, 128, 144);"))
                        self._horizontal = True
                        for i in range(self._currentLength):
                            self.buttonGroupPlayer.button(self._currentIndex - i).setStyleSheet(designShip._fromUtf8("background-color: rgba(178, 34, 34, 100);"))

                elif (self._currentIndex * (-1) - 2) % 15 >= 16 - self._currentLength and not self._horizontal:
                    for i in range(self._currentLength):
                        xx = (self._currentIndex - i * 15) * (-1) - 2
                        if self._layoutPlayer[xx / 15][xx % 15] == 0:
                            self.buttonGroupPlayer.button(self._currentIndex - i * 15).setStyleSheet(
                                designShip._fromUtf8(""))
                        else:
                            self.buttonGroupPlayer.button(self._currentIndex - i * 15).setStyleSheet(
                                designShip._fromUtf8("background-color: rgb(112, 128, 144);"))
                    self._horizontal = True
                    if self._currentIndex % 15 != 14: # if not at the right border
                        diff = self._currentIndex - 15 * (self._currentIndex // 15 - 1) - 14
                        self._currentIndex -= diff
                    self._currentIndex += (self._currentLength - 1)
                    for i in range(self._currentLength):
                        self.buttonGroupPlayer.button(self._currentIndex - i).setStyleSheet(designShip._fromUtf8("background-color: rgba(178, 34, 34, 100);"))

                elif self._currentIndex < -241 + self._currentLength * 15 and self._horizontal:
                    for i in range(self._currentLength):
                        xx = (self._currentIndex - i) * (-1) - 2
                        if self._layoutPlayer[xx / 15][xx % 15] == 0:
                            self.buttonGroupPlayer.button(self._currentIndex - i).setStyleSheet(designShip._fromUtf8(""))
                        else:
                            self.buttonGroupPlayer.button(self._currentIndex - i).setStyleSheet(
                                designShip._fromUtf8("background-color: rgb(112, 128, 144);"))
                    self._horizontal = False
                    # 15 * length - 227 = row index
                    row_index = 15 * self._currentLength - 227
                    if self._currentIndex % 15 == 14:
                        self._currentIndex = row_index - 14
                    else:
                        self._currentIndex = row_index + self._currentIndex % 15 - 13
                    for i in range(self._currentLength):
                        self.buttonGroupPlayer.button(self._currentIndex - i * 15).setStyleSheet(designShip._fromUtf8("background-color: rgba(178, 34, 34, 100);"))

            elif event.key() == QtCore.Qt.Key_D:
                if self._horizontal:
                    if (self._currentIndex * (-1) - 2) % 15 < 14 - self._currentLength + 1:
                        xx = self._currentIndex * (-1) - 2
                        if self._layoutPlayer[xx / 15][xx % 15] == 0:
                            self.buttonGroupPlayer.button(self._currentIndex).setStyleSheet(designShip._fromUtf8(""))
                        else:
                            self.buttonGroupPlayer.button(self._currentIndex).setStyleSheet(designShip._fromUtf8("background-color: rgb(112, 128, 144);"))
                        self._currentIndex -= 1
                        self.buttonGroupPlayer.button(self._currentIndex - self._currentLength + 1).setStyleSheet(designShip._fromUtf8("background-color: rgba(178, 34, 34, 100);"))
                else:
                    if self._currentIndex % 15 < 14:
                        for i in range(self._currentLength):
                            xx = (self._currentIndex - i * 15) * (-1) - 2
                            if self._layoutPlayer[xx / 15][xx % 15] == 0:
                                self.buttonGroupPlayer.button(self._currentIndex - i * 15).setStyleSheet(designShip._fromUtf8(""))
                            else:
                                self.buttonGroupPlayer.button(self._currentIndex - i * 15).setStyleSheet(designShip._fromUtf8("background-color: rgb(112, 128, 144);"))
                        self._currentIndex -= 1
                        for i in range(self._currentLength):
                            self.buttonGroupPlayer.button(self._currentIndex - i * 15).setStyleSheet(designShip._fromUtf8("background-color: rgba(178, 34, 34, 100);"))

            elif event.key() == QtCore.Qt.Key_A:
                if (self._currentIndex * (-1) - 2) % 15 > 0:
                    if self._horizontal:
                        xx = (self._currentIndex - self._currentLength + 1) * (-1) - 2
                        if self._layoutPlayer[xx / 15][xx % 15] == 0:
                            self.buttonGroupPlayer.button(self._currentIndex - self._currentLength + 1).setStyleSheet(designShip._fromUtf8(""))
                        else:
                            self.buttonGroupPlayer.button(self._currentIndex - self._currentLength + 1).setStyleSheet(designShip._fromUtf8("background-color: rgb(112, 128, 144);"))
                        self._currentIndex += 1
                        self.buttonGroupPlayer.button(self._currentIndex).setStyleSheet(designShip._fromUtf8("background-color: rgba(178, 34, 34, 100);"))
                    else:
                        for i in range(self._currentLength):
                            xx = (self._currentIndex - i * 15) * (-1) - 2
                            if self._layoutPlayer[xx / 15][xx % 15] == 0:
                                self.buttonGroupPlayer.button(self._currentIndex - i * 15).setStyleSheet(designShip._fromUtf8(""))
                            else:
                                self.buttonGroupPlayer.button(self._currentIndex - i * 15).setStyleSheet(designShip._fromUtf8("background-color: rgb(112, 128, 144);"))
                        self._currentIndex += 1
                        for i in range(self._currentLength):
                            self.buttonGroupPlayer.button(self._currentIndex - i * 15).setStyleSheet(designShip._fromUtf8("background-color: rgba(178, 34, 34, 100);"))

            elif event.key() == QtCore.Qt.Key_S:
                if self._horizontal:
                    if self._currentIndex > -212:  # -212 is first index in the last row
                        for i in range(self._currentLength):
                            xx = (self._currentIndex - i) * (-1) - 2
                            if self._layoutPlayer[xx / 15][xx % 15] == 0:
                                self.buttonGroupPlayer.button(self._currentIndex - i).setStyleSheet(designShip._fromUtf8(""))
                            else:
                                self.buttonGroupPlayer.button(self._currentIndex - i).setStyleSheet(designShip._fromUtf8("background-color: rgb(112, 128, 144);"))
                        self._currentIndex -= 15
                        for i in range(self._currentLength):
                            self.buttonGroupPlayer.button(self._currentIndex - i).setStyleSheet(designShip._fromUtf8("background-color: rgba(178, 34, 34, 100);"))
                else:
                    if self._currentIndex >= -226 + self._currentLength * 15:
                        xx = self._currentIndex * (-1) - 2
                        if self._layoutPlayer[xx / 15][xx % 15] == 0:
                            self.buttonGroupPlayer.button(self._currentIndex).setStyleSheet(designShip._fromUtf8(""))
                        else:
                            self.buttonGroupPlayer.button(self._currentIndex).setStyleSheet(designShip._fromUtf8("background-color: rgb(112, 128, 144);"))
                        self._currentIndex -= 15
                        self.buttonGroupPlayer.button(self._currentIndex - (self._currentLength - 1) * 15).setStyleSheet(designShip._fromUtf8("background-color: rgba(178, 34, 34, 100);"))

            elif event.key() == QtCore.Qt.Key_W:
                if self._currentIndex < -16:
                    if self._horizontal:
                        for i in range(self._currentLength):
                            xx = (self._currentIndex - i) * (-1) - 2
                            if self._layoutPlayer[xx / 15][xx % 15] == 0:
                                self.buttonGroupPlayer.button(self._currentIndex - i).setStyleSheet(designShip._fromUtf8(""))
                            else:
                                self.buttonGroupPlayer.button(self._currentIndex - i).setStyleSheet(designShip._fromUtf8("background-color: rgb(112, 128, 144);"))
                        self._currentIndex += 15
                        for i in range(self._currentLength):
                            self.buttonGroupPlayer.button(self._currentIndex - i).setStyleSheet(designShip._fromUtf8("background-color: rgba(178, 34, 34, 100);"))
                    else:
                        xx = (self._currentIndex - (self._currentLength - 1) * 15) * (-1) - 2
                        if self._layoutPlayer[xx / 15][xx % 15] == 0:
                            self.buttonGroupPlayer.button(self._currentIndex - (self._currentLength - 1) * 15).setStyleSheet(designShip._fromUtf8(""))
                        else:
                            self.buttonGroupPlayer.button(self._currentIndex - (self._currentLength - 1) * 15).setStyleSheet(designShip._fromUtf8("background-color: rgb(112, 128, 144);"))
                        self._currentIndex += 15
                        self.buttonGroupPlayer.button(self._currentIndex).setStyleSheet(designShip._fromUtf8("background-color: rgba(178, 34, 34, 100);"))

            elif event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
                for i in range(self._currentLength):
                    if self._horizontal:
                        xx = (self._currentIndex - i) * (-1) - 2
                        # don't let player to put new ship where another ship already exists
                        if self._layoutPlayer[xx / 15][xx % 15] == 1:
                            QtGui.QApplication.beep() # beep sound
                            return
                    else:
                        xx = (self._currentIndex - i * 15) * (-1) - 2
                        if self._layoutPlayer[xx / 15][xx % 15] == 1:
                            QtGui.QApplication.beep() # beep sound
                            return

                for i in range(self._currentLength):
                    if self._horizontal:
                        xx = (self._currentIndex - i) * (-1) - 2
                        self._layoutPlayer[xx / 15][xx % 15] = 1
                        self.buttonGroupPlayer.button(self._currentIndex - i).setStyleSheet(designShip._fromUtf8("background-color: rgb(112, 128, 144);"))
                    else:
                        xx = (self._currentIndex - i * 15) * (-1) - 2
                        self._layoutPlayer[xx / 15][xx % 15] = 1
                        self.buttonGroupPlayer.button(self._currentIndex - i * 15).setStyleSheet(designShip._fromUtf8("background-color: rgb(112, 128, 144);"))
                xx = self._currentIndex * (-1) - 2
                if self._currentLength > 3:
                    self._shipListPlayer[-self._currentLength + 5] = Ship(self._currentLength, xx % 15, xx / 15, self._horizontal)
                elif self._currentLength == 3:
                    if self._length_3_ind[0] == 2:
                        self._shipListPlayer[2] = Ship(self._currentLength, xx % 15, xx / 15, self._horizontal)
                        self._length_3_ind.remove(2)
                    else:
                        self._shipListPlayer[3] = Ship(self._currentLength, xx % 15, xx / 15, self._horizontal)
                else:
                    self._shipListPlayer[4] = Ship(self._currentLength, xx % 15, xx / 15, self._horizontal)
                if self.radioButton.isChecked():
                    self.radioButton.setEnabled(False)
                    self.radioButton.setChecked(False)
                    if self.radioButton_2.isEnabled():
                        self.radioButton_2.setChecked(True)
                        self._currentLength = 4
                    elif self.radioButton_3.isEnabled():
                        self.radioButton_3.setChecked(True)
                        self._currentLength = 3
                    elif self.radioButton_4.isEnabled():
                        self.radioButton_4.setChecked(True)
                        self._currentLength = 3
                    elif self.radioButton_5.isEnabled():
                        self.radioButton_5.setChecked(True)
                        self._currentLength = 2
                    else:
                        self._currentLength = 0
                        self.pushButton.setEnabled(True)
                elif self.radioButton_2.isChecked():
                    self.radioButton_2.setEnabled(False)
                    self.radioButton_2.setChecked(False)
                    if self.radioButton.isEnabled():
                        self.radioButton.setChecked(True)
                        self._currentLength = 5
                    elif self.radioButton_3.isEnabled():
                        self.radioButton_3.setChecked(True)
                        self._currentLength = 3
                    elif self.radioButton_4.isEnabled():
                        self.radioButton_4.setChecked(True)
                        self._currentLength = 3
                    elif self.radioButton_5.isEnabled():
                        self.radioButton_5.setChecked(True)
                        self._currentLength = 2
                    else:
                        self._currentLength = 0
                        self.pushButton.setEnabled(True)
                elif self.radioButton_3.isChecked():
                    self.radioButton_3.setEnabled(False)
                    self.radioButton_3.setChecked(False)
                    if self.radioButton.isEnabled():
                        self.radioButton.setChecked(True)
                        self._currentLength = 5
                    elif self.radioButton_2.isEnabled():
                        self.radioButton_2.setChecked(True)
                        self._currentLength = 4
                    elif self.radioButton_4.isEnabled():
                        self.radioButton_4.setChecked(True)
                        self._currentLength = 3
                    elif self.radioButton_5.isEnabled():
                        self.radioButton_5.setChecked(True)
                        self._currentLength = 2
                    else:
                        self._currentLength = 0
                        self.pushButton.setEnabled(True)
                elif self.radioButton_4.isChecked():
                    self.radioButton_4.setEnabled(False)
                    self.radioButton_4.setChecked(False)
                    if self.radioButton.isEnabled():
                        self.radioButton.setChecked(True)
                        self._currentLength = 5
                    elif self.radioButton_2.isEnabled():
                        self.radioButton_2.setChecked(True)
                        self._currentLength = 4
                    elif self.radioButton_3.isEnabled():
                        self.radioButton_3.setChecked(True)
                        self._currentLength = 3
                    elif self.radioButton_5.isEnabled():
                        self.radioButton_5.setChecked(True)
                        self._currentLength = 2
                    else:
                        self._currentLength = 0
                        self.pushButton.setEnabled(True)
                elif self.radioButton_5.isChecked():
                    self.radioButton_5.setEnabled(False)
                    self.radioButton_5.setChecked(False)
                    if self.radioButton.isEnabled():
                        self.radioButton.setChecked(True)
                        self._currentLength = 5
                    elif self.radioButton_2.isEnabled():
                        self.radioButton_2.setChecked(True)
                        self._currentLength = 4
                    elif self.radioButton_3.isEnabled():
                        self.radioButton_3.setChecked(True)
                        self._currentLength = 3
                    elif self.radioButton_4.isEnabled():
                        self.radioButton_4.setChecked(True)
                        self._currentLength = 3
                    else:
                        self._currentLength = 0
                        self.pushButton.setEnabled(True)

    def choosePosition(self, length):
        self._currentIndex = -2
        for i in range(225):
            if self._layoutPlayer[i / 15][i % 15] == 0:
                self.buttonGroupPlayer.button(i * (-1) - 2).setStyleSheet(designShip._fromUtf8(""))
            else:
                self.buttonGroupPlayer.button(i * (-1) - 2).setStyleSheet(designShip._fromUtf8("background-color: rgb(112, 128, 144);"))
        self._currentLength = length
        if self._horizontal:
            for i in range(length):
                self.buttonGroupPlayer.button(self._currentIndex - i).setStyleSheet(designShip._fromUtf8("background-color: rgba(178, 34, 34, 100);"))
        else:
            for i in range(length):
                self.buttonGroupPlayer.button(self._currentIndex - i * 15).setStyleSheet(designShip._fromUtf8("background-color: rgba(178, 34, 34, 100);"))

    def click_all_buttons(self):
        for btn_id in range(-226, -1):
            xx = btn_id * (-1) - 2
            if not self._buttonClickedComputer[xx]:
                if self._layoutPlayer[xx / 15][xx % 15] == 0:
                    self.buttonGroupPlayer.button(btn_id).setStyleSheet(designShip._fromUtf8("background-color: rgb(10, 105, 148);"))
                else:
                    self.buttonGroupPlayer.button(btn_id).setStyleSheet(designShip._fromUtf8("background-color: rgb(255, 50, 50);"))
            if not self._buttonClicked[xx]:
                self.buttonGroup.button(btn_id).setEnabled(False)
                if self._layout[xx / 15][xx % 15] == 0:
                    self.buttonGroup.button(btn_id).setStyleSheet(designShip._fromUtf8("background-color: rgb(10, 105, 148);"))
                else:
                    self.buttonGroup.button(btn_id).setStyleSheet(designShip._fromUtf8("background-color: rgb(0, 85, 0);"))

    def set_new_game(self):
        for i in range(-226, -1):
            self.buttonGroup.button(i).setEnabled(False)
            self.buttonGroup.button(i).setStyleSheet(designShip._fromUtf8("")) # reset button background-color
            self.buttonGroupPlayer.button(i).setStyleSheet(designShip._fromUtf8(""))  # reset button background-color
        self.pushButton.setEnabled(False)
        self.radioButton.setEnabled(True)
        self.radioButton_2.setEnabled(True)
        self.radioButton_3.setEnabled(True)
        self.radioButton_4.setEnabled(True)
        self.radioButton_5.setEnabled(True)
        self.actionSave_Game.setEnabled(False)
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
            file.write(str(self._destroyedShipsCounter) + "\n")
            file.write(str(self._layoutPlayer) + "\n")
            file.write(str(self._shipListPlayer) + "\n")
            file.write(str(self._allPositions) + "\n")
            file.write(str(self._prefferedPositions) + "\n")
            file.write(str(self._shipHit) + "\n")
            file.write(str(self._indexHit) + "\n")
            file.write(str(self._shipOrientation) + "\n")
            file.write(str(self._destroyedShipsCounterComp) + "\n")
            file.write(str(self._nmbOfHitsComputer) + "\n")
            file.write(str(self._buttonClickedComputer) + "\n")
            file.write(str(self._shipIndexWrong) + "\n")
            file.write(str(self._curLen))
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
                file.close()
                try:
                    layout = eval(content[0])
                    shiplist = eval(content[1])
                    buttons = eval(content[2])
                    nmbHits = eval(content[3])
                    counter = eval(content[4])
                    layoutPlayer = eval(content[5])
                    shiplistPlayer = eval(content[6])
                    allPositions = eval(content[7])
                    prefferedPos = eval(content[8])
                    shipHit = eval(content[9])
                    indexHit = eval(content[10])
                    shipOrient = eval(content[11])
                    counterComp = eval(content[12])
                    nmbHitsComp = eval(content[13])
                    buttonsComp = eval(content[14])
                    shipWrong = eval(content[15])
                    curLen = eval(content[16])
                    # check if objects are appropriate type
                    if not isinstance(layout, list) or not isinstance(shiplist, list) or not isinstance(buttons, list) or not isinstance(nmbHits, list) or not isinstance(counter, int) or not isinstance(allPositions, list)\
                            or not isinstance(layoutPlayer, list) or not isinstance(shiplistPlayer, list) or not isinstance(prefferedPos, list) or not (isinstance(indexHit, int) or isinstance(indexHit, type(None)))\
                            or not isinstance(shipHit, bool) or not isinstance(shipOrient, int) or not isinstance(counterComp, int) or not isinstance(nmbHitsComp, list) or not isinstance(buttonsComp, list)\
                            or not isinstance(shipWrong, list) or not isinstance(curLen, int):
                        self.msg.setIcon(QtGui.QMessageBox.Critical)
                        self.msg.setText("Wrong file opened. At least one object is not appropriate type.")
                        self.msg.setWindowTitle("Error")
                        self.msg.exec_()
                        return
                    if len(layout) != 15 or len(shiplist) != 5 or len(nmbHits) != 5 or counter < 0 or counter > 5 or len(layoutPlayer) != 15 or len(shiplistPlayer) != 5 or shipOrient not in [0, 1, 2] or counterComp < 0 or counterComp > 5 or len(nmbHitsComp) != 5 or len(buttons) != 225 or len(buttonsComp) != 225 or curLen < 0 or curLen > 5:
                        self.msg.setIcon(QtGui.QMessageBox.Critical)
                        self.msg.setText("Wrong file opened. At least one object is out of range.")
                        self.msg.setWindowTitle("Error")
                        self.msg.exec_()
                        return
                    for i in range(15):
                        # layout must be 2-dimensional list
                        if not isinstance(layout[i], list) or not isinstance(layoutPlayer[i], list):
                            self.msg.setIcon(QtGui.QMessageBox.Critical)
                            self.msg.setText("Wrong file opened. Layout list must be 2-dimensional.")
                            self.msg.setWindowTitle("Error")
                            self.msg.exec_()
                            return
                        # layout must be 2-dimensional list 15x15
                        if len(layout[i]) != 15 or len(layoutPlayer[i]) != 15:
                            self.msg.setIcon(QtGui.QMessageBox.Critical)
                            self.msg.setText("Wrong file opened. Layout list must be 2-dimensional 15 x 15.")
                            self.msg.setWindowTitle("Error")
                            self.msg.exec_()
                            return
                        for j in range(15):
                            # layout must contain 0 or 1
                            if (layout[i][j] != 0 and layout[i][j] != 1) or (layoutPlayer[i][j] != 0 and layoutPlayer[i][j] != 1):
                                self.msg.setIcon(QtGui.QMessageBox.Critical)
                                self.msg.setText("Wrong file opened. Layout values must be between 0 or 1.")
                                self.msg.setWindowTitle("Error")
                                self.msg.exec_()
                                return
                    for i in range(5):
                        # shiplist must contain objects of type Ship
                        if not isinstance(shiplist[i], Ship) or not (isinstance(shiplistPlayer[i], Ship) or isinstance(shiplistPlayer[i], type(None))):
                            self.msg.setIcon(QtGui.QMessageBox.Critical)
                            self.msg.setText("Wrong file opened. Object of type Ship cannot be found.")
                            self.msg.setWindowTitle("Error")
                            self.msg.exec_()
                            return
                    for i in range(len(buttons)):
                        # buttonlist must contain indices between -226 and -2
                        if not isinstance(buttons[i], bool) or not isinstance(buttonsComp[i], bool):
                            self.msg.setIcon(QtGui.QMessageBox.Critical)
                            self.msg.setText("Wrong file opened. Objects in button list must be of type bool.")
                            self.msg.setWindowTitle("Error")
                            self.msg.exec_()
                            return
                    # number of hits must be integers between 0 and 5
                    for i in range(5):
                        if not isinstance(nmbHits[i], int) or not isinstance(nmbHitsComp[i], int):
                            self.msg.setIcon(QtGui.QMessageBox.Critical)
                            self.msg.setText("Wrong file opened. Number of hits must be integers between 0 and 5.")
                            self.msg.setWindowTitle("Error")
                            self.msg.exec_()
                            return
                        if nmbHits[i] < 0 or nmbHits[i] > shiplist[i].l or nmbHitsComp[i] < 0 or nmbHitsComp[i] > shiplistPlayer[i].l:
                            self.msg.setIcon(QtGui.QMessageBox.Critical)
                            self.msg.setText("Wrong file opened. Number of hits must be integers between 0 and 5.")
                            self.msg.setWindowTitle("Error")
                            self.msg.exec_()
                            return
                    for i in range(len(allPositions)):
                        if not isinstance(allPositions[i], int) or (allPositions[i] < -226 or allPositions[i] > -2):
                            self.msg.setIcon(QtGui.QMessageBox.Critical)
                            self.msg.setText("Wrong file opened. Position indices must be integers between -226 and -2.")
                            self.msg.setWindowTitle("Error")
                            self.msg.exec_()
                            return
                    for i in range(len(prefferedPos)):
                        if not isinstance(prefferedPos[i], int) or (prefferedPos[i] < -226 or prefferedPos[i] > -2):
                            self.msg.setIcon(QtGui.QMessageBox.Critical)
                            self.msg.setText("Wrong file opened. Preffered position indices must be integers between -226 and -2.")
                            self.msg.setWindowTitle("Error")
                            self.msg.exec_()
                            return
                    for i in range(len(shipWrong)):
                        if not isinstance(shipWrong[i], int) or (shipWrong[i] < -226 or shipWrong[i] > -2):
                            self.msg.setIcon(QtGui.QMessageBox.Critical)
                            self.msg.setText("Wrong file opened. Wrong position indices must be integers between -226 and -2.")
                            self.msg.setWindowTitle("Error")
                            self.msg.exec_()
                            return
                    if indexHit != None:
                        if indexHit < -226 or indexHit > -2:
                            self.msg.setIcon(QtGui.QMessageBox.Critical)
                            self.msg.setText("Wrong file opened. Hit index must be integer between -226 and -2.")
                            self.msg.setWindowTitle("Error")
                            self.msg.exec_()
                            return
                    # first we need to reset buttons
                    for i in range(-226, -1):
                        self.buttonGroup.button(i).setEnabled(True)
                        self.buttonGroup.button(i).setStyleSheet(designShip._fromUtf8(""))
                        self.buttonGroupPlayer.button(i).setStyleSheet(designShip._fromUtf8(""))
                    self._layout = layout
                    self._shipList = shiplist
                    self._buttonClicked = buttons
                    self._nmbOfHits = nmbHits
                    self._layoutPlayer = layoutPlayer
                    self._shipListPlayer = shiplistPlayer
                    self._buttonClickedComputer = buttonsComp
                    self._nmbOfHitsComputer = nmbHitsComp
                    for i in range(5):
                        self._shipList[i]._hit = self._nmbOfHits[i]
                        self._shipListPlayer[i]._hit = self._nmbOfHitsComputer[i]
                    self._destroyedShipsCounter = counter
                    self._destroyedShipsCounterComp = counterComp
                    self._allPositions = allPositions
                    self._prefferedPositions = prefferedPos
                    self._shipHit = shipHit
                    self._indexHit = indexHit
                    self._shipOrientation = shipOrient
                    self._shipIndexWrong = shipWrong
                    self._curLen = curLen
                    for i in range(-226, -1):
                        btn_number = i * (-1) - 2
                        if self._buttonClicked[i * (-1) - 2]:
                            self.buttonGroup.button(i).setEnabled(False)
                            if self._layout[btn_number / 15][btn_number % 15] == 1:
                                self.buttonGroup.button(i).setStyleSheet(
                                    designShip._fromUtf8("background-color: rgb(0, 85, 0);"))
                            else:
                                self.buttonGroup.button(i).setStyleSheet(
                                    designShip._fromUtf8("background-color: rgb(10, 105, 148);"))
                        else:
                            self.buttonGroup.button(i).setEnabled(True)
                        if self._buttonClickedComputer[i * (-1) - 2]:
                            if self._layoutPlayer[btn_number / 15][btn_number % 15] == 1:
                                self.buttonGroupPlayer.button(i).setStyleSheet(designShip._fromUtf8("background-color: rgb(255, 50, 50);"))
                            else:
                                self.buttonGroupPlayer.button(i).setStyleSheet(designShip._fromUtf8("background-color: rgb(10, 105, 148);"))
                        else:
                            if self._layoutPlayer[btn_number / 15][btn_number % 15] == 1:
                                self.buttonGroupPlayer.button(i).setStyleSheet(designShip._fromUtf8("background-color: rgb(112, 128, 144);"))
                    self.pushButton.setEnabled(False)
                    self.radioButton.setEnabled(False)
                    self.radioButton_2.setEnabled(False)
                    self.radioButton_3.setEnabled(False)
                    self.radioButton_4.setEnabled(False)
                    self.radioButton_5.setEnabled(False)
                    self.actionSave_Game.setEnabled(True)
                except:
                    self.msg.setIcon(QtGui.QMessageBox.Critical)
                    self.msg.setText("Wrong file opened. Cannot evaluate appropriate objects.")
                    self.msg.setWindowTitle("Error")
                    self.msg.exec_()
                    return
            except:
                self.msg.setIcon(QtGui.QMessageBox.Critical)
                self.msg.setText("Cannot open selected file.")
                self.msg.setWindowTitle("Error")
                self.msg.exec_()
                return

    def showMessageBox(self, text, title, picturePath, soundPath):
        self.msg.setText(text)
        self.msg.setWindowTitle(title)
        iconMsg = QtGui.QPixmap(picturePath)
        iconMsg = iconMsg.scaled(100, 100, QtCore.Qt.KeepAspectRatio,
                                 transformMode=QtCore.Qt.SmoothTransformation)
        self.msg.setIconPixmap(iconMsg)
        Key(soundPath, self.msg).play()

    _allPositions = range(-226, -1)
    _prefferedPositions = list()
    _shipHit = False
    _indexHit = None
    _shipOrientation = 0 # 0 - we don't know, 1 - horizontal, 2 - vertical
    _destroyedShipsCounterComp = 0
    _nmbOfHitsComputer = [0, 0, 0, 0, 0]
    _buttonClickedComputer = 225 * [False] # list of button indices for computer -> important information for save/load game
    _shipIndexWrong = list()
    _curLen = 0 # current length of ship; if current length of ship is larger than the sinking ship then 2 ships are there

    def computerTurn(self):
        # missed in previous round and ship was not hit
        if not self._shipHit:
            pos = random.choice(self._allPositions)
            self._allPositions.remove(pos)
            self._buttonClickedComputer[pos * (-1) - 2] = True
            xx = pos * (-1) - 2
            # missed in this round
            if self._layoutPlayer[xx / 15][xx % 15] == 0:
                self.buttonGroupPlayer.button(pos).setStyleSheet(designShip._fromUtf8("background-color: rgb(10, 105, 148);"))
            # hit in this round
            else:
                self.buttonGroupPlayer.button(pos).setStyleSheet(designShip._fromUtf8("background-color: rgb(255, 50, 50);"))
                self._shipHit = True
                self._indexHit = pos
                self._curLen += 1
                for i in range(5):
                    if self._shipListPlayer[i].is_hit(xx % 15, xx / 15):
                        self._nmbOfHitsComputer[i] += 1
                        if self._shipListPlayer[i].sink():  # ship had length 2
                            self._destroyedShipsCounterComp += 1
                            for j in self._prefferedPositions:
                                self._allPositions.append(j)
                            self._prefferedPositions = list()
                            if len(self._shipIndexWrong) == 0:
                                if self._curLen > self._shipListPlayer[i].l:
                                    self._shipOrientation = 0
                                    self._curLen = 1
                                    if self._indexHit % 15 != 13 and not self._buttonClickedComputer[(self._indexHit + 1) * (-1) - 2]:
                                        self._prefferedPositions.append(self._indexHit + 1)
                                        self._allPositions.remove(self._indexHit + 1)
                                    if self._indexHit % 15 != 14 and not self._buttonClickedComputer[(self._indexHit - 1) * (-1) - 2]:
                                        self._prefferedPositions.append(self._indexHit - 1)
                                        self._allPositions.remove(self._indexHit - 1)
                                    if self._indexHit < -16:
                                        if not self._buttonClickedComputer[(self._indexHit + 15) * (-1) - 2]:
                                            self._prefferedPositions.append(self._indexHit + 15)
                                            self._allPositions.remove(self._indexHit + 15)
                                    if self._indexHit > -212:
                                        if not self._buttonClickedComputer[(self._indexHit - 15) * (-1) - 2]:
                                            self._prefferedPositions.append(self._indexHit - 15)
                                            self._allPositions.remove(self._indexHit - 15)
                                else:
                                    self._shipHit = False
                                    self._indexHit = None
                                    self._shipOrientation = 0
                                    self._curLen = 0
                            else:
                                self._indexHit = self._shipIndexWrong[0]
                                self._shipIndexWrong.remove(self._indexHit)
                                if self._shipOrientation == 1:
                                    if self._indexHit % 15 != 13 and not self._buttonClickedComputer[(self._indexHit + 1) * (-1) - 2]:
                                        self._prefferedPositions.append(self._indexHit + 1)
                                        self._allPositions.remove(self._indexHit + 1)
                                    if self._indexHit % 15 != 14 and not self._buttonClickedComputer[(self._indexHit - 1) * (-1) - 2]:
                                        self._prefferedPositions.append(self._indexHit - 1)
                                        self._allPositions.remove(self._indexHit - 1)
                                elif self._shipOrientation == 2:
                                    if self._indexHit < -16:
                                        if not self._buttonClickedComputer[(self._indexHit + 15) * (-1) - 2]:
                                            self._prefferedPositions.append(self._indexHit + 15)
                                            self._allPositions.remove(self._indexHit + 15)
                                    if self._indexHit > -212:
                                        if not self._buttonClickedComputer[(self._indexHit - 15) * (-1) - 2]:
                                            self._prefferedPositions.append(self._indexHit - 15)
                                            self._allPositions.remove(self._indexHit - 15)

                            if self._destroyedShipsCounterComp == 5:
                                self.showMessageBox("Sorry. You have lost this game.", "Hit and sunk!", "h-bomb.jpg",
                                                    "explosion.wav")
                                self.click_all_buttons()
                                self.msg.exec_()
                            else:
                                self.showMessageBox("Computer destroyed your ship of length " + str(
                                    self._shipList[i].l) + ".", "Hit and sunk!", "sinking-ship.jpg", "ship_sink.mp3")
                                self.msg.exec_()
                            return
                        else:
                            self.showMessageBox("Watch out! Computer hit one of your ships.", "Hit!", "bomb.png",
                                                "blast.wav")
                            self.msg.exec_()
                        break
                # left is possible location if not at the border and not clicked in the past
                if pos % 15 != 13 and not self._buttonClickedComputer[(pos + 1) * (-1) - 2]:
                    self._prefferedPositions.append(pos + 1)
                    self._allPositions.remove(pos + 1)
                # right is possible location if not at the border and not clicked in the past
                if pos % 15 != 14 and not self._buttonClickedComputer[(pos - 1) * (-1) - 2]:
                    self._prefferedPositions.append(pos - 1)
                    self._allPositions.remove(pos - 1)
                # up is possible
                if pos < -16:
                    if not self._buttonClickedComputer[(pos + 15) * (-1) - 2]:
                        self._prefferedPositions.append(pos + 15)
                        self._allPositions.remove(pos + 15)
                # down is possible
                if pos > -212:
                    if not self._buttonClickedComputer[(pos - 15) * (-1) - 2]:
                        self._prefferedPositions.append(pos - 15)
                        self._allPositions.remove(pos - 15)
        # hit in previous round
        else:
            try:
                pos = random.choice(self._prefferedPositions)
                self._prefferedPositions.remove(pos)
                self._buttonClickedComputer[pos * (-1) - 2] = True
            except:
                if self._shipOrientation == 2: # if computer thinks position is vertical
                    k = 1
                    while True:
                        if self._indexHit + 15 * (k - 1) < -16:
                            if self._buttonClickedComputer[(self._indexHit + 15 * k) * (-1) - 2] and self._layoutPlayer[((self._indexHit + 15 * k) * (-1) - 2) / 15][((self._indexHit + 15 * k) * (-1) - 2) % 15] == 1:
                                for i in range(5):
                                    if self._shipListPlayer[i].was_hit(((self._indexHit + 15 * k) * (-1) - 2) % 15, ((self._indexHit + 15 * k) * (-1) - 2) / 15):
                                        if self._shipListPlayer[i].sink():
                                            break
                                        self._shipIndexWrong.append(self._indexHit + 15 * k)
                                k += 1
                            else:
                                break
                        else:
                            break
                    k = 1
                    while True:
                        if self._indexHit - 15 * (k - 1) > -212:
                            if self._buttonClickedComputer[(self._indexHit - 15 * k) * (-1) - 2] and self._layoutPlayer[((self._indexHit - 15 * k) * (-1) - 2) / 15][((self._indexHit - 15 * k) * (-1) - 2) % 15] == 1:
                                for i in range(5):
                                    if self._shipListPlayer[i].was_hit(((self._indexHit - 15 * k) * (-1) - 2) % 15, ((self._indexHit - 15 * k) * (-1) - 2) / 15):
                                        if self._shipListPlayer[i].sink():
                                            break
                                        self._shipIndexWrong.append(self._indexHit - 15 * k)
                                k += 1
                            else:
                                break
                        else:
                            break
                    if self._indexHit % 15 != 13 and not self._buttonClickedComputer[(self._indexHit + 1) * (-1) - 2]:
                        self._prefferedPositions.append(self._indexHit + 1)
                        self._allPositions.remove(self._indexHit + 1)
                    if self._indexHit % 15 != 14 and not self._buttonClickedComputer[(self._indexHit - 1) * (-1) - 2]:
                        self._prefferedPositions.append(self._indexHit - 1)
                        self._allPositions.remove(self._indexHit - 1)
                    self._shipOrientation = 1
                elif self._shipOrientation == 1: # if computer thinks position is horizontal
                    k = 1
                    while (self._indexHit + k - 1) % 15 != 13 and self._buttonClickedComputer[(self._indexHit + k) * (-1) - 2] and self._layoutPlayer[((self._indexHit + k) * (-1) - 2) / 15][((self._indexHit + k) * (-1) - 2) % 15] == 1:
                        for i in range(5):
                            if self._shipListPlayer[i].was_hit(((self._indexHit + k) * (-1) - 2) % 15, ((self._indexHit + k) * (-1) - 2) / 15):
                                if self._shipListPlayer[i].sink():
                                    break
                                self._shipIndexWrong.append(self._indexHit + k)
                        k += 1
                    k = 1
                    while (self._indexHit - k + 1) % 15 != 14 and self._buttonClickedComputer[(self._indexHit - k) * (-1) - 2] and self._layoutPlayer[((self._indexHit - k) * (-1) - 2) / 15][((self._indexHit - k) * (-1) - 2) % 15] == 1:
                        for i in range(5):
                            if self._shipListPlayer[i].was_hit(((self._indexHit - k) * (-1) - 2) % 15, ((self._indexHit - k) * (-1) - 2) / 15):
                                if self._shipListPlayer[i].sink():
                                    break
                                self._shipIndexWrong.append(self._indexHit - k)
                        k += 1
                    if self._indexHit < -16:
                        if not self._buttonClickedComputer[(self._indexHit + 15) * (-1) - 2]:
                            self._prefferedPositions.append(self._indexHit + 15)
                            self._allPositions.remove(self._indexHit + 15)

                    if self._indexHit > -212:
                        if not self._buttonClickedComputer[(self._indexHit - 15) * (-1) - 2]:
                            self._prefferedPositions.append(self._indexHit - 15)
                            self._allPositions.remove(self._indexHit - 15)
                    self._shipOrientation = 2
                if len(self._prefferedPositions) > 0:
                    pos = random.choice(self._prefferedPositions)
                    self._prefferedPositions.remove(pos)
                    self._buttonClickedComputer[pos * (-1) - 2] = True
                else:
                    self._shipHit = False
                    self._indexHit = None
                    self._shipOrientation = 0
                    self._curLen = 0
                    pos = random.choice(self._allPositions)
                    self._allPositions.remove(pos)
                    self._buttonClickedComputer[pos * (-1) - 2] = True

            xx = pos * (-1) - 2
            # missed in this round
            if self._layoutPlayer[xx / 15][xx % 15] == 0:
                self.buttonGroupPlayer.button(pos).setStyleSheet(designShip._fromUtf8("background-color: rgb(10, 105, 148);"))
            # hit in this round
            else:
                self.buttonGroupPlayer.button(pos).setStyleSheet(designShip._fromUtf8("background-color: rgb(255, 50, 50);"))
                self._shipHit = True
                self._curLen += 1
                # we don't know ship orientation
                if self._shipOrientation == 0:
                    for i in range(5):
                        if self._shipListPlayer[i].is_hit(xx % 15, xx / 15):
                            self._nmbOfHitsComputer[i] += 1
                            if self._shipListPlayer[i].sink(): # ship had length 2
                                self._destroyedShipsCounterComp += 1
                                for j in self._prefferedPositions:
                                    self._allPositions.append(j)
                                self._prefferedPositions = list()
                                if len(self._shipIndexWrong) == 0:
                                    if self._curLen > self._shipListPlayer[i].l:
                                        self._shipOrientation = 0
                                        self._curLen = 1
                                        if self._indexHit % 15 != 13 and not self._buttonClickedComputer[(self._indexHit + 1) * (-1) - 2]:
                                            self._prefferedPositions.append(self._indexHit + 1)
                                            self._allPositions.remove(self._indexHit + 1)
                                        if self._indexHit % 15 != 14 and not self._buttonClickedComputer[(self._indexHit - 1) * (-1) - 2]:
                                            self._prefferedPositions.append(self._indexHit - 1)
                                            self._allPositions.remove(self._indexHit - 1)
                                        if self._indexHit < -16:
                                            if not self._buttonClickedComputer[(self._indexHit + 15) * (-1) - 2]:
                                                self._prefferedPositions.append(self._indexHit + 15)
                                                self._allPositions.remove(self._indexHit + 15)
                                        if self._indexHit > -212:
                                            if not self._buttonClickedComputer[(self._indexHit - 15) * (-1) - 2]:
                                                self._prefferedPositions.append(self._indexHit - 15)
                                                self._allPositions.remove(self._indexHit - 15)
                                    else:
                                        self._shipHit = False
                                        self._indexHit = None
                                        self._shipOrientation = 0
                                        self._curLen = 0
                                else:
                                    self._indexHit = self._shipIndexWrong[0]
                                    self._shipIndexWrong.remove(self._indexHit)
                                    if self._shipOrientation == 1:
                                        if self._indexHit % 15 != 13 and not self._buttonClickedComputer[(self._indexHit + 1) * (-1) - 2]:
                                            self._prefferedPositions.append(self._indexHit + 1)
                                            self._allPositions.remove(self._indexHit + 1)
                                        if self._indexHit % 15 != 14 and not self._buttonClickedComputer[(self._indexHit - 1) * (-1) - 2]:
                                            self._prefferedPositions.append(self._indexHit - 1)
                                            self._allPositions.remove(self._indexHit - 1)
                                    elif self._shipOrientation == 2:
                                        if self._indexHit < -16:
                                            if not self._buttonClickedComputer[(self._indexHit + 15) * (-1) - 2]:
                                                self._prefferedPositions.append(self._indexHit + 15)
                                                self._allPositions.remove(self._indexHit + 15)
                                        if self._indexHit > -212:
                                            if not self._buttonClickedComputer[(self._indexHit - 15) * (-1) - 2]:
                                                self._prefferedPositions.append(self._indexHit - 15)
                                                self._allPositions.remove(self._indexHit - 15)
                                if self._destroyedShipsCounterComp == 5:
                                    self.showMessageBox("Sorry. You have lost this game.", "Hit and sunk!", "h-bomb.jpg", "explosion.wav")
                                    self.click_all_buttons()
                                    self.msg.exec_()
                                else:
                                    self.showMessageBox("Computer destroyed your ship of length " + str(
                                        self._shipList[i].l) + ".", "Hit and sunk!", "sinking-ship.jpg", "ship_sink.mp3")
                                    self.msg.exec_()
                            else:
                                self.showMessageBox("Watch out! Computer hit one of your ships.", "Hit!", "bomb.png", "blast.wav")
                                self.msg.exec_()

                                # if current position is on the left or on the right of the previous position then orientation is horizontal
                                if pos == self._indexHit + 1 or pos == self._indexHit - 1:
                                    self._shipOrientation = 1 # horizontal
                                    if self._indexHit - 15 in self._prefferedPositions:
                                        self._prefferedPositions.remove(self._indexHit - 15)
                                        self._allPositions.append(self._indexHit - 15)
                                    if self._indexHit + 15 in self._prefferedPositions:
                                        self._prefferedPositions.remove(self._indexHit + 15)
                                        self._allPositions.append(self._indexHit + 15)
                                    if pos % 15 != 13 and not self._buttonClickedComputer[(pos + 1) * (-1) - 2]:
                                        self._prefferedPositions.append(pos + 1)
                                        self._allPositions.remove(pos + 1)
                                    if pos % 15 != 14 and not self._buttonClickedComputer[(pos - 1) * (-1) - 2]:
                                        self._prefferedPositions.append(pos - 1)
                                        self._allPositions.remove(pos - 1)
                                # elif current position is on the top or on bottom of the previous position then orientation is vertical
                                elif pos == self._indexHit + 15 or pos == self._indexHit - 15:
                                    self._shipOrientation = 2 # vertical
                                    if self._indexHit - 1 in self._prefferedPositions:
                                        self._prefferedPositions.remove(self._indexHit - 1)
                                        self._allPositions.append(self._indexHit - 1)
                                    if self._indexHit + 1 in self._prefferedPositions:
                                        self._prefferedPositions.remove(self._indexHit + 1)
                                        self._allPositions.append(self._indexHit + 1)
                                    if self._indexHit < -16:
                                        if not self._buttonClickedComputer[(pos + 15) * (-1) - 2]:
                                            self._prefferedPositions.append(pos + 15)
                                            self._allPositions.remove(pos + 15)
                                    if pos > -212:
                                        if not self._buttonClickedComputer[(pos - 15) * (-1) - 2]:
                                            self._prefferedPositions.append(pos - 15)
                                            self._allPositions.remove(pos - 15)
                            break
                # if computer knows that player's ship is in horizontal position
                elif self._shipOrientation == 1:
                    for i in range(5):
                        if self._shipListPlayer[i].is_hit(xx % 15, xx / 15):
                            self._nmbOfHitsComputer[i] += 1
                            if self._shipListPlayer[i].sink(): # ship had length 2
                                self._destroyedShipsCounterComp += 1
                                for j in self._prefferedPositions:
                                    self._allPositions.append(j)
                                self._prefferedPositions = list()
                                if len(self._shipIndexWrong) == 0:
                                    if self._curLen > self._shipListPlayer[i].l:
                                        self._shipOrientation = 0
                                        self._curLen = 1
                                        if self._indexHit % 15 != 13 and not self._buttonClickedComputer[(self._indexHit + 1) * (-1) - 2]:
                                            self._prefferedPositions.append(self._indexHit + 1)
                                            self._allPositions.remove(self._indexHit + 1)
                                        if self._indexHit % 15 != 14 and not self._buttonClickedComputer[(self._indexHit - 1) * (-1) - 2]:
                                            self._prefferedPositions.append(self._indexHit - 1)
                                            self._allPositions.remove(self._indexHit - 1)
                                        if self._indexHit < -16:
                                            if not self._buttonClickedComputer[(self._indexHit + 15) * (-1) - 2]:
                                                self._prefferedPositions.append(self._indexHit + 15)
                                                self._allPositions.remove(self._indexHit + 15)
                                        if self._indexHit > -212:
                                            if not self._buttonClickedComputer[(self._indexHit - 15) * (-1) - 2]:
                                                self._prefferedPositions.append(self._indexHit - 15)
                                                self._allPositions.remove(self._indexHit - 15)
                                    else:
                                        self._shipHit = False
                                        self._indexHit = None
                                        self._shipOrientation = 0
                                        self._curLen = 0
                                else:
                                    self._indexHit = self._shipIndexWrong[0]
                                    self._shipIndexWrong.remove(self._indexHit)
                                    if self._shipOrientation == 1:
                                        if self._indexHit % 15 != 13 and not self._buttonClickedComputer[(self._indexHit + 1) * (-1) - 2]:
                                            self._prefferedPositions.append(self._indexHit + 1)
                                            self._allPositions.remove(self._indexHit + 1)
                                        if self._indexHit % 15 != 14 and not self._buttonClickedComputer[(self._indexHit - 1) * (-1) - 2]:
                                            self._prefferedPositions.append(self._indexHit - 1)
                                            self._allPositions.remove(self._indexHit - 1)
                                    elif self._shipOrientation == 2:
                                        if self._indexHit < -16:
                                            if not self._buttonClickedComputer[(self._indexHit + 15) * (-1) - 2]:
                                                self._prefferedPositions.append(self._indexHit + 15)
                                                self._allPositions.remove(self._indexHit + 15)
                                        if self._indexHit > -212:
                                            if not self._buttonClickedComputer[(self._indexHit - 15) * (-1) - 2]:
                                                self._prefferedPositions.append(self._indexHit - 15)
                                                self._allPositions.remove(self._indexHit - 15)
                                if self._destroyedShipsCounterComp == 5:
                                    self.showMessageBox("Sorry. You have lost this game.", "Hit and sunk!", "h-bomb.jpg", "explosion.wav")
                                    self.click_all_buttons()
                                    self.msg.exec_()
                                else:
                                    self.showMessageBox("Computer destroyed your ship of length " + str(
                                        self._shipList[i].l) + ".", "Hit and sunk!", "sinking-ship.jpg", "ship_sink.mp3")
                                    self.msg.exec_()
                            else:
                                self.showMessageBox("Watch out! Computer hit one of your ships.", "Hit!", "bomb.png", "blast.wav")
                                self.msg.exec_()

                                # add left and right positions to preffered locations
                                if pos % 15 != 13 and not self._buttonClickedComputer[(pos + 1) * (-1) - 2]:
                                    self._prefferedPositions.append(pos + 1)
                                    self._allPositions.remove(pos + 1)
                                if pos % 15 != 14 and not self._buttonClickedComputer[(pos - 1) * (-1) - 2]:
                                    self._prefferedPositions.append(pos - 1)
                                    self._allPositions.remove(pos - 1)
                            break
                # if computer knows that player's ship is in vertical position
                elif self._shipOrientation == 2:
                    for i in range(5):
                        if self._shipListPlayer[i].is_hit(xx % 15, xx / 15):
                            self._nmbOfHitsComputer[i] += 1
                            if self._shipListPlayer[i].sink(): # ship had length 2
                                self._destroyedShipsCounterComp += 1
                                for j in self._prefferedPositions:
                                    self._allPositions.append(j)
                                self._prefferedPositions = list()
                                if len(self._shipIndexWrong) == 0:
                                    if self._curLen > self._shipListPlayer[i].l:
                                        self._shipOrientation = 0
                                        self._curLen = 1
                                        if self._indexHit % 15 != 13 and not self._buttonClickedComputer[(self._indexHit + 1) * (-1) - 2]:
                                            self._prefferedPositions.append(self._indexHit + 1)
                                            self._allPositions.remove(self._indexHit + 1)
                                        if self._indexHit % 15 != 14 and not self._buttonClickedComputer[(self._indexHit - 1) * (-1) - 2]:
                                            self._prefferedPositions.append(self._indexHit - 1)
                                            self._allPositions.remove(self._indexHit - 1)
                                        if self._indexHit < -16:
                                            if not self._buttonClickedComputer[(self._indexHit + 15) * (-1) - 2]:
                                                self._prefferedPositions.append(self._indexHit + 15)
                                                self._allPositions.remove(self._indexHit + 15)
                                        if self._indexHit > -212:
                                            if not self._buttonClickedComputer[(self._indexHit - 15) * (-1) - 2]:
                                                self._prefferedPositions.append(self._indexHit - 15)
                                                self._allPositions.remove(self._indexHit - 15)
                                    else:
                                        self._shipHit = False
                                        self._indexHit = None
                                        self._shipOrientation = 0
                                        self._curLen = 0
                                else:
                                    self._indexHit = self._shipIndexWrong[0]
                                    self._shipIndexWrong.remove(self._indexHit)
                                    if self._shipOrientation == 1:
                                        if self._indexHit % 15 != 13 and not self._buttonClickedComputer[(self._indexHit + 1) * (-1) - 2]:
                                            self._prefferedPositions.append(self._indexHit + 1)
                                            self._allPositions.remove(self._indexHit + 1)
                                        if self._indexHit % 15 != 14 and not self._buttonClickedComputer[(self._indexHit - 1) * (-1) - 2]:
                                            self._prefferedPositions.append(self._indexHit - 1)
                                            self._allPositions.remove(self._indexHit - 1)
                                    elif self._shipOrientation == 2:
                                        if self._indexHit < -16:
                                            if not self._buttonClickedComputer[(self._indexHit + 15) * (-1) - 2]:
                                                self._prefferedPositions.append(self._indexHit + 15)
                                                self._allPositions.remove(self._indexHit + 15)
                                        if self._indexHit > -212:
                                            if not self._buttonClickedComputer[(self._indexHit - 15) * (-1) - 2]:
                                                self._prefferedPositions.append(self._indexHit - 15)
                                                self._allPositions.remove(self._indexHit - 15)
                                if self._destroyedShipsCounterComp == 5:
                                    self.showMessageBox("Sorry. You have lost this game.", "Hit and sunk!", "h-bomb.jpg", "explosion.wav")
                                    self.click_all_buttons()
                                    self.msg.exec_()
                                else:
                                    self.showMessageBox("Computer destroyed your ship of length " + str(
                                        self._shipList[i].l) + ".", "Hit and sunk!", "sinking-ship.jpg", "ship_sink.mp3")
                                    self.msg.exec_()
                            else:
                                self.showMessageBox("Watch out! Computer hit one of your ships.", "Hit!", "bomb.png", "blast.wav")
                                self.msg.exec_()

                                # add top and bottom positions to preffered locations
                                if pos < -16:
                                    if not self._buttonClickedComputer[(pos + 15) * (-1) - 2]:
                                        self._prefferedPositions.append(pos + 15)
                                        self._allPositions.remove(pos + 15)
                                if pos > -212:
                                    if not self._buttonClickedComputer[(pos - 15) * (-1) - 2]:
                                        self._prefferedPositions.append(pos - 15)
                                        self._allPositions.remove(pos - 15)
                            break

    def handleButtonClicked(self, button):
        button.setEnabled(False)
        self._buttonClicked[self.buttonGroup.id(button) * (-1) - 2] = True
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
                            self.showMessageBox("Congratulations! You destroyed all ships.", "Hit and sunk!", "h-bomb.jpg", "explosion.wav")
                            self.click_all_buttons()
                            self.msg.exec_()
                        else:
                            self.showMessageBox("Congratulations! The ship of length " + str(self._shipList[i].l) + " was sunk.",
                                                "Hit and sunk!", "sinking-ship.jpg", "ship_sink.mp3")
                            self.msg.exec_()
                    else:
                        self.showMessageBox("You hit the ship.", "Hit!", "bomb.png", "blast.wav")
                        self.msg.exec_()
        else:
            button.setStyleSheet(designShip._fromUtf8("background-color: rgb(10, 105, 148);"))

        # after player's turn is computer's turn
        QtCore.QTimer.singleShot(250, self.computerTurn)

def main():
    app = QtGui.QApplication(sys.argv)
    form = BattleShipApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()