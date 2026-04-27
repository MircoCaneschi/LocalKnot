from PySide6.QtCore import QSize, QTimer
from PySide6.QtWidgets import (QSizePolicy ,QApplication, QMainWindow, QToolBar, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
                               QLabel, QLineEdit)
from PySide6.QtGui import QIcon, QAction


class FinestraPrinc(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app=app
        self.setWindowTitle("Finestra")

        self.statusBar()

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("file")
        quit_action = file_menu.addAction("quit")
        quit_action.triggered.connect(self.quit_app)

        self.voce2 = menu_bar.addMenu("voce2")
        modificaV2 = self.voce2.addAction("modifica")
        copiaV2 = self.voce2.addAction("copia")
        pippoV2 = self.voce2.addAction("pippo")
        ciaoV2 = self.voce2.addAction("ciao")
        ciaoV2.triggered.connect(self.saluta)

        menu_bar.addMenu("heeelp")
        menu_bar.addMenu("puppe")

        barra_tool = QToolBar("Barra degli strumenti")
        barra_tool.setIconSize(QSize(50, 40))
        self.addToolBar(barra_tool)

        barra_tool.addAction(quit_action) #usa la stessa action definita prima
        # 1. Assegna un'icona all'azione
        quit_action.setIcon(QIcon(r"C:\Users\mirco\OneDrive\Desktop\UNI\stage\codice progetto\pirateLogo2.png"))

        barra_tool.addSeparator()

        action1 = QAction("delle azioni", self)
        action1.setStatusTip("questa è un'azione di esempio")
        action1.triggered.connect(self.toolbar_button_click)
        barra_tool.addAction(action1)

        action2 = QAction(QIcon(r"C:\Users\mirco\OneDrive\Desktop\UNI\stage\codice progetto\pirateLogo2.png"), "azione con icona", self)
        action2.setStatusTip("questa è un'azione con icona")
        action2.triggered.connect(self.toolbar_button_click)
        action2.setCheckable(True)
        barra_tool.addAction(action2)

        barra_tool.addSeparator()
        barra_tool.addWidget(QPushButton("bottone separato"))

        self.count = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.increment_counter)
        timerButton = QPushButton("timer button")
        #self.setCentralWidget(timerButton)
        timerButton.pressed.connect(self.start_Timer)
        timerButton.released.connect(self.stop_Timer)

        corePart=QWidget()
        self.setCentralWidget(corePart)
        orizonatalLayout = QHBoxLayout()

        label = QLabel("labelllollolool")
        self.lineEdit = QLineEdit()
        self.lineEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.addWidget(label,1)
        self.verticalLayout.addWidget(self.lineEdit,1)
        orizonatalLayout.addLayout(self.verticalLayout,1)
        orizonatalLayout.addWidget(timerButton,0)
        corePart.setLayout(orizonatalLayout)


        self.showMaximized()



    def saluta(self):
        print("ciao a te!")
        sorpresaV2 = self.voce2.addAction("sorpresa!")
        self.verticalLayout.addWidget(QLabel("testo apparso"))

    def quit_app(self):
        self.app.quit()

    def toolbar_button_click(self):
        print("action1 triggerd")

    def start_Timer(self):
        self.count = 0
        self.timer.start(100)  # Incrementa ogni 100 ms

    def stop_Timer(self):
        self.timer.stop()
        print(f"Conteggio finale: {self.count}")

    def increment_counter(self):
        self.count += 1