# my_contingent.py

def log_arguments(func):
    def wrapper(*args,**kwargs): 
        print(f"调用{func.__name__}")
        print(f"{args}")
        print(f"{kwargs}")
        result = func(*args,**kwargs)
        print(f"result")
        return result
    return wrapper

@log_arguments
def add(a,b): 
    return a + b 
result1 = add(3,5)
print()
@log_arguments 
def greet(name,greeting="hello"): 
    return f"{greeting},{name}!"
result2 = greet("alice")

result3 = greet("Bob", greeting="Hi")


