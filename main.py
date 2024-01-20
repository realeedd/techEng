import sys
import io
import sqlite3
import csv

from random import choice, sample, randint
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog, QWidget, QAction, QMenu
from PyQt5.QtGui import QPixmap


class OpenWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('openingpage.ui', self)
        # объявляем базу данных
        self.con = sqlite3.connect('TechEngDB.sqlite')
        self.show()
        self.showMain()


    def showMain(self):
        mainWindow = MainWindow(self.con, self)
        self.setCentralWidget(mainWindow)
        mainWindow.registr.clicked.connect(self.regButton)
        mainWindow.signin.clicked.connect(self.signButton)
        mainWindow.show()

    def regButton(self):
        regWindow = RegWindow(self.con, self)
        self.setCentralWidget(regWindow)
        regWindow.backButton.clicked.connect(self.showMain)
        regWindow.show()

    # показываем окно входа
    def signButton(self):
        signWindow = SignWindow(self.con, self)
        self.setCentralWidget(signWindow)
        signWindow.backButton.clicked.connect(self.showMain)
        signWindow.show()

    def openTesting(self, userId):
        self.testingWindow = Testing(userId)
        try:
            self.testingWindow.show()
        except Exception as err:
            print(err)
        self.hide()

# главное окно
class MainWindow(QWidget):
    def __init__(self, con, openingwindow):
        super().__init__(openingwindow)
        uic.loadUi('main.ui', self)
        self.setStyleSheet('.QWidget {background-image: url(69c461fe46c248901150bfd7f23ea340.jpg);}')


# окно регистрации
class RegWindow(QWidget):
    def __init__(self, connection, openingwindow):
        super().__init__(openingwindow)
        self.con = connection
        uic.loadUi('reg.ui', self)
        self.regButton.clicked.connect(self.addData)
        self.setStyleSheet('.QWidget {background-image: url(8b5504825ea01ea1eb747632b8428926.png);}')
        self.openingwindow = openingwindow

    # добавляем пользователя
    def addData(self):
        try:
            login = self.regLogin.text()
            password = self.regPassword.text()
            cur = self.con.cursor()
            insert_data = """INSERT INTO users
                              (login, password)
                              VALUES
                              (?, ?)"""
            # проверка введеных данных
            if login == '':
                QMessageBox.critical(self, 'Ошибка', 'Логин не введен')

            elif len(login) < 3:
                QMessageBox.critical(self, 'Ошибка', 'Недостаточно символов')

            elif password == '':
                QMessageBox.critical(self, 'Ошибка', 'Пароль не введен')

            elif len(cur.execute('''SELECT login FROM users
                                    WHERE login = ?''', (login,)).fetchall()) != 0:
                QMessageBox.critical(self, 'Ошибка', 'Такой пользователь уже существует')
        except Exception as error:
            print(error)
        else:

            # регистрируем человека в базу данных
            try:
                cur.execute(insert_data, (login, password))
                self.con.commit()
                self.hide()
                users = cur.execute('''SELECT id, password FROM users
                            WHERE login = ?''', (login,)).fetchall()
                print(users)
                userId = users[0][0]
                print(userId)
                self.openingwindow.openTesting(userId)
            except Exception as err:
                print(err)


# окно входа
class SignWindow(QWidget):
    def __init__(self, connection, openingwindow):
        super().__init__(openingwindow)
        uic.loadUi('sign.ui', self)
        self.signButton.clicked.connect(self.logIn)
        self.con = connection
        self.setStyleSheet('.QWidget {background-image: url(8b5504825ea01ea1eb747632b8428926.png);}')
        self.openingwindow = openingwindow

    def logIn(self):
        try:
            login = self.signLogin.text()
            password = self.signPassword.text()
            cur = self.con.cursor()
            # ищем логин в базе данных и запоминаем айди и пароль
            users = cur.execute('''SELECT id, password FROM users
                            WHERE login = ?''', (login,)).fetchall()
            # проверка введеных данных
            if login == '':
                QMessageBox.critical(self, 'Ошибка', 'Логин не введен')

            elif password == '':
                QMessageBox.critical(self, 'Ошибка', 'Пароль не введен')

            elif len(users) == 0:
                QMessageBox.critical(self, 'Ошибка', 'Такой пользователь не существует')

            elif password != users[0][1]:
                QMessageBox.critical(self, 'Ошибка', 'Неверный пароль')

            else:
                # записываем айди, чтобы его позже передать в следующее окно
                userId = users[0][0]
                self.openingwindow.openTesting(userId)
        except Exception as err:
            print(err)


class Testing(QMainWindow):
    def __init__(self, userId):
        super().__init__()
        uic.loadUi('mainpage.ui', self)
        
        self.con = sqlite3.connect('TechEngDB.sqlite')
        self.setStyleSheet('.QWidget {background-image: url(8b5504825ea01ea1eb747632b8428926.png);}')
        # айди пользователя
        self.id = userId
        self.onMainAction()
        # подключаем меню
        self.mainMenu = QMenu("Результаты", self)
        self.menubar.addMenu(self.mainMenu)
        
        self.mainPageAction = QAction("Результаты", self)
        self.mainMenu.addAction(self.mainPageAction)
        self.mainPageAction.triggered.connect(self.onMainAction)

        self.theoryMenu = QMenu("Словарь", self)
        self.menubar.addMenu(self.theoryMenu)
        
        self.testsMenu = QMenu("Тесты", self)
        self.menubar.addMenu(self.testsMenu)

        self.newWordMenu= QMenu("Добавить слово", self)
        self.menubar.addMenu(self.newWordMenu)

        
        #добавляем элементы в меню
        #меню с заданиями
        self.newWordAction = QAction("Добавить слово", self)
        self.newWordMenu.addAction(self.newWordAction)
        self.newWordAction.triggered.connect(self.onNewWordAction)

        self.keywordstestingAction = QAction("Ключевые слова", self)
        self.testsMenu.addAction(self.keywordstestingAction)
        self.keywordstestingAction.triggered.connect(self.onKeywordsAction)

        self.developtestingAction = QAction("Слова для разработки", self)
        self.testsMenu.addAction(self.developtestingAction)
        self.developtestingAction.triggered.connect(self.onDevelopAction)

        self.comptestingAction = QAction("Компьютер", self)
        self.testsMenu.addAction(self.comptestingAction)
        self.comptestingAction.triggered.connect(self.onCompTesting)

        self.termstestingAction = QAction("Вставь термин", self)
        self.testsMenu.addAction(self.termstestingAction)
        self.termstestingAction.triggered.connect(self.onTermsTesting)

        #меню с теорией
        self.keywordstheoryAction = QAction("Ключевые слова", self)
        self.theoryMenu.addAction(self.keywordstheoryAction)
        self.keywordstheoryAction.triggered.connect(self.onKeywordsThAction)

        self.developtheoryAction = QAction("Слова для разработки", self)
        self.theoryMenu.addAction(self.developtheoryAction)
        self.developtheoryAction.triggered.connect(self.onDevelopThAction)

        self.comptheoryAction = QAction("Компьютер", self)
        self.theoryMenu.addAction(self.comptheoryAction)
        self.comptheoryAction.triggered.connect(self.onCompTheory)

        self.termstheoryAction = QAction("Back-end разработка", self)
        self.theoryMenu.addAction(self.termstheoryAction)
        self.termstheoryAction.triggered.connect(self.onTermsTheory)
        self.setStyleSheet('''.QMenu {background-color: rgb(226, 234, 255 );
                           font-size: 20px;
                           font-family: "Trebuchet MS", "Lucida Grande",
                           "Lucida Sans Unicode", "Lucida Sans", Tahoma, sans-serif;
                           color:rgb(57, 57, 57);}''')
        self.dictionaryAction = QAction('Слова в алфавитном порядке')
        self.theoryMenu.addAction(self.dictionaryAction)
        self.dictionaryAction.triggered.connect(self.onDictionary)

    def onNewWordAction(self):
        self.newWord = ChooseWord(self)
        self.setCentralWidget(self.newWord)
        self.newWord.show()

    def onDictionary(self):
        self.dictionary = DictionaryWindow(self.con, self.id, self)
        self.setCentralWidget(self.dictionary)
        self.dictionary.show()

    def onKeywordsAction(self):
        print('do')
        self.keywordstesting = KeywordsTestWindow(self.con, self.id, self)
        self.setCentralWidget(self.keywordstesting)
        self.keywordstesting.show()
        print('posle')

    def onDevelopAction(self):
        self.developtesting = DevelopTestWindow(self.con, self.id, self)
        self.setCentralWidget(self.developtesting)
        self.developtesting.show()

    def onCompTesting(self):
        self.comptesting = ComputerTestWindow(self.con, self.id, self)
        self.setCentralWidget(self.comptesting)
        self.comptesting.show()

    def onTermsTesting(self):
        self.termstesting = TermsTestWindow(self.con, self.id, self)
        self.setCentralWidget(self.termstesting)
        self.termstesting.show()

    def onKeywordsThAction(self):
        self.keywordswindow = KeywordsWindow(self.con, self.id, self)
        self.setCentralWidget(self.keywordswindow)
        self.keywordswindow.show()

    def onDevelopThAction(self):
        self.developwindow = DevelopWindow(self.con, self.id, self)
        self.setCentralWidget(self.developwindow)
        self.developwindow.show()

    def onCompTheory(self):
        self.computerwindow = ComputerWindow(self.con, self.id, self)
        self.setCentralWidget(self.computerwindow)
        self.computerwindow.show()

    def onTermsTheory(self):
        self.termswindow = TermsWindow(self.con, self.id, self)
        self.setCentralWidget(self.termswindow)
        self.termswindow.show()
        
    def onMainAction(self):
        self.mainpage = MainPage(self.con, self.id, self)
        self.setCentralWidget(self.mainpage)
        self.mainpage.show()


class DictionaryWindow(QWidget):
    def __init__(self, connection, userId, testWindow):
        super().__init__(testWindow)
        uic.loadUi('dictionary.ui', self)
        
        self.con = connection
        cur = self.con.cursor()
        self.setStyleSheet('.QWidget {background-image: url(8b5504825ea01ea1eb747632b8428926.png);}')
        #слово по клику
        self.wordList.currentTextChanged.connect(self.selectionChanged)
        self.refresh()
        
    def refresh(self):

        self.wordList.clear()
        self.words = []
        self.disc = []
        self.lst = []
        self.discWord.setText('')
        #составляем список слов
        with open('developing.csv', encoding='windows-1251') as csvf:
            reader = csv.reader(csvf, delimiter=';', quotechar='"')
            for x in reader:
                self.words.append(x[0])
                self.disc.append(x[1])
                
        with open('keywords.csv', encoding='windows-1251') as csvf:
            reader = csv.reader(csvf, delimiter=';', quotechar='"')
            for x in reader:
                self.words.append(x[0])
                self.disc.append(x[1])
        try:       
            with open('termsdisc.csv', encoding='windows-1251') as csvf:
                reader = csv.reader(csvf, delimiter=';', quotechar='"')
                for x in reader:
                    self.words.append(x[0])
                    self.disc.append(x[1])
            #изначальный список слов
            for i in range(len(self.words)):
                self.lst.append(self.words[i])
            #слова в алфавитном прядке
            self.words = sorted(self.words)
            #выводим слова на экран
            for i in range(len(self.words)):
                self.wordList.addItem(self.words[i]) 
        except Exception as error:
            print(error)


            
    #выводим значение слова      
    def selectionChanged(self, item):
        if item:
            ind = self.lst.index(item)
            self.discWord.setText(self.disc[ind])

        
class ChooseWord(QWidget):
    def __init__(self, testWindow):
        super().__init__(testWindow)
        self.testWindow = testWindow
        uic.loadUi('chooseword.ui', self)
        self.setStyleSheet('.QWidget {background-image: url(8b5504825ea01ea1eb747632b8428926.png);}')
        
        self.addword.clicked.connect(self.addWord)


    def addWord(self):
        newWord = self.word.text()
        meaning = self.meaning.text()
        if newWord != '' and meaning != '':
            typeWord = self.comboBox.currentText()
            if typeWord == 'Ключевые слова':
                with open('keywords.csv', mode='a', encoding='windows-1251') as csvf:
                    s = f'{newWord};{meaning}\n'
                    csvf.writelines(s)
            if typeWord == 'Слова для разработки':
                with open('developing.csv', mode='a', encoding='windows-1251') as csvf:
                    s = f'{newWord};{meaning}\n'
                    csvf.writelines(s)
            if typeWord == 'Back-end разработка':
                with open('termsdisc.csv', mode='a', encoding='windows-1251') as csvf:
                    s = f'{newWord};{meaning}\n'
                    csvf.writelines(s)
            self.testWindow.onDictionary()

        else:
            QMessageBox.critical(self, 'Ошибка', 'Неверный ввод')


        
class MainPage(QWidget):
    def __init__(self, connection, userId, testWindow):
        super().__init__(testWindow)
        uic.loadUi('lessons.ui', self)
        self.con = connection
        cur = self.con.cursor()
        self.setStyleSheet('.QWidget {background-image: url(8b5504825ea01ea1eb747632b8428926.png);}')
        # айди пользователя
        self.id = userId
        self.refresh()
        self.picture.setStyleSheet('background-image: url(english-for-it-specialists-1.png);')
        self.picture_2.setStyleSheet('background-image: url(pngwing.com.png);')
        try:
            name = cur.execute('''SELECT login FROM users
                                WHERE id = ?''', (self.id,)).fetchall()[0][0]
            print(name)
            self.login.setText(name)
        except Exception as error:
            print(error)

    
    # показываем обновленные данные пользователей
    def refresh(self):
        cur = self.con.cursor()
        kc = 0
        for row in open("keywords.csv", encoding='windows-1251'):
            kc += 1
        dc = 0
        for row in open("developing.csv", encoding='windows-1251'):
            dc += 1
        keywordsPointsData = cur.execute('''SELECT points FROM test_results
        WHERE user_id = ? and lesson = ? ORDER BY column DESC LIMIT 1''', (self.id, 'keywords')).fetchall()
        keywordsPoints = 0
        if len(keywordsPointsData) > 0:
            keywordsPoints = keywordsPointsData[0][0]
        self.keywordsPoints.setText(f'{keywordsPoints // 10} / {kc}')


        developPointsData = cur.execute('''SELECT points FROM test_results
        WHERE user_id = ? and lesson = ? ORDER BY column DESC LIMIT 1''', (self.id, 'develop')).fetchall()
        developPoints = 0
        if len(developPointsData) > 0:
            developPoints = developPointsData[0][0]
        self.developPoints.setText(f'{developPoints // 10} / {dc}')

        compPointsData = cur.execute('''SELECT points FROM test_results
        WHERE user_id = ? and lesson = ? ORDER BY column DESC LIMIT 1''', (self.id, 'computer')).fetchall()
        compPoints = 0
        if len(compPointsData) > 0:
            compPoints = compPointsData[0][0]
        self.compPoints.setText(f'{compPoints // 10} / 8')

        termsPointsData = cur.execute('''SELECT points FROM test_results
        WHERE user_id = ? and lesson = ? ORDER BY column DESC LIMIT 1''', (self.id, 'terms')).fetchall()
        termsPoints = 0
        if len(termsPointsData) > 0:
            termsPoints = termsPointsData[0][0]
        self.termsPoint.setText(f'{termsPoints // 10} / 9')

greenButton = '''
QPushButton{background: rgba(0, 170, 127, 0.8);
border-radius: 20px;
border-style: outset;
 border-width: 5px;
border-color:rgb(191, 191, 191);
color:rgb(57, 57, 57);}
'''
redButton = '''
QPushButton{background: rgba(197, 52, 23, 0.8);
border-radius: 20px;
border-style: outset;
 border-width: 5px;
border-color:rgb(191, 191, 191);
color:rgb(57, 57, 57);}
'''
greyButton = '''
QPushButton{background: rgba(255, 255, 255, 0.6);
border-radius: 20px;
border-style: outset;
 border-width: 5px;
border-color:rgb(191, 191, 191);
color:rgb(57, 57, 57);}
'''
# окно тестов с ключевыми словами
class KeywordsTestWindow(QWidget):
    global greenButton
    global redButton
    global greyButton
    def __init__(self, connection, userId, testWindow):
        super().__init__(testWindow)
        uic.loadUi('keywordsquestions.ui', self)
        self.con = connection
        self.id = userId
        self.testWindow = testWindow
        self.setStyleSheet('.QWidget {background-image: url(8b5504825ea01ea1eb747632b8428926.png);}')

        # cоздаем список слов и их объяснений
        with open('keywords.csv', encoding='windows-1251') as csvf:
            reader = csv.reader(csvf, delimiter=';', quotechar='"')
            self.words = []
            self.disc = []
            for x in reader:
                self.words.append(x[0])
                self.disc.append(x[1])
        self.continueButton.clicked.connect(self.chooseWord)
        # кнопки ответов
        self.anButton1.clicked.connect(self.firstButtonCheck)
        self.anButton2.clicked.connect(self.secondButtonCheck)
        self.anButton3.clicked.connect(self.thirdButtonCheck)
        self.reset()
        self.chooseWord()

    # сбрасываем переменные чтобы заново проходить тест
    def reset(self):
        # правильный ответ
        self.rightAnswer = ''
        self.answerCount = 0
        # индексы слов для тестов
        self.left = [int(i) for i in range(0, len(self.words))]

    # кнопка 1
    def firstButtonCheck(self):
        if self.disc1.text() == self.rightAnswer:
            self.anButton1.setStyleSheet(greenButton)
            self.answerCount += 1

        else:
            self.anButton1.setStyleSheet(redButton)
            if self.disc2.text() == self.rightAnswer:
                self.anButton2.setStyleSheet(greenButton)
            elif self.disc3.text() == self.rightAnswer:
                self.anButton3.setStyleSheet(greenButton)

    # кнопка 2
    def secondButtonCheck(self):
        if self.disc2.text() == self.rightAnswer:
            self.anButton2.setStyleSheet(greenButton)
            self.answerCount += 1

        else:
            self.anButton2.setStyleSheet(redButton)
            if self.disc1.text() == self.rightAnswer:
                self.anButton1.setStyleSheet(greenButton)
            elif self.disc3.text() == self.rightAnswer:
                self.anButton3.setStyleSheet(greenButton)

    # кнопка 3
    def thirdButtonCheck(self):
        # проверяем на правильность
        if self.disc3.text() == self.rightAnswer:
            self.anButton3.setStyleSheet(greenButton)
            self.answerCount += 1
        else:
            # отмечаем что неправильно и отмечаем правильное
            self.anButton3.setStyleSheet(redButton)
            if self.disc2.text() == self.rightAnswer:
                self.anButton2.setStyleSheet(greenButton)
            elif self.disc1.text() == self.rightAnswer:
                self.anButton1.setStyleSheet(greenButton)

    # рандомно выбираем неповторяющиеся индексы
    def randAns(self, a, b, lst):
        while True:
            n = randint(a, b)
            if n not in lst:
                return n

    def chooseWord(self):
        # сбрасываем цвет кнопок
        button_style = greyButton
        self.anButton1.setStyleSheet(button_style)
        self.anButton2.setStyleSheet(button_style)
        self.anButton3.setStyleSheet(button_style)
        # проверяем, что есть еще слова
        try:
            if len(self.left) > 0:
                variants = []
                # индекс правильного слова с правильным ответом и двух рандомных ответов
                ind = choice(self.left)
                self.left.remove(ind)
                variants.append(ind)

                ans1 = self.randAns(0, len(self.words)-1, variants)
                variants.append(ans1)

                ans2 = self.randAns(0, len(self.words)-1, variants)

                self.word.setText(self.words[ind])
                rightAn = self.disc[ind]
                self.rightAnswer = rightAn
                # список вариантов ответов
                answers = [rightAn, self.disc[ans1], self.disc[ans2]]
                choice1 = choice(answers)
                # вписываем варианты ответов
                self.disc1.setText(choice1)
                answers.remove(choice1)
                choice2 = choice(answers)
                self.disc2.setText(choice2)
                answers.remove(choice2)
                self.disc3.setText(answers[0])
            else:
                # когда тест закончился
                points = 10 * self.answerCount
                cur = self.con.cursor()
                cur.execute('''INSERT INTO test_results(user_id, lesson, points)
                VALUES(?, "keywords", ?)''', (self.id, points,))
                self.con.commit()
                kc = 0
                for row in open("keywords.csv", encoding='windows-1251'):
                    kc += 1
                QMessageBox.information(self, 'Тест пройден', f"Правильных ответов: {points // 10} из {kc}")
                self.testWindow.onMainAction()

        except Exception as error:
            print(error)


class DevelopTestWindow(QWidget):
    global greenButton
    global redButton
    global greyButton
    def __init__(self, connection, userId, testWindow):
        super().__init__(testWindow)
        uic.loadUi('developquestions.ui', self)
        self.con = connection
        self.id = userId
        self.testWindow = testWindow
        cur = self.con.cursor()
        self.setStyleSheet('.QWidget {background-image: url(8b5504825ea01ea1eb747632b8428926.png);}')
        with open('developing.csv', encoding='windows-1251') as csvf:
            reader = csv.reader(csvf, delimiter=';', quotechar='"')
            self.words = []
            self.disc = []
            for x in reader:
                self.words.append(x[0])
                self.disc.append(x[1])
        self.continueButton.clicked.connect(self.chooseWord)

        # кнопки ответов
        self.anButton1.clicked.connect(self.firstButtonCheck)
        self.anButton2.clicked.connect(self.secondButtonCheck)
        self.anButton3.clicked.connect(self.thirdButtonCheck)
        self.reset()
        self.chooseWord()

    # сбрасываем переменные чтобы заново проходить тест
    def reset(self):
        # правильный ответ
        self.rightAnswer = ''
        self.answerCount = 0
        # индексы слов для тестов
        self.left = [int(i) for i in range(0, len(self.words))]

    # кнопка 1
    def firstButtonCheck(self):
        if self.disc1.text() == self.rightAnswer:
            self.anButton1.setStyleSheet(greenButton)
            self.answerCount += 1
        else:
            self.anButton1.setStyleSheet(redButton)
            if self.disc2.text() == self.rightAnswer:
                self.anButton2.setStyleSheet(greenButton)
            elif self.disc3.text() == self.rightAnswer:
                self.anButton3.setStyleSheet(greenButton)

    # кнопка 2
    def secondButtonCheck(self):
        if self.disc2.text() == self.rightAnswer:
            self.anButton2.setStyleSheet(greenButton)
            self.answerCount += 1
        else:
            self.anButton2.setStyleSheet(redButton)
            if self.disc1.text() == self.rightAnswer:
                self.anButton1.setStyleSheet(greenButton)
            elif self.disc3.text() == self.rightAnswer:
                self.anButton3.setStyleSheet(greenButton)

    # кнопка 3
    def thirdButtonCheck(self):
        # проверяем на правильность
        if self.disc3.text() == self.rightAnswer:
            self.anButton3.setStyleSheet(greenButton)
            self.answerCount += 1
        else:
            # отмечаем что неправильно и отмечаем правильное
            self.anButton3.setStyleSheet(redButton)
            if self.disc2.text() == self.rightAnswer:
                self.anButton2.setStyleSheet(greenButton)
            elif self.disc1.text() == self.rightAnswer:
                self.anButton1.setStyleSheet(greenButton)
        # рандомно выбираем неповторяющиеся индексы

    def randAns(self, a, b, lst):
        while True:
            n = randint(a, b)
            if n not in lst:
                return n

    def chooseWord(self):
        button_style = greyButton
        self.anButton1.setStyleSheet(button_style)
        self.anButton2.setStyleSheet(button_style)
        self.anButton3.setStyleSheet(button_style)
        # проверяем, что есть еще слова
        try:
            if len(self.left) > 0:
                variants = []
                # индекс правильного слова с правильным ответом и двух рандомных ответов
                ind = choice(self.left)
                self.left.remove(ind)
                variants.append(ind)

                ans1 = self.randAns(0, len(self.words) - 1, variants)
                variants.append(ans1)

                ans2 = self.randAns(0, len(self.words) - 1, variants)

                self.word.setText(self.words[ind])
                rightAn = self.disc[ind]
                self.rightAnswer = rightAn
                # список вариантов ответов
                answers = [rightAn, self.disc[ans1], self.disc[ans2]]
                choice1 = choice(answers)
                self.disc1.setText(choice1)
                answers.remove(choice1)
                choice2 = choice(answers)
                self.disc2.setText(choice2)
                answers.remove(choice2)
                self.disc3.setText(answers[0])
            else:
                # когда тест закончился
                points = 10 * self.answerCount
                cur = self.con.cursor()
                # вставляем результат в таблицу
                cur.execute('''INSERT INTO test_results(user_id, lesson, points)
                VALUES(?, "develop", ?)''', (self.id, points,))
                self.con.commit()
                dc = 0
                for row in open("developing.csv", encoding='windows-1251'):
                    dc += 1
                QMessageBox.information(self, 'Тест пройден', f"Правильных ответов: {points // 10} из {dc}")
                self.testWindow.onMainAction()
        except Exception as error:
            print(error)

            
class ComputerTestWindow(QWidget):
    def __init__(self, connection, userId, testWindow):
        super().__init__(testWindow)
        uic.loadUi('comptest.ui', self)
        self.con = connection
        self.id = userId
        cur = self.con.cursor()
        self.setStyleSheet('.QWidget {background-image: url(8b5504825ea01ea1eb747632b8428926.png);}')

        
        self.checkAnswer.clicked.connect(self.check)
        self.elements = [self.answer1, self.answer2, self.answer3, self.answer4, self.answer5, self.answer6,
                         self.answer7, self.answer8, self.answer9, self.answer10]
        self.cpu.setStyleSheet('background-image: url(cpu.png);')
        self.cpucooler.setStyleSheet('background-image: url(cpucooler.png);')
        self.graphiccard.setStyleSheet('background-image: url(graphiccard.png);')
        self.hdd.setStyleSheet('background-image: url(hdd.png);')
        self.motherboard.setStyleSheet('background-image: url(motherboard.png);')
        self.powersupply.setStyleSheet('background-image: url(powersupply.png);')
        self.ram.setStyleSheet('background-image: url(ram.png);')
        self.soundcard.setStyleSheet('background-image: url(soundcard.png);')
        self.ssd.setStyleSheet('background-image: url(ssd.png);')
        self.ports.setStyleSheet('background-image: url(ports.png);')

        self.tryAgain.clicked.connect(self.again)

    def again(self):
        self.points.setText(' ')
        style = '''color:rgb(57, 57, 57);
                background-color: rgba(221, 221, 221, 0.1)
                '''
        for i in range(0, 10):
            self.elements[i].setStyleSheet(style)
            self.elements[i].setText('')
            
    def check(self):
        try:
            k = 0
            words = ['cpu', 'cpu cooler', 'Graphics card', 'hdd', 'motherboard',
                     'power supply', 'ram', 'sound card', 'ssd', 'ports']
            for i in range(0, 10):
                if self.elements[i].text().lower() == words[i]:
                    k+= 1
                    self.elements[i].setStyleSheet('background: rgb(170, 255, 127);')
                    self.elements[i].setStyleSheet('background: rgb(170, 255, 127);')
                else:
                    self.elements[i].setStyleSheet('background: rgb(255, 73, 73);')
            points = 10 * k
            cur = self.con.cursor()
                # вставляем результат в таблицу
            cur.execute('''INSERT INTO test_results(user_id, lesson, points)
                VALUES(?, "computer", ?)''', (self.id, points,))
            self.con.commit()
            self.points.setText(f'Правильных ответов: {points // 10}')
            
                
        except Exception as error:
            print(error)

class TermsTestWindow(QWidget):
    global greenButton
    global redButton
    global greyButton
    def __init__(self, connection, userId, testWindow):
        super().__init__()
        uic.loadUi('termstest.ui', self)
        self.con = connection
        self.id = userId
        cur = self.con.cursor()
        self.testWindow = testWindow
        self.setStyleSheet('.QWidget {background-image: url(8b5504825ea01ea1eb747632b8428926.png);}')
        with open('terms.csv', encoding='windows-1251') as csvf:
            reader = csv.reader(csvf, delimiter=';', quotechar='"')
            self.words = []
            self.sentence = []
            for x in reader:
                self.words.append(x[0])
                self.sentence.append(x[1])
        self.continueButton.clicked.connect(self.chooseWord)

        # кнопки ответов
        self.anButton1.clicked.connect(self.firstButtonCheck)
        self.anButton2.clicked.connect(self.secondButtonCheck)
        self.anButton3.clicked.connect(self.thirdButtonCheck)

        self.reset()
        self.chooseWord()

    # сбрасываем переменные чтобы заново проходить тест
    def reset(self):
        # правильный ответ
        self.rightAnswer = ''
        self.answerCount = 0
        # индексы слов для тестов
        self.left = [int(i) for i in range(0, len(self.sentence) - 1)]


    # кнопка 1
    def firstButtonCheck(self):
        if self.disc1.text() == self.rightAnswer:
            self.anButton1.setStyleSheet(greenButton)
            self.answerCount += 1
        else:
            self.anButton1.setStyleSheet(redButton)
            if self.disc2.text() == self.rightAnswer:
                self.anButton2.setStyleSheet(greenButton)
            elif self.disc3.text() == self.rightAnswer:
                self.anButton3.setStyleSheet(greenButton)

    # кнопка 2
    def secondButtonCheck(self):
        if self.disc2.text() == self.rightAnswer:
            self.anButton2.setStyleSheet(greenButton)
            self.answerCount += 1
        else:
            self.anButton2.setStyleSheet(redButton)
            if self.disc1.text() == self.rightAnswer:
                self.anButton1.setStyleSheet(greenButton)
            elif self.disc3.text() == self.rightAnswer:
                self.anButton3.setStyleSheet(greenButton)

    # кнопка 3
    def thirdButtonCheck(self):
        # проверяем на правильность
        if self.disc3.text() == self.rightAnswer:
            self.anButton3.setStyleSheet(greenButton)
            self.answerCount += 1
        else:
            # отмечаем что неправильно и отмечаем правильное
            self.anButton3.setStyleSheet(redButton)
            if self.disc2.text() == self.rightAnswer:
                self.anButton2.setStyleSheet(greenButton)
            elif self.disc1.text() == self.rightAnswer:
                self.anButton1.setStyleSheet(greenButton)
        # рандомно выбираем неповторяющиеся индексы

    def randAns(self, a, b, lst):
        while True:
            n = randint(a, b)
            if n not in lst:
                return n

    def chooseWord(self):
        button_style = greyButton
        self.anButton1.setStyleSheet(button_style)
        self.anButton2.setStyleSheet(button_style)
        self.anButton3.setStyleSheet(button_style)
        # проверяем, что есть еще слова
        try:
            if len(self.left) > 0:
                variants = []
                # индекс правильного слова с правильным ответом и двух рандомных ответов
                ind = choice(self.left)
                self.left.remove(ind)
                variants.append(ind)

                ans1 = self.randAns(0, len(self.sentence) - 1, variants)
                variants.append(ans1)

                ans2 = self.randAns(0, len(self.sentence) - 1, variants)

                self.word.setText(self.sentence[ind])
                rightAn = self.words[ind]
                self.rightAnswer = rightAn
                # список вариантов ответов
                answers = [rightAn, self.words[ans1], self.words[ans2]]
                choice1 = choice(answers)
                self.disc1.setText(choice1)
                answers.remove(choice1)
                choice2 = choice(answers)
                self.disc2.setText(choice2)
                answers.remove(choice2)
                self.disc3.setText(answers[0])
            else:
                # когда тест закончился
                points = 10 * self.answerCount
                cur = self.con.cursor()
                # вставляем результат в таблицу
                cur.execute('''INSERT INTO test_results(user_id, lesson, points)
                VALUES(?, "terms", ?)''', (self.id, points,))
                self.con.commit()
                QMessageBox.information(self, 'Тест пройден', f"Правильных ответов: {points // 10} из 9")
                self.testWindow.onMainAction()
        except Exception as error:
            print(error)
            
##############################################

# окно урока с ключевыми словами
class KeywordsWindow(QWidget):
    def __init__(self, connection, userId, theoryWindow):
        super().__init__()
        uic.loadUi('keywords.ui', self)
        self.con = connection
        self.id = userId
        self.setStyleSheet('.QWidget {background-image: url(8b5504825ea01ea1eb747632b8428926.png);}')
        cur = self.con.cursor()

        #слово по клику
        try:
            self.wordList.currentTextChanged.connect(self.selectionChanged)
            self.refresh()
        except Exception as error:
            print(error)


    def refresh(self):
        self.wordList.clear()
        self.words = []
        self.disc = []
        self.lst = []
        self.answer.setText('')
        #составляем список слов
        with open('keywords.csv', encoding='windows-1251') as csvf:
            reader = csv.reader(csvf, delimiter=';', quotechar='"')
            for x in reader:
                self.words.append(x[0])
                self.disc.append(x[1])
            for i in range(len(self.words)):
                self.lst.append(self.words[i])
            #слова в алфавитном прядке
            self.words = sorted(self.words)
            #выводим слова на экран
            for i in range(len(self.words)):
                self.wordList.addItem(self.words[i])


    def selectionChanged(self, item):
        if item:
            ind = self.lst.index(item)
            self.answer.setText(self.disc[ind])





# окно урока со словами для разработки
class DevelopWindow(QWidget):
    def __init__(self, connection, userId, theoryWindow):
        super().__init__()
        uic.loadUi('develop.ui', self)
        self.con = connection
        self.id = userId
        self.setStyleSheet('.QWidget {background-image: url(8b5504825ea01ea1eb747632b8428926.png);}')
        cur = self.con.cursor()
        #слово по клику
        try:
            self.wordList.currentTextChanged.connect(self.selectionChanged)
            self.refresh()
        except Exception as error:
            print(error)


    def refresh(self):
        self.wordList.clear()
        self.words = []
        self.disc = []
        self.lst = []
        self.answer.setText('')
        #составляем список слов
        with open('developing.csv', encoding='windows-1251') as csvf:
            reader = csv.reader(csvf, delimiter=';', quotechar='"')
            for x in reader:
                self.words.append(x[0])
                self.disc.append(x[1])
            for i in range(len(self.words)):
                self.lst.append(self.words[i])
            #слова в алфавитном прядке
            self.words = sorted(self.words)
            #выводим слова на экран
            for i in range(len(self.words)):
                self.wordList.addItem(self.words[i])


    def selectionChanged(self, item):
        if item:
            ind = self.lst.index(item)
            self.answer.setText(self.disc[ind])


    # проверяем прочитан ли уже урок и записываем, если да

            
class ComputerWindow(QWidget):
    def __init__(self, connection, userId, theoryWindow):
        super().__init__()
        uic.loadUi('comp.ui', self)
        self.con = connection
        self.id = userId
        self.setStyleSheet('.QWidget {background-image: url(8b5504825ea01ea1eb747632b8428926.png);}')
        self.theoryWindow = theoryWindow

        self.cpu.setStyleSheet('background-image: url(cpu.png);')
        self.cpucooler.setStyleSheet('background-image: url(cpucooler.png);')
        self.graphiccard.setStyleSheet('background-image: url(graphiccard.png);')
        self.hdd.setStyleSheet('background-image: url(hdd.png);')
        self.motherboard.setStyleSheet('background-image: url(motherboard.png);')
        self.powersupply.setStyleSheet('background-image: url(powersupply.png);')
        self.ram.setStyleSheet('background-image: url(ram.png);')
        self.soundcard.setStyleSheet('background-image: url(soundcard.png);')
        self.ssd.setStyleSheet('background-image: url(ssd.png);')
        self.ports.setStyleSheet('background-image: url(ports.png);')

            



class TermsWindow(QWidget):
    def __init__(self, connection, userId, theoryWindow):
        super().__init__()
        uic.loadUi('terms.ui', self)
        self.con = connection
        self.id = userId
        self.setStyleSheet('.QWidget {background-image: url(8b5504825ea01ea1eb747632b8428926.png);}')
        cur = self.con.cursor()

        self.setStyleSheet('.QWidget {background-image: url(8b5504825ea01ea1eb747632b8428926.png);}')
        #слово по клику
        try:
            self.wordList.currentTextChanged.connect(self.selectionChanged)
            self.refresh()
        except Exception as error:
            print(error)


    def refresh(self):
        self.wordList.clear()
        self.words = []
        self.disc = []
        self.lst = []
        self.answer.setText('')
        #составляем список слов
        with open('termsdisc.csv', encoding='windows-1251') as csvf:
            reader = csv.reader(csvf, delimiter=';', quotechar='"')
            for x in reader:
                self.words.append(x[0])
                self.disc.append(x[1])
            for i in range(len(self.words)):
                self.lst.append(self.words[i])
            #слова в алфавитном прядке
            self.words = sorted(self.words)
            #выводим слова на экран
            for i in range(len(self.words)):
                self.wordList.addItem(self.words[i])


    def selectionChanged(self, item):
        if item:
            ind = self.lst.index(item)
            self.answer.setText(self.disc[ind])


        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = OpenWindow()
    sys.exit(app.exec_())
