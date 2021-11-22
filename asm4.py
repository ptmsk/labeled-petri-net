from asm3 import m_net

"""
Petri net m_net is the superimposed (merged) petri net
created by Specialist petri net and Patient petri net
"""

if __name__ == "__main__":
    print("please enter the token in place ", ", ".join(m_net._places.keys()), " respectively: ", sep="")
    token_num = [int(input().strip()) for _ in range(len(m_net._places))]

    m_net.set_markings(token_num)

    m_net.result_firing_one()