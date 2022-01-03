import random
import math


class Model:

# instance variables
    def __init__(self):
        self.allNodes = []
        self.customers = []
        self.matrix = []
        self.profit = 0.0
        self.capacity = -1

    def pretty_print(self, matrix):
        s = [[str(e) for e in row] for row in matrix]
        lens = [max(map(len, col)) for col in zip(*s)]
        fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
        table = [fmt.format(*row) for row in s]
        print('\n'.join(table))

    def BuildModel(self):
        random.seed(1)
        depot = Node(0, 50, 50, 0, 0)
        self.allNodes.append(depot)
        birthday = 5051997
        random.seed(birthday)
        self.capacity = 150.0
        totalCustomers = 200
        for i in range (0, totalCustomers):
            x = random.randint(0, 100)
            y = random.randint(0, 100)
            service_time = random.randint(5,20)
            profit = random.randint(5, 20)
            cust = Node(i + 1, x, y, service_time, profit)
            self.allNodes.append(cust)
            self.customers.append(cust)
        
        rows = len(self.allNodes)
        self.matrix = [[0.0 for x in range(rows)] for y in range(rows)]

        for i in range(0, len(self.allNodes)):
            for j in range(0, len(self.allNodes)):
                a = self.allNodes[i]
                b = self.allNodes[j]
                dist = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2))
                self.matrix[i][j] = dist
        #self.pretty_print(self.matrix)
        #for i in self.customers:
           #print('Customer ID : ' + str(i.ID) + " Customer profit : " + str(i.profit) + ' Customer service time : ' + str(i.service_time))
       

# 0      1           4          5          6            3          0
#       8.24   +   26.24     + 12.04   +   89.89    +   59.13 +   49                
# 0      3          2          0
#        50  +      19    +    39
class Node:
    def __init__(self, idd, xx, yy, service_time, profit):
        self.x = xx
        self.y = yy
        self.ID = idd
        self.service_time = service_time
        self.profit = profit
        self.isRouted = False

class Route:
    def __init__(self, dp, cap, profit):
        self.sequenceOfNodes = []
        self.sequenceOfNodes.append(dp)
        self.sequenceOfNodes.append(dp)
        self.cost = 0
        self.capacity = cap
        self.profit = profit
        self.load = 0