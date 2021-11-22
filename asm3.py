from asm1b_i import s_net
from asm2 import p_net

# Merge 2 net using add operator
m_net = s_net + p_net
m_net._places["wait"]._max_token = 10

if __name__ == "__main__":  
    s_net.detail_Print("Special")
    p_net.detail_Print("Patient")
    m_net.detail_Print("Superismposed")