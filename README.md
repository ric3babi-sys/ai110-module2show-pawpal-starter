# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```
Sample Output from TERMINAL
(.venv-1) mait@Ubuntu-dev:~/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter$ clear && python3 main.py
======================================================================
PawPal+ Pet Care System - Example Usage
======================================================================

[1] Creating Owner...
    ✓ Owner created: John Smith (ID: 1)

[2] Creating first Pet...
    ✓ Pet created: Fluffy (ID: 1)
      Owner: John Smith

[3] Creating second Pet...
    ✓ Pet created: Buddy (ID: 2)
      Owner: John Smith

[4] John Smith's Pets Summary:
    Total pets owned: 2
      • Fluffy (ID: 1)
      • Buddy (ID: 2)

[5] Creating Tasks for Fluffy...
    ✓ Task 1: Walk (30 min) - Today at 09:00
    ✓ Task 2: Feed (15 min) - Today at 12:30
    ✓ Task 3: Nap Time (60 min) - Tomorrow at 14:00

[6] Creating Tasks for Buddy...
    ✓ Task 1: Feed (15 min) - Today at 08:00
    ✓ Task 2: Walk (45 min) - Today at 16:00
    ✓ Task 3: Vet Visit (30 min) - Day after tomorrow at 10:00

[7] System Statistics:
    Total Owners: 1
    Total Pets: 2
    Total Tasks: 0
    Average pets per owner: 2

[8] Pet Statistics:
    Total Pets in system: 2
    Total Tasks: 0
    Pets with pending tasks: 0
    Pets with no tasks: 2

======================================================================
TODAY'S SCHEDULE
======================================================================

Date: 2026-07-07
Total activities scheduled: 4

  1. [08:00] Buddy - Feed Pet (15 min)
  2. [09:00] Fluffy - Walk Pet (30 min)
  3. [12:30] Fluffy - Feed Pet (15 min)
  4. [16:00] Buddy - Walk Pet (45 min)

[9] Scheduler Statistics:
    Total Schedulers: 6
    Total Dates Scheduled: 3
    Today's Activities: 4
    Pending Activities: 6
    Total Duration: 195 minutes

======================================================================
Example completed successfully!
======================================================================

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest
(.venv-1) mait@Ubuntu-dev:~/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter$ pytest
======================================================= test session starts ========================================================
platform linux -- Python 3.13.7, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/mait/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter
plugins: anyio-4.13.0
collected 19 items                                                                                                                 

tests/test_pawpal.py ...................                                                                                     [100%]

======================================================== 19 passed in 0.56s ========================================================

# Run with coverage:
pytest --cov
```
(.venv-1) mait@Ubuntu-dev:~/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter$ pytest --cov
======================================================= test session starts ========================================================
platform linux -- Python 3.13.7, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/mait/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter
plugins: cov-7.1.0, anyio-4.13.0
collected 19 items                                                                                                                 

tests/test_pawpal.py ...................                                                                                     [100%]

========================================================== tests coverage ==========================================================
_________________________________________ coverage: platform linux, python 3.13.7-final-0 __________________________________________

Name                   Stmts   Miss  Cover
------------------------------------------
pawpal_system.py         692    408    41%
tests/__init__.py          0      0   100%
tests/test_pawpal.py     199      1    99%
------------------------------------------
TOTAL                    891    409    54%
======================================================== 19 passed in 0.80s ========================================================

Sample test output:
(.venv-1) mait@Ubuntu-dev:~/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter$ python3 tests/test_pawpal.py 
======================================================= test session starts ========================================================
platform linux -- Python 3.13.7, pytest-9.0.3, pluggy-1.6.0 -- /home/mait/Documents/codepath/AI/.venv-1/bin/python3
cachedir: .pytest_cache
rootdir: /home/mait/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter
plugins: cov-7.1.0, anyio-4.13.0
collected 19 items                                                                                                                 

tests/test_pawpal.py::TestTaskDoTask::test_task_initial_status_is_incomplete PASSED                                          [  5%]
tests/test_pawpal.py::TestTaskDoTask::test_doTask_marks_task_as_completed PASSED                                             [ 10%]
tests/test_pawpal.py::TestTaskDoTask::test_doTask_sets_completed_timestamp PASSED                                            [ 15%]
tests/test_pawpal.py::TestTaskDoTask::test_doTask_multiple_calls PASSED                                                      [ 21%]
tests/test_pawpal.py::TestTaskDoTask::test_doTask_with_different_task_types PASSED                                           [ 26%]
tests/test_pawpal.py::TestTaskDoTask::test_task_completion_flow PASSED                                                       [ 31%]
tests/test_pawpal.py::TestTaskDoTask::test_completed_attribute_vs_method PASSED                                              [ 36%]
tests/test_pawpal.py::TestPetTasks::test_pet_initial_task_count_is_zero PASSED                                               [ 42%]
tests/test_pawpal.py::TestPetTasks::test_add_single_task_increases_count PASSED                                              [ 47%]
tests/test_pawpal.py::TestPetTasks::test_add_multiple_tasks_increases_count PASSED                                           [ 52%]
tests/test_pawpal.py::TestPetTasks::test_add_tasks_maintains_task_list PASSED                                                [ 57%]
tests/test_pawpal.py::TestPetTasks::test_add_multiple_different_task_types PASSED                                            [ 63%]
tests/test_pawpal.py::TestPetTasks::test_task_count_matches_task_list_length PASSED                                          [ 68%]
tests/test_pawpal.py::TestPetTasks::test_prevent_duplicate_task_addition PASSED                                              [ 73%]
tests/test_pawpal.py::TestPetTasks::test_add_task_with_pending_and_completed PASSED                                          [ 78%]
tests/test_pawpal.py::TestTaskInitialization::test_task_requires_pet_and_taskcode PASSED                                     [ 84%]
tests/test_pawpal.py::TestTaskInitialization::test_task_default_values PASSED                                                [ 89%]
tests/test_pawpal.py::TestTaskInitialization::test_invalid_taskcode_raises_error PASSED                                      [ 94%]
tests/test_pawpal.py::TestTaskInitialization::test_negative_duration_raises_error PASSED                                     [100%]

======================================================== 19 passed in 0.13s ========================================================
```
# Paste your pytest output here
```
(.venv-1) mait@Ubuntu-dev:~/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter$ python -m pytest
======================================================= test session starts ========================================================
platform linux -- Python 3.13.7, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/mait/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter
plugins: cov-7.1.0, anyio-4.13.0
collected 19 items                                                                                                                 

tests/test_pawpal.py ...................                                                                                     [100%]

======================================================== 19 passed in 0.18s ========================================================

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
