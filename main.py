import json
import csv
from heapq import heappush, heappop

debug_mode = False


def load(file_dir):
    # course_file = "rounds.csv"
    # course_file = "rounds_nick.csv"
    # course_file = "round-pretest-02.csv"
    # course_file = "round-pretest-03.csv"
    # course_file = "round-final-01.csv"
    course_file = "round-final-02.csv"
    # accept_file = "small-test01.csv"
    # accept_file = "small-test02.csv"
    # accept_file = "01-univ-uniform-uniform.csv"
    # accept_file = "02-univ-weighted-uniform.csv"
    # accept_file = "03-univ-weighted-uniform-float.csv"
    # accept_file = "04-univ-uniform-intbiased.csv"
    # accept_file = "05-univ-weighted-intbiased.csv"
    # accept_file = "06-univ-weighted-floatbiased.csv"
    # accept_file = "student-prd-test-02.csv"
    # accept_file = "student-prd-test-03.csv"
    # accept_file = "student-final-01.csv"
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
        print('++', course["amount"],
              course['receive_student_number'], course['heap'])


def rem(course, mark):
    last = course['heap'][0][0]
    while course["amount"] > 0 and course['heap'][0][0] == last:
        mark[course['heap'][0][1]][0] = False
        mark[course['heap'][0][1]][1] += 1
        course['min'] = course['heap'][0][0]
        course["amount"] -= 1
        heappop(course['heap'])


def rem_l(course, mark):
    kick_list = []
    i = 0
    while course["amount"]-i > course['receive_student_number']:
        kick_list.append(heappop(course['heap']))
        i += 1
    last = course['heap'][0][0]
    for i in kick_list:
        if i[0] == last:
            heappush(course['heap'], (i[0], i[1]))
        else:
            mark[i[1]][0] = False
            mark[i[1]][1] += 1
            course['min'] = i[0]
            course["amount"] -= 1
            if debug_mode and i[1] == debug_id:
                print("kick", mark[i[1]])


def comp(std, course, mark):
    # round_4_receive => receive_student_number
    # round_4_condition => receive_add_limit
    # 1 2 3 => A B C
    # course['round_4_add_limit'] => extend = int(course['receive_add_limit'][1:])
    if debug_mode and std['citizen_id'] == debug_id:
        print(course["amount"], course['receive_student_number'],
              course['heap'][0][0] if course["amount"] else 'x', std['ranking'])
    if course['receive_student_number'] == 0:
        mark[std['citizen_id']][1] += 1
        return 1
    if std['ranking'] == 0:
        mark[std['citizen_id']][1] += 1
        return 1
    if course["amount"] < course['receive_student_number']:
        if debug_mode and std['citizen_id'] == debug_id:
            print(1, course['min'], std['ranking'])
        if course['min'] != False:
            if course['min'] < std['ranking']:
                add_std(course, std['ranking'], std['citizen_id'], mark)
                return 0
            else:
                mark[std['citizen_id']][1] += 1
                return 1
        else:
            add_std(course, std['ranking'], std['citizen_id'], mark)
            return 0
    elif course['heap'][0][0] < std['ranking']:
        if debug_mode and std['citizen_id'] == debug_id:
            print(2)
        add_std(course, std['ranking'], std['citizen_id'], mark)
        if course['receive_add_limit'] == 'A':
            rem_l(course, mark)
        elif course['receive_add_limit'] == 'B':
            rem(course, mark)
        elif course['receive_add_limit'][0] == 'C':
            extend = int(course['receive_add_limit'][1:])
            if course["amount"] > course['receive_student_number']+extend:
                rem(course, mark)
            else:
                rem_l(course, mark)
        return 1
    elif course['heap'][0][0] == std['ranking']:
        if debug_mode and std['citizen_id'] == debug_id:
            print(3)
        if course['receive_add_limit'] == 'A':
            add_std(course, std['ranking'], std['citizen_id'], mark)
            return 0
        elif course['receive_add_limit'] == 'B':
            rem(course, mark)
        elif course['receive_add_limit'][0] == 'C':
            extend = int(course['receive_add_limit'][1:])
            if course["amount"] >= course['receive_student_number']+extend:
                rem(course, mark)
            else:
                add_std(course, std['ranking'], std['citizen_id'], mark)
                return 0
    mark[std['citizen_id']][1] += 1
    if debug_mode and std['citizen_id'] == debug_id:
        print(mark[std['citizen_id']])
    return 1


def add(std_id, std_list, mark):
    if len(std_list) <= mark[std_id][1]:
        return False
    std = std_list[mark[std_id][1]]
    course = course_map[std['round_id']]
    if course["join_id"]:
        join_id = course['university_id']+course["join_id"]
        course = course_map[join_amount[join_id][0]]
    kick = comp(std, course, mark)
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

    # file_dir = './data/small/'
    # file_dir = './data/large/'
    # file_dir = './data/real/'
    # file_dir = './data/real/ver2'
    # file_dir = './data/real/ver3'
    file_dir = './data/real/ver4'

    course_map, join_amount, enroll_map, std_map, accept_raw, header = load(
        file_dir)

    mark = {}
    for key, val in std_map.items():
        val.sort(key=lambda x: enroll_map[x['citizen_id']][x['round_id']])
        mark[key] = [False, 0]

    debug_id = '1103703406035'
    debug_course = '5e225a6ab8e2112970564c97'
    # debug_mode = True

    solve(course_map, std_map, mark)

    if debug_mode:
        print(mark[debug_id])
        print(std_map[debug_id])
        print(enroll_map[debug_id])
        print(course_map[debug_course])
        print(join_amount[course_map[debug_course]
                          ['university_id']+course_map[debug_course]['join_id']])

    print(','.join(header))
    output_file = "chay-final-4.csv"
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
