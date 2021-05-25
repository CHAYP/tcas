import json
import csv
from heapq import heappush, heappop
from cmp import cmp

debug_mode = False

# receive_type = ['formal','international','vocational','nonformal','male','female']
receive_type = [0, 1, 2, 3, 4, 11, 12]


def load(file_dir):
    # course_file = "round_21may-8371rows.csv"
    course_file = "round_25may-8371rows.csv"
    # accept_file = "student_21may-775926rows-randomized.csv"
    # accept_file = "21may-output-no-adjustment-randomized-jittat-1.csv"
    # accept_file = "21may-output-randomized-jittat-1.csv"
    # accept_file = "student_25may-775926rows-randomized.csv"
    # accept_file = "25may-output-randomized-jittat-2.csv"
    accept_file = "result-update-round-1.csv"

    with open(f"{file_dir}/{course_file}", "r", encoding="utf-8-sig") as course_file:
        course_list = csv.DictReader(course_file)
        course_map = {}
        join_amount = {}
        for i in course_list:
            course_map[i["_id"]] = i

            for j in receive_type:
                course_map[i["_id"]][f"amount_{j}"] = 0
                course_map[i["_id"]][f"heap_{j}"] = []
                course_map[i["_id"]][f"min_{j}"] = False

            course_map[i["_id"]]["receive_0"] = int(
                course_map[i["_id"]]["receive_student_number"]
            )

            course_map[i["_id"]]["receive_1"] = int(
                course_map[i["_id"]]["receive_student_number_formal"]
            )
            course_map[i["_id"]]["receive_2"] = int(
                course_map[i["_id"]]["receive_student_number_international"]
            )
            course_map[i["_id"]]["receive_3"] = int(
                course_map[i["_id"]]["receive_student_number_vocational"]
            )
            course_map[i["_id"]]["receive_4"] = int(
                course_map[i["_id"]]["receive_student_number_nonformal"]
            )

            course_map[i["_id"]]["receive_11"] = int(
                course_map[i["_id"]]["gender_male_number"]
            )
            course_map[i["_id"]]["receive_12"] = int(
                course_map[i["_id"]]["gender_female_number"]
            )

            # receive 0 is mean no limit
            for j in receive_type:
                if course_map[i["_id"]][f"receive_{j}"] == 0:
                    course_map[i["_id"]][f"receive_{j}"] = 9999999

            if i["join_id"]:
                join_id = make_join_id(i)
                if not join_amount.get(join_id):
                    join_amount[join_id] = []
                join_amount[join_id].append(i["_id"])

    with open(f"{file_dir}/{accept_file}") as student_file:
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

            if not enroll_map.get(line["citizen_id"]):
                enroll_map[line["citizen_id"]] = {}
            enroll_map[line["citizen_id"]][line["round_id"]] = int(line["priority"])

            if not std_map.get(line["citizen_id"]):
                std_map[line["citizen_id"]] = []

            try:
                line["score"] = float(line["score"])
                line["ranking"] = -float(line["ranking"])
            except:
                print("error", line)
                exit()
            std_map[line["citizen_id"]].append(line)

    return course_map, join_amount, enroll_map, std_map, accept_raw, header


def add_std(course, score, std_id, mark, num=0):
    heappush(course[f"heap_{num}"], (score, std_id))
    course[f"amount_{num}"] += 1
    if num > 0:
        mark[std_id][0] = True
    if debug_mode and course["_id"] == debug_course:
        print("+=", score, std_id, num)
        print(
            "++",
            len(course[f"heap_{num}"]),
            course[f"receive_{num}"],
            course[f"heap_{num}"],
        )


def rem_in_plan(course, num, std_id):
    # print('b',course[f'heap_{num}'])
    for ix, i in enumerate(course[f"heap_{num}"]):
        if i[1] == std_id:
            del course[f"heap_{num}"][ix]
            course[f"heap_{num}"].sort()
            break
    # print('c',course[f'heap_{num}'])


def rem_all_plan(course, std_id):
    for i in receive_type:
        rem_in_plan(course, i, std_id)

def get_course(course):
    if course["join_id"]:
        join_id = make_join_id(course)
        return course_map[join_amount[join_id][0]]
    return course

def get_course_by_id(id):
    return get_course(course_map[id])

def add_kicked(mark, std_id):
    std = std_map[std_id][mark[std_id][1]]
    round_id = std["round_id"]
    course = get_course_by_id(round_id)
    if course['type'][1] != '2': return False
    kicked_id = make_balance_id(course)
    score = get_std_score(std)
    if kicked_id not in kicked:
        kicked[kicked_id] = []
    kicked[kicked_id].append((score, (std_id, mark[std_id][1], course['_id'])))

def get_std_score(std):
    return std["ranking"] if std["type"][1] == "1" else std["score"] 

def unmark(mark, std_id):
    if is_debug_id(std_id):
        print("#kick ", mark[std_id])

    overflow[get_course_by_id(std_map[std_id][mark[std_id][1]]["round_id"])["_id"]] = True
    add_kicked(mark, std_id)

    mark[std_id][0] = False
    mark[std_id][1] += 1

    if is_debug_id(std_id):
        print("#kick2 ", mark[std_id])

def comp_global(std, course, mark, num=0):
    # return true if std was add to heap array, kick list
    kicks = []
    std_score = get_std_score(std)
    std_score -= score_offset
    if float_equal(std_score,0): 
        if std["type"][1] == "1":
            return False, []
    if is_debug_id(std["citizen_id"]):
        print("DB", course["_id"], std_score, course[f"min_{num}"], num)

    if course[f"min_{num}"] is False or std_score > course[f"min_{num}"]:
        if is_debug_id(std["citizen_id"]):
            print("DBX")
        add_std(course, std_score, std["citizen_id"], mark, num)
        kicks = cmp(
            course[f"heap_{num}"], course[f"receive_{num}"], course["receive_add_limit"]
        )
        if is_debug_course(course["_id"]):
            print("cmp", kicks, std["citizen_id"])

        return len([i for i in kicks if i[1] == std["citizen_id"]]) == 0, kicks

    return False, []

def float_equal(a,b):
    return abs(a-b) <= 0.000001

def comp_new(std, course, mark):
    # when someone kicked return 1 and return 0 otherwise
    # kick by mark[id] = (is_ok, order)
    # is_ok false mean need to compare order
    # order++ to next order

    num = int(std["school_program"])
    if course["receive_11"] > 0 and course["receive_11"] != 9999999:
        if std["gender"]:
            num = int("1" + std["gender"])
        else:
            num = 11
    pass_global, kicks = comp_global(std, course, mark, 0)
    if is_debug_course(course["_id"]):
        print("global", pass_global, kicks)
    if pass_global:
        pass_plan, kicks_plan = comp_global(std, course, mark, num)

        if is_debug_course(course["_id"]):
            print("plan", pass_plan, kicks_plan)
        kick_mark = {}

        if pass_plan:
            # rem kicks
            if not kicks_plan:
                for i in kicks:
                    unmark(mark, i[1])
                    course[f"min_0"] = i[0]
                    rem_all_plan(course, i[1])
                    kick_mark[i[1]] = 1
        else:
            # restore kicks
            for i in kicks:
                heappush(course[f"heap_0"], i)

        # rem kicks_plan
        for i in kicks_plan:
            if i[1] not in kick_mark:
                unmark(mark, i[1])
                course[f"min_{num}"] = i[0]
                rem_in_plan(course, 0, i[1])

        if not kicks_plan and not pass_plan:
            unmark(mark, std["citizen_id"])
            rem_in_plan(course, 0, std["citizen_id"])

        return 1 if kicks_plan else 0

    else:
        if not kicks and not pass_global:
            unmark(mark, std["citizen_id"])
            return 1

        for i in kicks:
            unmark(mark, i[1])
            course[f"min_0"] = i[0]
            rem_all_plan(course, i[1])

    if is_debug_course(course["_id"]):
        print("-=", kicks, course[f"min_0"])
        # print('-=', kicks_plan, course[f'min_{num}'])

    return 1 if kicks else 0


def add(std_id, std_list, mark):
    if is_debug_id(std_id):
        print('#new',mark[std_id])
    if len(std_list) <= mark[std_id][1]:
        return False
    std = std_list[mark[std_id][1]]
    course = course_map[std["round_id"]]
    if course["join_id"]:
        join_id = make_join_id(course)
        course = course_map[join_amount[join_id][0]]
    kick = comp_new(std, course, mark)
    return kick


def make_join_id(course):
    return course["university_id"] + course["join_id"] + course["type"]

def make_balance_id(course):
    if course["join_id"]:
        course = course_map[join_amount[make_join_id(course)][0]]
        return course["program_id"]+course["major_id"]+course["university_id"]+course["join_id"]
        # return make_join_id(course)
    return course["program_id"]+course["major_id"]+course["university_id"]

def solve(course_map, std_map, mark):
    change = True
    t = 0
    for i in range(100):
    # while change:
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
    return y + 1


def is_debug_id(std_id):
    return debug_mode and std_id == debug_id


def is_debug_course(course_id):
    return debug_mode and course_id == debug_course

def sum_empty(programs):
    ret = 0
    backup = []
    for i in programs:
        if not i['overflow']:
            amount = max(0,i['receive']-i['amount'])
            ret += amount
            course_map[i['id']]['receive_0'] -= amount
            backup.append((i['id'], i['receive']))
    return ret,backup

def can_recv(program):
    return program['overflow'] and program['limit'] == 'A'

def inc_recv(program, amount):
    course_map[program['id']]['receive_0'] += amount    

def adj_a(empty, programs):
    if empty == 0: return False
    programs.sort(key=lambda x: x['id'])
    give_programs = sum([1 for i in programs if can_recv(i)])
    if give_programs == 0: return False
    give_amount = int(empty/give_programs)
    j = 0
    for i in programs:
        if can_recv(i):
            inc_recv(i, give_amount+int(j<empty%give_programs))
            j+=1
    return j>0

def adj_b(empty, programs, balance_id):
    if empty == 0: return False
    kicked.get(balance_id,[]).sort(reverse=True)
    j = 0
    dup = {}
    for i in kicked.get(balance_id,[]):
        if j>= empty: break
        if i[1][2] not in dup:
            dup[i[1][2]] = 0
        dup[i[1][2]]+=1
        j+=1

    # print(dup)
    is_adj = False
    for course_id, amount in dup.items():
        for program in programs:
            if program['id'] == course_id:
                if can_recv(program):
                    if j<empty:
                        amount+=empty-j
                        j=empty
                    inc_recv(program, amount)
                    is_adj = True
                    break

    if balance_id == make_balance_id(get_course_by_id('602e1f46ed347e0ff026a663')):
        print(balance_id)
        print(kicked.get(balance_id,[]))
    return is_adj


def balancer(info, balance_id):
    # in 61
    empty_a, backup_a = sum_empty(info[0])
    is_adj_a = adj_a(empty_a, info[0])
    # print(empty_a, is_adj_a)
    # in 62
    empty_b, backup_b = sum_empty(info[1])
    is_adj_b = adj_b(empty_b, info[1], balance_id)

    if not is_adj_a:
        is_adj_a_to_b = adj_b(empty_a, info[1], balance_id)
        if not is_adj_a_to_b:
            for i in backup_a: # (id, reveive_0)
                course_map[i[0]]['receive_0'] = i[1]
            # return to itself

    if not is_adj_b:
        is_adj_b_to_a = adj_a(empty_b, info[0])
        if not is_adj_b_to_a:
            for i in backup_b: # (id, reveive_0)
                course_map[i[0]]['receive_0'] = i[1]

    if info[1] and info[1][0]['id'] == "602e1f46ed347e0ff026a663":
        print(is_adj_a,is_adj_b,is_adj_a_to_b,is_adj_b_to_a)
    

    return is_adj_a or is_adj_b or is_adj_a_to_b or is_adj_b_to_a

if __name__ == "__main__":

    file_dir = "./data_21"

    course_map, join_amount, enroll_map, std_map, accept_raw, header = load(file_dir)

    score_offset = 0
    mark = {}
    # mark = [bool, num] => [pass status, piority pointer]
    for key, val in std_map.items():
        val.sort(key=lambda x: enroll_map[x["citizen_id"]][x["round_id"]])
        mark[key] = [False, 0]

    debug_id = "4241681226522"
    debug_course = "5fc7100447d79dc41d05a45f"
    # debug_mode = True

    balance = True
    # balance = False

    balancing = True
    while balancing:
        print("start")
        # reset
        for key, val in std_map.items():
            mark[key] = [False, 0]
            # if not mark[key]:
            #     mark[key] = [False, 0]

        for key, val in course_map.items():
            for j in receive_type:
                val[f"amount_{j}"] = 0
                val[f"heap_{j}"] = []
                val[f"min_{j}"] = False

        overflow = {}
        kicked = {}

        solve(course_map, std_map, mark)

        if not balance:
            break

        for key, val in course_map.items():
            if len(val["heap_0"]) > val["receive_0"]:
                overflow[key] = True

        program = {}
        for key, val in course_map.items():
            if val['join_id']:
                # continue
                # dont adj with join
                if val['_id'] != join_amount[make_join_id(val)][0]:
                    continue
                val = course_map[join_amount[make_join_id(val)][0]]
            _id = make_balance_id(val)
            if not program.get(_id):
                program[_id] = [[], []]
            program[_id][int(val["type"][1]) - 1].append({
                # 'amount': val["amount_0"],
                'amount': len(val["heap_0"]),
                'receive': val["receive_0"],
                'limit': val["receive_add_limit"],
                'id': val["_id"],
                'overflow': overflow.get(val["_id"], False),
            })

        # print(program)
        balancing = False

        debug_balance_id = make_balance_id(course_map['602e1f46ed347e0ff026a663'])
        # debug_balance_id = make_balance_id(course_map['602e1f46ed347e0ff026a664'])
        
        
        print(program[debug_balance_id])
        for key, val in program.items():
            if len(val[0]) > 0 or len(val[1]) > 0:
                condA = 1 if sum([overflow.get(i['id'], False)==False for i in val[0]]) else 0
                condB = 1 if sum([overflow.get(i['id'], False)==False for i in val[1]]) else 0
                if condA or condB:
                    # print(condA, condB)
                    # print(val)
                    balancing |= balancer(val, key)
                    # print('>', val)
                if key == debug_balance_id:
                    print(val)
                    print('31', [course_map[i['id']]['receive_0'] for i in val[0]])
                    print('32', [course_map[i['id']]['receive_0'] for i in val[1]])
                #     break
                    # for i in range(2):
                    #     if not overflow.get(val[i][3], False):
                    #         ext = max(0, val[i][1] - val[i][0])
                    #         balancing |= ext > 0
                    #         course_map[val[i][3]]["receive_0"] -= ext
                    #         course_map[val[(i + 1) % 2][3]]["receive_0"] += ext
        

        # break

        # score_offset += 1000000

        # if val[0] != 0 and val[1] != 0:
        #     if overflow.get(val[0][3]) or overflow.get(val[1][3]):
        #         print(val)
        #         print(overflow.get(val[0][3]), overflow.get(val[1][3]))
        #     if val[0][2] != val[1][2]:
        #         print(key, val)
        # if val[0][0] > val[0][1] and val[1][0] < val[1][1]:
        #     print(key, val)
        # if val[0][0] < val[0][1] and val[1][0] > val[1][1]:
        #     print(key, val)

        # debug in first round noly
        # if debug_mode:
        #     break

    # fuck = course_map["602cd9f0e8e0b19386dc011f"]
    # fuck = course_map["602cd9f0e8e0b19386dc0120"]
    # fuck = course_map["602cd9f0e8e0b19386dc0121"]
    # fuck = course_map["602cd9f0e8e0b19386dc0122"]
    # fuck = course_map["602cd9f0e8e0b19386dc0123"]
    # fuck = course_map["602cd9f0e8e0b19386dc0124"]
    # fuck = course_map["602cd9f0e8e0b19386dc0125"]
    # print(len(fuck["heap_0"]), fuck["receive_0"])

    if debug_mode:
        print(mark[debug_id])
        print(std_map[debug_id])
        print(enroll_map[debug_id])
        print(course_map[debug_course])
        # print(join_amount[course_map[debug_course]
        #                   ['university_id']+course_map[debug_course]['join_id']])

    # 602cd9f0e8e0b19386dc011f

    print(",".join(header))
    output_file = "chay-test.csv" if balance else "chay-test-no.csv"
    print(f"writed in {output_file}")
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
                if mark[i[id_order]][1] + 1 == p:
                    # pass this order
                    i[-1] = 9
                    # pp += 1 # for count
                elif mark[i[id_order]][1] + 1 > p:
                    # not pass at all
                    i[-1] = -2
                else:
                    # not pass but pass before
                    i[-1] = -3
            else:
                # not pass at all
                i[-1] = -2
            # print(','.join([str(j) for j in i]))

    if not debug_mode:
        # pass
        with open(output_file, "w") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(header)
            for i in accept_raw:
                csvwriter.writerow(i)
    # print(pp)
