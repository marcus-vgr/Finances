import sys
import numpy as np
import sqlite3

from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QComboBox, QLabel

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class DatabaseHandler:
    def __init__(self):
        self.db_file = "MyExpenses.db"
        
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                            month TEXT,
                            year TEXT,
                            day INT,
                            category TEXT,
                            value FLOAT,
                            description TEXT
            )                   
        ''')
    
    def close_connection(self):
        self.conn.close()

    def add_entry(self, month, year, day, category, value, description):
        self.cursor.execute('INSERT INTO user_data VALUES (?, ?, ?, ?, ?, ?)',
                            (month, year, day, category, value, description))
        self.conn.commit()

    def delete_entry(self, month, year, day, category, value, description):
        self.cursor.execute('''DELETE FROM user_data WHERE 
                            month=? AND 
                            year=? AND
                            day=? AND
                            category=? AND
                            value=? AND
                            description=?
        ''',(month, year, day, category, value, description))
        self.conn.commit()
    
    def get_elements_period(self, month, year):
        self.cursor.execute('SELECT * FROM user_data WHERE month=? AND year=?',
                                       (month, year))
        items = self.cursor.fetchall()
        return items

class ExpensesWindow(QMainWindow):
    def __init__(self, db_handler, month, year):
        super().__init__()

        self.db_handler = db_handler
        self.month = month
        self.year = year

        

class DateWindow(QMainWindow):

    closed = pyqtSignal() # This will be to emit a signal if this window is closed. This will be used to avoid closing the main window while this one is open.


    def __init__(self, db_handler, month, year):
        super().__init__()

        self.db_handler = db_handler
        self.month = month
        self.year = year
        
        self.setWindowTitle(f"Expenses of {self.month} {self.year}")
        self.setGeometry(500, 300, 600, 300)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(0)  # Set a smaller value for spacing

        """
        Interface to add expenses
        """
        self.h_layout_expense1 = QHBoxLayout()
        self.day = QLineEdit()
        self.day.setFixedWidth(120)
        self.day.setPlaceholderText("Day: ")
        self.day.setStyleSheet("color: gray") # Color is gray while no input
        self.day.textChanged.connect(lambda: self.day.setStyleSheet("color: black") if self.day.text() else self.day.setStyleSheet("color: gray")) 
        self.h_layout_expense1.addWidget(self.day)
        
        self.value = QLineEdit()
        self.value.setFixedWidth(120)
        self.value.setPlaceholderText("Value (€)")
        self.value.setStyleSheet("color: gray") # Color is gray while no input
        self.value.textChanged.connect(lambda: self.value.setStyleSheet("color: black") if self.value.text() else self.value.setStyleSheet("color: gray")) 
        self.h_layout_expense1.addWidget(self.value)

        self.description = QLineEdit()
        self.description.setFixedWidth(400)
        self.description.setPlaceholderText("Description...")
        self.description.setStyleSheet("color: gray") # Color is gray while no input
        self.description.textChanged.connect(lambda: self.description.setStyleSheet("color: black") if self.description.text() else self.description.setStyleSheet("color: gray")) 
        self.h_layout_expense1.addWidget(self.description)

        self.h_layout_expense2 = QHBoxLayout()
        self.category = QComboBox()
        self.category.addItems(["Category..."] + CATEGORIES)
        self.category.setCurrentText("Category...")
        self.category.setFixedWidth(120)
        self.h_layout_expense2.addWidget(self.category)

        self.expense_button = QPushButton("Add Expense")
        self.expense_button.setFixedWidth(130)
        self.expense_button.clicked.connect(self.add_expense)
        self.h_layout_expense2.addWidget(self.expense_button)

        self.label_confirm_info = QLabel() # Adding a label right next to the Add Expense button. It will show, for limited time, if info was added or not.
        self.h_layout_expense2.addWidget(self.label_confirm_info)
        self.timer_label = QTimer()
        self.timer_label.setSingleShot(True)
        self.timer_label.timeout.connect(lambda: self.label_confirm_info.clear())

        self.h_layout_expense1.setSpacing(6) # space between the blank spaces and button
        self.h_layout_expense1.addStretch() # align to the left
        self.layout.addLayout(self.h_layout_expense1)
        self.h_layout_expense2.setSpacing(6) # space between the blank spaces and button
        self.h_layout_expense2.addStretch() # align to the left
        self.layout.addLayout(self.h_layout_expense2)

        """
        Add Button to pop-up all expenses of the month
        """
        self.button_show_expenses = QPushButton("Show all expenses of the month")
        self.button_show_expenses.clicked.connect(self.show_expenses)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.button_show_expenses)


        """
        Adding figure with the plot summary
        """
        self.figure_summary_date = Figure(figsize=(6,4), dpi=100)
        self.canvas_summary_date = FigureCanvasQTAgg(self.figure_summary_date)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.canvas_summary_date)
        self.plotSummaryDate()
        self.timer_plotSummary = QTimer() # Put timer to always update plot summary
        self.timer_plotSummary.timeout.connect(self.plotSummaryDate)
        self.timer_plotSummary.start(3000) #3 seconds

        self.central_widget.setLayout(self.layout)

    def closeEvent(self, event):
        # Override closeEvent to avoid closing the main window while this one is open
        self.closed.emit() #Emit signal so that the main window knows this one is now closed.
        event.accept() 

    def add_expense(self):
        day = self.day.text()
        value = self.value.text()
        description = self.description.text()
        category = self.category.currentText()
        
        infoValid = False
        try:  # Checking if all info given by the user makes sense
            value = float(value)
            if day.isdigit():
                day = int(day)
                if value > 0 and day > 0 and day < 32 and description != "" and category in CATEGORIES:
                    infoValid = True
        except:
            pass            

        self.timer_label.start(3000) #3 seconds for the label timer
        if infoValid > 0:
            self.label_confirm_info.setStyleSheet("color: green")
            self.label_confirm_info.setText("Expense added "+u'\u2713') #\u2713 is unicode for the checkmark

            self.db_handler.add_entry(self.month, self.year, day, category, value, description)
        else:
            self.label_confirm_info.setStyleSheet("color: red")
            self.label_confirm_info.setText("Information not valid...")
        

    def show_expenses(self):
        self.db_handler.cursor.execute('SELECT * FROM user_data WHERE month=? AND year=?',
                                       (self.month, self.year))
        expenses = self.db_handler.cursor.fetchall()
        for expense in expenses:
            print(expense)

    def plotSummaryDate(self):
        self.figure_summary_date.clear()
        
        ax = self.figure_summary_date.add_subplot(111)
        ax.text(0.5, 0.5, 'PLACEHOLDER '+str(np.random.random()), fontsize=10, ha='center', va='center')
        
        self.canvas_summary_date.draw()

class ExpenseManager(QMainWindow):
    def __init__(self, db_handler):
        super().__init__()

        self.date_window = None
        self.db_handler = db_handler

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
        #self.input_month.setCurrentText("Month...")
        self.input_month.setCurrentText("January")
        self.input_month.setFixedWidth(100)
        self.h_layout_input.addWidget(self.input_month)
        
        self.input_year = QComboBox()
        self.input_year.addItems(["Year..."] + self.YEARS)
        #self.input_year.setCurrentText("Year...")
        self.input_year.setCurrentText("2024")
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

    def closeEvent(self, event): 
        # Override closeEvent to ensure database closure when closing main window
        # Also be sure the Date window is already closed.
        if self.date_window is not None: 
            event.ignore()
        else:
            self.db_handler.close_connection()
            event.accept()

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

        self.date_window = DateWindow(self.db_handler, month, year)
        self.date_window.closed.connect(self.close_WindowDate)
        self.date_window.show()
    
    def close_WindowDate(self):
        self.date_window = None

    def plotSummaryAllMonths(self):
        self.figure_summary_all.clear()
        
        ax = self.figure_summary_all.add_subplot(111)
        ax.text(0.5, 0.5, 'PLACEHOLDER '+str(np.random.random()), fontsize=10, ha='center', va='center')
        ax.set_title("Average of expenses till [MONTH/YEAR]")
        
        self.canvas_summary_all.draw()



def main():
    app = QApplication(sys.argv)
    db_handler = DatabaseHandler()
    window = ExpenseManager(db_handler)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    CATEGORIES = ["Home", "Travel", "Food", "Leisure", "To myself", "Education", "Others"]
    main()
