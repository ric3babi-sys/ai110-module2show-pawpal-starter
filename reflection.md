# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core functions to provide are
1. Walking pet involes taking pet on a walk in the park or dog friendly trail.
2. Feeding pet at lunch, dinner, and snacks, Give it water to keep hydrated.
3. Nap time for pet gives it time to relax and rest after walking.

- Briefly describe your initial UML design.
  Initial UML design will show the relationship between various classes. Classes will define attributes and methods relevant to a class.

- What classes did you include, and what responsibilities did you assign to each?
  Classes for this project are Owner, Pet, Task, and Scheduler.
    Global variables are predefined constant values and list of objects.
      ownerList
        Methods: getOwnerByID and getOwnerByName.
      petList
        Methods: getPetByID and getPetByName.
      taskList all scheduled tasks.
        Methods: getTaskByID and getTaskByPetID.
      services is a dictionary where key is integer taskCode and value is taskDescription.
        Sample {0: "Walk Pet", 1: "Feed Pet", 2: "Nap Time", 3: "Veterinarian Visit"}
      scheduleDictionary where key is date (YYYYMMDD) and value is list of scheduler object.
        Methods: addTask, viewTodaysTask, and cancelTask.
    Owner class is a pet owner.
      Constructor: required string ownerName.
      Attributes: unique integer ownerID, ownerName, and petList.
      Methods: getOwnerID, getOwnerName, setPet, getPetByName and getPetList.
    Pet class is a pet with it's owner and scheduled tasks.
      Constructor: required string petName.
      Attributes: owner object, unique integer petID, petName, and petTaskList (task for this pet).
      Methods: getOwner, ggetPetID, getPetName, addPetTask, removePetTask, and getPetTaskList.
    Task class defines the different services a pet can receive.
      Constructor: required pet object and required taskCode.
      Attributes: unique integer taskID, pet object, taskCode, duration, and completed.
      Methods: getTaskID, getPet, getTaskCode, isTaskCompleted, setTaskDuration, getTaskDuration, and doTask.
    Scheduler class reserves a date and time for a pet service.
      Constructor: task object.
      Attributes: unique integer schedulerID, task object, year, month, date, and time.
      Methods: getSchedulerID, getYear, setYear, getMonth, setMonth, getDate, setDate, getTime, setTime, and getTask

**b. Design changes**

- Did your design change during implementation?
  Claude Code identified 5 Missing Relationships and 6 Critical Bottlenecks.
- If yes, describe at least one change and why you made it.
  As documented in DesignChanges.txt; BOTTLENECK #6: NO TASK STATUS FILTERING describes missing functionality. Originally, only Pet.getPetTaskList() was implemented. There was no way to filter a pet's task status. This is a bottleneck because you can't identify which tasks were completed or not. You had to programatically loop thru all tasks. By defining filter member methods we can re-use this logic.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  My constraint focus was on prioritizing tasks defined in global dictionary DEFAULT_TASK_PRIORITY.
- How did you decide which constraints mattered most?
  I set the scale according to my interpretation of a pet's activities. This is biased because the scale is my personal preference.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  The lookup for scheduler is indexed by date in global variable schedulerDictionary.
- Why is that tradeoff reasonable for this scenario?
  This makes lookup for a date ver fast. I choose this strategy because I think looking up scheduled tasks by date provides a more robust presentation allowing the view for daily activities. The tradeoff is all other queries are slow because to get at a desired filter, you need to traverse the object graph, e.g. scheduler -> task -> status

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
