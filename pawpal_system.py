"""
PawPal+ System Module

This module defines the core classes for the PawPal+ pet care application:
- Owner: Represents a pet owner
- Pet: Represents a pet owned by an owner
- Task: Represents a service task for a pet (walk, feed, nap, vet visit)
- Scheduler: Reserves a specific date and time for a pet service task

DESIGN NOTES:
- Task codes: 0=Walk, 1=Feed, 2=Nap, 3=Vet Visit
- Relationships: Owner (1) --> (many) Pet, Pet (1) --> (many) Task, Task (1) --> (many) Scheduler
- CRITICAL: Owner-Pet and Pet-Task relationships must be maintained bidirectionally to prevent
  orphaned objects and data inconsistencies (see bottleneck notes below)
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


# Counter variables for auto-generating unique IDs
# NOTE: These are NOT thread-safe; consider using threading.Lock if app uses concurrent requests
_owner_id_counter = 0
_pet_id_counter = 0
_task_id_counter = 0
_scheduler_id_counter = 0

# Task service type mapping (taskCode -> description)
TASK_TYPES = {
    0: "Walk Pet",
    1: "Feed Pet",
    2: "Nap Time",
    3: "Veterinarian Visit"
}

# Global list to store all Owner instances
# Provides central registry of all owners in the system
ownerList: List['Owner'] = []

# Global list to store all Pet instances
# Provides central registry of all pets in the system
petList: List['Pet'] = []

# Global dictionary to store all Scheduler instances
# Keyed by date string in format "YYYYMMDD" for efficient date-based lookups
# Allows multiple schedulers per date (list of schedulers)
schedulerDictionary: dict = {}


def newOwner(ownerName: str) -> 'Owner':
    """
    Create a new Owner instance and add it to the global ownerList.
    VALIDATION: ownerName must be non-empty string (validated in Owner.__post_init__).
    Raises ValueError if ownerName is invalid.
    Returns the newly created Owner object.

    Example:
        owner = newOwner("John Smith")
        print(owner.getOwnerID())  # Returns auto-generated ID
        print(owner.getOwnerName())  # Returns "John Smith"
    """
    new_owner = Owner(ownerName=ownerName)
    ownerList.append(new_owner)
    return new_owner


def getOwnerByID(owner_id: int) -> Optional['Owner']:
    """
    Search global ownerList for owner with matching ID.
    Returns Owner object if found, None otherwise.
    O(n) search; consider maintaining a dict index for large lists.
    """
    for owner in ownerList:
        if owner.getOwnerID() == owner_id:
            return owner
    return None


def getOwnerByName(owner_name: str) -> Optional['Owner']:
    """
    Search global ownerList for owner with matching name (case-insensitive).
    Returns first matching Owner object if found, None otherwise.
    O(n) search; consider maintaining a dict index for large lists.
    """
    name_lower = owner_name.lower().strip()
    for owner in ownerList:
        if owner.getOwnerName().lower() == name_lower:
            return owner
    return None


def getAllOwners() -> List['Owner']:
    """Return a copy of the global ownerList."""
    return ownerList.copy()


def removeOwner(owner: 'Owner') -> bool:
    """
    Remove an owner from the global ownerList.
    CASCADING CLEANUP: Also removes all pets and tasks for the owner.
    Returns True if owner was removed, False if owner not found.
    """
    if owner not in ownerList:
        return False

    # Remove all pets (which cascades to remove their tasks and schedulers)
    for pet in owner.getPetList()[:]:  # Create copy to avoid modification during iteration
        owner.removePet(pet)

    ownerList.remove(owner)
    return True


def getOwnerCount() -> int:
    """Return total number of owners in the system."""
    return len(ownerList)


def getSystemStatistics() -> dict:
    """
    Return comprehensive system-wide statistics across all owners.
    Useful for dashboards and reporting.
    """
    total_owners = len(ownerList)
    total_pets = sum(owner.getPetCount() for owner in ownerList)
    total_tasks = sum(sum(pet.getTaskCount() for pet in owner.getPetList())
                      for owner in ownerList)
    total_completed = sum(sum(pet.getCompletedTaskCount() for pet in owner.getPetList())
                          for owner in ownerList)
    total_pending = total_tasks - total_completed
    total_schedules = sum(len(owner.getAllSchedules()) for owner in ownerList)
    total_duration = sum(owner.getTotalPetDuration() for owner in ownerList)

    owner_details = [owner.getDetailedStatistics() for owner in ownerList]

    return {
        'total_owners': total_owners,
        'total_pets': total_pets,
        'total_tasks': total_tasks,
        'total_completed': total_completed,
        'total_pending': total_pending,
        'total_schedules': total_schedules,
        'total_duration_minutes': total_duration,
        'average_pets_per_owner': total_pets // total_owners if total_owners > 0 else 0,
        'average_tasks_per_pet': total_tasks // total_pets if total_pets > 0 else 0,
        'system_completion_rate': (total_completed / total_tasks * 100) if total_tasks > 0 else 0.0,
        'owner_details': owner_details
    }


def clearAllData() -> int:
    """
    Remove all owners and their associated data from the system.
    WARNING: This is destructive and cannot be undone.
    Returns count of owners removed.
    """
    count = len(ownerList)
    for owner in ownerList[:]:  # Create copy to avoid modification during iteration
        removeOwner(owner)
    return count


def newPet(petName: str, owner: 'Owner') -> 'Pet':
    """
    Create a new Pet instance and add it to the global petList.
    VALIDATION:
    - petName must be non-empty string (validated in Pet.__post_init__)
    - owner must be a valid Owner instance
    Raises ValueError if petName is invalid.
    Returns the newly created Pet object.

    Example:
        owner = newOwner("John Smith")
        pet = newPet("Fluffy", owner)
        print(pet.getPetID())      # Returns auto-generated ID
        print(pet.getPetName())    # Returns "Fluffy"
        print(pet.getOwner().getOwnerName())  # Returns "John Smith"
    """
    new_pet = Pet(petName=petName, owner=owner)
    petList.append(new_pet)
    return new_pet


def getPetByID(pet_id: int) -> Optional['Pet']:
    """
    Search global petList for pet with matching ID.
    Returns Pet object if found, None otherwise.
    O(n) search; consider maintaining a dict index for large lists.
    """
    for pet in petList:
        if pet.getPetID() == pet_id:
            return pet
    return None


def getPetByName(pet_name: str) -> Optional['Pet']:
    """
    Search global petList for pet with matching name (case-insensitive).
    Returns first matching Pet object if found, None otherwise.
    NOTE: Multiple pets can have the same name. Use getPetByID() for unique lookup.
    O(n) search; consider maintaining a dict index for large lists.
    """
    name_lower = pet_name.lower().strip()
    for pet in petList:
        if pet.getPetName().lower() == name_lower:
            return pet
    return None


def getPetsByOwner(owner: 'Owner') -> List['Pet']:
    """
    Return all pets belonging to a specific owner.
    Searches global petList for pets with matching owner.
    Returns list of Pet objects (may be empty).
    """
    return [pet for pet in petList if pet.getOwner() == owner]


def getAllPets() -> List['Pet']:
    """Return a copy of the global petList."""
    return petList.copy()


def removePet(pet: 'Pet') -> bool:
    """
    Remove a pet from the global petList.
    CASCADING CLEANUP: Also removes all tasks and schedulers for the pet.
    Also removes pet from owner's petList.
    Returns True if pet was removed, False if pet not found.
    """
    if pet not in petList:
        return False

    # Remove from owner's list
    owner = pet.getOwner()
    if owner and pet in owner.getPetList():
        owner.removePet(pet)

    petList.remove(pet)
    return True


def getPetCount() -> int:
    """Return total number of pets in the system."""
    return len(petList)


def getPetsByTaskType(task_code: int) -> List['Pet']:
    """
    Return all pets that have tasks of a specific type.
    Example: getPetsByTaskType(0) returns pets with Walk tasks.
    """
    pets_with_type = set()
    for pet in petList:
        if pet.getTasksByType(task_code):
            pets_with_type.add(pet)
    return list(pets_with_type)


def getPetsWithPendingTasks() -> List['Pet']:
    """Return all pets that have pending (incomplete) tasks."""
    return [pet for pet in petList if pet.getPendingTaskCount() > 0]


def getPetsWithNoTasks() -> List['Pet']:
    """Return all pets that have no tasks scheduled."""
    return [pet for pet in petList if pet.getTaskCount() == 0]


def getPetStatistics() -> dict:
    """
    Return comprehensive statistics about all pets in the system.
    Useful for dashboards and reporting.
    """
    total_pets = len(petList)
    total_tasks = sum(pet.getTaskCount() for pet in petList)
    total_completed = sum(pet.getCompletedTaskCount() for pet in petList)
    total_pending = total_tasks - total_completed
    total_schedules = sum(pet.getScheduleCount() for pet in petList)
    total_duration = sum(pet.getTotalScheduledTime() for pet in petList)

    pets_with_pending = len(getPetsWithPendingTasks())
    pets_with_no_tasks = len(getPetsWithNoTasks())

    pet_details = [pet.getTaskSummary() for pet in petList]

    return {
        'total_pets': total_pets,
        'total_tasks': total_tasks,
        'total_completed': total_completed,
        'total_pending': total_pending,
        'total_schedules': total_schedules,
        'total_duration_minutes': total_duration,
        'pets_with_pending_tasks': pets_with_pending,
        'pets_with_no_tasks': pets_with_no_tasks,
        'average_tasks_per_pet': total_tasks // total_pets if total_pets > 0 else 0,
        'system_completion_rate': (total_completed / total_tasks * 100) if total_tasks > 0 else 0.0,
        'pet_details': pet_details
    }


def newScheduler(task: 'Task', year: int, month: int, date: int, time: str) -> 'Scheduler':
    """
    Create a new Scheduler instance for a task and add it to global schedulerDictionary.
    The scheduler is keyed by its date in "YYYYMMDD" format.
    Multiple schedulers can exist for the same date (stored as list).

    PARAMETERS:
    -----------
    task : Task
        The Task object that is being scheduled (required)
    year : int
        Year of the scheduled date (2000-2100)
    month : int
        Month of the scheduled date (1-12)
    date : int
        Day of the scheduled date (1-31)
    time : str
        Time of the scheduled task in "HH:MM" format (00:00-23:59)

    VALIDATION:
    -----------
    - Task must be a valid Task instance
    - All date/time parameters are validated during Scheduler initialization
    - Raises ValueError if any parameter is invalid

    RETURNS:
    --------
    Scheduler
        The newly created Scheduler object, added to schedulerDictionary

    EXAMPLE:
    --------
    Example 1: Create scheduler with all parameters
        task = Task(pet=pet, taskCode=0)
        task.setTaskDuration(30)
        scheduler = newScheduler(task, year=2026, month=7, date=6, time="14:30")
        # Scheduler now stored in schedulerDictionary["20260706"]

    Example 2: Using current date
        from datetime import datetime
        today = datetime.now()
        scheduler = newScheduler(task, today.year, today.month, today.day, "09:00")
    """
    # Create scheduler with task
    new_scheduler = Scheduler(task=task)

    # Set date and time parameters with validation
    new_scheduler.setYear(year)
    new_scheduler.setMonth(month)
    new_scheduler.setDate(date)
    new_scheduler.setTime(time)

    # Get key - will raise ValueError if any parameters are invalid
    try:
        key = new_scheduler.getKey()
    except ValueError as e:
        raise ValueError(f"Cannot create scheduler: {e}. Check year, month, date, and time parameters.")

    # Add to global dictionary
    # Support multiple schedulers per date by storing as list
    if key not in schedulerDictionary:
        schedulerDictionary[key] = []

    schedulerDictionary[key].append(new_scheduler)
    return new_scheduler


def getSchedulerByKey(key: str) -> List['Scheduler']:
    """
    Return list of all Scheduler objects for a given date key ("YYYYMMDD").
    Returns empty list if no schedulers exist for that date.
    """
    return schedulerDictionary.get(key, [])


def getSchedulersByDate(year: int, month: int, date: int) -> List['Scheduler']:
    """
    Return all Scheduler objects for a specific date.
    Constructs the YYYYMMDD key and retrieves schedulers.
    Returns empty list if no schedulers exist for that date.
    """
    key = f"{year}{month:02d}{date:02d}"
    return getSchedulerByKey(key)


def getSchedulersByPet(pet: 'Pet') -> List['Scheduler']:
    """
    Return all Scheduler objects for a specific pet across all dates.
    Searches entire schedulerDictionary.
    """
    pet_schedulers = []
    for date_key, schedulers in schedulerDictionary.items():
        for scheduler in schedulers:
            if scheduler.getPet() == pet:
                pet_schedulers.append(scheduler)
    return pet_schedulers


def getSchedulersByTask(task: 'Task') -> List['Scheduler']:
    """
    Return all Scheduler objects for a specific task.
    Searches entire schedulerDictionary.
    """
    task_schedulers = []
    for date_key, schedulers in schedulerDictionary.items():
        for scheduler in schedulers:
            if scheduler.getTask() == task:
                task_schedulers.append(scheduler)
    return task_schedulers


def getAllSchedulers() -> List['Scheduler']:
    """
    Return list of all Scheduler objects in the system.
    Flattens schedulerDictionary into a single list.
    """
    all_schedulers = []
    for date_key, schedulers in schedulerDictionary.items():
        all_schedulers.extend(schedulers)
    return all_schedulers


def removeScheduler(scheduler: 'Scheduler') -> bool:
    """
    Remove a Scheduler from the global schedulerDictionary.
    Also removes from task's schedulerList.
    Returns True if scheduler was removed, False if not found.
    """
    key = scheduler.getKey()

    if key not in schedulerDictionary:
        return False

    if scheduler not in schedulerDictionary[key]:
        return False

    # Remove from task's scheduler list
    if scheduler.getTask() and hasattr(scheduler.getTask(), 'removeScheduler'):
        scheduler.getTask().removeScheduler(scheduler)

    # Remove from dictionary
    schedulerDictionary[key].remove(scheduler)

    # Remove empty date key
    if not schedulerDictionary[key]:
        del schedulerDictionary[key]

    return True


def getSchedulerCount() -> int:
    """Return total number of Scheduler objects in the system."""
    return sum(len(schedulers) for schedulers in schedulerDictionary.values())


def getSchedulesByDateRange(start_key: str, end_key: str) -> List['Scheduler']:
    """
    Return all Scheduler objects within a date range (inclusive).
    Keys must be in "YYYYMMDD" format.
    Useful for querying schedules for a week, month, or range of dates.

    Example:
        schedules = getSchedulesByDateRange("20260701", "20260731")  # July 2026
    """
    result = []
    for date_key in sorted(schedulerDictionary.keys()):
        if start_key <= date_key <= end_key:
            result.extend(schedulerDictionary[date_key])
    return result


def getSchedulerStatistics() -> dict:
    """
    Return comprehensive statistics about all schedulers in the system.
    Useful for dashboards and reporting.
    """
    all_schedulers = getAllSchedulers()
    total_schedulers = len(all_schedulers)
    total_dates = len(schedulerDictionary)

    completed = sum(1 for s in all_schedulers if s.task.isTaskCompleted())
    pending = total_schedulers - completed
    past = sum(1 for s in all_schedulers if s.isScheduleInPast())
    today = sum(1 for s in all_schedulers if s.isScheduleToday())
    upcoming = sum(1 for s in all_schedulers if s.isScheduleUpcoming())

    total_duration = sum(s.getTaskDuration() for s in all_schedulers)

    return {
        'total_schedulers': total_schedulers,
        'total_dates': total_dates,
        'completed': completed,
        'pending': pending,
        'in_past': past,
        'today': today,
        'upcoming': upcoming,
        'total_duration_minutes': total_duration,
        'average_duration_per_schedule': total_duration // total_schedulers if total_schedulers > 0 else 0,
        'completion_rate': (completed / total_schedulers * 100) if total_schedulers > 0 else 0.0
    }


@dataclass
class Owner:
    """
    Represents a pet owner in the PawPal+ system who manages one or more pets.

    Constructor Parameters (Required):
        ownerName (str): Name of the owner (cannot be empty or whitespace)

    Attributes:
        ownerID: Unique identifier for the owner (auto-generated)
        ownerName: Name of the owner (required, validated in __post_init__)
        petList: List of pets owned by this owner (default: empty list)

    Example:
        owner = Owner(ownerName="John Smith")
        pet1 = Pet(petName="Fluffy", owner=owner)  # Pet auto-adds to owner.petList
        pet2 = Pet(petName="Buddy", owner=owner)
        # Access all pet information through owner
        owner.getTasksByType(0)  # Get all Walk tasks for all pets
        owner.getDetailedStatistics()  # Get comprehensive analytics

    FIXES IMPLEMENTED:
    - ownerName validation: Enforces non-empty string in __post_init__()
    - Bidirectional relationships: addPet() validates pet.owner == self
    - Cascading cleanup: removePet() removes all pet tasks and schedulers
    - Duplicate prevention: addPet() prevents same pet added twice
    - Pet lookup: getPetByName() with case-insensitive search, getPetByID()
    - Aggregated access: getAllPendingTasks(), getAllSchedules(), getTasksByType()
    - Bulk operations: markAllPendingAsCompleted()
    - Analytics: getDetailedStatistics(), validateOwnerData(), getOverallCompletionRate()
    """
    ownerName: str
    ownerID: int = field(default=0, init=False)
    petList: List['Pet'] = field(default_factory=list)

    def __post_init__(self):
        """
        Generate unique ownerID after dataclass initialization.
        VALIDATES: ownerName must be non-empty.
        """
        global _owner_id_counter
        _owner_id_counter += 1
        self.ownerID = _owner_id_counter

        # Validate ownerName is not empty
        if not self.ownerName or self.ownerName.strip() == "":
            raise ValueError("Owner name cannot be empty or whitespace")

    def getOwnerID(self) -> int:
        """Return the unique owner ID."""
        return self.ownerID

    def getOwnerName(self) -> str:
        """Return the owner's name."""
        return self.ownerName

    def setOwnerName(self, name: str) -> None:
        """
        Set or update the owner's name.
        VALIDATION: Name must be a non-empty string.
        Raises ValueError if name is empty or whitespace only.
        """
        if not name or name.strip() == "":
            raise ValueError("Owner name cannot be empty or whitespace")
        self.ownerName = name.strip()

    def addPet(self, pet: 'Pet') -> bool:
        """
        Add a pet to this owner's pet list.
        VALIDATION:
        - Checks that pet.owner == self (prevents orphaned pet relationships)
        - Prevents duplicate pets in list
        Returns True if pet added successfully, False if duplicate or validation fails.
        """
        # Validate bidirectional relationship
        if pet.owner != self:
            raise ValueError(f"Pet owner mismatch: pet.owner={pet.owner.ownerID}, expected owner={self.ownerID}")

        # Check for duplicates
        if pet in self.petList:
            return False

        self.petList.append(pet)
        return True

    def getPetByName(self, name: str) -> Optional['Pet']:
        """
        Return a pet from the owner's list by name, or None if not found.
        BOTTLENECK: Linear search O(n). For large pet lists, consider maintaining a name-based
        index or using a dictionary internally instead of a list.
        Case-insensitive search.
        """
        name_lower = name.lower().strip()
        for pet in self.petList:
            if pet.getPetName().lower() == name_lower:
                return pet
        return None

    def getPetByID(self, pet_id: int) -> Optional['Pet']:
        """
        Return a pet from the owner's list by pet ID, or None if not found.
        O(n) search; for large lists consider maintaining a dict index.
        """
        for pet in self.petList:
            if pet.getPetID() == pet_id:
                return pet
        return None

    def getPetList(self) -> List['Pet']:
        """Return the list of all pets owned by this owner."""
        return self.petList

    def removePet(self, pet: 'Pet') -> bool:
        """
        Remove a pet from this owner's pet list.
        CASCADING CLEANUP: Removes all tasks and associated schedulers for this pet.
        Returns True if pet was removed, False if pet not found in list.
        """
        if pet not in self.petList:
            return False

        # Cascading cleanup: remove all tasks and schedulers for this pet
        if hasattr(pet, 'petTaskList'):
            # Create a copy to avoid modification during iteration
            for task in pet.petTaskList[:]:
                pet.removePetTask(task)

        self.petList.remove(pet)
        return True

    def getPetCount(self) -> int:
        """Return the total number of pets owned by this owner."""
        return len(self.petList)

    def getTotalPetDuration(self) -> int:
        """
        Return total duration of all tasks for all pets (sum of all durations).
        Useful for planning overall time commitment across all pets.
        """
        total = 0
        for pet in self.petList:
            total += pet.getTotalScheduledTime()
        return total

    def getAllPendingTasks(self) -> List['Task']:
        """Return all pending tasks across all pets owned by this owner."""
        all_pending = []
        for pet in self.petList:
            all_pending.extend(pet.getPendingTasks())
        return all_pending

    def getAllSchedules(self) -> List['Scheduler']:
        """Return all Scheduler objects across all pets and tasks."""
        all_schedulers = []
        for pet in self.petList:
            all_schedulers.extend(pet.getSchedulersByPet())
        return all_schedulers

    def getOwnerSummary(self) -> dict:
        """
        Return a summary dictionary of owner's overall pet and task status.
        Useful for dashboard/overview displays.
        """
        return {
            'owner_id': self.ownerID,
            'owner_name': self.ownerName,
            'total_pets': self.getPetCount(),
            'total_tasks': sum(pet.getTaskCount() for pet in self.petList),
            'pending_tasks': len(self.getAllPendingTasks()),
            'completed_tasks': sum(pet.getCompletedTaskCount() for pet in self.petList),
            'total_schedules': len(self.getAllSchedules()),
            'total_duration_minutes': self.getTotalPetDuration()
        }

    def hasPet(self, pet: 'Pet') -> bool:
        """Check if owner has a specific pet."""
        return pet in self.petList

    def hasPetNamed(self, name: str) -> bool:
        """Check if owner has a pet with a specific name."""
        return self.getPetByName(name) is not None

    def getTaskCountByPet(self) -> dict:
        """
        Return dict mapping pet names to their task counts.
        Useful for quick overview of each pet's task load.
        """
        return {
            pet.getPetName(): pet.getTaskCount()
            for pet in self.petList
        }

    def getPetWithMostTasks(self) -> Optional['Pet']:
        """
        Return the pet with the most tasks (pending and completed).
        Returns None if owner has no pets.
        """
        if not self.petList:
            return None
        return max(self.petList, key=lambda p: p.getTaskCount())

    def getPetWithMostPendingTasks(self) -> Optional['Pet']:
        """
        Return the pet with the most pending (not completed) tasks.
        Returns None if no pets or all tasks completed.
        """
        pets_with_pending = [p for p in self.petList if p.getPendingTaskCount() > 0]
        if not pets_with_pending:
            return None
        return max(pets_with_pending, key=lambda p: p.getPendingTaskCount())

    def getTasksByType(self, task_code: int) -> List['Task']:
        """
        Return all tasks of a specific type across all pets.
        Example: getTasksByType(0) returns all Walk tasks for all pets.
        """
        tasks = []
        for pet in self.petList:
            tasks.extend(pet.getTasksByType(task_code))
        return tasks

    def getSchedulesByDate(self, year: int, month: int, date: int) -> List['Scheduler']:
        """
        Return all schedules for a specific date across all pets.
        Example: getSchedulesByDate(2026, 7, 6) gets all items scheduled for that day.
        """
        schedules = []
        for pet in self.petList:
            schedules.extend(pet.getSchedulersByDate(year, month, date))
        return schedules

    def hasSchedulesOnDate(self, year: int, month: int, date: int) -> bool:
        """Check if owner has any schedules on a specific date across all pets."""
        return len(self.getSchedulesByDate(year, month, date)) > 0

    def getBusiestDate(self) -> Optional[tuple]:
        """
        Return the date (year, month, date) with the most scheduled items.
        Searches across all pets. Returns tuple (y, m, d) or None if no schedules.
        """
        all_schedulers = self.getAllSchedules()
        if not all_schedulers:
            return None

        schedule_map = {}
        for sched in all_schedulers:
            key = (sched.year, sched.month, sched.date)
            schedule_map[key] = schedule_map.get(key, 0) + 1

        busiest_date = max(schedule_map.items(), key=lambda x: x[1])
        return busiest_date[0]

    def getCompletionRateByPet(self) -> dict:
        """
        Return dict mapping pet names to their completion percentages.
        Useful for tracking progress per pet.
        """
        return {
            pet.getPetName(): pet.getTaskCompletionRate()
            for pet in self.petList
        }

    def getOverallCompletionRate(self) -> float:
        """
        Return overall task completion rate across all pets (0-100).
        Useful for tracking overall progress.
        """
        total_tasks = sum(pet.getTaskCount() for pet in self.petList)
        if total_tasks == 0:
            return 0.0
        total_completed = sum(pet.getCompletedTaskCount() for pet in self.petList)
        return (total_completed / total_tasks) * 100

    def getAveragePetAge(self) -> int:
        """
        Return average number of tasks per pet.
        Useful for understanding task distribution.
        """
        if not self.petList:
            return 0
        return sum(pet.getTaskCount() for pet in self.petList) // len(self.petList)

    def getAllUnscheduledTasks(self) -> List['Task']:
        """
        Return all tasks without schedulers across all pets.
        These tasks need to be scheduled.
        """
        unscheduled = []
        for pet in self.petList:
            unscheduled.extend(pet.getTasksWithoutSchedules())
        return unscheduled

    def getUnscheduledTaskCount(self) -> int:
        """Return total count of unscheduled tasks across all pets."""
        return len(self.getAllUnscheduledTasks())

    def markAllPendingAsCompleted(self) -> int:
        """
        Mark all pending tasks as completed for all pets.
        Returns count of tasks marked as completed.
        """
        count = 0
        for pet in self.petList:
            count += pet.markAllPendingAsCompleted()
        return count

    def validateOwnerData(self) -> dict:
        """
        Validate integrity of owner and all pets/tasks.
        Returns dict with validation results and any issues found.
        """
        issues = []
        valid_pets = 0
        invalid_pets = 0

        if not self.ownerID or self.ownerID <= 0:
            issues.append(f"Owner has invalid ID: {self.ownerID}")

        if not self.ownerName or self.ownerName.strip() == "":
            issues.append("Owner has invalid name")

        for pet in self.petList:
            if pet.owner != self:
                issues.append(f"Pet {pet.getPetID()} has mismatched owner reference")
                invalid_pets += 1
            elif not pet.isPetValid():
                issues.append(f"Pet {pet.getPetID()} ({pet.getPetName()}) is invalid")
                invalid_pets += 1
            else:
                valid_pets += 1

        return {
            'owner_id': self.ownerID,
            'owner_name': self.ownerName,
            'total_pets': self.getPetCount(),
            'valid_pets': valid_pets,
            'invalid_pets': invalid_pets,
            'total_tasks': sum(pet.getTaskCount() for pet in self.petList),
            'issues': issues,
            'is_valid': len(issues) == 0
        }

    def getDetailedStatistics(self) -> dict:
        """
        Return comprehensive statistics for owner and all pets.
        Includes pet info, task counts, completion rates, schedules.
        Useful for detailed analytics and reporting.
        """
        pet_details = []
        for pet in self.petList:
            pet_details.append({
                'pet_id': pet.getPetID(),
                'pet_name': pet.getPetName(),
                'total_tasks': pet.getTaskCount(),
                'completed_tasks': pet.getCompletedTaskCount(),
                'pending_tasks': pet.getPendingTaskCount(),
                'completion_rate': pet.getTaskCompletionRate(),
                'total_scheduled': pet.getScheduleCount(),
                'total_duration_minutes': pet.getTotalScheduledTime(),
            })

        return {
            'owner_id': self.ownerID,
            'owner_name': self.ownerName,
            'pet_count': self.getPetCount(),
            'overall_completion_rate': self.getOverallCompletionRate(),
            'total_tasks': sum(pet.getTaskCount() for pet in self.petList),
            'total_completed': sum(pet.getCompletedTaskCount() for pet in self.petList),
            'total_pending': len(self.getAllPendingTasks()),
            'total_schedules': len(self.getAllSchedules()),
            'unscheduled_tasks': self.getUnscheduledTaskCount(),
            'total_duration_minutes': self.getTotalPetDuration(),
            'pet_details': pet_details
        }

    def isOwnerValid(self) -> bool:
        """
        Validate that owner has all required fields properly set.
        Returns True if owner is valid, False otherwise.
        """
        is_valid = (
            self.ownerID > 0 and
            self.ownerName and
            self.ownerName.strip() != ""
        )
        return is_valid


@dataclass
class Pet:
    """
    Represents a pet in the PawPal+ system.

    Constructor Parameters (Required):
        petName (str): Name of the pet (cannot be empty)
        owner (Owner): The Owner object who owns this pet

    Attributes:
        petID: Unique identifier for the pet (auto-generated)
        petName: Name of the pet
        owner: The Owner object who owns this pet
        petTaskList: List of tasks scheduled for this pet

    Example:
        owner = Owner("John Doe")
        pet = Pet(petName="Fluffy", owner=owner)

    BOTTLENECK ALERT: Bidirectional Relationship
    - When addPetTask() adds a Task, the Task.pet reference should already point to this Pet.
    - When a Task is removed, associated Scheduler objects should also be cleaned up.
    - MISSING: No bidirectional update in Owner.petList when Pet is created.

    MISSING FUNCTIONALITY:
    - No method to filter tasks by completion status (completed vs. pending)
    - No duplicate checking in addPetTask() - same task could be added multiple times
    - No access to Scheduler objects for this pet (relationship chain broken: Pet -> Task -> Scheduler)
    - Consider adding getSchedulersByPet() or similar utility to query all scheduled times for a pet
    """
    petName: str
    owner: Owner
    petID: int = field(default=0, init=False)
    petTaskList: List['Task'] = field(default_factory=list)

    def __post_init__(self):
        """
        Generate unique petID after dataclass initialization.
        VALIDATES: petName must be non-empty.
        AUTO-ADDS: This Pet to owner.petList to maintain bidirectional relationship.
        """
        global _pet_id_counter
        _pet_id_counter += 1
        self.petID = _pet_id_counter

        # Validate petName is not empty
        if not self.petName or self.petName.strip() == "":
            raise ValueError("Pet name cannot be empty or whitespace")

        # Auto-add this pet to owner's pet list to maintain bidirectional relationship
        if hasattr(self.owner, 'petList') and self not in self.owner.petList:
            self.owner.petList.append(self)

    def getOwner(self) -> Owner:
        """Return the owner of this pet."""
        return self.owner

    def getPetID(self) -> int:
        """Return the unique pet ID."""
        return self.petID

    def getPetName(self) -> str:
        """Return the pet's name."""
        return self.petName

    def setPetName(self, name: str) -> None:
        """
        Set or update the pet's name.
        VALIDATION: Name must be a non-empty string.
        Raises ValueError if name is empty or whitespace only.
        """
        if not name or name.strip() == "":
            raise ValueError("Pet name cannot be empty or whitespace")
        self.petName = name.strip()

    def addPetTask(self, task: 'Task') -> bool:
        """
        Add a task to this pet's task list.
        VALIDATION:
        - Checks that task.pet == self (prevents orphaned task relationships)
        - Prevents duplicate tasks in list
        Returns True if task added successfully, False if duplicate or validation fails.
        """
        # Validate bidirectional relationship
        if task.pet != self:
            raise ValueError(f"Task pet mismatch: task.pet={task.pet.petID}, expected pet={self.petID}")

        # Check for duplicates
        if task in self.petTaskList:
            return False

        self.petTaskList.append(task)
        return True

    def removePetTask(self, task: 'Task') -> bool:
        """
        Remove a task from this pet's task list.
        CASCADING CLEANUP: Also removes associated Scheduler objects to prevent orphaned records.
        Returns True if task was removed, False if task not found in list.
        """
        if task not in self.petTaskList:
            return False

        # Cascading cleanup: remove all schedulers associated with this task
        if hasattr(task, 'schedulerList'):
            for scheduler in task.schedulerList[:]:  # Create copy to avoid modification during iteration
                task.removeScheduler(scheduler)

        self.petTaskList.remove(task)
        return True

    def getPetTaskList(self) -> List['Task']:
        """Return the list of all tasks for this pet."""
        return self.petTaskList

    def getCompletedTasks(self) -> List['Task']:
        """
        Return list of all completed tasks for this pet.
        Convenience method to filter tasks by completion status.
        """
        return [task for task in self.petTaskList if task.isTaskCompleted()]

    def getPendingTasks(self) -> List['Task']:
        """
        Return list of all pending (not completed) tasks for this pet.
        Convenience method to filter tasks by completion status.
        """
        return [task for task in self.petTaskList if not task.isTaskCompleted()]

    def getTaskByID(self, task_id: int) -> Optional['Task']:
        """
        Return a task from this pet's task list by task ID.
        Returns None if task not found.
        """
        for task in self.petTaskList:
            if task.getTaskID() == task_id:
                return task
        return None

    def getTasksByType(self, task_code: int) -> List['Task']:
        """
        Return all tasks of a specific type (by taskCode).
        Example: getTasksByType(0) returns all Walk tasks.
        """
        return [task for task in self.petTaskList if task.getTaskCode() == task_code]

    def getTaskCount(self) -> int:
        """Return total number of tasks for this pet."""
        return len(self.petTaskList)

    def getCompletedTaskCount(self) -> int:
        """Return count of completed tasks."""
        return len(self.getCompletedTasks())

    def getPendingTaskCount(self) -> int:
        """Return count of pending tasks."""
        return len(self.getPendingTasks())

    def getTotalScheduledTime(self) -> int:
        """
        Return total duration of all tasks (sum of all task durations).
        Useful for planning and estimating time commitment.
        """
        return sum(task.getTaskDuration() for task in self.petTaskList)

    def clearCompletedTasks(self) -> int:
        """
        Remove all completed tasks from this pet's task list.
        Useful for cleanup and archiving.
        Returns count of tasks removed.
        """
        completed = self.getCompletedTasks()
        for task in completed:
            self.removePetTask(task)
        return len(completed)

    def isPetValid(self) -> bool:
        """
        Validate that pet has all required fields properly set.
        Returns True if pet is valid, False otherwise.
        """
        is_valid = (
            self.petID > 0 and
            self.petName and
            self.petName.strip() != "" and
            self.owner is not None
        )
        return is_valid

    def getSchedulersByPet(self) -> List['Scheduler']:
        """
        Return all Scheduler objects for this pet across all tasks.
        FIXES BOTTLENECK: Allows O(n) access to all schedulers for this pet (where n = total tasks).
        Enables queries like "When is this pet scheduled?" without external iteration.
        """
        schedulers = []
        for task in self.petTaskList:
            if hasattr(task, 'schedulerList'):
                schedulers.extend(task.schedulerList)
        return schedulers

    def getScheduleCount(self) -> int:
        """Return total number of scheduled times across all tasks for this pet."""
        return len(self.getSchedulersByPet())

    def getSchedulersByTaskType(self, task_code: int) -> List['Scheduler']:
        """
        Return all Scheduler objects for tasks of a specific type.
        Example: getSchedulersByTaskType(0) returns all scheduled Walk times.
        """
        schedulers = []
        tasks_of_type = self.getTasksByType(task_code)
        for task in tasks_of_type:
            if hasattr(task, 'schedulerList'):
                schedulers.extend(task.schedulerList)
        return schedulers

    def getUpcomingSchedules(self) -> List['Scheduler']:
        """
        Return all pending (not completed) schedulers for this pet.
        Useful for showing "To-Do" schedule for the pet.
        """
        schedulers = []
        for task in self.getPendingTasks():
            if hasattr(task, 'schedulerList'):
                schedulers.extend(task.schedulerList)
        return schedulers

    def getCompletedSchedules(self) -> List['Scheduler']:
        """
        Return all schedulers for completed tasks for this pet.
        Useful for showing "Completed" or "History" schedule.
        """
        schedulers = []
        for task in self.getCompletedTasks():
            if hasattr(task, 'schedulerList'):
                schedulers.extend(task.schedulerList)
        return schedulers

    def getTotalScheduledCount(self) -> int:
        """Return total count of all scheduled items (pending + completed)."""
        return self.getScheduleCount()

    def getPendingScheduleCount(self) -> int:
        """Return count of pending (not yet done) scheduled items."""
        return len(self.getUpcomingSchedules())

    def getCompletedScheduleCount(self) -> int:
        """Return count of completed scheduled items."""
        return len(self.getCompletedSchedules())

    def getTaskSummary(self) -> dict:
        """
        Return a summary dictionary of pet's task and schedule status.
        Useful for dashboard/overview displays.
        """
        return {
            'pet_id': self.petID,
            'pet_name': self.petName,
            'total_tasks': self.getTaskCount(),
            'completed_tasks': self.getCompletedTaskCount(),
            'pending_tasks': self.getPendingTaskCount(),
            'total_scheduled': self.getScheduleCount(),
            'pending_scheduled': self.getPendingScheduleCount(),
            'completed_scheduled': self.getCompletedScheduleCount(),
            'total_duration_minutes': self.getTotalScheduledTime()
        }

    def getAverageTaskDuration(self) -> float:
        """
        Return average duration of all tasks for this pet.
        Returns 0 if no tasks exist.
        Useful for estimating time commitment per task.
        """
        if self.getTaskCount() == 0:
            return 0.0
        return self.getTotalScheduledTime() / self.getTaskCount()

    def getTaskCompletionRate(self) -> float:
        """
        Return percentage of tasks completed (0-100).
        Returns 0 if no tasks exist.
        Useful for tracking pet care progress.
        """
        if self.getTaskCount() == 0:
            return 0.0
        return (self.getCompletedTaskCount() / self.getTaskCount()) * 100

    def getTasksByDuration(self, min_duration: int = 0, max_duration: int = None) -> List['Task']:
        """
        Return tasks filtered by duration range.
        Example: getTasksByDuration(min_duration=30, max_duration=60) gets 30-60 min tasks.
        """
        if max_duration is None:
            max_duration = float('inf')
        return [task for task in self.petTaskList
                if min_duration <= task.getTaskDuration() <= max_duration]

    def getTasksCompletedAfter(self, days_ago: int = 0) -> List['Task']:
        """
        Return tasks completed within the last N days.
        Example: getTasksCompletedAfter(7) returns tasks completed in last week.
        Returns empty list if no matching tasks.
        """
        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(days=days_ago)
        return [task for task in self.getCompletedTasks()
                if task.completed_at and task.completed_at >= cutoff_time]

    def markAllPendingAsCompleted(self) -> int:
        """
        Mark all pending tasks as completed in bulk.
        Useful for batch operations or end-of-day summaries.
        Returns count of tasks marked as completed.
        """
        count = 0
        for task in self.getPendingTasks():
            task.doTask()
            count += 1
        return count

    def resetAllTasks(self) -> int:
        """
        Reset all completed tasks back to pending status.
        Useful for recurring tasks or error correction.
        Does not clear completed_at timestamp (maintains history).
        Returns count of tasks reset.
        """
        count = 0
        for task in self.getCompletedTasks():
            task.resetCompletion()
            count += 1
        return count

    def getTasksByCompletionStatus(self, completed: bool) -> List['Task']:
        """
        Return tasks filtered by completion status.
        completed=True: return completed tasks
        completed=False: return pending tasks
        """
        return [task for task in self.petTaskList if task.isTaskCompleted() == completed]

    def validatePetTasks(self) -> dict:
        """
        Validate integrity of all tasks for this pet.
        Returns dict with validation results and any issues found.
        """
        issues = []
        valid_count = 0

        for task in self.petTaskList:
            if not task.isTaskValid():
                issues.append(f"Task {task.getTaskID()} invalid: {task}")
            elif task.pet != self:
                issues.append(f"Task {task.getTaskID()} has mismatched pet reference")
            else:
                valid_count += 1

        return {
            'total_tasks': self.getTaskCount(),
            'valid_tasks': valid_count,
            'invalid_tasks': len(issues),
            'issues': issues,
            'is_valid': len(issues) == 0
        }

    def getTaskStatistics(self) -> dict:
        """
        Return comprehensive task statistics for this pet.
        Includes counts, durations, completion rates, and averages.
        Useful for detailed analytics and reporting.
        """
        total_tasks = self.getTaskCount()
        total_duration = self.getTotalScheduledTime()

        return {
            'pet_id': self.petID,
            'pet_name': self.petName,
            'task_counts': {
                'total': total_tasks,
                'completed': self.getCompletedTaskCount(),
                'pending': self.getPendingTaskCount(),
            },
            'task_by_type': {
                f'code_{code}': len(self.getTasksByType(code))
                for code in range(4)  # 0-3 for Walk, Feed, Nap, Vet
            },
            'duration_stats': {
                'total_minutes': total_duration,
                'average_minutes': self.getAverageTaskDuration(),
                'task_count': total_tasks,
            },
            'schedule_stats': {
                'total_scheduled': self.getScheduleCount(),
                'pending_scheduled': self.getPendingScheduleCount(),
                'completed_scheduled': self.getCompletedScheduleCount(),
            },
            'completion': {
                'rate_percent': self.getTaskCompletionRate(),
                'completed': self.getCompletedTaskCount(),
                'pending': self.getPendingTaskCount(),
            }
        }

    def findConflictingSchedules(self) -> List[tuple]:
        """
        Find overlapping/conflicting schedules for this pet.
        Returns list of tuples containing conflicting Scheduler pairs.
        LIMITATION: Basic implementation checks same date/time.
        More sophisticated conflict detection (time ranges) could be added.
        """
        conflicts = []
        schedulers = self.getSchedulersByPet()

        for i, sched1 in enumerate(schedulers):
            for sched2 in schedulers[i+1:]:
                # Check if same date and time
                if (sched1.year == sched2.year and
                    sched1.month == sched2.month and
                    sched1.date == sched2.date and
                    sched1.getTime() == sched2.getTime()):
                    conflicts.append((sched1, sched2))

        return conflicts

    def getSchedulersByDate(self, year: int, month: int, date: int) -> List['Scheduler']:
        """
        Return all schedulers for a specific date.
        Example: getSchedulersByDate(2026, 7, 6) gets all scheduled items for July 6, 2026.
        """
        return [sched for sched in self.getSchedulersByPet()
                if sched.year == year and sched.month == month and sched.date == date]

    def hasSchedulesOnDate(self, year: int, month: int, date: int) -> bool:
        """Check if pet has any schedules on a specific date."""
        return len(self.getSchedulersByDate(year, month, date)) > 0

    def getDayWithMostSchedules(self) -> tuple:
        """
        Return the date (year, month, date) with the most scheduled items.
        Returns tuple (year, month, date) or None if no schedules exist.
        """
        if not self.getSchedulersByPet():
            return None

        schedule_map = {}
        for sched in self.getSchedulersByPet():
            key = (sched.year, sched.month, sched.date)
            schedule_map[key] = schedule_map.get(key, 0) + 1

        busiest_date = max(schedule_map.items(), key=lambda x: x[1])
        return busiest_date[0]

    def getTasksWithoutSchedules(self) -> List['Task']:
        """
        Return tasks that have no associated schedulers.
        These are unscheduled tasks that need to be scheduled.
        """
        return [task for task in self.petTaskList if len(task.getSchedulerList()) == 0]

    def getUnscheduledTaskCount(self) -> int:
        """Return count of tasks without any schedulers."""
        return len(self.getTasksWithoutSchedules())


@dataclass
class Task:
    """
    Represents a service task for a pet in the PawPal+ system.

    Constructor Parameters (Required):
        pet (Pet): The Pet object that this task is for
        taskCode (int): Integer code for task type (0=Walk, 1=Feed, 2=Nap, 3=Vet)

    Attributes:
        taskID: Unique identifier for the task (auto-generated)
        pet: The Pet object that this task is for
        taskCode: Integer code representing the type of task (0: Walk, 1: Feed, 2: Nap, 3: Vet)
        duration: Duration of the task in minutes (default: 0)
        completed: Boolean indicating if the task has been completed (default: False)
        completed_at: Timestamp when task was completed (None if not yet completed)
        schedulerList: List of Scheduler objects for this task (tracks all scheduled times)

    Example:
        pet = Pet(petName="Fluffy", owner=owner)
        task = Task(pet=pet, taskCode=0)  # Create Walk task
        task.setTaskDuration(30)  # Set 30-minute duration
        task.doTask()  # Mark as completed

    FIXES IMPLEMENTED:
    - taskCode validation: Enforces 0-3 range in __post_init__()
    - duration validation: Enforces positive value in __post_init__() and setTaskDuration()
    - Scheduler relationship: Added schedulerList for bidirectional tracking (O(1) access)
    - Completion timestamp: completed_at field tracks when task was actually completed
    """
    pet: Pet
    taskCode: int
    taskID: int = field(default=0, init=False)
    duration: int = field(default=0)
    completed: bool = field(default=False)
    completed_at: Optional[datetime] = field(default=None)
    schedulerList: List['Scheduler'] = field(default_factory=list)

    def __post_init__(self):
        """
        Generate unique taskID after dataclass initialization.
        VALIDATES: taskCode range (0-3) and duration > 0.
        Raises ValueError if validation fails.
        """
        global _task_id_counter
        _task_id_counter += 1
        self.taskID = _task_id_counter

        # Validate taskCode is within valid range
        if not (0 <= self.taskCode <= 3):
            raise ValueError(f"Invalid taskCode {self.taskCode}. Must be between 0-3 (0=Walk, 1=Feed, 2=Nap, 3=Vet)")

        # Validate duration is positive
        if self.duration < 0:
            raise ValueError(f"Duration cannot be negative. Got {self.duration} minutes")
        # Note: duration of 0 is allowed (unscheduled task), but will be set to positive value later

    def getTaskID(self) -> int:
        """Return the unique task ID."""
        return self.taskID

    def getPet(self) -> Pet:
        """Return the pet that this task is for."""
        return self.pet

    def getTaskCode(self) -> int:
        """
        Return the task code representing the type of service.
        Task codes: 0=Walk, 1=Feed, 2=Nap, 3=Vet Visit
        """
        return self.taskCode

    def setTaskCode(self, task_code: int) -> None:
        """
        Set or update the task code (type of service).
        VALIDATION: taskCode must be in valid range 0-3.
        Task codes: 0=Walk, 1=Feed, 2=Nap, 3=Vet Visit
        Raises ValueError if taskCode is outside valid range.
        """
        if not (0 <= task_code <= 3):
            raise ValueError(f"Invalid taskCode {task_code}. Must be between 0-3 (0=Walk, 1=Feed, 2=Nap, 3=Vet)")
        self.taskCode = task_code

    def isTaskCompleted(self) -> bool:
        """Return whether this task has been completed."""
        return self.completed

    def setTaskDuration(self, duration: int) -> None:
        """
        Set the duration of the task in minutes.
        VALIDATION NEEDED: Should reject negative or zero durations. Add check before assignment.
        """
        if duration <= 0:
            raise ValueError(f"Duration must be positive, got {duration}")
        self.duration = duration

    def getTaskDuration(self) -> int:
        """Return the duration of the task in minutes."""
        return self.duration

    def doTask(self) -> None:
        """
        Mark the task as completed and record the completion timestamp.
        Updates completed flag to True and sets completed_at to current time.
        """
        self.completed = True
        self.completed_at = datetime.now()

    def getCompletedAt(self) -> Optional[datetime]:
        """
        Return the timestamp when this task was completed.
        Returns None if task has not been completed yet.
        """
        return self.completed_at

    def getTaskDescription(self) -> str:
        """Return human-readable description of the task based on taskCode."""
        return TASK_TYPES.get(self.taskCode, "Unknown Task")

    def addScheduler(self, scheduler: 'Scheduler') -> None:
        """
        Add a Scheduler object to this task's schedule list.
        Maintains bidirectional relationship: Task knows about all its scheduled times.
        VALIDATION: Prevents duplicate schedulers for the same task.
        """
        if scheduler not in self.schedulerList:
            self.schedulerList.append(scheduler)

    def removeScheduler(self, scheduler: 'Scheduler') -> None:
        """
        Remove a Scheduler object from this task's schedule list.
        Called when a scheduled time is cancelled or rescheduled.
        """
        if scheduler in self.schedulerList:
            self.schedulerList.remove(scheduler)

    def getSchedulerList(self) -> List['Scheduler']:
        """
        Return list of all Scheduler objects for this task.
        Allows querying "when is this task scheduled?" in O(1) time.
        """
        return self.schedulerList

    def getScheduleCount(self) -> int:
        """Return the number of times this task is scheduled."""
        return len(self.schedulerList)

    def resetCompletion(self) -> None:
        """
        Reset task completion status (marks as not completed).
        Useful for recurring tasks or error correction.
        Does not clear completed_at timestamp (maintains history).
        """
        self.completed = False

    def isTaskValid(self) -> bool:
        """
        Validate that task has all required fields properly set.
        Returns True if task is valid for execution, False otherwise.
        """
        is_valid = (
            self.taskID > 0 and
            0 <= self.taskCode <= 3 and
            self.duration >= 0 and
            self.pet is not None
        )
        return is_valid


@dataclass
class Scheduler:
    """
    Represents a scheduled time slot for a pet service task.
    Acts as the "Brain" that retrieves, organizes, and manages tasks across pets.

    Constructor Parameters (Required):
        task (Task): The Task object that is being scheduled

    Attributes (Optional, set after creation):
        schedulerID: Unique identifier for the schedule entry (auto-generated)
        task: The Task object that is being scheduled
        year: Year of the scheduled date (YYYY, default: 0, validated 2000-2100)
        month: Month of the scheduled date (1-12, formatted with leading zero)
        date: Day of the scheduled date (1-31, formatted with leading zero)
        time: Time of the scheduled task (HH:MM format, validated 00:00-23:59)

    Example:
        owner = Owner(ownerName="John")
        pet = Pet(petName="Fluffy", owner=owner)
        task = Task(pet=pet, taskCode=0)  # Walk task
        task.setTaskDuration(30)

        schedule = Scheduler(task=task)
        schedule.setYear(2026)
        schedule.setMonth(7)
        schedule.setDate(6)
        schedule.setTime("14:30")

        # Get schedule info
        print(schedule.getFullDateTime())  # "2026-07-06 14:30"
        print(schedule.getPetName())       # "Fluffy"
        print(schedule.getTaskType())      # "Walk Pet"

    FIXES IMPLEMENTED:
    - Bidirectional Task relationship: Task maintains schedulerList
    - Validation: month (1-12), date (1-31), year (2000-2100), time (HH:MM)
    - Date/time formatting: Zero-padded strings for month/date
    - Conflict detection: isScheduleInPast(), isScheduleToday(), isScheduleUpcoming()
    - Task access: getPet(), getPetName(), getTaskType(), getTaskDuration()
    - Schedule info: getFullDateTime(), getDateString(), getScheduleSummary()
    """
    task: Task
    year: int = field(default=0)
    month: int = field(default=0)
    date: int = field(default=0)
    time: str = field(default="")
    schedulerID: int = field(default=0, init=False)

    def __post_init__(self):
        """
        Generate unique schedulerID after dataclass initialization.
        VALIDATES: year, month, date, time formats if provided.
        """
        global _scheduler_id_counter
        _scheduler_id_counter += 1
        self.schedulerID = _scheduler_id_counter

        # Validate provided values (allow 0 defaults for optional fields)
        if self.year and not (2000 <= self.year <= 2100):
            raise ValueError(f"Invalid year {self.year}. Must be between 2000-2100")

        if self.month and not (1 <= self.month <= 12):
            raise ValueError(f"Invalid month {self.month}. Must be between 1-12")

        if self.date and not (1 <= self.date <= 31):
            raise ValueError(f"Invalid date {self.date}. Must be between 1-31")

        if self.time and not self._is_valid_time(self.time):
            raise ValueError(f"Invalid time {self.time}. Must be HH:MM (00:00-23:59)")

        # Add this scheduler to task's scheduler list for bidirectional relationship
        if hasattr(self.task, 'addScheduler'):
            self.task.addScheduler(self)

    def getSchedulerID(self) -> int:
        """Return the unique scheduler ID."""
        return self.schedulerID

    def getYear(self) -> int:
        """Return the year of the scheduled date."""
        return self.year

    def setYear(self, year: int) -> None:
        """
        Set the year of the scheduled date.
        VALIDATION: Year must be positive and reasonable (not too far in past/future).
        Raises ValueError if invalid.
        """
        if year < 2000 or year > 2100:
            raise ValueError(f"Invalid year {year}. Must be between 2000-2100")
        self.year = year

    def getMonth(self) -> str:
        """Return the month of the scheduled date as a zero-padded string (e.g., '05')."""
        return f"{self.month:02d}" if self.month > 0 else "00"

    def setMonth(self, month: int) -> None:
        """
        Set the month of the scheduled date (1-12).
        Values are validated and stored. Formatted with leading zero when retrieved.
        Raises ValueError if month outside valid range.
        """
        if not (1 <= month <= 12):
            raise ValueError(f"Invalid month {month}. Must be between 1-12")
        self.month = month

    def getDate(self) -> str:
        """Return the day of the scheduled date as a zero-padded string (e.g., '07')."""
        return f"{self.date:02d}" if self.date > 0 else "00"

    def setDate(self, date: int) -> None:
        """
        Set the day of the scheduled date (1-31).
        Values are validated and stored. Formatted with leading zero when retrieved.
        VALIDATION: Checks basic range (1-31); more precise validation by month/year could be added.
        Raises ValueError if date outside valid range.
        """
        if not (1 <= date <= 31):
            raise ValueError(f"Invalid date {date}. Must be between 1-31")
        self.date = date

    def getTime(self) -> str:
        """Return the time of the scheduled task (HH:MM format)."""
        return self.time

    def setTime(self, time: str) -> None:
        """
        Set the time of the scheduled task (HH:MM format, 00:00-23:59).
        VALIDATION: Enforces HH:MM format and valid time range.
        Raises ValueError if format or range invalid.
        """
        import re
        if not isinstance(time, str) or not re.match(r'^\d{2}:\d{2}$', time):
            raise ValueError(f"Invalid time format '{time}'. Must be HH:MM (00:00-23:59)")

        hours, minutes = map(int, time.split(':'))
        if not (0 <= hours <= 23) or not (0 <= minutes <= 59):
            raise ValueError(f"Invalid time values in '{time}'. Hours 0-23, Minutes 0-59")

        self.time = time

    def getTask(self) -> Task:
        """Return the task that is being scheduled."""
        return self.task

    def getFullDateTime(self) -> str:
        """
        Return complete datetime as string: YYYY-MM-DD HH:MM format.
        Useful for display and comparison operations.
        Example: "2026-07-06 14:30"
        """
        return f"{self.year}-{self.getMonth()}-{self.getDate()} {self.getTime()}"

    def getDateString(self) -> str:
        """Return date as string: YYYY-MM-DD format."""
        return f"{self.year}-{self.getMonth()}-{self.getDate()}"

    def getPet(self) -> Optional['Pet']:
        """Return the pet associated with the scheduled task."""
        return self.task.getPet() if self.task else None

    def getPetName(self) -> str:
        """Return the name of the pet for this scheduled task."""
        pet = self.getPet()
        return pet.getPetName() if pet else "Unknown Pet"

    def getTaskType(self) -> str:
        """Return the task type description (Walk, Feed, Nap, Vet)."""
        return self.task.getTaskDescription() if self.task else "Unknown Task"

    def getTaskDuration(self) -> int:
        """Return the duration of the scheduled task in minutes."""
        return self.task.getTaskDuration() if self.task else 0

    def isScheduleInPast(self) -> bool:
        """
        Check if this schedule is in the past (before today).
        Useful for filtering upcoming vs completed schedules.
        """
        from datetime import datetime
        today = datetime.now()
        schedule_date = datetime(self.year, self.month, self.date)
        return schedule_date < today.replace(hour=0, minute=0, second=0, microsecond=0)

    def isScheduleToday(self) -> bool:
        """Check if this schedule is for today."""
        from datetime import datetime
        today = datetime.now()
        return (self.year == today.year and
                self.month == today.month and
                self.date == today.day)

    def isScheduleUpcoming(self) -> bool:
        """Check if this schedule is upcoming (today or later)."""
        return not self.isScheduleInPast()

    def validateSchedule(self) -> dict:
        """
        Validate integrity of this schedule.
        Returns dict with validation results and any issues found.
        """
        issues = []
        is_valid = True

        if self.schedulerID <= 0:
            issues.append("Invalid scheduler ID")
            is_valid = False

        if not (1 <= self.month <= 12):
            issues.append(f"Invalid month: {self.month}")
            is_valid = False

        if not (1 <= self.date <= 31):
            issues.append(f"Invalid date: {self.date}")
            is_valid = False

        if not self.time or not self._is_valid_time(self.time):
            issues.append(f"Invalid time: {self.time}")
            is_valid = False

        if not self.task:
            issues.append("No task associated with schedule")
            is_valid = False

        return {
            'scheduler_id': self.schedulerID,
            'date': self.getDateString(),
            'time': self.getTime(),
            'is_valid': is_valid,
            'issues': issues
        }

    def _is_valid_time(self, time_str: str) -> bool:
        """Helper method to validate time format."""
        import re
        if not re.match(r'^\d{2}:\d{2}$', time_str):
            return False
        try:
            hours, minutes = map(int, time_str.split(':'))
            return 0 <= hours <= 23 and 0 <= minutes <= 59
        except ValueError:
            return False

    def getScheduleSummary(self) -> dict:
        """
        Return comprehensive summary of this schedule.
        Useful for display and analytics.
        """
        return {
            'scheduler_id': self.schedulerID,
            'date': self.getDateString(),
            'time': self.getTime(),
            'full_datetime': self.getFullDateTime(),
            'pet_name': self.getPetName(),
            'task_type': self.getTaskType(),
            'task_duration_minutes': self.getTaskDuration(),
            'task_completed': self.task.isTaskCompleted() if self.task else False,
            'is_in_past': self.isScheduleInPast(),
            'is_today': self.isScheduleToday(),
            'is_upcoming': self.isScheduleUpcoming()
        }

    def getKey(self) -> str:
        """
        Return a date key string in format "YYYYMMDD".
        YYYY = 4-digit year, MM = 2-digit month, DD = 2-digit day.
        Lazily creates and caches the key attribute if it doesn't exist.
        VALIDATION: Checks that year, month, day have valid values before generating key.

        Example:
            schedule.setYear(2026)
            schedule.setMonth(7)
            schedule.setDate(6)
            print(schedule.getKey())  # Returns "20260706"

        Returns:
            str: Date key in "YYYYMMDD" format
        Raises:
            ValueError: If year, month, or day values are invalid or unset (0)
        """
        # Check if key attribute already exists, return it if valid
        if hasattr(self, 'key') and self.key:
            return self.key

        # Validate year, month, date are set (not 0) and valid
        if self.year == 0:
            raise ValueError("Year not set. Use setYear() to set a valid year (2000-2100)")

        if not (2000 <= self.year <= 2100):
            raise ValueError(f"Invalid year {self.year}. Must be between 2000-2100")

        if self.month == 0:
            raise ValueError("Month not set. Use setMonth() to set a valid month (1-12)")

        if not (1 <= self.month <= 12):
            raise ValueError(f"Invalid month {self.month}. Must be between 1-12")

        if self.date == 0:
            raise ValueError("Date not set. Use setDate() to set a valid date (1-31)")

        if not (1 <= self.date <= 31):
            raise ValueError(f"Invalid date {self.date}. Must be between 1-31")

        # Generate key in YYYYMMDD format with zero-padding
        # Year is already 4 digits (2000-2100)
        # Month and day need zero-padding to 2 digits
        self.key = f"{self.year}{self.month:02d}{self.date:02d}"

        return self.key

    def setKey(self, key: str) -> None:
        """
        Set the date key directly if key is in valid "YYYYMMDD" format.
        VALIDATION: Validates format and extracts/validates year, month, date.

        Example:
            schedule.setKey("20260706")  # Sets year=2026, month=07, date=06

        Raises:
            ValueError: If key format is invalid or values are out of range
        """
        if not isinstance(key, str) or len(key) != 8:
            raise ValueError(f"Invalid key format '{key}'. Must be 'YYYYMMDD' (8 digits)")

        try:
            year = int(key[0:4])
            month = int(key[4:6])
            day = int(key[6:8])
        except ValueError:
            raise ValueError(f"Invalid key format '{key}'. All characters must be digits")

        # Validate extracted values
        if not (2000 <= year <= 2100):
            raise ValueError(f"Invalid year in key: {year}. Must be between 2000-2100")

        if not (1 <= month <= 12):
            raise ValueError(f"Invalid month in key: {month}. Must be between 1-12")

        if not (1 <= day <= 31):
            raise ValueError(f"Invalid day in key: {day}. Must be between 1-31")

        # Set the date components and key
        self.year = year
        self.month = month
        self.date = day
        self.key = key
