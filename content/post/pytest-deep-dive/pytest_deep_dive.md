---
title: "Deep Dive into Pytest: Fixtures, Scopes, Parameterization, and Testing Spark Remotely"
description: "An intermediate look at solving my testing problems"
date: 2025-04-28 22:21:04+0000
lastmod: 2025-04-29T19:48:44+01:00
categories:
    - Deep Dive
    - Testing
tags:
    - Pytest
draft: true
---

## 🧪 Test hard. Test often

If there is one thing I wish I learned earlier in my programming journey, it would be:

> **DON'T. SKIP. TESTING.**

Well now I'm slightly older and perhaps slightly wiser, I'm starting to see the benefits of approaching a programming problem from a *testing first* workflow. Today in my work I was building out a metadata system to programmatically gather metadata from external sources (yeah okay... it's Excel 😔) and parse them into a standardised format that could be applied to table comments and table tags within [Unity Catalog](https://www.databricks.com/product/unity-catalog).

In this post I'll be diving into some intermediate pytest concepts that will save a lot of time and boiler plate in your code, and allow for you to rapidly add or tweak test cases on the fly.

With some simple examples!

### Testing is tiring (if done badly)

If you'd have asked me when I first started writing tests what the most annoying part would be, chances are you'd get one of these answers:

- Making the mock data or inputs to the test
- Manually having to write out many variations of a test case

### Fixtures

A [Pytest Fixture](https://linkhttps://docs.pytest.org/en/6.2.x/fixture.html) is the first important topic to understand. I'll leave the detailed explanation for the docs, but in a nutshell, they allow you to specify functions that provide chunks of code that your test cases can access to perform various repetitive tasks.

This helps with a few things:

1. **Providing Data:** Supplying consistent test data (like mock objects or configurations) to multiple tests.
2. **Managing Resources:** Setting up resources (like database connections, temporary files, or running services) before a test and ensuring they are cleaned up afterwards, regardless of whether the test passes or fails.
3. **Reducing Boilerplate:** Avoiding writing the same setup/teardown logic in multiple test functions.

Let's take a look at an example, of a simple multiplication function to start with:

```python
# A Simple function to test
def multiply(a, b):
    return a * b
```

Creating a basic pytest test would look like this:

```python
# A basic Pytest test
def test_multiply():
    assert multiply(3, 4) == 12
```

Now that's great, but let's introduce a more realistic scenario. Imagine our multiply function needs to write to a temporary file for some reason (very common when handling user data).

If we wrap a function with a `@pytest.fixture` [decorator](https://realpython.com/primer-on-python-decorators/) we can use the function to perform operations before *each* test:

```python
import os
import pytest

# Defining a pytest fixture for opening and closing a file
@pytest.fixture # This decorator declares the function as a pytest fixture
def temp_output_path():
    """Creates a temporary file path and ensures cleanup."""
    filepath = 'temp_multiply_output.txt'
    # Remove file if it exists already
    if os.path.exists(filepath)
        os.remove(filepath)

    yield filepath # Provides filepath to the test

    # Teardown: Cleaning up the file after the test runs
    if os.path.exists(filepath):
        os.remove(filepath)
    else:
        print(f" TEARDOWN: temp_output_path (File not found, maybe test failed early?)")
```

Now, we've created a pytest fixture that will run before every test. Notice something interesting we are doing. We aren't `returning` anything from the function, but rather using the keyword `yield`. This is important as return would end the function call and our teardown code would never run. So we'd be left with a temporary file path that never gets automatically cleaned up.

Using `yield` allows us to write teardown logic which will only run after the test completes.

Now let's incorporate this into a test:

```python
# --- Test using our fixture ---
def test_multiplication_with_file_output(temp_output_path): # Fixture is passed in a parameter
    """
    Tests multiplication, writes result to a temp file managed by a fixture,
    and verifies the file content.
    """
    result = multiply(3, 4)

    # 2. Use the file path from the fixture
    with open(temp_output_path, "w") as f:
        f.write(str(result))

    # 3. Verify the file contents
    with open(temp_output_path, "r") as f:
        content = f.read()
    assert int(content) == 12
```

Looks great! This keeps our test code much cleaner, and allows us to reuse the fixture across multiple tests which interact with a temporary file.

### Controlling Setup/Teardown Frequency with Scopes

By default, the `temp_output_path` fixture we created runs its setup (checking/deleting the old file) and teardown (deleting the new file) for *every single test* that uses it. If this setup/teardown were time-consuming (like starting a database service), this would be inefficient.

Pytest allows us to control this using the `scope` argument in the `@pytest.fixture` decorator. Let's change our `temp_output_path` fixture to have `module` scope. This means it will only set up *once* before the first test in the module that needs it runs, and tear down *once* after the last test in the module finishes.

Let's modify our fixture to create an entire folder, that all our tests can use temporarily:

```python
import pytest
import os

@pytest.fixture(scope="module") # Defining the scope as "module" for the fixture
def temp_output_dir():
    """Creates a temporary directory once per module and ensures cleanup."""
    dirpath = "temp_module_output_dir"
    print(f"\nSETUP: temp_output_dir (scope: module) - Creating directory: {dirpath}")
    os.makedirs(dirpath, exist_ok=True)

    yield dirpath # Provide the directory path to the tests

    # Teardown: Clean up the directory after all tests in the module run
    print(f"TEARDOWN: temp_output_dir (scope: module) - Removing directory: {dirpath}")
    # Be careful with rmtree in real code!
    if os.path.exists(dirpath):
        # Simple example cleanup: remove files first, then dir
        for item in os.listdir(dirpath):
            item_path = os.path.join(dirpath, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
        os.rmdir(dirpath)
    print("TEARDOWN: temp_output_dir finished.")
```

Now our fixture runs *once* at the very beginning of our tests. Specifically once per *module* (i.e., per `.py` file).

And our test function will use this folder now:

```python
# --- Test Functions ---
def test_multiplication_file_output_1(temp_output_dir): # Reminder: Fixture passed as parameter
    """Test using the module-scoped directory."""
    result = multiply(3, 4)
    filepath = os.path.join(temp_output_dir, "output.txt")

    with open(filepath, "w") as f:
        f.write(str(result))

    with open(filepath, "r") as f:
        content = f.read()

    assert int(content) == 12
```

Pytest offers different scopes to control how often a fixture is set up and torn down:

- `function`: Runs once per test function.
- `class`: Runs once per test class.
- `module`: Runs once per module (i.e., per `.py` file).
- `session`: Runs once per test session (i.e., when you run `pytest`).

### Handling Test Variations Cleanly with Parameterization

Okay, now let's tackle the second common pain point mentioned earlier: manually writing out many variations of the same test case. This is where parameterization comes in.

Imagine you want to test your multiply function with several different inputs: positive numbers, negative numbers, zero, etc. Without parameterization, you might write separate tests:

```python
# --- Repetitive Tests (What we want to avoid) ---
def test_multiply_positive():
    assert multiply(3, 4) == 12

def test_multiply_negative():
    assert multiply(-2, 5) == -10

def test_multiply_zero():
    assert multiply(6, 0) == 0
```

This is tedious and violates the *DRY* (Don't Repeat Yourself) principle. Pytest's parameterization lets you run the same test function multiple times with different arguments.

You use the @pytest.mark.parametrize decorator to achieve this. You provide it with:

1. A string containing the names of the arguments the test function will receive (comma-separated).
2. A list of tuples (or lists), where each tuple represents one set of arguments to pass to the test function for one run.

Let's add a parameterized test to our example file:

```python
# --- Parameterized Test ---
@pytest.mark.parametrize(
    "a, b, expected_product", # Argument names for the test function
    [
        (2, 5, 10),      # Test case 1: a=2, b=5, expected_product=10
        (-3, 6, -18),    # Test case 2: a=-3, b=6, expected_product=-18
        (0, 100, 0),     # Test case 3: a=0, b=100, expected_product=0
        (7, -7, -49),    # Test case 4: a=7, b=-7, expected_product=-49
    ],
    ids=["pos*pos", "neg*pos", "zero*pos", "pos*neg"] # Optional: Custom IDs for test runs
)
def test_parametrized_multiplication(a, b, expected_product, temp_output_dir): # Pass parameterized arguments
    """Tests multiplication with multiple input sets using parameterization."""
    # Note: We can still use fixtures alongside parameterization!
    print(f"\n    TEST: test_parametrized_multiplication [{a=}, {b=}] (Dir: {temp_output_dir})")
    result = multiply(a, b)
    assert result == expected_product
    # Optional: Could also write to a unique file per parameter set in temp_output_dir
    # filepath = os.path.join(temp_output_dir, f"output_param_{a}_{b}.txt")
    # with open(filepath, "w") as f: f.write(str(result))
```

1. `@pytest.mark.parametrize("a, b, expected_product", ...)` tells `pytest` that this test function takes three arguments (`a`, `b`, `expected_product`) that will be parameterized.
2. The list `[(2, 5, 10), (-3, 6, -18), ...]` provides the different sets of values for these arguments.  
    `pytest` will run the `test_parametrized_multiplication` function four times, once for each tuple in the list:
    - Run 1: `a=2`, `b=5`, `expected_product=10`
    - Run 2: `a=-3`, `b=6`, `expected_product=-18`
    - Run 3: `a=0`, `b=100`, `expected_product=0`
    - Run 4: `a=7`, `b=-7`, `expected_product=-49`
3. The `ids` list provides clearer names for each parameterized run in the `pytest` output (e.g., `test_parametrized_multiplication[pos*pos]`).

> Notice that we can still request fixtures (like temp_output_dir) in a parameterized test. The fixture's scope rules still apply (e.g., temp_output_dir is set up only once for the module, even though this test function runs four times).

Parameterization makes it incredibly easy to add new test cases – just add another tuple to the list! This significantly reduces boilerplate code and makes your tests more comprehensive and maintainable.

### But Wait... There's MORE (Parameterization)

<p align="center">
    <img src="https://upload.wikimedia.org/wikipedia/commons/4/47/River_terrapin.jpg" alt="turtles all the way down">
</p>
<p align="center"><em>"Turtles all the way down" - It just keeps going.</em></p>

Sometimes, you want a fixture to provide slightly different setup or data depending on the test. You can achieve this by passing parameters to the fixture when requesting it in the test function and accessing these parameters within the fixture using request.param.

Let's create a fixture and parametrize the fixture itself (not the test case) accept a parameter that determines the numbers it yields:

```python
# --- Parameterizable Fixture ---
@pytest.fixture(params=[
    {"x": 3, "y": 4, "id": "standard"},  # Parameter set 1
    {"x": 10, "y": 2, "id": "large_x"}, # Parameter set 2
    pytest.param({"x": -5, "y": -5, "id": "negatives"}, marks=pytest.mark.skip) # Parameter set 3 (skipped)
])
def parameterized_operands(request):
    """Provides different pairs of numbers based on fixture parameterization."""
    param_data = request.param # Access the current parameter set
    yield {"x": param_data["x"], "y": param_data["y"]} # Yield only the needed data

# --- Module-scoped fixture (unchanged) ---
# ...

# --- Test using the parameterized fixture ---
def test_with_parameterized_fixture(parameterized_operands, temp_output_dir):
    """This test will run multiple times, once for each fixture parameter."""
    operands = parameterized_operands # Get the data yielded by the fixture for this run
    print(f"TEST: test_with_parameterized_fixture (Operands: {operands}, Dir: {temp_output_dir})")
    result = multiply(operands["x"], operands["y"])
    expected = operands["x"] * operands["y"]
    assert result == expected
    
    # Example: Write to a file named after the fixture param ID
    filepath = os.path.join(temp_output_dir, f"output_{operands['x']}_{operands['y']}.txt")
    with open(filepath, "w") as f: f.write(str(result))
```

Let's walk through what we just did:

1. We add `params=[...]` to the `@pytest.fixture` decorator for `parameterized_operands`. Each item in the `params` list will cause any test requesting this fixture to run once *per parameter*.
2. Inside the fixture, `request.param` holds the *current* parameter value for that specific run (e.g., `{"x": 3, "y": 4, "id": "standard"}` on the first run).
3. We use `request.param['id']` in the print statements and `request.param['x']`, `request.param['y']` to yield the correct data.
4. The `test_with_parameterized_fixture` function requests `parameterized_operands`. Pytest sees the fixture is parameterized and runs the test twice (once for each non-skipped parameter set in the fixture definition). The third parameter set is marked with `pytest.mark.skip`.
5. The `temp_output_dir` fixture (module scope) is still set up only once.

## Wrapping up

Once I got my head around these concepts, writing tests became much less daunting, and the tests I was writing started to have the speed and agility required for me to actually go and write them (shout-out to all the lazy developers out there).

There is a lot more to delve into when it comes to Pytest. The future me will likely write about some more complex topics, like running Pytest both locally and also in Databricks Connect on a cluster in the cloud. And perhaps even, 

**Is there such a thing as too much Testing**?

> *Hint. Yes there is.*

But this post has already grown too large so... Thanks for reading!
