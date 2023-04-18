import sys
import sqlite3
from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QWidget,
    QApplication,
    QLineEdit,
    QPushButton,
    QListWidget,
    QCalendarWidget,
    QListWidgetItem,
    QLabel,
    # QCheckBox
)


class application(QWidget):
    def __init__(self):
        super(application, self).__init__()
        loadUi("main.ui", self)
        self.add_btn: QPushButton
        self.save_btn: QPushButton
        self.calendar: QCalendarWidget
        self.calendar.selectionChanged.connect(self.datechanged)
        self.datechanged()
        self.save_btn.clicked.connect(self.Save)
        self.add_btn.clicked.connect(self.addNew)
        # ! self.itemList.itemChanged.connect(self.auto_save) DB locked error.

    def datechanged(self):
        self.calendar: QCalendarWidget
        global dateSelected
        dateSelected = self.calendar.selectedDate().toPyDate()
        self.DB(dateSelected)
        self.yesterdaysTasks()

    def DB(self, date):
        self.itemList: QListWidget
        self.itemList.clear()
        db = sqlite3.connect("db/todo.db")
        cursor = db.cursor()
        query = "SELECT task, completed from todo WHERE date = ?"
        row = (date,)
        results = cursor.execute(query, row).fetchall()

        for result in results:
            item = QListWidgetItem(str(result[0]))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)  # noqa

            if result[1] == "Yes":
                item.setCheckState(QtCore.Qt.Checked)
                font = item.font()
                font.setStrikeOut(True)
                item.setFont(font)

            if result[1] == "No":
                item.setCheckState(QtCore.Qt.Unchecked)

            self.itemList.addItem(item)

    def Save(self):
        self.print_lbl: QLabel
        db = sqlite3.connect("db/todo.db")
        cursor = db.cursor()
        date = self.calendar.selectedDate().toPyDate()

        for index in range(self.itemList.count()):
            item = self.itemList.item(index)
            task = item.text()

            if item.checkState() == QtCore.Qt.Checked:
                font = item.font()
                font.setStrikeOut(True)
                item.setFont(font)
                query = "UPDATE todo SET completed = 'Yes' WHERE task = ? AND date = ?"  # noqa
                row = (task, date,)
                cursor.execute(query, row)
                row = (task, date2,)
                cursor.execute(query, row)
            elif item.checkState() == QtCore.Qt.Unchecked:

                query = "UPDATE todo SET completed = 'No' WHERE task = ? AND date = ?"  # noqa
                row = (task, date,)
                cursor.execute(query, row)

            self.print_lbl.setText("Kayıt Edildi.")

        db.commit()
        self.datechanged()

    def addNew(self):
        self.print_lbl: QLabel
        self.addItem_edit: QLineEdit

        db = sqlite3.connect("db/todo.db")
        cursor = db.cursor()
        newTask = self.addItem_edit.text()
        date = self.calendar.selectedDate().toPyDate()
        query = "INSERT INTO todo(task, completed, date) VALUES (?, ?, ?)"
        row = (newTask, "No", date)

        cursor.execute(query, row,)
        self.print_lbl.setText("Yeni Görev Eklendi.")
        db.commit()

    def yesterdaysTasks(self):
        self.print_lbl: QLabel
        db = sqlite3.connect("db/todo.db")
        cursor = db.cursor()
        date = dateSelected.strftime("%Y-%m-%d")
        spldate = date.split("-")
        day = int(date.split("-")[2]) - 1
        global date2
        date2 = spldate[0] + "-" + spldate[1] + "-" + str(day)
        query = "SELECT task, completed from todo WHERE date = ?"
        row = (date2,)
        results = cursor.execute(query, row).fetchall()
        for result in results:
            item = QListWidgetItem(str(result[0]))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)  # noqa
            if result[1] == "No":
                item.setCheckState(QtCore.Qt.Unchecked)
                self.itemList.addItem(item)
                self.print_lbl.setText("Tamamlanmamış Görevler Eklendi.")

    """def auto_save(self):
        self.autosave: QCheckBox
        if self.autosave.isChecked():
            self.Save()  # Auto Save"""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = application()
    screen.show()
    sys.exit(app.exec_())
