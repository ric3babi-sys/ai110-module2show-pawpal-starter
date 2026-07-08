# Streamlit st.session_state for PawPal+ System

## Problem
Streamlit reruns the entire script from top to bottom on every user interaction (button click, text input, etc.). This means:
- Global variables are reset on every rerun
- New Owner/Pet/Task objects are created unnecessarily
- Data is lost between interactions

## Solution: st.session_state
`st.session_state` is a persistent dictionary that survives across script reruns within a single user session.

## Implementation Pattern

### 1. Check if object exists, create if not
```python
if "ownerList" not in st.session_state:
    st.session_state.ownerList = []
    
if "petList" not in st.session_state:
    st.session_state.petList = []

if "schedulerDictionary" not in st.session_state:
    st.session_state.schedulerDictionary = {}

if "TASK_TYPES" not in st.session_state:
    st.session_state.TASK_TYPES = {
        0: "Walk Pet",
        1: "Feed Pet",
        2: "Nap Time",
        3: "Veterinarian Visit"
    }
```

### 2. Initialize PawPal+ System on First Load
```python
def init_pawpal_session():
    """Initialize PawPal+ system objects in session_state if they don't exist."""
    
    # Initialize global lists/dicts
    if "ownerList" not in st.session_state:
        st.session_state.ownerList = []
    
    if "petList" not in st.session_state:
        st.session_state.petList = []
    
    if "schedulerDictionary" not in st.session_state:
        st.session_state.schedulerDictionary = {}
    
    if "TASK_TYPES" not in st.session_state:
        st.session_state.TASK_TYPES = {
            0: "Walk Pet",
            1: "Feed Pet",
            2: "Nap Time",
            3: "Veterinarian Visit"
        }
    
    # Other app-specific initializations
    if "current_owner" not in st.session_state:
        st.session_state.current_owner = None
    
    if "current_pet" not in st.session_state:
        st.session_state.current_pet = None

# Call at app start
init_pawpal_session()
```

### 3. Access Objects from session_state
```python
# Creating new owner
owner = newOwner("John Smith")
st.session_state.ownerList.append(owner)

# Accessing from session_state
all_owners = st.session_state.ownerList
task_types = st.session_state.TASK_TYPES
schedules = st.session_state.schedulerDictionary
```

## Why This Matters

### Without session_state (Bad)
```python
# This resets on every rerun!
ownerList = []
petList = []
schedulerDictionary = {}

owner = newOwner("John")  # Created on every rerun!
# Data lost when user clicks a button
```

### With session_state (Good)
```python
# This persists across reruns
if "ownerList" not in st.session_state:
    st.session_state.ownerList = []

owner = newOwner("John")  # Only created once
st.session_state.ownerList.append(owner)
# Data survives user interactions
```

## Rerun Cycle Explained

1. **User interacts** (button click, text input)
2. **Streamlit reruns script** from top to bottom
3. **session_state persists** - objects created in previous run are still there
4. **New objects can be created** - code runs again, but checks if objects exist first
5. **Loop repeats** on next interaction

## session_state Features

### Check if key exists
```python
if "owner_name" in st.session_state:
    name = st.session_state.owner_name
else:
    name = "Unknown"
```

### Get with default
```python
owners = st.session_state.get("ownerList", [])
```

### Delete key
```python
del st.session_state.owner_name
```

### Clear all
```python
st.session_state.clear()
```

## Best Practices

1. **Initialize at app startup**: Create a `init_session()` function called at the top of app.py
2. **Use consistent names**: `st.session_state.ownerList` not `st.session_state.owners` or `st.session_state.owner_list`
3. **Check before use**: Always verify key exists before accessing
4. **Document structure**: Comment what keys are stored and their types
5. **Clear when needed**: Implement a reset button if needed

## Example App Structure
```python
import streamlit as st
from pawpal_system import newOwner, newPet, newScheduler

def init_session():
    """Initialize session state on app load."""
    if "ownerList" not in st.session_state:
        st.session_state.ownerList = []
    if "petList" not in st.session_state:
        st.session_state.petList = []
    if "schedulerDictionary" not in st.session_state:
        st.session_state.schedulerDictionary = {}

# Call once at app start
init_session()

st.title("🐾 PawPal+")

# Now ownerList persists across reruns
if st.button("Add Owner"):
    owner = newOwner("New Owner")
    st.session_state.ownerList.append(owner)

st.write(f"Total owners: {len(st.session_state.ownerList)}")
```

## Key Takeaway

**session_state = "memory" for your Streamlit app**

Without it: App has amnesia, forgets everything on rerun
With it: App remembers your data across interactions
