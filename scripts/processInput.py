from datetime import datetime
import re

from .utils import (
    DICT_MONTHS_NUMBERTONAME,
    DICT_CATEGORIES_LOWERTONAME,
    DICT_CATEGORIES_NAMETOLOWER,
)

class UserInputProcessor:
    def __init__(self, message: str, debug: bool=False):
        """
        We expect from the user a message like
        "DD/MM/YYYY; VALUE; CATEGORY; DESCRIPTION"
        """
        self.message = message
        self.debug = debug
    
        self.day = None
        self.month = None
        self.year = None
        self.value = None
        self.category = None
        self.description = None
 
        self.processMessage()
        self.isValid = self.isValid()
        
    def isValid(self):
        """
        If any of the message attributes is None, return False
        """
        attrib_list = [
            "day", "month", "year", "value", "category", "description",
        ]
        for attrib in attrib_list:
            if getattr(self, attrib) is None:
                return False
        return True
    
    def processMessage(self):
        split_message = self.message.split(';')
        if len(split_message) != 4:
            if self.debug:
                print(f"""
                '''{self.message}''' doesn't have format  'DD/MM/YYYY; VALUE; CATEGORY; DESCRIPTION' 
                """)
            return None

        self.processDate(split_message[0].strip())
        self.processValue(split_message[1].strip())
        self.processCategory(split_message[2].strip())
        self.processDescription(split_message[3].strip())
                
    def processDate(self, dateString: str):
        try:
            date = datetime.strptime(dateString, "%d/%m/%Y") 
            self.day = f"{date.day:02}" #Number with two digits
            self.month = DICT_MONTHS_NUMBERTONAME[date.month]
            self.year = date.year
        except ValueError:
            if self.debug:
                print(f"""
                    '{dateString}' isn't a valid 'DD/MM/YYYY' date.
                """)
                
    def processValue(self, valueString: str):
        """
        Value should be integer or float of at most 2 decimal places.
        We accept addition operation e.g. "2 + 4.50"
        """
        values = [value for value in valueString.split('+')]
        
        validValues = True
        value_pattern = r"^\d+(\.\d{1,2})?$"
        for value in values:
            if not re.match(value_pattern, value):
                validValues = False
        if validValues:
            self.value = f"{sum([float(v) for v in values]):.2f}" 
        else:
            if self.debug:
                print(f"""
                    '''{valueString}''' isn't a valid value ($$).
                """)   
    
    def processCategory(self, categoryString: str):
        """
        Check if a valid category was given.
        """
        categoryString = categoryString.lower().replace(' ', '')
        if categoryString in DICT_CATEGORIES_NAMETOLOWER.values():
            self.category = DICT_CATEGORIES_LOWERTONAME[categoryString]
        else:
            if self.debug:
                print(f"""
                    '''{categoryString}''' isn't a valid category.
                """)  
    
    def processDescription(self, descriptionString: str):
        """ 
        Check if any description was provided.
        """
        descriptionString = descriptionString.strip()
        if descriptionString:
            self.description = descriptionString
        else:
            if self.debug:
                print("No description of expense was given.")
        

if __name__ == "__main__":
    message_string = "24/12/2024; 35.00+45.1+3; OTHeRs; This is a test :) "
    message = UserInputProcessor(message_string, debug=True)
    print(message.isValid)