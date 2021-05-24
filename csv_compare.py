import sys
import csv


def load(file_name):
    tmp = []
    with open(file_name, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            tmp.append(row)
    return tmp


if __name__ == "__main__":
    A = load(sys.argv[1])
    B = load(sys.argv[2])

    i, d = 1, 0
    for a, b in zip(A, B):
        for key in a:
            if key == "sorting_result" and a[key] != b[key]:
                print(
                    f"diff in line: {i}, key: '{key}'",
                    a[key],
                    b[key],
                    b["id"],
                    b["citizen_id"],
                    b["round_id"],
                )
                d += 1
        i += 1

    print(f"total diff {d}")
    print("done")
