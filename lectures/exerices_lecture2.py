class Stack ():


    def __init(self):
        self.stack = []


    def is_empty(self):
        return len(self.stack) == 0
    
    def push(self, item):
        self.stack.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self.stack.pop()
    
    def top(self):
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self.stack[-1]
    
    def __str__(self):
        return str(self.stack)
        print(self.stack)

    def __add__(self, other):
        self.stack += other.stack
        return self
    
stack1 = Stack()
    
 
