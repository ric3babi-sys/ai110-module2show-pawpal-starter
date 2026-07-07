"""
Unit tests for PawPal+ pet care system.
Tests core functionality of Owner, Pet, Task, and Scheduler classes.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path to import pawpal_system
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from pawpal_system import (
    Owner, Pet, Task, Scheduler,
    newOwner, newPet, newScheduler,
    clearAllData, ownerList, petList, schedulerDictionary
)


class TestTaskDoTask:
    """Test suite for Task.doTask() method and completion status."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        # Clear global data structures
        clearAllData()
        ownerList.clear()
        petList.clear()
        schedulerDictionary.clear()

    def test_task_initial_status_is_incomplete(self):
        """Verify that a newly created Task has incomplete status."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=0)

        assert task.isTaskCompleted() is False, "New task should be incomplete"
        assert task.completed is False, "Task.completed should be False"

    def test_doTask_marks_task_as_completed(self):
        """Verify that doTask() changes task status from incomplete to completed."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=0)

        # Verify initial state
        assert task.isTaskCompleted() is False, "Task should initially be incomplete"

        # Call doTask()
        task.doTask()

        # Verify status changed
        assert task.isTaskCompleted() is True, "Task should be completed after doTask()"
        assert task.completed is True, "Task.completed should be True after doTask()"

    def test_doTask_sets_completed_timestamp(self):
        """Verify that doTask() sets the completed_at timestamp."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=0)

        # Verify timestamp is initially None
        assert task.completed_at is None, "completed_at should be None before doTask()"

        # Call doTask()
        before_time = datetime.now()
        task.doTask()
        after_time = datetime.now()

        # Verify timestamp is set
        assert task.completed_at is not None, "completed_at should be set after doTask()"
        assert isinstance(task.completed_at, datetime), "completed_at should be a datetime object"
        assert before_time <= task.completed_at <= after_time, \
            "completed_at should be between before and after call time"

    def test_doTask_multiple_calls(self):
        """Verify that calling doTask() multiple times keeps task completed."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=0)

        # First call to doTask()
        task.doTask()
        first_completion_time = task.completed_at

        assert task.isTaskCompleted() is True, "Task should be completed after first doTask()"

        # Second call to doTask()
        task.doTask()
        second_completion_time = task.completed_at

        # Task should still be completed
        assert task.isTaskCompleted() is True, "Task should remain completed after second doTask()"
        # Second completion time should be later or equal to first
        assert second_completion_time >= first_completion_time, \
            "Second completion time should be >= first completion time"

    def test_doTask_with_different_task_types(self):
        """Verify that doTask() works for all task types."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)

        task_codes = [0, 1, 2, 3]  # Walk, Feed, Nap, Vet
        task_names = ["Walk", "Feed", "Nap", "Vet"]

        for task_code, task_name in zip(task_codes, task_names):
            task = Task(pet=pet, taskCode=task_code)

            assert task.isTaskCompleted() is False, \
                f"{task_name} task should initially be incomplete"

            task.doTask()

            assert task.isTaskCompleted() is True, \
                f"{task_name} task should be completed after doTask()"

    def test_task_completion_flow(self):
        """Verify complete workflow: create task -> set duration -> do task -> verify."""
        owner = newOwner("John")
        pet = newPet("Fluffy", owner)
        task = Task(pet=pet, taskCode=0)  # Walk task

        # Setup phase
        task.setTaskDuration(30)
        assert task.getTaskDuration() == 30, "Duration should be set to 30"
        assert task.isTaskCompleted() is False, "Task should be incomplete initially"

        # Create scheduler
        scheduler = newScheduler(
            task,
            year=datetime.now().year,
            month=datetime.now().month,
            date=datetime.now().day,
            time="09:00"
        )
        assert scheduler.getTask() == task, "Scheduler should reference the task"

        # Execute task
        task.doTask()

        # Verify completion
        assert task.isTaskCompleted() is True, "Task should be completed"
        assert task.completed_at is not None, "Completion timestamp should be set"
        assert scheduler.getTask().isTaskCompleted() is True, \
            "Scheduler's referenced task should show as completed"

    def test_completed_attribute_vs_method(self):
        """Verify that completed attribute and isTaskCompleted() method are consistent."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=0)

        # Before doTask()
        assert task.completed is False, "completed attribute should be False"
        assert task.isTaskCompleted() is False, "isTaskCompleted() should return False"

        # After doTask()
        task.doTask()
        assert task.completed is True, "completed attribute should be True"
        assert task.isTaskCompleted() is True, "isTaskCompleted() should return True"


class TestPetTasks:
    """Test suite for Pet task management and counting."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        clearAllData()
        ownerList.clear()
        petList.clear()
        schedulerDictionary.clear()

    def test_pet_initial_task_count_is_zero(self):
        """Verify that a newly created Pet has zero tasks."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)

        assert pet.getTaskCount() == 0, "New pet should have zero tasks"
        assert len(pet.getPetTaskList()) == 0, "Pet task list should be empty"

    def test_add_single_task_increases_count(self):
        """Verify that adding a single task increases task count to 1."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=0)

        # Add task
        result = pet.addPetTask(task)

        assert result is True, "addPetTask should return True"
        assert pet.getTaskCount() == 1, "Task count should be 1 after adding one task"
        assert len(pet.getPetTaskList()) == 1, "Pet task list should contain one task"
        assert pet.getPetTaskList()[0] == task, "Task list should contain the added task"

    def test_add_multiple_tasks_increases_count(self):
        """Verify that adding multiple tasks increases task count correctly."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)

        # Create and add 3 tasks
        task1 = Task(pet=pet, taskCode=0)  # Walk
        task2 = Task(pet=pet, taskCode=1)  # Feed
        task3 = Task(pet=pet, taskCode=2)  # Nap

        # Initial count
        assert pet.getTaskCount() == 0, "Initial task count should be 0"

        # Add first task
        pet.addPetTask(task1)
        assert pet.getTaskCount() == 1, "Task count should be 1 after adding first task"

        # Add second task
        pet.addPetTask(task2)
        assert pet.getTaskCount() == 2, "Task count should be 2 after adding second task"

        # Add third task
        pet.addPetTask(task3)
        assert pet.getTaskCount() == 3, "Task count should be 3 after adding third task"

    def test_add_tasks_maintains_task_list(self):
        """Verify that added tasks are maintained in the pet's task list."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)

        # Create tasks with different types
        tasks = [
            Task(pet=pet, taskCode=0),  # Walk
            Task(pet=pet, taskCode=1),  # Feed
            Task(pet=pet, taskCode=2),  # Nap
        ]

        # Add all tasks
        for task in tasks:
            pet.addPetTask(task)

        # Verify all tasks are in the list
        task_list = pet.getPetTaskList()
        assert len(task_list) == 3, "Task list should contain 3 tasks"
        for i, task in enumerate(tasks):
            assert task_list[i] == task, f"Task {i} should match added task"

    def test_add_multiple_different_task_types(self):
        """Verify task count increases for all task types."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)

        task_types = [0, 1, 2, 3]  # Walk, Feed, Nap, Vet
        task_names = ["Walk", "Feed", "Nap", "Vet"]

        for task_code, task_name in zip(task_types, task_names):
            task = Task(pet=pet, taskCode=task_code)
            result = pet.addPetTask(task)

            assert result is True, f"Adding {task_name} task should return True"
            assert pet.getTaskCount() == task_code + 1, \
                f"Task count should be {task_code + 1} after adding {task_name} task"

    def test_task_count_matches_task_list_length(self):
        """Verify that getTaskCount() matches the actual task list length."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)

        for i in range(5):
            task = Task(pet=pet, taskCode=i % 4)
            pet.addPetTask(task)

            count = pet.getTaskCount()
            list_length = len(pet.getPetTaskList())
            assert count == list_length, \
                f"Task count ({count}) should match task list length ({list_length})"

    def test_prevent_duplicate_task_addition(self):
        """Verify that adding the same task twice is prevented."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=0)

        # Add task first time
        result1 = pet.addPetTask(task)
        assert result1 is True, "First add should return True"
        assert pet.getTaskCount() == 1, "Task count should be 1"

        # Try to add same task again
        result2 = pet.addPetTask(task)
        assert result2 is False, "Duplicate add should return False"
        assert pet.getTaskCount() == 1, "Task count should still be 1 (no duplicate added)"

    def test_add_task_with_pending_and_completed(self):
        """Verify task count includes both pending and completed tasks."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)

        # Create multiple tasks
        tasks = [Task(pet=pet, taskCode=i % 4) for i in range(4)]

        # Add all tasks
        for task in tasks:
            pet.addPetTask(task)

        assert pet.getTaskCount() == 4, "Task count should be 4"
        assert pet.getPendingTaskCount() == 4, "All tasks should be pending"

        # Complete some tasks
        tasks[0].doTask()
        tasks[2].doTask()

        assert pet.getTaskCount() == 4, "Total task count should still be 4"
        assert pet.getCompletedTaskCount() == 2, "Completed task count should be 2"
        assert pet.getPendingTaskCount() == 2, "Pending task count should be 2"


class TestTaskInitialization:
    """Test suite for Task initialization and validation."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        clearAllData()
        ownerList.clear()
        petList.clear()
        schedulerDictionary.clear()

    def test_task_requires_pet_and_taskcode(self):
        """Verify that Task requires pet and taskCode parameters."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)

        # Valid task creation
        task = Task(pet=pet, taskCode=0)
        assert task.pet == pet, "Task should store pet reference"
        assert task.taskCode == 0, "Task should store taskCode"

    def test_task_default_values(self):
        """Verify Task default attribute values."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=1)

        assert task.duration == 0, "Duration should default to 0"
        assert task.completed is False, "Completed should default to False"
        assert task.completed_at is None, "completed_at should default to None"
        assert isinstance(task.schedulerList, list), "schedulerList should be a list"
        assert len(task.schedulerList) == 0, "schedulerList should be empty initially"

    def test_invalid_taskcode_raises_error(self):
        """Verify that invalid taskCode raises ValueError."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)

        with pytest.raises(ValueError):
            Task(pet=pet, taskCode=999)  # Invalid taskCode

    def test_negative_duration_raises_error(self):
        """Verify that negative duration raises ValueError."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=0)

        with pytest.raises(ValueError):
            task.setTaskDuration(-30)  # Negative duration


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
