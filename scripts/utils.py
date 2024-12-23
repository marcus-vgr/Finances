import os


MAIN_DIR = os.path.join(os.path.dirname(__file__), '../')

CATEGORIES_AVAILABLE = [
    "Home", "Food", "Leisure", "To myself", "Travel", "Education", "Others",
]
DICT_CATEGORIES_NAMETOLOWER = {
    c:c.lower().replace(' ','') for c in CATEGORIES_AVAILABLE
}
DICT_CATEGORIES_LOWERTONAME = {
    lower:name for name,lower in DICT_CATEGORIES_NAMETOLOWER.items()
}
YEARS = [str(y) for y in range(2024, 2031)]
MONTHS = [
    "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December",
]
DICT_MONTHS_NAMETONUMBER = {name:number+1 for number,name in enumerate(MONTHS)}
DICT_MONTHS_NUMBERTONAME = {number+1:name for number,name in enumerate(MONTHS)}

with open(os.path.join(MAIN_DIR, ".tokenTelegram"), "r") as f:
    API_TELEGRAM_BOT = f.readlines()[0].strip()
    
DB_FILENAME = os.path.join(MAIN_DIR, "MyExpenses.db")

FONT = "PT Mono"