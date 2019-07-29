def get_max_multiple(num, x):
    return int(num / 10) * 10

#0.32323232323
def get_up_bound_x(num, x):
    if int(num * pow(10,x)) / float(pow(10,x)) == num:
        return num
    res = int(num * pow(10,x)) / float(pow(10,x)) + 1 / float(pow(10,x))
    return round(res, x)
    # return int(num * (10 ^ x)) / (10 ^ x) + 0.000001

def get_down_bound_x(num, x):
    res =  int(num * pow(10,x)) / float(pow(10,x))
    return round(res, x)


