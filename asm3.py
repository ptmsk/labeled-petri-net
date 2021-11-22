from asm1b_i import s_net
from asm2 import p_net

# Merge 2 net using add operator
m_net = s_net + p_net

if __name__ == "__main__":  
    m_net._places["wait"]._max_token = 10
    
    print("Initial marking: [", ", ".join(["{0}.{1}".format(p[1]._max_token, p[0]) for p in m_net._places.items()]), "]")
    s_net.detail_Print("Special")
    p_net.detail_Print("Patient")
    m_net.detail_Print("Superismposed")