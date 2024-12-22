import sqlite3
import shutil
import time
import os

from .utils import(
    DB_FILENAME,
    YEARS,
    MONTHS,
    CATEGORIES_AVAILABLE,
    MAIN_DIR
)

class DatabaseHandler:
    
    def __init__(self):
        self.db_file = DB_FILENAME
        
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                            month TEXT,
                            year TEXT,
                            day TEXT,
                            category TEXT,
                            value TEXT,
                            description TEXT
            )                   
        ''')
    
    def close_connection(self):
        self.conn.close()

    def add_entry(self, month: str, year: str, day: str, category: str, value: str, description: str):
        self.cursor.execute('INSERT INTO user_data VALUES (?, ?, ?, ?, ?, ?)',
                            (month, year, day, category, value, description))
        self.conn.commit()

    def delete_entry(self, month: str, year: str, day: str, category: str, value: str, description: str):
        self.cursor.execute('''DELETE FROM user_data WHERE 
                            month=? AND 
                            year=? AND
                            day=? AND
                            category=? AND
                            value=? AND
                            description=?
        ''',(month, year, day, category, value, description))
        self.conn.commit()
    
    def get_elements_period(self, month: str, year: str):
        self.cursor.execute('SELECT * FROM user_data WHERE month=? AND year=?',
                                       (month, year))
        items = self.cursor.fetchall()
        items_list = []
        for item in items:
            l = [elem for elem in item[2:]] # Getting just the important entries
            items_list.append(l)
        
        items_list.sort(key=lambda x: int(x[0])) #sorting list
        return items_list
    
    def get_cumulative_expenses_until_period(self, month: str, year: str):
        
        ## Create a list with all entries we should get
        periods = []
        to_break = False
        for y in YEARS:
            for m in MONTHS:
                if y == year and m == month:
                    to_break = True
                    break
                periods.append([m, y])
            if to_break:
                break        
        
        sql_query = 'SELECT * FROM user_data WHERE month=? AND year=?'
        items_list = {}
        for period in periods:
            m, y = period
            self.cursor.execute(sql_query, (m,y))
            items = self.cursor.fetchall()
            
            items_list[f"{m}|{y}"] = {}
            for category in CATEGORIES_AVAILABLE:
                items_list[f"{m}|{y}"][category] = 0.0 # Initialising with 0euros
            
            for item in items:
                category = item[3]
                value = float(item[4])
                items_list[f"{m}|{y}"][category] += value
                 
        return items_list
    
def CreateBackup():
    timestamp = time.strftime("%Y%m%d")
    
    db_basename = os.path.basename(DB_FILENAME)
    filename_backup = db_basename.replace(".db", f"_{timestamp}.db")
    
    backupDir = os.path.join(MAIN_DIR, "Backup")
    shutil.copy(
        DB_FILENAME, os.path.join(backupDir, filename_backup)
    )
    
    for file in os.listdir(backupDir):
        if ".db" in file and file != filename_backup:
            os.remove(os.path.join(backupDir, file))
            
    return True