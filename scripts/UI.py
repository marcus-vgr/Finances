import sys
import time
import numpy as np

from PyQt5.QtCore import QTimer, pyqtSignal, QPoint
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QComboBox, QLabel, QListWidget, QListWidgetItem
from PyQt5.QtGui import QFont

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from .utils import(
    FONT,
    CATEGORIES_AVAILABLE,
    YEARS,
    MONTHS,
    DICT_MONTHS_NAMETONUMBER,
)
from .database import(
    DatabaseHandler,
    CreateBackup,
)
from .processInput import(
    UserInputProcessor
)

plt.rcParams.update({
        "font.family": FONT,
        "font.size": 9,
})

class ExpensesWindow(QMainWindow):
    def __init__(self, db_handler, month, year):
        super().__init__()

        self.db_handler = db_handler
        self.month = month
        self.year = year
        self.items = self.db_handler.get_elements_period(self.month, self.year)
        
        self.setWindowTitle(f"Expenses of {self.month} {self.year}")
        self.setGeometry(550, 300, 800, 400)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        
        self.h_layout = QHBoxLayout()
        sort_label = QLabel("Sort by: ")
        self.sort_by_date_button = QPushButton()
        self.sort_by_date_button.setFixedWidth(35)
        sort_date_label = QLabel(" date ")
        self.sort_by_category_button = QPushButton()
        self.sort_by_category_button.setFixedWidth(35)
        sort_category_label = QLabel(" category ")
        self.sort_by_date_button.setCheckable(True)
        self.sort_by_category_button.setCheckable(True)
        self.sort_by_date_button.clicked.connect(self._sort_by_date)
        self.sort_by_category_button.clicked.connect(self._sort_by_category)
        self.sort_by_date_button.setChecked(True)
        self.sort_by_category_button.setChecked(False)
        self.h_layout.addWidget(sort_label) 
        self.h_layout.addWidget(self.sort_by_date_button)
        self.h_layout.addWidget(sort_date_label)
        self.h_layout.addWidget(self.sort_by_category_button)
        self.h_layout.addWidget(sort_category_label)
        self.h_layout.addStretch() # align to the left
    
        self.list_widget = QListWidget()
        self.sorting_type = "date"
        self.write_expenses_window()
    
        self.layout.addLayout(self.h_layout)
        self.layout.addWidget(self.list_widget)
        self.central_widget.setLayout(self.layout)

    def _sort_by_date(self):
        self.sort_items("date")
        self.sort_by_category_button.setChecked(False)
        self.write_expenses_window()
        # Keep checked
        self.sort_by_date_button.setChecked(True)
        
    def _sort_by_category(self):
        self.sort_items("category")
        self.sort_by_date_button.setChecked(False)
        self.write_expenses_window()
        # Keep checked
        self.sort_by_category_button.setChecked(True)

    def sort_items(self, method):   # Sort self.items based on button choice
        if method == "date":
            self.items = sorted(self.items, key=lambda x: int(x[0]))
        elif method == "category":
            self.items = sorted(self.items, key=lambda x: CATEGORIES_AVAILABLE.index(x[1]))

    def make_printing_nice(self):
        #Making our printing nice in the table. So everything is well separated in tabs
        #items_print and self.items MUST have the same ordering!!
        
        items_print = []
        for item in self.items:
            day, category, value, description = item
            cols_days = 5
            cols_category = 15
            cols_values = 10
            
            line = day + " "*(cols_days-len(day))
            line += category + " "*(cols_category-len(category))
            line += value + " "*(cols_values-len(value))
            line += description
            
            items_print.append(line)
        return items_print


    def write_expenses_window(self):
        
        self.list_widget.clear()
        self.items_print = self.make_printing_nice()

        for item in self.items_print:
            
            label_item = QLabel(item)
            label_item.setFixedWidth(500)
        
            delete_button = QPushButton("Delete")
            delete_button.setStyleSheet("color: red")
            delete_button.setFixedWidth(100)
            delete_button.clicked.connect(self.delete_item)

            h_layout = QHBoxLayout()
            h_layout.addWidget(QLabel(item))
            h_layout.addWidget(delete_button)
            item_widget = QWidget()
            item_widget.setLayout(h_layout)

            list_item = QListWidgetItem()
            sizeHint = item_widget.sizeHint()
            sizeHint.setHeight(40)
            list_item.setSizeHint(sizeHint)
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)

        
    def delete_item(self):

        clicked_signal = self.sender() # Get which button sent a signal
        globalPoint = clicked_signal.mapToGlobal(QPoint())
        localPoint = self.list_widget.viewport().mapFromGlobal(globalPoint) # Finding which row of the list our clicked widget is
        widget = self.list_widget.itemAt(localPoint) # Getting the widget
        item = self.list_widget.itemWidget(widget).findChild(QLabel).text() #Getting the QLabel.text() of the widget 
        self.list_widget.takeItem( self.list_widget.row(widget) ) #Exclude widget from list 
        
        for idx in range(len(self.items_print)): #Finding the info of the item based on idx of the print list 
            if self.items_print[idx] == item:
                expense_to_exclude = self.items[idx]
                break
        self.db_handler.delete_entry(self.month, self.year, *expense_to_exclude)

  
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
        self.category.addItems(["Category..."] + CATEGORIES_AVAILABLE)
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
        self.figure_summary_date.set_tight_layout(True)
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
        
        date = f"{day}/{DICT_MONTHS_NAMETONUMBER[self.month]}/{self.year}"
        message = f"{date}; {value}; {category}; {description}"
        info = UserInputProcessor(message, debug=True)
        
        self.timer_label.start(3000) #3 seconds for the label timer
        if info.isValid:
            self.label_confirm_info.setStyleSheet("color: green")
            self.label_confirm_info.setText(f"Expense {category}/{info.value}€ added "+u'\u2713') #\u2713 is unicode for the checkmark
            
            self.db_handler.add_entry(
                month=info.month, 
                year=info.year,
                day=info.day, 
                category=info.category, 
                value=info.value, 
                description=info.description,
            )

            self.day.setText("") # Back to default
            self.value.setText("")
            self.description.setText("")
            self.category.setCurrentText("Category...")

        else:
            self.label_confirm_info.setStyleSheet("color: red")
            self.label_confirm_info.setText("Information not valid...")
        

    def show_expenses(self):
        self.expenses_window = ExpensesWindow(self.db_handler, self.month, self.year)
        self.expenses_window.show()

    def plotSummaryDate(self):
        self.figure_summary_date.clear()
        ax = self.figure_summary_date.add_subplot(111)
        
        expenses = self.db_handler.get_elements_period(self.month, self.year)
        if len(expenses) > 0:
            dict_expenses = {}
            for category in CATEGORIES_AVAILABLE:
                total = 0.0
                for expense in expenses:
                    if expense[1] == category:
                        total += float(expense[2])
                dict_expenses[category] = total
            
            types_expenses = list(dict_expenses.keys())
            values_expenses = list(dict_expenses.values())
            ax.bar(types_expenses, values_expenses, color='#5688e5')
            for day, value in zip(types_expenses, values_expenses):
                ax.text(day, value + 0.1, "{:.2f}€".format(value), ha='center', va='bottom')

            ax.set_title("Total: {:.2f}€".format(sum(values_expenses)), loc='right')
            ax.set_ylim(top=1.15*max(values_expenses))
        else:
            ax.text(0.5, 0.5, "No expenses so far", fontsize=10, ha='center', va='center')
        
        ax.get_yaxis().set_visible(False)
        self.canvas_summary_date.draw()


class ConfirmationDateWindow(QMainWindow):
    
    proceedAction = pyqtSignal(bool)

    def __init__(self, month_selected, year_selected, month_today, year_today):
        super().__init__()
  
        self.month_selected = month_selected
        self.year_selected = year_selected
        self.month_today = month_today
        self.year_today = year_today
        
        self.setGeometry(600, 250, 300, 150)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        
        self.label = QLabel(f"You selected {self.month_selected}/{self.year_selected} but today is {self.month_today}/{self.year_today}.\nDo you want to continue?")
        self.layout.addWidget(self.label)

        self.buttons_layout = QHBoxLayout()
        self.accept = QPushButton(u'\u2713')
        self.accept.setFixedWidth(130)
        self.accept.setStyleSheet("color: green; font: bold 30px")
        self.accept.clicked.connect(self.__accept)
        self.cancel = QPushButton("X")
        self.cancel.setFixedWidth(130)
        self.cancel.setStyleSheet("color: red; font: bold 30px")
        self.cancel.clicked.connect(self.__cancel)
        self.buttons_layout.addWidget(self.accept)
        self.buttons_layout.addWidget(self.cancel)
        
        self.layout.addLayout(self.buttons_layout)
        self.central_widget.setLayout(self.layout)

    def __accept(self):
        self.proceedAction.emit(True)
        self.close()
        
    def __cancel(self):
        self.proceedAction.emit(False)
        self.close()

class ExpenseManager(QMainWindow):
    def __init__(self, db_handler):
        super().__init__()

        self.date_window = None
        self.db_handler = db_handler

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
        self.input_month.addItems(["Month..."] + MONTHS)
        self.input_month.setCurrentText("Month...")
        self.input_month.setFixedWidth(100)
        self.h_layout_input.addWidget(self.input_month)
        
        self.input_year = QComboBox()
        self.input_year.addItems(["Year..."] + YEARS)
        currentYear = time.strftime("%Y")
        self.input_year.setCurrentText(currentYear)
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
        self.figure_summary_all.set_tight_layout(True)
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

    def open_WindowDate(self):
        month = self.input_month.currentText() 
        year  = self.input_year.currentText()
        if month not in MONTHS or year not in YEARS:
            return

        year_today, month_today = time.strftime("%Y,%m").split(',')
        month_today = MONTHS[int(month_today)-1] #Convert to proper month name
        
        if month_today != month or year_today != year:
            self.confirmation_window = ConfirmationDateWindow(month, year, month_today, year_today)
            self.confirmation_window.proceedAction.connect(lambda accept_date: self.onConfirmationWindow(accept_date, month, year))
            self.confirmation_window.show()
        else:
            self.onConfirmationWindow(True, month, year)

    def onConfirmationWindow(self, accept_date, month, year):
        if accept_date:
            self.date_window = DateWindow(self.db_handler, month, year)
            self.date_window.closed.connect(self.close_WindowDate)
            self.date_window.show()
        
        
    def close_WindowDate(self):
        self.date_window = None

    def plotSummaryAllMonths(self):
        self.figure_summary_all.clear()
        
        year, month = time.strftime("%Y,%m").split(',')
        month_label = MONTHS[int(month)-2] # The name of the month before, for the plot
        year_label = year if month_label != "December" else str( int(year)-1 )
        month = MONTHS[int(month)-1] #Convert to proper month name 
        
        items = self.db_handler.get_cumulative_expenses_until_period(month, year)
        ax = self.figure_summary_all.add_subplot(111)
        if len(items) > 0:
            types_expenses = CATEGORIES_AVAILABLE.copy()
            values_expenses = []
            for category in CATEGORIES_AVAILABLE:
                aux = [items[key][category] for key in items.keys()]
                mean, std = np.mean(aux), np.std(aux)
                values_expenses.append([mean, std])

            values_expenses = np.array(values_expenses)
            ax.bar(types_expenses, values_expenses.T[0], color='#5688e5')
            ax.errorbar(range(len(types_expenses)), values_expenses.T[0], yerr=values_expenses.T[1], 
                        fmt='.', color='black', capsize=2, alpha=0.3)
            for day, value, std in zip(types_expenses, values_expenses.T[0], values_expenses.T[1]):
                ax.text(day, value+std + 75, "{:.2f}€".format(value), ha='center', va='bottom')
                ax.text(day, value+std + 0.5, "(±{:d}€)".format(int(std)), ha='center', va='bottom', fontsize=7)

            ax.set_title(f"Average of expenses until {month_label} {year_label}"+" [Total: {:.2f}€]".format(sum(values_expenses.T[0])), loc='right')
            
            value_plus_std = np.sum(values_expenses, axis=1)
            ax.set_ylim(top=1.25*max(value_plus_std))
            
        else:
            ax.text(0.5, 0.5, "No expenses so far", fontsize=10, ha='center', va='center')

        
        self.canvas_summary_all.draw()



def mainUI():
    CreateBackup()
    app = QApplication(sys.argv)
    app.setFont(QFont(FONT))
    db_handler = DatabaseHandler()
    window = ExpenseManager(db_handler)
    window.show()
    sys.exit(app.exec_())