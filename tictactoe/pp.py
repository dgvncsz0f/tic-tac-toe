
def pp_value (v):
    if v is None:
        return(" ")
    else:
        return(v)

def pp (state):
    out = []
    for i in range(3):
        r = []
        for j in range(3):
            r.append(pp_value(state[i * 3 + j]))
        out.append(" " + " | ".join(r))
        if (i < 2):
            out.append("-" + "-+-".join(["-" for _ in range(3)]) + "-")
    return("\n".join(out))
    
