import argparse
import json

"""
Converts a .PU file to an editable .PUMAP file
"""


def translate_param(output, param_key, param_obj, task_key):
    param_obj['id'] = int(param_key)
    param_obj['taskId'] = int(task_key)
    param_obj['description'] = param_obj.pop('timerInfo')

    # Still kinda unsure if this will work properly
    param_obj['valueType'] = param_obj.pop('unit')
    if 'timeUnit' not in param_obj.keys():
        param_obj['timeUnit'] = 'minutes'
        if param_obj['value'] % 1440 == 0:
            param_obj['timeUnit'] = 'days'
        elif param_obj['value'] % 60 == 0:
            param_obj['timeUnit'] = 'hours'
        else:
            param_obj['timeUnit'] = 'minutes'
    output['params'].append(param_obj)


def translate_task(output, task_obj):
    task_obj['id'] = int(task_obj['id'])
    task_obj['description'] = task_obj.pop('task')

    for tag in task_obj['tags']:
        output['tags'].append(tag)

    # Filter parameters into own list
    params = task_obj.pop('parameters')
    for param_key, param_obj in params.items():
        translate_param(output, param_key, param_obj, task_obj['id'])
    output['tasks'].append(task_obj)

    if 'isExam' in task_obj.keys() and task_obj['isExam'] is True:
        return 'exam', int(task_obj['id'])
    else:
        return 'reg', int(task_obj['id'])


def translate_perks(output, perk_obj):
    perk_obj['id'] = int(perk_obj['id'])
    perk_obj.pop('job')
    perk_obj.pop('perk')
    if 'description' not in perk_obj.keys():
        perk_obj['description'] = "undefined"
    if 'tags' in perk_obj.keys():
        for tag in perk_obj['tags']:
            output['tags'].append(tag)
    output['modifiers'].append(perk_obj)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", metavar='Input Path', type=str, help='- Absolute path to *.pu file')
    args = parser.parse_args()

    input_path = args.input
    if not input_path.endswith('pu'):
        print('Only *.pu files can be converted')
        exit(2)
    output_path = input_path + 'map'

    #
    output = json.loads('{"version":1, "mapId":"", "globalIndex":-1, "general":{}, "tags":[], "majors":[], '
                        '"classes":[], "tasks":[], "params":[], "punishments":[], "clubs":[], "partners":[], '
                        '"modifiers":[], "help":[], "rouletteOptions":[]}')

    with open(input_path) as json_file:
        content = json.load(json_file)

        # General stuff
        output['mapId'] = content['mapId']
        output['general'] = content['general']
        if 'moduleId' in output.keys():
            output['moduleId'] = content['moduleId']

        # Sorting and Renaming, mostly
        for class_key, class_obj in content['classes'].items():
            class_obj['id'] = int(class_obj['id'])
            class_obj['title'] = class_obj.pop('name')
            class_obj['subtitle'] = class_obj.pop('name2')
            tasks = class_obj.pop('tasks')
            task_ids = {'reg': [], 'exam': []}
            # Filter tasks into own list
            for task_key, task_obj in tasks.items():
                task_type, task_id = translate_task(output, task_obj)
                task_ids[task_type].append(task_id)
            if 'imageUrl' not in class_obj.keys():
                class_obj['imageUrl'] = ""
            class_obj['tasks'] = task_ids['reg']
            class_obj['exams'] = task_ids['exam']
            class_obj.pop('type')
            output['classes'].append(class_obj)

        for major_key, major_obj in content['majors'].items():
            major_obj.pop('type')
            major_obj['id'] = int(major_obj['id'])
            major_obj['title'] = major_obj.pop('name')
            major_obj['subtitle'] = major_obj.pop('name2')
            if 'imageUrl' not in major_obj.keys():
                major_obj['imageUrl'] = ""
            major_obj['exams'] = []
            tasks = major_obj.pop('tasks')
            for task_key, task_obj in tasks.items():
                major_obj['exams'].append(task_obj)
            output['majors'].append(major_obj)

        for part_key, part_obj in content['partners'].items():
            part_obj['id'] = int(part_obj['id'])
            part_obj.pop('type')
            part_obj.pop('name2')
            part_obj.pop('tier')  # TODO What is the point of that key?
            if 'imageUrl' not in part_obj.keys():
                part_obj['imageUrl'] = ""
            perks = part_obj.pop('perks')
            part_obj['modifiers'] = []
            for perk_key, perk_obj in perks.items():
                part_obj['modifiers'].append(int(perk_obj['id']))
                translate_perks(output, perk_obj)
            output['partners'].append(part_obj)

        for club_key, club_obj in content['clubs'].items():
            club_obj['id'] = int(club_obj['id'])
            club_obj.pop('type')
            if 'imageUrl' not in club_obj.keys():
                club_obj['imageUrl'] = ""
            perks = club_obj.pop('perks')
            club_obj['modifiers'] = []
            for perk_key, perk_obj in perks.items():
                club_obj['modifiers'].append(int(perk_obj['id']))
                translate_perks(output, perk_obj)
            output['clubs'].append(club_obj)

        for pun_key, pun_obj in content['punishments'].items():
            pun_obj['id'] = int(pun_obj['id'])
            pun_obj['title'] = pun_obj.pop('name')
            pun_obj.pop('type')
            if 'imageUrl' not in pun_obj.keys():
                pun_obj['imageUrl'] = ""
            tasks = pun_obj.pop('tasks')
            for task_key, task_obj in tasks.items():
                task_type, task_id = translate_task(output, task_obj)
                pun_obj['punishment'] = task_id
            output['punishments'].append(pun_obj)

        for roul_key, roul_obj in content['rouletteOptions'].items():
            roul_obj['id'] = int(roul_obj['id'])
            roul_obj.pop('type')
            output['rouletteOptions'].append(roul_obj)

        output['help'] = content['general']['help']

        # Deduplicate tags
        output['tags'] = list(set(output['tags']))

        # Deduplicate JSON-objects
        ids = []
        for group_key, group_list in output.items():
            # Only check top-level keys that actually contain JSON-objects
            if isinstance(group_list, list) and group_key != 'tags':
                group_list[:] = {each['id']: each for each in group_list}.values()
                for subgroup_dict in group_list:
                    ids.append(subgroup_dict['id'])

        # Set globalIndex
        output['globalIndex'] = max(ids) + 1

        with open(output_path, 'w') as output_file:
            json.dump(output, output_file)
            output_file.close()

        json_file.close()


if __name__ == '__main__':
    main()
