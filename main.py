"""
Main module for PawPal+ pet care application.
Imports all classes and utility functions from pawpal_system.
"""

# Import core classes
from pawpal_system import Owner, Pet, Task, Scheduler

# Import global data structures
from pawpal_system import ownerList, petList, schedulerDictionary, TASK_TYPES

# Import Owner utility functions
from pawpal_system import (
    newOwner,
    getOwnerByID,
    getOwnerByName,
    getAllOwners,
    removeOwner,
    getOwnerCount,
    getSystemStatistics,
    clearAllData
)

# Import Pet utility functions
from pawpal_system import (
    newPet,
    getPetByID,
    getPetByName,
    getPetsByOwner,
    getAllPets,
    removePet,
    getPetCount,
    getPetsByTaskType,
    getPetsWithPendingTasks,
    getPetsWithNoTasks,
    getPetStatistics
)

# Import Scheduler utility functions
from pawpal_system import (
    newScheduler,
    getSchedulerByKey,
    getSchedulersByDate,
    getSchedulersByPet,
    getSchedulersByTask,
    getAllSchedulers,
    removeScheduler,
    getSchedulerCount,
    getSchedulesByDateRange,
    getSchedulerStatistics,
    sortSchedulesByTime,
    filterSchedules,
    checkScheduleConflict,
)

__all__ = [
    # Classes
    'Owner',
    'Pet',
    'Task',
    'Scheduler',
    # Global data structures
    'ownerList',
    'petList',
    'schedulerDictionary',
    'TASK_TYPES',
    # Owner functions
    'newOwner',
    'getOwnerByID',
    'getOwnerByName',
    'getAllOwners',
    'removeOwner',
    'getOwnerCount',
    'getSystemStatistics',
    'clearAllData',
    # Pet functions
    'newPet',
    'getPetByID',
    'getPetByName',
    'getPetsByOwner',
    'getAllPets',
    'removePet',
    'getPetCount',
    'getPetsByTaskType',
    'getPetsWithPendingTasks',
    'getPetsWithNoTasks',
    'getPetStatistics',
    # Scheduler functions
    'newScheduler',
    'getSchedulerByKey',
    'getSchedulersByDate',
    'getSchedulersByPet',
    'getSchedulersByTask',
    'getAllSchedulers',
    'removeScheduler',
    'getSchedulerCount',
    'getSchedulesByDateRange',
    'getSchedulerStatistics',
    'sortSchedulesByTime',
    'filterSchedules',
    'checkScheduleConflict',
]


def main():
    """
    Example usage of PawPal+ system.
    Creates an Owner and two Pets with Tasks and Schedulers.
    Demonstrates task creation, scheduling, and querying.
    """
    from datetime import datetime

    print("=" * 70)
    print("PawPal+ Pet Care System - Example Usage")
    print("=" * 70)

    # Create an Owner
    print("\n[1] Creating Owner...")
    owner = newOwner("John Smith")
    print(f"    ✓ Owner created: {owner.getOwnerName()} (ID: {owner.getOwnerID()})")

    # Create first Pet
    print("\n[2] Creating first Pet...")
    pet1 = newPet("Fluffy", owner)
    print(f"    ✓ Pet created: {pet1.getPetName()} (ID: {pet1.getPetID()})")
    print(f"      Owner: {pet1.getOwner().getOwnerName()}")

    # Create second Pet
    print("\n[3] Creating second Pet...")
    pet2 = newPet("Buddy", owner)
    print(f"    ✓ Pet created: {pet2.getPetName()} (ID: {pet2.getPetID()})")
    print(f"      Owner: {pet2.getOwner().getOwnerName()}")

    # Display Owner's pets
    print(f"\n[4] {owner.getOwnerName()}'s Pets Summary:")
    pets = owner.getPetList()
    print(f"    Total pets owned: {len(pets)}")
    for pet in pets:
        print(f"      • {pet.getPetName()} (ID: {pet.getPetID()})")

    # Create Tasks for Pet 1 (Fluffy)
    print("\n[5] Creating Tasks for Fluffy...")

    # Task 1: Walk - Today at 09:00
    task1_fluffy = Task(pet=pet1, taskCode=0)  # Walk
    task1_fluffy.setTaskDuration(30)
    scheduler1_fluffy = newScheduler(task1_fluffy, datetime.now().year, datetime.now().month, datetime.now().day, "09:00")
    print(f"    ✓ Task 1: Walk (30 min) - Today at 09:00")

    # Task 2: Feed - Today at 12:30
    task2_fluffy = Task(pet=pet1, taskCode=1)  # Feed
    task2_fluffy.setTaskDuration(15)
    scheduler2_fluffy = newScheduler(task2_fluffy, datetime.now().year, datetime.now().month, datetime.now().day, "12:30")
    print(f"    ✓ Task 2: Feed (15 min) - Today at 12:30")

    # Task 3: Nap Time - Tomorrow at 14:00
    task3_fluffy = Task(pet=pet1, taskCode=2)  # Nap
    task3_fluffy.setTaskDuration(60)
    scheduler3_fluffy = newScheduler(task3_fluffy, datetime.now().year, datetime.now().month, datetime.now().day + 1, "14:00")
    print(f"    ✓ Task 3: Nap Time (60 min) - Tomorrow at 14:00")

    # Create Tasks for Pet 2 (Buddy)
    print("\n[6] Creating Tasks for Buddy...")

    # Task 1: Feed - Today at 08:00
    task1_buddy = Task(pet=pet2, taskCode=1)  # Feed
    task1_buddy.setTaskDuration(15)
    scheduler1_buddy = newScheduler(task1_buddy, datetime.now().year, datetime.now().month, datetime.now().day, "08:00")
    print(f"    ✓ Task 1: Feed (15 min) - Today at 08:00")

    # Task 2: Walk - Today at 16:00
    task2_buddy = Task(pet=pet2, taskCode=0)  # Walk
    task2_buddy.setTaskDuration(45)
    scheduler2_buddy = newScheduler(task2_buddy, datetime.now().year, datetime.now().month, datetime.now().day, "16:00")
    print(f"    ✓ Task 2: Walk (45 min) - Today at 16:00")

    # Task 3: Vet Visit - Day after tomorrow at 10:00
    task3_buddy = Task(pet=pet2, taskCode=3)  # Vet
    task3_buddy.setTaskDuration(30)
    scheduler3_buddy = newScheduler(task3_buddy, datetime.now().year, datetime.now().month, datetime.now().day + 2, "10:00")
    print(f"    ✓ Task 3: Vet Visit (30 min) - Day after tomorrow at 10:00")

    # Display System Statistics
    print("\n[7] System Statistics:")
    stats = getSystemStatistics()
    print(f"    Total Owners: {stats['total_owners']}")
    print(f"    Total Pets: {stats['total_pets']}")
    print(f"    Total Tasks: {stats['total_tasks']}")
    print(f"    Average pets per owner: {stats['average_pets_per_owner']}")

    # Display Pet Statistics
    print("\n[8] Pet Statistics:")
    pet_stats = getPetStatistics()
    print(f"    Total Pets in system: {pet_stats['total_pets']}")
    print(f"    Total Tasks: {pet_stats['total_tasks']}")
    print(f"    Pets with pending tasks: {pet_stats['pets_with_pending_tasks']}")
    print(f"    Pets with no tasks: {pet_stats['pets_with_no_tasks']}")

    # Print Today's Schedule
    print("\n" + "=" * 70)
    print("TODAY'S SCHEDULE")
    print("=" * 70)

    today_year = datetime.now().year
    today_month = datetime.now().month
    today_day = datetime.now().day

    today_schedule = getSchedulersByDate(today_year, today_month, today_day)

    if today_schedule:
        print(f"\nDate: {today_year:04d}-{today_month:02d}-{today_day:02d}")
        print(f"Total activities scheduled: {len(today_schedule)}\n")

        # Sort by time
        sorted_schedule = sorted(today_schedule, key=lambda s: s.getTime())

        for idx, scheduler in enumerate(sorted_schedule, 1):
            pet_name = scheduler.getPetName()
            task_type = scheduler.getTaskType()
            duration = scheduler.getTaskDuration()
            time = scheduler.getTime()

            print(f"  {idx}. [{time}] {pet_name} - {task_type} ({duration} min)")
    else:
        print("\nNo activities scheduled for today.")

    # =====================================================================
    # Sort Scheduler By Time
    # ---------------------------------------------------------------------
    # Create several tasks for a NEW pet, all on the SAME day but deliberately
    # added OUT OF chronological order, then sort them with the global
    # sortSchedulesByTime() helper to prove it orders by time regardless of
    # the order the schedules were created in.
    # =====================================================================
    print("\n" + "=" * 70)
    print("SORT SCHEDULER BY TIME")
    print("=" * 70)

    # Dedicated pet so this demo is independent of the schedules created above.
    demo_pet = newPet("Ziggy", owner)

    # A single target day for every task in this demo.
    demo_year = datetime.now().year
    demo_month = datetime.now().month
    demo_day = datetime.now().day

    # (taskCode, duration, time) pairs added out of time order on purpose:
    # 15:45 first, then 07:15, 20:00, 06:30, 11:00.
    unsorted_entries = [
        (0, 30, "15:45"),  # Walk
        (1, 15, "07:15"),  # Feed
        (2, 60, "20:00"),  # Nap
        (3, 45, "06:30"),  # Vet Visit
        (1, 15, "11:00"),  # Feed
    ]

    demo_schedulers = []
    for task_code, duration, time in unsorted_entries:
        task = Task(pet=demo_pet, taskCode=task_code)
        task.setTaskDuration(duration)
        scheduler = newScheduler(task, demo_year, demo_month, demo_day, time)
        demo_schedulers.append(scheduler)

    print(f"\nCreated {len(demo_schedulers)} tasks for {demo_pet.getPetName()} "
          f"on {demo_year:04d}-{demo_month:02d}-{demo_day:02d} (out of order):")
    for scheduler in demo_schedulers:
        print(f"  • [{scheduler.getTime()}] {scheduler.getTaskType()} "
              f"({scheduler.getTaskDuration()} min)")

    # Sort the schedules chronologically using the global helper.
    sorted_demo = sortSchedulesByTime(demo_schedulers)

    print("\nAfter sortSchedulesByTime() (chronological):")
    for idx, scheduler in enumerate(sorted_demo, 1):
        print(f"  {idx}. [{scheduler.getTime()}] {scheduler.getTaskType()} "
              f"({scheduler.getTaskDuration()} min)")

    # =====================================================================
    # Sorting and Filtering
    # ---------------------------------------------------------------------
    # Example A: filter the system's schedules down to a single pet (by name)
    #            and display all of that pet's scheduled tasks.
    # Example B: sort those filtered schedules chronologically (across days)
    #            using the global sortSchedulesByTime() helper.
    # =====================================================================
    print("\n" + "=" * 70)
    print("SORTING AND FILTERING")
    print("=" * 70)

    # --- Example A: filter by pet name ---
    target_name = "Fluffy"
    target_pet = getPetByName(target_name)
    # filterSchedules(pet=...) narrows every scheduler in the system to one pet.
    pet_schedules = filterSchedules(getAllSchedulers(), pet=target_pet) if target_pet else []

    print(f"\n[A] All scheduled tasks for '{target_name}':")
    if not target_pet:
        print(f"    No pet named '{target_name}' found.")
    elif not pet_schedules:
        print(f"    {target_name} has no scheduled tasks.")
    else:
        print(f"    Found {len(pet_schedules)} scheduled task(s).")
        for scheduler in pet_schedules:
            print(f"      • {scheduler.getDateString()} [{scheduler.getTime()}] "
                  f"{scheduler.getTaskType()} ({scheduler.getTaskDuration()} min)")

    # --- Example B: sort the filtered schedules by time (global helper) ---
    print(f"\n[B] '{target_name}' schedule sorted by time (sortSchedulesByTime):")
    if pet_schedules:
        sorted_pet_schedules = sortSchedulesByTime(pet_schedules)
        for idx, scheduler in enumerate(sorted_pet_schedules, 1):
            print(f"    {idx}. {scheduler.getDateString()} [{scheduler.getTime()}] "
                  f"{scheduler.getTaskType()} ({scheduler.getTaskDuration()} min)")
    else:
        print("    Nothing to sort.")

    # =====================================================================
    # Conflict Detection (lightweight, non-fatal)
    # ---------------------------------------------------------------------
    # Schedule two tasks at the SAME date and time. newScheduler() runs a
    # lightweight conflict check and PRINTS a warning (it does not crash), and
    # checkScheduleConflict() can be called directly to get the warning message.
    # =====================================================================
    print("\n" + "=" * 70)
    print("CONFLICT DETECTION")
    print("=" * 70)

    conflict_year = datetime.now().year
    conflict_month = datetime.now().month
    conflict_day = datetime.now().day
    conflict_time = "18:30"

    print(f"\nScheduling two tasks at {conflict_year:04d}-{conflict_month:02d}-"
          f"{conflict_day:02d} {conflict_time} ...")

    # Task 1: Fluffy - Feed at 18:30 (first booking, no conflict yet)
    clash_task_1 = Task(pet=pet1, taskCode=1)  # Feed
    clash_task_1.setTaskDuration(15)
    print(f"  → Booking {pet1.getPetName()}'s Feed:")
    newScheduler(clash_task_1, conflict_year, conflict_month, conflict_day, conflict_time)

    # Task 2: Buddy - Walk at the SAME time (different pet, same slot -> conflict)
    clash_task_2 = Task(pet=pet2, taskCode=0)  # Walk
    clash_task_2.setTaskDuration(30)
    print(f"  → Booking {pet2.getPetName()}'s Walk (same slot):")
    newScheduler(clash_task_2, conflict_year, conflict_month, conflict_day, conflict_time)

    # Direct use of the detection strategy: returns the warning message (or None).
    print("\nDirect checkScheduleConflict() call for that slot:")
    message = checkScheduleConflict(conflict_year, conflict_month, conflict_day, conflict_time)
    if message:
        print(f"  {message}")
    else:
        print("  No conflict detected.")

    # Verify a free slot returns no warning.
    free_message = checkScheduleConflict(conflict_year, conflict_month, conflict_day, "23:15")
    print(f"  Free slot (23:15) -> {'conflict' if free_message else 'no conflict (as expected)'}")

    # Display Scheduler Statistics
    print("\n[9] Scheduler Statistics:")
    scheduler_stats = getSchedulerStatistics()
    print(f"    Total Schedulers: {scheduler_stats['total_schedulers']}")
    print(f"    Total Dates Scheduled: {scheduler_stats['total_dates']}")
    print(f"    Today's Activities: {len(today_schedule)}")
    print(f"    Pending Activities: {scheduler_stats['pending']}")
    print(f"    Total Duration: {scheduler_stats['total_duration_minutes']} minutes")

    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)

    return owner, pet1, pet2


if __name__ == "__main__":
    main()
