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
import random

class Task_Inputs(object):

    def __init__(self, start=None, end=None, priority=None, a_start=None, a_end=None, a_deadline=None, name='Task'):
        """
        Initialize Input Task Constructor
        :param start: Start of task
        :param end: End of task
        :param priority: Set priority
        :param a_start: Set aperiodic start
        :param a_end: Set aperiodic end
        :param a_deadline: Set aperiodic deadline
        :param name: Name of task
        """

        self.start = start
        self.end = end
        self.usage = 0
        self.priority = priority
        self.name = name.replace("\n", "")
        self.budget = None
        if self.name[:9] == "Sporadic=":
            self.budget = int(self.name[9:])
            self.name = self.name[:8]
        self.a_start = a_start
        self.a_end = a_end
        self.a_deadline = a_deadline
        self.id = int(random.random() * 10000)

    def use_cpu(self, usage):
        """
        Set instance for periodic CPU-mode
        :param usage: Clock step
        :return: Boolean
        """
        self.usage += usage
        if self.usage >= self.end - self.start:
            return True
        return False

    def aperiodic_cpu(self, usage):
        """
        Set instance for aperiodic CPU-mode
        :param usage: Clock step
        :return: Boolean
        """
        self.usage += usage
        if self.usage >= self.a_end - self.a_start:
            return True
        return False

    def budget_consume(self, usage):
        """

        :param usage: Clock step
        :return: Amount of budget left after consumption
        """
        if self.budget is None:
            raise TypeError("This task is not a deferrable server.")
        amount = self.budget - usage
        if amount < 0:
            amount = self.budget
        self.budget -= amount
        return amount

    def __repr__(self):
        """

        :return: String reporting status of budget
        """
        budget_text = ""
        if self.budget is not None:
            budget_text = " budget: " + str(self.budget)
        return str(self.name) + "#" + str(self.id) + " - start: " + str(self.start) + " priority: " + str(self.priority) + budget_text

    def get_name(self):
        """
        Return name for HTML in form of Name#id
        :return:
        """
        return str(self.name) + "#" + str(self.id)


class Jump2PeriodicTaskExecution(Exception):
    """
    Create exceptions for aperiodic tasks
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class TaskType(object):
    """
    Class for periodic tasks
    """
    def __init__(self, period, release, execution, deadline, name):
        """
        Parameters for periodic task
        :param period: Period
        :param release: Release
        :param execution: Execution
        :param deadline: Deadline
        :param name: Name of Task
        """
        self.period = period
        self.release = release
        self.execution = execution
        self.deadline = deadline
        self.name  = name

    def __repr__(self):
        """
        Return description of periodic task
        :return: String describing periodic task
        """
        return "Task Type: " + str(self.name) + " - period: " + str(self.period)

