'''
Copyright (c) 2020 Yashovardhan Dhanania 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

==================================================================================


Library:-
Open from 9-5 Monday - Saturday
counters - 2 (for both check out and check in)
Each counter takes from 1 - 2 time units for checkout;
                        2 - 5 time units for late checkin
                        1 - 3 time units for checkin;
                        5 - 10 time units for lost books

Books:-
Total Books - 10000 (2000 books, 5 copies of each)
New copies of existing books may be added about every 60*24*15 time units
Books are issud for 60*24*15 time units
Lost books are not replaced

Students:-
Total students - 5000
Students can borrow a max of 3 books at a time
Students come looking for a particular book at a time and will return if they can't find it
Probability of losing the book - 0.001
Time taken before starting to look for a book:-
                                expo distribution
                                mean = 60*24*30*(books_borrowed + 1) time units
Time taken for returning a book:-
                                Normal distribution:-
                                mean = 60*24*15 time units
                                standard deviation = 100 time units

Time taken to look for a book = 1 - 10 time units


Stats to track:-
* No. of total books over time (Available+Borrowed - Lost)
* No. of books borrowed over time
* Average time books are borrowed for
* Frequency with which books are lost

Assuming time is in minutes
1 hour = 60 units
t=0 => Monday 00:00
t=1 => Monday 00:01
t=60 => Monday 01:00
t=540 => Monday 09:00
t=1020 => Monday 17:00
t=1440 => Tuesday 00:00
t=6 Days => Sunday 00:00
'''

ONE_HOUR = 60
ONE_DAY = 24*ONE_HOUR
ONE_WEEK = 7*ONE_DAY
SUNDAY = ONE_DAY*6
OPENING_TIME = 9*ONE_HOUR
CLOSING_TIME = 17*ONE_HOUR

MEAN_PATIENCE = 20
PATIENCE_SD = 5

BORROW_DURATION = ONE_DAY*15

RANDOM_SEED = 42
TOTAL_STUDENTS = 5000
TOTAL_BOOKS = 10000
BOOK_TITLES = 2000
NEW_BOOK_INTERVAL = ONE_DAY*15

BOOKS_BORROWED_MEAN = ONE_DAY*30
PROB_STUD_NEEDS_BOOK = 0.5
MIN_TIME_BOOK_SEARCH = 1
MAX_TIME_BOOK_SEARCH = 10

BOOKS_RETURN_MEAN = BORROW_DURATION
BOOKS_RETURN_SD = ONE_DAY

PROB_LOSE_TRESHOLD = 0.001
MAX_BOOKS_ALLOWED = 3
COUNTERS = 2
LOGS_ENABLED = False # Change this to enable logging

CHECKOUT_MIN_TIME = 1
CHECKOUT_MAX_TIME = 2
CHECKIN_MIN_TIME = 1
CHECKIN_MAX_TIME = 3
LATE_CHECKIN_MIN = 2
LATE_CHECKIN_MAX = 5
LOST_TIME_MIN = 5
LOST_TIME_MAX = 10

RUN_DURATION = ONE_DAY*365

import random
import simpy
from simpy.util import start_delayed
import enum
from faker import Faker

books_lost_count = 0
borrowed_books_count = 0
returned_books_count = 0
books_return_time = 0
lost_patience_counts = 0

fake = Faker()
Faker.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)


class Status(enum.Enum): # Book status
    AVAILABLE = 0
    BORROWING = 1
    BORROWED = 2
    RETURNING = 3
    LOST = 4

available_books = {}
book_names = []
students = []


class Book:
    def __init__(self, id, name, status, due_date, borrower):
        self.id = id
        self.name = name
        self.status = status
        self.resouce = simpy.Resource(env, capacity= 1)
        self.due_date = due_date
        self.borrower = borrower
        self.req = None

class Student:
    def __init__(self, id, name, env):
        self.id = id
        self.name = name
        self.env = env
        self.books_borrowed = []
        self.action = env.process(self.run())
        self.free = env.event()
        self.patience = random.normalvariate(MEAN_PATIENCE, PATIENCE_SD)
        if(self.patience < 0):
            self.patience = 0
        self.books_probability = random.expovariate(1 / PROB_STUD_NEEDS_BOOK)
        self.books_probability = 1 if (self.books_probability > 1) else self.books_probability
    
    def checkin_book(self, book): # Checking in book process
        # global LOGS_ENABLED
        if(LOGS_ENABLED):
            print("Day %03d Student %s is reading %s" %(self.env.now//ONE_DAY, self.name, book.name))
        reading_time = random.normalvariate(BOOKS_RETURN_MEAN, BOOKS_RETURN_SD)
        if(reading_time < ONE_HOUR): # Reading time is dependent on a random normal distribution
            reading_time = ONE_HOUR
        yield self.env.timeout(reading_time)
        
        if((env.now % ONE_DAY) < OPENING_TIME): # If Library is not yet open
            yield self.env.timeout(random.uniform(OPENING_TIME, CLOSING_TIME) - self.env.now%ONE_DAY)
        elif((self.env.now%ONE_DAY) > CLOSING_TIME): # Library is closed
            yield self.env.timeout(ONE_DAY + (random.uniform(OPENING_TIME, CLOSING_TIME)) - self.env.now%ONE_DAY)
        if(self.env.now%ONE_WEEK >= SUNDAY): # It's sunday!
            yield env.timeout(ONE_DAY + random.uniform(OPENING_TIME, CLOSING_TIME) - self.env.now%ONE_DAY)
        
        if(LOGS_ENABLED):
            print("Day %03d Student %s is returning %s" %(self.env.now//ONE_DAY, self.name, book.name))
        book.status = Status.RETURNING
        # Checking if book is lost
        with counter.request() as req:
            results = yield req | env.timeout(self.patience) # Wait for counter to be free or until patience runs out
            if(req not in results): # We lost patience
                if(LOGS_ENABLED):
                    print("Day %03d Student %s lost patience while returning book %s. They will be back in an hour" %(self.env.now//ONE_DAY, self.name, book.name))
                global lost_patience_counts
                lost_patience_counts+=1
                self.free.succeed
                self.free = self.env.event()
                if(env.now > book.due_date):
                    yield self.env.process(self.checkin_book(book))
                else: # If book is not due today, return back tomorrow
                    yield start_delayed(env, self.checkin_book(book), delay=ONE_DAY)
                return None

            if(random.random() < PROB_LOSE_TRESHOLD): # Probability that the book is lost
                if(LOGS_ENABLED):
                    print("Day %03d Student %s lost the book %s" %(self.env.now//ONE_DAY, self.name, book.name))
                book.status = Status.LOST
                global books_lost_count
                books_lost_count+=1
        

            if(book.status == Status.LOST): #       If book is lost
                yield self.env.timeout(random.randint(LOST_TIME_MIN, LOST_TIME_MAX))
            elif(book.due_date >= self.env.now): #  If returning on time
                yield self.env.timeout(random.randint(CHECKIN_MIN_TIME, CHECKIN_MAX_TIME))
            else: #                                 If returning late
                yield self.env.timeout(random.randint(LATE_CHECKIN_MIN, LATE_CHECKIN_MAX))
            
            if(book.status != Status.LOST):
                book.resouce.release(book.req)
                book.status = Status.AVAILABLE
                global returned_books_count
                returned_books_count+=1
                global books_return_time
                books_return_time+= env.now - book.due_date
            self.books_borrowed.remove(book)
        self.free.succeed() # The student is now free
        self.free = self.env.event()


    def searchBook(self): # Search and check out book
        # print('Selecting book')
        book_choice = random.choice(book_names) # Deciding which book to pick
        if(LOGS_ENABLED):
            print('Day %03d Student %s is looking to check out %s' %(self.env.now//ONE_DAY, self.name, book_choice))
        yield self.env.timeout(random.uniform(MIN_TIME_BOOK_SEARCH, MAX_TIME_BOOK_SEARCH))
        # Looking for the book
        borrowing = None
        for book in available_books[book_choice]:
            if(book.status == Status.AVAILABLE): # If book found
                req = book.resouce.request()
                res = yield req | self.env.timeout(1)
                if(req not in res): # Did not acquire book
                    break
                book.status = Status.BORROWING
                book.req = req
                borrowing = book
                break
        if(borrowing == None): # If not found
            if(LOGS_ENABLED):
                print("Day %03d Student %s couldn't find a copy of %s" %(self.env.now//ONE_DAY, self.name, book_choice))
            self.free.succeed() # Student is now free
            self.free = self.env.event()
            return None
        
        # yield for counter
        with counter.request() as req:
            results = yield req | env.timeout(self.patience) # Wait for counter to be free or until patience runs out
            if(req not in results): # We lost patience
                if(LOGS_ENABLED):
                    print("Day %03d Student %s lost patience while borrowing book %s. They will be back later" %(self.env.now//ONE_DAY, self.name, book.name))
                global lost_patience_counts
                lost_patience_counts+=1
                self.free.succeed
                self.free = self.env.event()
                return None

            if(LOGS_ENABLED):
                print('Day %03d Student %s is checking out %s' %(self.env.now//ONE_DAY, self.name, book_choice))

            yield env.timeout(random.randint(CHECKOUT_MIN_TIME, CHECKOUT_MAX_TIME)) # Time takn to checkout book

            # Borrow book here
            borrowing.status = Status.BORROWED
            borrowing.borrower = self
            borrowing.due_date = env.now + BORROW_DURATION
            global borrowed_books_count
            borrowed_books_count+=1
            self.books_borrowed.append(borrowing)
            self.free.succeed() # Student is now free
            self.free = self.env.event()
            self.env.process(self.checkin_book(borrowing)) # Call check in process to ensure student checks in book


    def run(self): # Main process which decides when to check out
        while(True):
            if(len(self.books_borrowed) < 3):
                while(random.random() >= self.books_probability): # Student doesn't need book right now
                    t = random.expovariate(1.0 / BOOKS_BORROWED_MEAN * (1 + len(self.books_borrowed)))
                    yield self.env.timeout(t) # Depends on a exponential function which considers no. of books borrowed
                
                if((env.now % ONE_DAY) < OPENING_TIME): # If Library is not yet open
                    yield self.env.timeout(random.uniform(OPENING_TIME, CLOSING_TIME) - self.env.now%ONE_DAY)
                elif((self.env.now%ONE_DAY) > CLOSING_TIME): # Library is closed
                    yield self.env.timeout(ONE_DAY + (random.uniform(OPENING_TIME, CLOSING_TIME)) - self.env.now%ONE_DAY)
                if(self.env.now%ONE_WEEK >= SUNDAY): # It's sunday!
                    yield env.timeout(ONE_DAY + random.uniform(OPENING_TIME, CLOSING_TIME) - self.env.now%ONE_DAY)

                if(LOGS_ENABLED):
                    print('Day %03d Student %s is now looking for a book' %(self.env.now//ONE_DAY, self.name))
                    # if(self.env.now%ONE_WEEK >= SUNDAY):
                    #     print(self.env.now)
                self.env.process(self.searchBook()) # Check out book
            yield self.free # Wait for student to be free

# Book generator which generates book at a random interval
def book_generator(env, available_books, book_names):
    global TOTAL_BOOKS
    while True:
        yield env.timeout(random.expovariate(1.0 / NEW_BOOK_INTERVAL))
        book_name = random.choice(book_names) # Choosing which book to add a copy of
        book = Book(TOTAL_BOOKS, book_name, Status.AVAILABLE, None, None)
        available_books[book_name].append(book) # Add the new book
        TOTAL_BOOKS += 1
        if(LOGS_ENABLED):
            print('Day %03d : Added new book - copy of "%s"' %(env.now //ONE_DAY, book_name))
            # print('Total books in stock = %d' % TOTAL_BOOKS)


# env = simpy.rt.RealtimeEnvironment(factor=0.1, strict=False ) # Change this to change simulation speed
env = simpy.Environment()
# Add all books to the library
for i in range(BOOK_TITLES): # Creating books
    book_name = fake.sentence(nb_words = 4)
    book_names.append(book_name)
    available_books[book_name] = []
    for j in range(5):
        book = Book(i*5+j, book_name, Status.AVAILABLE, None, None)
        available_books[book_name].append(book)

# Create student instances
for i in range(TOTAL_STUDENTS): # Creating students
    student_name = fake.name()
    students.append(Student(i, student_name, env))
    
# Available counter resources
counter = simpy.Resource(env, capacity=COUNTERS)


daily_total_book_counts = []
daily_borrowed_counts = []
daily_return_counts = []
daily_return_times = []
daily_lost_patience = []

def dailyReporter(env):
    last_borrowed_count = 0
    last_return_count = 0
    last_return_time = 0
    last_lost_patience = 0
    while True:
        daily_total_book_counts.append(TOTAL_BOOKS - books_lost_count)
        today_borrowed_count = borrowed_books_count - returned_books_count - books_lost_count - last_borrowed_count
        daily_borrowed_counts.append(today_borrowed_count)
        last_borrowed_count = last_borrowed_count + today_borrowed_count

        today_return_count = returned_books_count - last_return_count
        today_return_time = books_return_time - last_return_time
        
        last_return_count = returned_books_count
        last_return_time = books_return_time
        
        daily_return_times.append(today_return_time / today_return_count if today_return_count>0 else 0)

        daily_lost_patience.append(lost_patience_counts - last_lost_patience)
        last_lost_patience = lost_patience_counts

        yield env.timeout(ONE_DAY)


env.process(book_generator(env, available_books, book_names)) # Process for random addition of books

env.process(dailyReporter(env))


print("Starting simulation")
env.run(until=RUN_DURATION)
print("Simulation completed")

import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="darkgrid")
import pandas as pd
import numpy as np
df = pd.DataFrame({
    'time':np.arange(RUN_DURATION//ONE_DAY),
    'total books':daily_total_book_counts,
    'borrowed_books': daily_borrowed_counts,
    'Average return times': daily_return_times,
    'Daily patience lost': daily_lost_patience})

print(df[:15])

df = pd.melt(df, ['time'])
g = sns.FacetGrid(df, row= 'variable')
g.map(sns.lineplot, 'time', 'value', ci=None)
plt.show()