"""
class MyClass:
    MyConstant=5

    def __init__(self):
        self.test = trythis()
        self.OtherConstant = 7
        self.text = TextClass()

    def printme(self):
        return print(self.MyConstant)
    
    def trythis():
        return 'something'

    def changeConstant(self, newConstant):
        self.MyConstant = newConstant

class TextClass:
    def __init__(self):
        self.myDiameter = 18

        
classy = MyClass()

classy.printme()
classy.changeConstant(6)
classy.printme()
print(classy.OtherConstant)
print(classy.text.myDiameter)

"""

class Sample:

    def __init__(self):
        self.initial_length = input('Initial sample thickness (mm): ')
        self.initial_diamter = input('Initial sample diameter (mm): ')
        
        #To be added later
        self.material = False
        self.pressure = False
        self.voltage = False
        self.current_limit = False


mySample = Sample()

print(mySample.initial_length)
    
