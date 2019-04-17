
"""
***************************************************************************************
*
*                   Sporadic Scheduling
*
*
*  Name : Idaly Ali
*
*  GitHub : ottermegazord
*
*  Description : Sporadic Scheduling
*
*  License: MIT
*
*
***************************************************************************************

"""


"""Import Packages"""
import random
from lcm import LCM
from sporadic_class import Task_Inputs
from sporadic_class import Jump2PeriodicTaskExecution
from sporadic_class import TaskType

'''Create methods for sorting comparators'''

def priority_cmp(one, other):
    """
    Create comparator for priority sorting
    :param one: 1st item
    :param other: 2nd item
    :return: -1, 0 or 1
    """
    if one.priority < other.priority:
        return -1
    elif one.priority > other.priority:
        return 1
    return 0


def aperiodic_cmp(one, other):
    """
       Create comparator for aperiodic priority sorting
       :param one: 1st item
       :param other: 2nd item
       :return: -1, 0 or 1
       """
    if one.a_start < other.a_start:
        return -1
    elif one.a_start > other.a_start:
        return 1
    return 0

#Rate monotonic comparison
def tasktype_cmp(self, other):
    """
    Task type comparator for sorting
    :param self: 1st item
    :param other: 2nd item
    :return: -1, 0 or 1
    """
    if self.period < other.period:
        return -1
    if self.period > other.period:
        return 1
    return 0


def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'

    class K:
        def __init__(self, obj, *args):
            self.obj = obj

        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0

    return K

"""Start Program"""
if __name__ == '__main__':

    """Create colors for each type of task"""
    html_color = {'Task1': 'green',
                  'Task2': 'blue',
                  'Task3': 'red',
                  'Task4': 'turqoise',
                  'Task5': 'firebrick',
                  'Sporadic': 'gold',
                  'Empty': 'black',
                  'Finish': 'grey'}

    """Read task list from text file"""

    FILE_PATH = 'task_inputs.txt'
    OUT_PATH = 'viz.html'
    task_data = open(FILE_PATH)

    # Read individual lines
    task_instances = task_data.readlines()

    """Create arrays for storing status"""

    task_types = []
    tasks = []
    hyperperiod = []
    aperiodic_tasks = []
    last_sporadic = None
    next_sporadic = None
    sporadic_template = None

    """Task type allocations"""
    for task_instance in task_instances:

        # Split task_instances
        task_instance = task_instance.split(' ')
        for i in range (0,4):
            task_instance[i] = int(task_instance[i])

        # Check input file for formatting
        if len(task_instance) == 5:
            name = task_instance[4]
        elif len(task_instance) == 4:
            name = 'Task'
        else:
            raise Exception('Input file (task_inputs.txt) not in correct format')

        # Create task list
        if int(task_instance[0]) > 0:

            new_type = TaskType(period=task_instance[0], release=task_instance[1], execution=task_instance[2], deadline=task_instance[3], name=name)
            task_types.append(new_type)

            if new_type.name[:8] == "Sporadic":
                sporadic_template = new_type
        else:
            aperiodic_tasks.append(Task_Inputs(a_start=task_instance[1], a_end=int(task_instance[1]) + int(task_instance[2]), a_deadline=task_instance[3], name=name))


    """Calculate Hyperperiod from task"""

    for task_type in task_types:
        hyperperiod.append(task_type.period)

    hyperperiod = LCM(hyperperiod)


    # Sort task types
    task_types = sorted(task_types, key=cmp_to_key(tasktype_cmp))
    aperiodic_tasks = sorted(aperiodic_tasks, key=cmp_to_key(aperiodic_cmp))

    """Create Task Instances"""
    is_first_sporadic_set = False
    for i in range(0, hyperperiod):
        for task_type in task_types:
            if  (i - task_type.release) % task_type.period == 0 and i >= task_type.release:
                if task_type.name[:8] == "Sporadic":
                    if is_first_sporadic_set == True:
                        continue
                    else:
                        is_first_sporadic_set = True
                start = i
                end = start + task_type.execution
                priority = task_type.period
                new_task = Task_Inputs(start=start, end=end, priority=priority, name=task_type.name)
                tasks.append(new_task)
                if new_task.name == "Sporadic":
                    last_sporadic = new_task

    """HTML Visualization"""

    html = "<!DOCTYPE html><html><head><title>Sporadic Server</title></head><body>"

    # Check for utilization error
    utilization = 0
    for task_type in task_types:
        utilization += float(task_type.execution) / float(task_type.period)
    if utilization > 1:
        print ('Fault: Error Utilization')
        html += '<br /><br />Fault: Error Utilization<br /><br />'

    """Generate Clock steps"""
    clock_step = 1
    first_lower_priority_occurence = 0
    is_previous_idle = False
    for i in range(0, hyperperiod, clock_step):

        # Retrieve tasks capable of CPU-mode
        # Sort according to priority
        possible_tasks = []
        for t in tasks:
            if t.start <= i:
                possible_tasks.append(t)
        possible_tasks = sorted(possible_tasks, key=cmp_to_key(priority_cmp))

        # Replenishment

        for possible_task in possible_tasks:
            if possible_task.start == i and possible_task.name == "Sporadic":
                for deprecate_server in possible_tasks:
                    if deprecate_server.start < i and deprecate_server.name == "Sporadic":
                        tasks.remove(deprecate_server)
                        possible_tasks.remove(deprecate_server)
        possible_tasks = sorted(possible_tasks, key=cmp_to_key(priority_cmp))

        # Search and choose task with top priority
        try:
            on_cpu = possible_tasks[0]
            on_spa = None

            # Search aperiodic task given if it is a server
            if on_cpu.name == "Sporadic":

                # Search for request
                for a in aperiodic_tasks:
                    if a.a_start <= i:
                        on_spa = a
                        break

                # Consume server if no request
                if on_spa is not None:

                    # Select next replenishment
                    next_replenishment = last_sporadic.start + sporadic_template.period
                    if first_lower_priority_occurence > last_sporadic.start:
                        next_replenishment = first_lower_priority_occurence + sporadic_template.period
                    start = next_replenishment
                    end = start + sporadic_template.execution
                    priority = sporadic_template.period
                    next_sporadic = Task_Inputs(start=start, end=end, priority=priority, name=sporadic_template.name)
                    tasks.append(next_sporadic)

                    # Consume server if consume
                    if on_cpu.budget_consume(clock_step):
                        is_previous_idle = False
                        print (on_spa.get_name() , " uses CPU " )
                        html += '<div style="float: left; text-align: center; width: 110px; height: 20px; background-color:' + html_color[on_cpu.name] + ';">' + on_spa.get_name() + '<br />' + str(i) + '-' + str(i+1) + '</div>'
                        if on_cpu.use_cpu(clock_step):
                            tasks.remove(on_cpu)
                        if on_spa.aperiodic_cpu(clock_step):
                            aperiodic_tasks.remove(on_spa)
                            html += '<div style="float: left; text-align: center; width: 10px; height: 20px; background-color:' + html_color['Finish'] + ';">' + '<br />' + str(i+1) +'</div>'                            #
                            print ("Completed")

                    # Unsucessful consumption
                    else:
                        tasks.remove(on_cpu)
                        on_cpu = possible_tasks[1]
                        raise Jump2PeriodicTaskExecution("")

                # No tasks for server
                else:
                    on_cpu = possible_tasks[1]
                    raise Jump2PeriodicTaskExecution("")

            # If task is Periodic
            else:
                raise Jump2PeriodicTaskExecution("")

        except IndexError:
            is_previous_idle = True
            print ('Processor not used')
            html += '<div style="float: left; text-align: center; width: 110px; height: 20px; background-color:' + html_color['Empty'] + ';">Empty' + '<br />' + str(i) + '-' + str(i+1) + '</div>'

        # CPU-mode
        except Jump2PeriodicTaskExecution:
            if is_previous_idle:
                start = i
                end = start + sporadic_template.execution
                priority = sporadic_template.period
                tasks.remove(next_sporadic)
                next_sporadic = Task_Inputs(start=start, end=end, priority=priority, name=sporadic_template.name)
                tasks.append(next_sporadic)
            is_previous_idle = False
            if last_sporadic.priority < on_cpu.priority:
                first_lower_priority_occurence = i
            print (on_cpu.get_name() , " uses CPU.")
            html += '<div style="float: left; text-align: center; width: 110px; height: 20px; background-color:' + html_color[on_cpu.name] + ';">' + on_cpu.get_name() + '<br />' + str(i) + '-' + str(i+1) + '</div>'
            if on_cpu.use_cpu(clock_step):
                tasks.remove(on_cpu)
                html += '<div style="float: left; text-align: center; width: 10px; height: 20px; background-color:' + html_color['Finish'] + ';">' + '<br />' + str(i+1) + '</div>'
                print ("Completed.")
        print ("\n")

    #Show list of remaining periodic tasks
    html += "<br /><br />"
    for possible_task in tasks:
        if possible_task.name == "Sporadic":
            continue
        print (possible_task.get_name() + " dropped. Overload at time: " + str(i))
        html += "<p>" + possible_task.get_name() + " dropped. Overload at time: " + str(i) + "</p>"

    # Show list of remaining aperiodic tasks
    html += "<br /><br />"
    for a in aperiodic_tasks:
        print (a.get_name() + " dropped. Overload at time: " + str(i))
        html += "<p>" + a.get_name() + " dropped. Overload at time: " + str(i) + "</p>"

    # Write to file
    html += "</body></html>"
    output = open(OUT_PATH, 'w')
    output.write(html)
    output.close()
