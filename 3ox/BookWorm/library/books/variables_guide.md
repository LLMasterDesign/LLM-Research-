# Variables and Data Types: The Foundation

## What is a Variable?

Think of a variable as a labeled box. You give it a name, and you can put something inside it. That "something" is a value - it could be a number, text, true/false, or many other things.

```python
age = 25
name = "Lucius"
is_learning = True
```

In these examples:
- `age` is a box containing the number 25
- `name` is a box containing the text "Lucius"  
- `is_learning` is a box containing the boolean value True

## Why Variables Matter

Without variables, you'd have to write the same values over and over:

```python
# Without variables (tedious!)
print("Hello, Lucius!")
print("Lucius, you are 25 years old")
print("Lucius's email is: lucius@example.com")

# With variables (much better!)
name = "Lucius"
age = 25
email = "lucius@example.com"

print(f"Hello, {name}!")
print(f"{name}, you are {age} years old")
print(f"{name}'s email is: {email}")
```

Variables let you:
- **Store** values for later use
- **Reuse** the same value in multiple places
- **Update** values as your program runs
- **Give meaningful names** to data, making code readable

## Core Data Types

### 1. Integers (int)
Whole numbers, positive or negative, no decimals.

```python
score = 100
temperature = -5
year = 2025
```

### 2. Floats (float)
Numbers with decimal points.

```python
price = 19.99
pi = 3.14159
temperature = 98.6
```

### 3. Strings (str)
Text, wrapped in quotes (single or double).

```python
greeting = "Hello, world!"
name = 'Lucius'
message = """This is a
multi-line string"""
```

### 4. Booleans (bool)
True or False values, used for logic.

```python
is_sunny = True
has_key = False
game_over = False
```

### 5. None
Represents "no value" or "nothing."

```python
result = None
user_input = None
```

## Variable Rules and Best Practices

### Naming Rules (Required)
1. Start with a letter or underscore: `name`, `_temp`
2. Can contain letters, numbers, underscores: `user_1`, `total_score`
3. Case-sensitive: `age` and `Age` are different
4. No spaces: use `user_name`, not `user name`
5. Can't use reserved words: `for`, `if`, `while`, etc.

### Naming Conventions (Best Practice)
```python
# Good - descriptive, lowercase with underscores
student_count = 30
max_temperature = 100
is_valid = True

# Bad - unclear, too short
sc = 30
mt = 100
iv = True

# Bad - too long
the_number_of_students_currently_enrolled = 30
```

## Type Checking and Conversion

You can check a variable's type:

```python
age = 25
print(type(age))  # <class 'int'>

name = "Lucius"
print(type(name))  # <class 'str'>
```

You can convert between types:

```python
# String to integer
age_str = "25"
age_int = int(age_str)  # Now it's 25 (number)

# Integer to string
score = 100
score_str = str(score)  # Now it's "100" (text)

# String to float
price_str = "19.99"
price = float(price_str)  # Now it's 19.99 (decimal)
```

## Variables Are Mutable

Variables can change (that's why they're called variables!):

```python
score = 0
print(score)  # 0

score = 10
print(score)  # 10

score = score + 5
print(score)  # 15
```

## Multiple Assignment

Python lets you assign multiple variables at once:

```python
# Assign same value to multiple variables
x = y = z = 0

# Assign different values
name, age, city = "Lucius", 25, "Rome"

# Swap values
a, b = 10, 20
a, b = b, a  # Now a=20, b=10
```

## Common Mistakes

### 1. Using variables before assignment
```python
# Wrong!
print(name)  # Error: name is not defined
name = "Lucius"

# Right!
name = "Lucius"
print(name)  # Works!
```

### 2. Mixing incompatible types
```python
# Wrong!
age = "25"
next_year = age + 1  # Error: can't add string and int

# Right!
age = 25
next_year = age + 1  # Works! Result is 26
```

### 3. Confusing = (assignment) with == (comparison)
```python
# Assignment (sets value)
x = 5

# Comparison (checks equality)
if x == 5:
    print("x is five")
```

## Practice Exercises

### Exercise 1: Variable Basics
Create variables for your information and print them:

```python
# Your turn:
first_name = 
last_name = 
age = 
favorite_color = 

print(f"Name: {first_name} {last_name}")
print(f"Age: {age}")
print(f"Favorite color: {favorite_color}")
```

### Exercise 2: Type Conversion
Fix this code so it works:

```python
# This has bugs - fix it!
user_age = "25"
years_until_30 = 30 - user_age  # This will error
print(f"Years until 30: {years_until_30}")
```

### Exercise 3: Variable Updates
Track a bank balance:

```python
balance = 100
print(f"Starting balance: ${balance}")

# Deposit $50

# Withdraw $30

# Deposit $20

print(f"Final balance: ${balance}")
```

## Key Takeaways

✅ **Variables store data** - They're labeled containers for values  
✅ **Data types matter** - int, float, str, bool, None each behave differently  
✅ **Names should be descriptive** - `student_count` beats `sc`  
✅ **Variables can change** - That's their superpower  
✅ **Type conversion is common** - Use int(), float(), str() as needed  

## What's Next?

Now that you understand variables, you're ready to learn about **operators** - the tools that let you do things WITH your variables (math, comparisons, logic).

---

**Questions to Reflect On:**
1. Can you explain what a variable is to someone who's never programmed?
2. Why would you choose an integer over a float, or vice versa?
3. What makes a good variable name?
4. When might you need to convert between types?

:: ∎
