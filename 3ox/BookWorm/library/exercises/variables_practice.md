# Variables Practice Exercises

## Warm-Up: Basic Variable Creation

### Exercise 1.1: Personal Profile
Create variables to represent yourself:

```python
# Fill in your information
name = 
age = 
city = 
favorite_language = 

# Test: Print them all
print(f"{name} is {age} years old")
print(f"Lives in {city} and loves {favorite_language}")
```

**Expected Output:**
```
Lucius is 25 years old
Lives in Rome and loves Python
```

---

## Challenge: Type Conversion

### Exercise 1.2: Input Handling
User input always comes as strings. Practice converting:

```python
# This is what you get from user input
user_age = "25"
user_height = "5.9"
user_is_student = "True"

# Convert to appropriate types
age = 
height = 
is_student = 

# Test: These should work
years_until_30 = 30 - age
print(f"Years until 30: {years_until_30}")

height_in_cm = height * 30.48
print(f"Height in cm: {height_in_cm}")

if is_student:
    print("You get a student discount!")
```

**Expected Output:**
```
Years until 30: 5
Height in cm: 179.832
You get a student discount!
```

---

## Application: Shopping Cart Calculator

### Exercise 1.3: Total Price
Calculate the total for a shopping cart:

```python
# Item prices
apple_price = 0.50
banana_price = 0.30
orange_price = 0.75

# Quantities
apples = 6
bananas = 4
oranges = 3

# Calculate totals (fill in the blanks)
apple_total = 
banana_total = 
orange_total = 

# Grand total
total = 

# Tax (8%)
tax = 
final_price = 

print(f"Subtotal: ${total:.2f}")
print(f"Tax: ${tax:.2f}")
print(f"Total: ${final_price:.2f}")
```

**Expected Output:**
```
Subtotal: $6.45
Tax: $0.52
Total: $6.97
```

---

## Debugging: Fix the Errors

### Exercise 1.4: Debug This Code
This code has 5 bugs. Find and fix them:

```python
# Bug-ridden code - fix it!
1age = 25
user name = "Lucius"
score = "100"
is_valid == True

print(f"User: {username}")
print(f"Age next year: {1age + 1}")
print(f"Double score: {score * 2}")
if is_valid:
    print("Valid user!")
```

**Bugs to Find:**
1. Variable names can't start with numbers
2. Variable names can't have spaces
3. Score is string, should be int
4. `==` is comparison, not assignment
5. Variable name inconsistency

**Corrected Code:**
```python
age = 25
user_name = "Lucius"
score = 100
is_valid = True

print(f"User: {user_name}")
print(f"Age next year: {age + 1}")
print(f"Double score: {score * 2}")
if is_valid:
    print("Valid user!")
```

---

## Advanced: Variable Swapping

### Exercise 1.5: Swap Without Temp
Swap two variables without using a temporary variable:

```python
a = 10
b = 20

print(f"Before: a={a}, b={b}")

# Swap using simultaneous assignment
# Your code here:


print(f"After: a={a}, b={b}")
```

**Expected Output:**
```
Before: a=10, b=20
After: a=20, b=10
```

**Hint:** Python allows `a, b = b, a`

---

## Synthesis: Temperature Converter

### Exercise 1.6: Build a Converter
Create a temperature conversion tool:

```python
# Temperature in Fahrenheit
temp_f = 68

# Convert to Celsius: (F - 32) × 5/9
temp_c = 

# Convert to Kelvin: C + 273.15
temp_k = 

print(f"{temp_f}°F equals:")
print(f"  {temp_c:.1f}°C")
print(f"  {temp_k:.1f}K")

# Bonus: Create a "feels like" description
if temp_f < 32:
    feeling = "freezing"
elif temp_f < 60:
    feeling = "cold"
elif temp_f < 80:
    feeling = "comfortable"
else:
    feeling = "hot"

print(f"It feels {feeling} outside")
```

**Expected Output:**
```
68°F equals:
  20.0°C
  293.2K
It feels comfortable outside
```

---

## Reflection Questions

After completing these exercises, reflect:

1. **When did you need type conversion?** Why can't Python just figure it out?

2. **What makes a variable name good vs. bad?** Give examples.

3. **Why use f-strings instead of + concatenation?** What's the benefit?

4. **Variable scope**: If you create a variable inside an if-block, can you use it outside? Try it!

```python
if True:
    inner_var = "inside"

print(inner_var)  # Does this work? Why or why not?
```

---

## Mastery Check

You've mastered variables when you can:

✅ Create and name variables following conventions  
✅ Identify and use appropriate data types  
✅ Convert between types when needed  
✅ Update variable values  
✅ Debug common variable errors  
✅ Explain what variables are and why they matter

**Self-Assessment:** On a scale of 1-5, how confident are you with variables?

1. Still confused about basics
2. Understand concept, but make mistakes
3. Can use variables in simple programs
4. Comfortable with variables and type conversion
5. Could teach variables to someone else

If you're at 3 or above, you're ready to move on to **Operators**!
If you're below 3, review the guide and retry exercises 1.1-1.3.

:: ∎
