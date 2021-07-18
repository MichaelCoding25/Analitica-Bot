# Handles graph creation
import matplotlib.pyplot as plt
import numpy as np

from start import CURRENT_DIR as CD

GRAPHS_DIRECTORY = CD + '/server/graphs'


def create_status_pie_graph(stats_list):
    """
    Creates a pie graph for discord statuses.
    :param stats_list: A list  containing the number of times each status was logged.
    :type stats_list: list
    """
    stats_num = len(stats_list)

    ind_stats_nums = [0, 0, 0, 0]
    for stat in stats_list:
        if stat == 'offline':
            ind_stats_nums[0] += 1
        elif stat == 'online':
            ind_stats_nums[1] += 1
        elif stat == 'idle':
            ind_stats_nums[2] += 1
        elif stat == 'dnd':
            ind_stats_nums[3] += 1

    labels = []
    labels_names = 'Offline', 'Online', 'Idle', 'Do Not Disturb'
    sizes = []
    for i in range(len(ind_stats_nums)):
        if ind_stats_nums[i] > 0:
            labels.append(labels_names[i])
            sizes.append(int(ind_stats_nums[i] / stats_num * 100))

    colors_list = []
    if 'Offline' in labels:
        colors_list.append('grey')
    if 'Online' in labels:
        colors_list.append('green')
    if 'Idle' in labels:
        colors_list.append('orange')
    if 'Do Not Disturb' in labels:
        colors_list.append('red')

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=0, colors=colors_list)
    ax1.axis('equal')
    plt.legend()
    plt.savefig(GRAPHS_DIRECTORY + '/status_pie_graph.png')

    plt.clf()


def create_status_bar_graph(stats_list):
    """
    Creates a bar graph for discord statuses.
    :param stats_list: A list  containing the number of times each status was logged, per day.
    :type stats_list: list
    """
    num_of_days = len(stats_list)

    online = []
    offline = []
    idle = []
    dnd = []

    for day in stats_list:
        day_stats_nums = [0, 0, 0, 0]
        for stat in day:
            if stat == 'offline':
                day_stats_nums[1] += 1
            elif stat == 'online':
                day_stats_nums[0] += 1
            elif stat == 'idle':
                day_stats_nums[2] += 1
            elif stat == 'dnd':
                day_stats_nums[3] += 1

        if len(day) != 0:
            online.append(float(day_stats_nums[0] / len(day) * 100))
            offline.append(float(day_stats_nums[1] / len(day) * 100))
            idle.append(float(day_stats_nums[2] / len(day) * 100))
            dnd.append(float(day_stats_nums[3] / len(day) * 100))
        else:
            online.append(0)
            offline.append(0)
            idle.append(0)
            dnd.append(0)

    ind = np.arange(num_of_days)  # the x locations for the groups
    width = 0.35  # the width of the bars: can also be len(x) sequence

    plt.bar(ind, online, width, color='green', label='Online')
    plt.bar(ind, offline, width, bottom=online, color='grey', label='Offline')
    plt.bar(ind, idle, width, bottom=np.array(offline)+np.array(online), color='orange', label='Idle')
    plt.bar(ind, dnd, width, bottom=np.array(idle)+np.array(offline)+np.array(online), color='red', label='Do Not '
                                                                                                          'Disturb')

    plt.ylabel('Percent')
    plt.title('Statuses by Day and Percentage of Day')
    plt.xlabel('Days Ago')
    names_list = []
    for day in range(num_of_days):
        names_list.append(str(day))
    plt.xticks(ind, names_list)
    plt.yticks(np.arange(0, 101, 10))
    plt.legend()

    plt.savefig(GRAPHS_DIRECTORY + '/status_bar_graph.png')

    plt.clf()


def create_activity_pie_graph(activity_list, activities_names):
    """
    Creates a pie graph for discord activities.
    :param activity_list: A list containing the number of times each activity was logged.
    :type activity_list: list
    :param activities_names: A list containing the names of all the activities.
    :type activities_names: list
    """
    activity_num = len(activity_list)

    ind_activity_nums = []

    for _ in activities_names:
        ind_activity_nums.append(0)
    for act in activity_list:
        for num in range(len(activities_names)):
            if act == activities_names[num]:
                ind_activity_nums[num] += 1

    labels = []
    labels_names = activities_names
    sizes = []
    for i in range(len(ind_activity_nums)):
        if ind_activity_nums[i] > 0:
            labels.append(labels_names[i])
            sizes.append(int(ind_activity_nums[i] / activity_num * 100))

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=0)
    ax1.axis('equal')
    plt.legend()
    plt.savefig(GRAPHS_DIRECTORY + '/activity_pie_graph.png')

    plt.clf()


def create_activity_bar_graph(activity_list, activities_names):
    """
    Creates a bar graph for discord activities.
    :param activity_list: A list  containing the number of times each activity was logged, per day.
    :type activity_list: list
    :param activities_names: A list containing the names of all the activities.
    :type activities_names: list
    """
    num_of_days = len(activity_list)

    new_activities_list = []

    for _ in activities_names:
        new_activities_list.append([])

    for day in activity_list:
        day_activities_nums = []
        for _ in activities_names:
            day_activities_nums.append(0)
        for act in day:
            for num in range(len(activities_names)):
                if act == activities_names[num]:
                    day_activities_nums[num] += 1

        if len(day) != 0:
            for activity_num in range(len(activities_names)):
                new_activities_list[activity_num].append(float(day_activities_nums[activity_num] / len(day) * 100))
        else:
            for activity_num in range(len(activities_names)):
                new_activities_list[activity_num].append(0)

    ind = np.arange(num_of_days)  # the x locations for the groups
    width = 0.35  # the width of the bars: can also be len(x) sequence

    bottom_list = 0.0
    for activity_num in range(len(activities_names)):
        plt.bar(ind, new_activities_list[activity_num], width, bottom=bottom_list, label=activities_names[activity_num])
        bottom_list += np.array(new_activities_list[activity_num])

    plt.ylabel('Percent')
    plt.title('Activities by Day and Percentage of Day')
    plt.xlabel('Days Ago')
    names_list = []
    for day in range(num_of_days):
        names_list.append(str(day))
    plt.xticks(ind, names_list)
    plt.yticks(np.arange(0, 101, 10))
    plt.legend()

    plt.savefig(GRAPHS_DIRECTORY + '/activity_bar_graph.png')

    plt.clf()
