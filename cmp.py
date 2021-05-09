from heapq import heappush, heappop

def cmp(arr, rec, rec_type):
    # use heapq for better complexity than sort but more complex code
    # arr must be sorted or heap array // (asc)
    # arr is [(score, id)]

    pev = -99999999
    watchs = []

    while len(arr) and (len(arr) > rec or pev == arr[0][0]):
        watchs.append(heappop(arr))
        pev = watchs[-1][0]

    # cuz heappop watchs be asc list
    if rec_type == 'A':
        if len(arr) < rec:
            while watchs and watchs[-1][0] == pev:
                heappush(arr, watchs.pop())
    elif rec_type == 'B':
        pass
    else:
        # rec_type == 'CXX' // XX is number
        if len(arr) < rec:
            ext = int(rec_type[1:])
            dup = len([i for i in watchs if i[0]==pev])

            # print('debug', ext, dup, watchs)
            if len(arr)+dup <= rec+ext:
                while watchs and watchs[-1][0] == pev:
                    heappush(arr, watchs.pop())
    
    return watchs
