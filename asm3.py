from asm1b_i import s_net
from asm2 import p_net

# Merge 2 net using add operator
m_net = s_net + p_net
m_net._places["wait"]._max_token = 10

if __name__ == "__main__":
    valid = False
    while not valid:
        valid = True
        choice = input("Please press '0' for setting default initial marking and '1' for manually setting initial marking: ")
        if choice == '1':
            print("please enter the number of tokens in places:", ", ".join([p for p in m_net._places]) , "respectively")
            print("Where max token of some places: [", ", ".join(["{0}.{1}".format(p[1]._max_token, p[0]) for p in m_net._places.items() if p[1]._max_token != -1]),"]")    
            m0 = [int(input().strip()) for _ in range(len(m_net._places))]
        elif choice == '0':
            m0 = [1, 0, 0, 4, 0, 1]
        else:
            print("Invalid Input!")
            valid = False
            
    m_net.set_markings(m0)
    m_net.detail_Print("Superismposed")
    m_net.run_debug("Superismposed", "asm3")