import sqlite3
import datetime
from calendar import monthrange
import termtables

conn = sqlite3.connect('site.db')

c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        ongoing INTEGER
        )""")

c.execute("""CREATE TABLE IF NOT EXISTS tracking (
        id INTEGER PRIMARY KEY,
        habit INTEGER,
        year TEXT,
        month TEXT,
        day TEXT,
        time TEXT,
        value INTEGER,
        FOREIGN KEY (habit)
        REFERENCES habits (id)
        ON UPDATE CASCADE 
        ON DELETE CASCADE
        )""")


class User:

    def __init__(self, name):
        self.name = name
        self.ongoing_habits = []


    def add_habit(self, habit_name):
        with conn:
            c.execute("INSERT INTO habits(name, ongoing) VALUES(?, ?)", (habit_name, 1))
        

    def display_ongoing_habits(self):
        res = []
        with conn:
            c.execute("SELECT * FROM habits WHERE ongoing=1")
            res = c.fetchall()
        if res:
            print(res)
        else:
            print("You currently don't have any ongoing habits.")
            return -1
    
    def track_habit(self, habit_id, day, month, year, value):
        ctime = datetime.datetime.now().time().strftime("%H:%M:%S")
        with conn:
            c.execute("INSERT INTO tracking(habit, year, month, day, time, value) VALUES(?, ?, ?, ?, ?, ?)", (habit_id, year, month, day, ctime, value))
    
    def display_month(self, month, year):
        n = monthrange(year, month)[1]
        table = []
        header = ['Habits']
        for i in range(1, n + 1):
            header.append(f'{i}')
        # table.append(header)
        ongoing_habits = []
        with conn:
            c.execute("SELECT * FROM habits WHERE ongoing=1")
            ongoing_habits = c.fetchall()
            for habit in ongoing_habits:
                temp = [habit[1]]
                for i in range(1, n + 1):
                    c.execute("SELECT * FROM tracking WHERE habit=? AND month=? AND day=?", (habit[0], month, i))
                    result = c.fetchone()
                    if result:
                        if result[6] == 0:
                            temp.append(' ') 
                        else:
                            temp.append('*')
                    else:
                        temp.append(' ')
                table.append(temp)

        termtables.print(table, header)
    

class Habit:
    def __init__(self, id, name, ongoing):
        self.name = name
        self.id = id
        self.ongoing = ongoing

user = User("root")

menu_options = {
    1: 'Track Today',
    2: 'Track a Date',
    3: 'Add a Habit',
    4: 'Remove a Habit',
    5: 'Display a month',
    6: 'Exit'
}

def print_menu():
    print()
    print("Menu: ")
    for key in menu_options.keys():
        print (key, '--', menu_options[key] )

def option1():
    tday = datetime.date.today()
    ongoing_habits = []
    with conn:
        c.execute("SELECT * FROM habits WHERE ongoing=1")
        ongoing_habits = c.fetchall()
    for habit in ongoing_habits:
        while True:
            ans = input(f"Did you complete {habit[1]} today?")
            if(ans.lower() == "yes"):
                user.track_habit(habit[0], str(tday.day), str(tday.month), str(tday.year), 1)
                break
            elif(ans.lower() == "no"):
                user.track_habit(habit[0], str(tday.day), str(tday.month), str(tday.year), 0)
                break
            else:
                print("Please enter either 'yes' or 'no'")
    print()
    print("Your progress of the current month:")
    user.display_month(tday.month, tday.year)    

def option2():
    day, month, year = input("Enter the date (day month year): ").split(' ')
    ongoing_habits = []
    with conn:
        c.execute("SELECT * FROM habits WHERE ongoing=1")
        ongoing_habits = c.fetchall()
    for habit in ongoing_habits:
        while True:
            ans = input(f"Did you complete {habit[1]}  on {day}/{month}/{year}?")
            if(ans.lower() == "yes"):
                user.track_habit(habit[0], day, month, year, 1)
                break
            elif(ans.lower() == "no"):
                user.track_habit(habit[0], day, month, year, 0)
                break
            else:
                print("Please enter either 'yes' or 'no'")
    print()
    print("Your progress of this month:")
    user.display_month(int(month), int(year))   

def option3():
    habit_name = input("Enter the habit you want to add: ")
    user.add_habit(habit_name)

if __name__=='__main__':
    ongoing_habits = []
    with conn:
        c.execute("SELECT * FROM habits WHERE ongoing=1")
        ongoing_habits = c.fetchall()
    if ongoing_habits:
        print("Currently ongoing habits: ")
        for habit in ongoing_habits:
            print(habit[0], '--', habit[1])
    else:
        print("You don't have any ongoing habits")
    while(True):
        print_menu()
        option = ''
        try:
            option = int(input('Enter your choice: '))
        except:
            print('Wrong input. Please enter a number ...')
        #Check what choice was entered and act accordingly
        if option == 1:
           option1()
        elif option == 2:
            option2()
        elif option == 3:
            option3()
        elif option == 6:
            exit()
        else:
            print('Invalid option. Please enter a number between 1 and 6.')

conn.commit()
conn.close()