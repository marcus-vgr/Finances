import sys

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QComboBox

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np


class ExpenseManager(QMainWindow):
    def __init__(self):
        super().__init__()

        self.getPrivateConstants()

        self.setWindowTitle('My Expenses')
        self.setGeometry(400, 200, 600, 300)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        """
        Adding buttons to put date information
        """
        self.h_layout_input = QHBoxLayout() # Creating horizontal summary for the buttons
        
        self.input_month = QComboBox()
        self.input_month.addItems(["Month..."] + self.MONTHS)
        self.input_month.setCurrentText("Month...")
        self.input_month.setFixedWidth(100)
        self.h_layout_input.addWidget(self.input_month)
        
        self.input_year = QComboBox()
        self.input_year.addItems(["Year..."] + self.YEARS)
        self.input_year.setCurrentText("Year...")
        self.input_year.setFixedWidth(80)
        self.h_layout_input.addWidget(self.input_year)
        
        self.button_WindowDate = QPushButton("Go")
        self.button_WindowDate.setFixedWidth(50)
        self.button_WindowDate.clicked.connect(self.open_WindowDate)
        self.h_layout_input.addWidget(self.button_WindowDate)
        
        self.h_layout_input.setSpacing(6) # space between the blank spaces and button
        self.h_layout_input.addStretch() # align to the left
        self.layout.addLayout(self.h_layout_input)

        """
        Adding figure with the plot summary
        """
        self.figure_summary_all = Figure(figsize=(6,4), dpi=100)
        self.canvas_summary_all = FigureCanvasQTAgg(self.figure_summary_all)
        self.layout.addWidget(self.canvas_summary_all)
        self.plotSummaryAllMonths()
        self.timer_plotSummary = QTimer() # Put timer to always update plot summary
        self.timer_plotSummary.timeout.connect(self.plotSummaryAllMonths)
        self.timer_plotSummary.start(3000) #3 seconds


        self.central_widget.setLayout(self.layout)

    def getPrivateConstants(self):
        self.MONTHS = [
                        "January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December"
                    ]
        self.YEARS  = [str(y) for y in range(2024, 2031)]

    def open_WindowDate(self):
        month = self.input_month.currentText() 
        year  = self.input_year.currentText()
        if month not in self.MONTHS or year not in self.YEARS:
            return

        print(month, year)


    def plotSummaryAllMonths(self):
        self.figure_summary_all.clear()
        
        ax = self.figure_summary_all.add_subplot(111)
        ax.text(0.5, 0.5, 'PLACEHOLDER', fontsize=20, ha='center', va='center')
        ax.set_title("Average of expenses till [MONTH/YEAR]")
        
        self.canvas_summary_all.draw()


def main():
    app = QApplication(sys.argv)
    window = ExpenseManager()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
