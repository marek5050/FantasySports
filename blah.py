def recurse( s):
    st = s.split(",", maxsplit=1)
    if len(st) > 1 and st[0][0] == '[':
        v = st[0][1:]
    else:
        v = st[0][0:]

    v = v.replace("]","").replace("[","")
    n = [int(v)]
    if len(st) > 1:
        r = recurse(st[1])
        if r != None:
            n.append(r)
    return n


def deserialize( s):
    """
    :type s: str
    :rtype: NestedInteger
    """
    return recurse(s)

print(deserialize("[123,[456,[789]]]"))