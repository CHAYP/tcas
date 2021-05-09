import json
import csv
from heapq import heappush, heappop
from cmp import cmp

debug_mode = False


def load(file_dir):
    course_file = "round-final-02.csv"
    accept_file = "student-final-02.csv"

    with open(f'{file_dir}/{course_file}', 'r', encoding='utf-8-sig') as course_file:
        course_list = csv.DictReader(course_file)
        course_map = {}
        join_amount = {}
        for i in course_list:
            course_map[i['_id']] = i
            course_map[i['_id']]['amount'] = 0
            course_map[i['_id']]['heap'] = []
            course_map[i['_id']]['min'] = False

            course_map[i['_id']]['receive_student_number'] = int(
                course_map[i['_id']]['receive_student_number'])

            if i["join_id"]:
                join_id = i['university_id']+i["join_id"]
                if not join_amount.get(join_id):
                    join_amount[join_id] = []
                join_amount[join_id].append(i['_id'])

    with open(f'{file_dir}/{accept_file}') as student_file:
        reader = csv.DictReader(student_file)
        header = []
        accept_raw = []
        std_map = {}
        enroll_map = {}
        for num, line in enumerate(reader):
            if num == 0:
                header = [i for i in line]
            raw = [line[i] for i in line]
            accept_raw.append(raw)

            if not enroll_map.get(line['citizen_id']):
                enroll_map[line['citizen_id']] = {}
            enroll_map[line['citizen_id']][line['round_id']] = int(
                line['priority'])

            if not std_map.get(line['citizen_id']):
                std_map[line['citizen_id']] = []

            try:
                # if int(line['ranking']) == 0:
                #     line['ranking'] = -99999
                # else:
                line['ranking'] = -float(line['ranking'])
            except:
                print(line)
                exit()
            std_map[line['citizen_id']].append(line)

    return course_map, join_amount, enroll_map, std_map, accept_raw, header


def add_std(course, score, std_id, mark):
    heappush(course['heap'], (score, std_id))
    course["amount"] += 1
    mark[std_id][0] = True
    if debug_mode and course['_id'] == debug_course:
        print('+=', score, std_id)
        # print('++', course["amount"],
        #       course['receive_student_number'], course['heap'])

def unmark(mark, std_id):
    mark[std_id][0] = False
    mark[std_id][1] += 1

def comp_new(std, course, mark):
    # when someone kicked return 1 and return 0 otherwise
    # kick by mark[id] = (is_ok, order)
    # is_ok false mean need to compare order
    # order++ to next order

    if std['ranking'] == 0:
        mark[std['citizen_id']][1] += 1
        return 1

    kicks = []
    if not course['min'] or std['ranking'] > course['min']:
        add_std(course, std['ranking'], std['citizen_id'], mark)
        kicks = cmp(
            course['heap'], course['receive_student_number'], \
            course['receive_add_limit']
        )

        # course['amount'] = len(course['heap'])
        course['amount'] += -len(kicks)
        for i in kicks:
            unmark(mark, i[1])
            course['min'] = i[0]
    else:
        unmark(mark, std['citizen_id'])
        return 1

    if debug_mode and course['_id'] == debug_course:
        print('-=', kicks, course['min'])

    return 1 if kicks else 0

def add(std_id, std_list, mark):
    if len(std_list) <= mark[std_id][1]:
        return False
    std = std_list[mark[std_id][1]]
    course = course_map[std['round_id']]
    if course["join_id"]:
        join_id = course['university_id']+course["join_id"]
        course = course_map[join_amount[join_id][0]]
    # kick = comp(std, course, mark)
    kick = comp_new(std, course, mark)
    return kick


def solve(course_map, std_map, mark):
    change = True
    t = 0
    while change:
        change = False
        x = 0
        for std_id, std_list in std_map.items():
            if not mark[std_id][0]:
                x += 1
                change |= add(std_id, std_list, mark)
        t += 1
        # print('#', t, x)


def get_real_order(std_id, course_id):
    x = enroll_map[std_id][course_id]
    y = 0
    for i in enroll_map[std_id].values():
        if i < x:
            y += 1
    return y+1


if __name__ == "__main__":

    file_dir = './data/real/ver4'

    course_map, join_amount, enroll_map, std_map, accept_raw, header = load(
        file_dir)

    mark = {}
    for key, val in std_map.items():
        val.sort(key=lambda x: enroll_map[x['citizen_id']][x['round_id']])
        mark[key] = [False, 0]

    debug_id = '1248100003773'
    debug_course = '5e1afdd9552088a0512f60ce'
    # debug_mode = True

    solve(course_map, std_map, mark)

    if debug_mode:
        print(mark[debug_id])
        print(std_map[debug_id])
        print(enroll_map[debug_id])
        print(course_map[debug_course])
        # print(join_amount[course_map[debug_course]
        #                   ['university_id']+course_map[debug_course]['join_id']])

    print(','.join(header))
    output_file = "chay-r4-test.csv"
    # id_order = 7
    id_order = 1
    course_order = 5
    # pp = 0
    for i in accept_raw:
        if debug_mode:
            if i[id_order] == debug_id:
                print(i)
                print(mark[i[id_order]])
                print(enroll_map[i[id_order]][i[course_order]])
        else:
            if mark[i[id_order]][0]:
                p = get_real_order(i[id_order], i[course_order])
                if mark[i[id_order]][1]+1 == p:
                    i[-1] = 2
                    # pp += 1 # for count
                elif mark[i[id_order]][1]+1 > p:
                    i[-1] = 8
                else:
                    i[-1] = 9
            else:
                i[-1] = 8
            # print(','.join([str(j) for j in i]))

    if not debug_mode:
        with open(output_file, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(header)
            for i in accept_raw:
                csvwriter.writerow(i)
    # print(pp)
