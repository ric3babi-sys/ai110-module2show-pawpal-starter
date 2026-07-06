"""
PawPal+ System Module

This module defines the core classes for the PawPal+ pet care application:
- Owner: Represents a pet owner
- Pet: Represents a pet owned by an owner
- Task: Represents a service task for a pet (walk, feed, nap, vet visit)
- Scheduler: Reserves a specific date and time for a pet service task
"""

from dataclasses import dataclass, field
from typing import List, Optional


# Counter variables for auto-generating unique IDs
_owner_id_counter = 0
_pet_id_counter = 0
_task_id_counter = 0
_scheduler_id_counter = 0


@dataclass
class Owner:
    """
    Represents a pet owner in the PawPal+ system.

    Attributes:
        ownerID: Unique identifier for the owner (auto-generated)
        ownerName: Name of the owner
        petList: List of pets owned by this owner
    """
    ownerName: str
    ownerID: int = field(default=0, init=False)
    petList: List['Pet'] = field(default_factory=list)

    def __post_init__(self):
        """Generate unique ownerID after dataclass initialization."""
        global _owner_id_counter
        _owner_id_counter += 1
        self.ownerID = _owner_id_counter

    def getOwnerID(self) -> int:
        """Return the unique owner ID."""
        pass

    def getOwnerName(self) -> str:
        """Return the owner's name."""
        pass

    def setPet(self, pet: 'Pet') -> None:
        """Add a pet to this owner's pet list."""
        pass

    def getPetByName(self, name: str) -> Optional['Pet']:
        """Return a pet from the owner's list by name, or None if not found."""
        pass

    def getPetList(self) -> List['Pet']:
        """Return the list of all pets owned by this owner."""
        pass


@dataclass
class Pet:
    """
    Represents a pet in the PawPal+ system.

    Attributes:
        petID: Unique identifier for the pet (auto-generated)
        petName: Name of the pet
        owner: The Owner object who owns this pet
        petTaskList: List of tasks scheduled for this pet
    """
    petName: str
    owner: Owner
    petID: int = field(default=0, init=False)
    petTaskList: List['Task'] = field(default_factory=list)

    def __post_init__(self):
        """Generate unique petID after dataclass initialization."""
        global _pet_id_counter
        _pet_id_counter += 1
        self.petID = _pet_id_counter

    def getOwner(self) -> Owner:
        """Return the owner of this pet."""
        pass

    def getPetID(self) -> int:
        """Return the unique pet ID."""
        pass

    def getPetName(self) -> str:
        """Return the pet's name."""
        pass

    def addPetTask(self, task: 'Task') -> None:
        """Add a task to this pet's task list."""
        pass

    def removePetTask(self, task: 'Task') -> None:
        """Remove a task from this pet's task list."""
        pass

    def getPetTaskList(self) -> List['Task']:
        """Return the list of all tasks for this pet."""
        pass


@dataclass
class Task:
    """
    Represents a service task for a pet in the PawPal+ system.

    Attributes:
        taskID: Unique identifier for the task (auto-generated)
        pet: The Pet object that this task is for
        taskCode: Integer code representing the type of task (0: Walk, 1: Feed, 2: Nap, 3: Vet)
        duration: Duration of the task in minutes
        completed: Boolean indicating if the task has been completed
    """
    pet: Pet
    taskCode: int
    taskID: int = field(default=0, init=False)
    duration: int = field(default=0)
    completed: bool = field(default=False)

    def __post_init__(self):
        """Generate unique taskID after dataclass initialization."""
        global _task_id_counter
        _task_id_counter += 1
        self.taskID = _task_id_counter

    def getTaskID(self) -> int:
        """Return the unique task ID."""
        pass

    def getPet(self) -> Pet:
        """Return the pet that this task is for."""
        pass

    def getTaskCode(self) -> int:
        """Return the task code representing the type of service."""
        pass

    def isTaskCompleted(self) -> bool:
        """Return whether this task has been completed."""
        pass

    def setTaskDuration(self, duration: int) -> None:
        """Set the duration of the task in minutes."""
        pass

    def getTaskDuration(self) -> int:
        """Return the duration of the task in minutes."""
        pass

    def doTask(self) -> None:
        """Mark the task as completed."""
        pass


@dataclass
class Scheduler:
    """
    Represents a scheduled time slot for a pet service task.

    Attributes:
        schedulerID: Unique identifier for the schedule entry (auto-generated)
        task: The Task object that is being scheduled
        year: Year of the scheduled date (YYYY)
        month: Month of the scheduled date (1-12), formatted with leading zero if < 10
        date: Day of the scheduled date (1-31), formatted with leading zero if < 10
        time: Time of the scheduled task (HH:MM format)
    """
    task: Task
    year: int = field(default=0)
    month: int = field(default=0)
    date: int = field(default=0)
    time: str = field(default="")
    schedulerID: int = field(default=0, init=False)

    def __post_init__(self):
        """Generate unique schedulerID after dataclass initialization."""
        global _scheduler_id_counter
        _scheduler_id_counter += 1
        self.schedulerID = _scheduler_id_counter

    def getSchedulerID(self) -> int:
        """Return the unique scheduler ID."""
        pass

    def getYear(self) -> int:
        """Return the year of the scheduled date."""
        pass

    def setYear(self, year: int) -> None:
        """Set the year of the scheduled date."""
        pass

    def getMonth(self) -> str:
        """Return the month of the scheduled date as a zero-padded string (e.g., '05')."""
        pass

    def setMonth(self, month: int) -> None:
        """
        Set the month of the scheduled date (1-12).
        Values will be stored and formatted with a leading zero if less than 10.
        """
        pass

    def getDate(self) -> str:
        """Return the day of the scheduled date as a zero-padded string (e.g., '07')."""
        pass

    def setDate(self, date: int) -> None:
        """
        Set the day of the scheduled date (1-31).
        Values will be stored and formatted with a leading zero if less than 10.
        """
        pass

    def getTime(self) -> str:
        """Return the time of the scheduled task (HH:MM format)."""
        pass

    def setTime(self, time: str) -> None:
        """Set the time of the scheduled task (HH:MM format)."""
        pass

    def getTask(self) -> Task:
        """Return the task that is being scheduled."""
        pass
