#calculate (a+bi)*(c+di) with 3 multiplications

def multiply(a,b,c,d):
    ac = a*c
    bd = b*d
    sum_product = (a+b)*(c+d)
    print(f"f{ac - bd} + {sum_product - (ac + bd)}i")


ac + ad + bc + bd