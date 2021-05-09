import json
import csv
from heapq import heappush, heappop
from cmp import cmp

debug_mode = False


def load(file_dir):
    # course_file = "round4-pre01.csv"
    # course_file = "round4-final-01.csv"
    course_file = "round4-final-02.csv"
    # accept_file = "cat-a01.csv"
    # accept_file = "cat-b01.csv"
    # accept_file = "student-final-01.csv"
    accept_file = "student-r4-final-02.csv"

    with open(f'{file_dir}/{course_file}', 'r', encoding='utf-8-sig') as course_file:
        course_list = csv.DictReader(course_file)
        course_map = {}
        join_amount = {}
        for i in course_list:
            course_map[i['_id']] = i

            for j in [0,1,2,3,4,11,12]:
                course_map[i['_id']][f'amount_{j}'] = 0
                course_map[i['_id']][f'heap_{j}'] = []
                course_map[i['_id']][f'min_{j}'] = False

            course_map[i['_id']]['receive_0'] = int(
                course_map[i['_id']]['receive_student_number'])

            course_map[i['_id']]['receive_1'] = int(
                course_map[i['_id']]['receive_student_number_formal'])
            course_map[i['_id']]['receive_2'] = int(
                course_map[i['_id']]['receive_student_number_international'])
            course_map[i['_id']]['receive_3'] = int(
                course_map[i['_id']]['receive_student_number_vocational'])
            course_map[i['_id']]['receive_4'] = int(
                course_map[i['_id']]['receive_student_number_nonformal'])

            course_map[i['_id']]['receive_11'] = int(
                course_map[i['_id']]['gender_male_number'])
            course_map[i['_id']]['receive_12'] = int(
                course_map[i['_id']]['gender_female_number'])

            for j in [0,1,2,3,4,11,12]:
                if course_map[i['_id']][f'receive_{j}'] == 0:
                    course_map[i['_id']][f'receive_{j}'] = 9999999

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
                line['score'] = float(line['score'])
            except:
                print('error', line)
                exit()
            std_map[line['citizen_id']].append(line)

    return course_map, join_amount, enroll_map, std_map, accept_raw, header


def add_std(course, score, std_id, mark, num=0):
    heappush(course[f'heap_{num}'], (score, std_id))
    course[f"amount_{num}"] += 1
    if num>0:
        mark[std_id][0] = True
    if debug_mode and course['_id'] == debug_course:
        print('+=', score, std_id, num)
        print('++', len(course[f'heap_{num}']),
              course[f'receive_{num}'], course[f'heap_{num}'])

def rem_in_plan(course, num, std_id):
    # print('b',course[f'heap_{num}'])
    for ix,i in enumerate(course[f'heap_{num}']):
        if i[1]==std_id:
            del course[f'heap_{num}'][ix]
            course[f'heap_{num}'].sort()
            break
    # print('c',course[f'heap_{num}'])    

def rem_all_plan(course, std_id):
    for i in [0,1,2,3,4,11,12]:
        rem_in_plan(course, i, std_id)

def unmark(mark, std_id):
    if debug_mode and std_id == debug_id:
        print('#kick ', mark[std_id])
    mark[std_id][0] = False
    mark[std_id][1] += 1

def comp_global(std, course, mark, num=0):
    # return true if std was add to heap array, kick list
    kicks = []
    if debug_mode and std['citizen_id'] == debug_id:
        print('DB',course['_id'], std['score'],course[f'min_{num}'], num)
    
    if course[f'min_{num}'] is False or std['score'] > course[f'min_{num}']:
        if debug_mode and std['citizen_id'] == debug_id:
            print('DBX')
        add_std(course, std['score'], std['citizen_id'], mark, num)
        kicks = cmp(
            course[f'heap_{num}'], course[f'receive_{num}'], \
            course['receive_add_limit']
        )
        if debug_mode and course['_id'] == debug_course:
            print('cmp',kicks,std['citizen_id'])

        return len([i for i in kicks if i[1] == std['citizen_id']])==0, kicks

    return False, []

def comp_new(std, course, mark):
    # when someone kicked return 1 and return 0 otherwise
    # kick by mark[id] = (is_ok, order)
    # is_ok false mean need to compare order
    # order++ to next order

    # if std['score'] == 0:
    #     unmark(mark, std['citizen_id'])
    #     return 1

    num = int(std['school_program'])
    if course['receive_11']>0 and course['receive_11'] != 9999999:
        if std['gender']:
            num = int('1'+std['gender'])
        else:
            num = 11
    pass_global, kicks = comp_global(std, course, mark, 0)
    if debug_mode and course['_id'] == debug_course:
        print('global', pass_global, kicks)
    if pass_global:
        pass_plan, kicks_plan = comp_global(std, course, mark, num)

        if debug_mode and course['_id'] == debug_course:
            print('plan', pass_plan, kicks_plan)
        kick_mark = {}

        if pass_plan:
            # rem kicks
            if not kicks_plan:
                for i in kicks:
                    unmark(mark, i[1])
                    course[f'min_0'] = i[0]
                    rem_all_plan(course, i[1])
                    kick_mark[i[1]]=1
        else:   
            # restore kicks
            for i in kicks:
                heappush(course[f'heap_0'], i)

        # rem kicks_plan
        for i in kicks_plan:
            if i[1] not in kick_mark:
                unmark(mark, i[1])
                course[f'min_{num}'] = i[0]
                rem_in_plan(course, 0, i[1])

        if not kicks_plan and not pass_plan:
            unmark(mark, std['citizen_id'])
            rem_in_plan(course, 0, std['citizen_id'])

        return 1 if kicks_plan else 0

    else:
        if not kicks and not pass_global:
            unmark(mark, std['citizen_id'])
            return 1

        for i in kicks:
            unmark(mark, i[1])
            course[f'min_0'] = i[0]
            rem_all_plan(course, i[1])

    if debug_mode and course['_id'] == debug_course:
        print('-=', kicks, course[f'min_0'])
        # print('-=', kicks_plan, course[f'min_{num}'])

    return 1 if kicks else 0


def add(std_id, std_list, mark):
    if len(std_list) <= mark[std_id][1]:
        return False
    std = std_list[mark[std_id][1]]
    course = course_map[std['round_id']]
    if course["join_id"]:
        join_id = course['university_id']+course["join_id"]
        course = course_map[join_amount[join_id][0]]
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

    file_dir = './data/real-r4'

    course_map, join_amount, enroll_map, std_map, accept_raw, header = load(
        file_dir)

    mark = {}
    for key, val in std_map.items():
        val.sort(key=lambda x: enroll_map[x['citizen_id']][x['round_id']])
        mark[key] = [False, 0]

    debug_id = '1500101122555'
    debug_course = '5de4c04ad01dc4a664f84d62'
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
    output_file = "chay-r4-gender-2.csv"
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
