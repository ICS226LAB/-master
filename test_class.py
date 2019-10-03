#!/usr/bin/python3

import datetime

class Vehicle:
 def __init__(self, make, model, year):
  self.make = make
  self.model = model
  self.year = year

 def age(self):
  return datetime.date.today().year - self.year

v = Vehicle('Toyota','Prius', 2015)
print(v.age())
