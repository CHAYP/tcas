import unittest
from cmp import cmp

class TestCmp(unittest.TestCase):
    # A receive type test
    def test_A_normal(self):
        inp = [(100,'1'), (90,'2'), (80,'3')]
        inp.sort()
        self.assertCountEqual(cmp(inp, 3, 'A'), [])
    
    def test_A_kick(self):
        inp = [(100,'1'), (90,'2'), (80,'3'), (70,'4')]
        inp.sort()
        self.assertCountEqual(cmp(inp, 3, 'A'), [(70,'4')])
    
    def test_A_kick_extend(self):
        inp = [(100,'1'), (90,'2'), (80,'3'), (70,'4'), (60,'5')]
        inp.sort()
        self.assertCountEqual(cmp(inp, 3, 'A'), [(70,'4'), (60,'5')])

    def test_A_no_kick(self):
        inp = [(100,'1'), (90,'2'), (80,'3'), (80,'4'), (80,'5')]
        inp.sort()
        self.assertCountEqual(cmp(inp, 3, 'A'), [])

    # B receive type test
    def test_B_normal(self):
        inp = [(100,'1'), (90,'2'), (80,'3')]
        inp.sort()
        self.assertCountEqual(cmp(inp, 3, 'B'), [])

    def test_B_normal_2(self):
        inp = [(100,'1'), (90,'2')]
        inp.sort()
        self.assertCountEqual(cmp(inp, 3, 'B'), [])

    def test_B_kick(self):
        inp = [(100,'1'), (90,'2'), (80,'3'), (70,'4')]
        inp.sort()
        self.assertCountEqual(cmp(inp, 3, 'B'), [(70,'4')])

    def test_B_kick_extend(self):
        inp = [(100,'1'), (90,'2'), (80,'3'), (70,'4'), (60,'5')]
        inp.sort()
        self.assertCountEqual(cmp(inp, 3, 'B'), [(70,'4'), (60,'5')])
    
    def test_B_kick_extend_2(self):
        inp = [(100,'1'), (90,'2'), (80,'3'), (70,'4'), (70,'5')]
        inp.sort()
        self.assertCountEqual(cmp(inp, 3, 'B'), [(70,'4'), (70,'5')])

    def test_B_kick_in(self):
        inp = [(100,'1'), (90,'2'), (80,'3'), (80,'4'), (80,'5')]
        inp.sort()
        self.assertCountEqual(cmp(inp, 3, 'B'), [(80,'3'), (80,'4'), (80,'5')])
    
    def test_B_kick_in_all(self):
        inp = [(80,'1'), (80,'2'), (80,'3'), (80,'4')]
        inp.sort()
        self.assertCountEqual(cmp(inp, 3, 'B'), [(80,'1'), (80,'2'), (80,'3'), (80,'4')])

    # C receive type test
    def test_C2_normal(self):
        inp = [(100,'1'), (90,'2'), (80,'3')]
        inp.sort()
        self.assertCountEqual(cmp(inp, 3, 'C2'), [])

    def test_C2_kick(self):
        inp = [(100,'1'), (90,'2'), (80,'3'), (70,'4')]
        inp.sort()
        self.assertCountEqual(cmp(inp, 3, 'C2'), [(70,'4')])

    def test_C2_kick_2(self):
        inp = [(100,'1'), (90,'2'), (80,'3'), (70,'4'), (70,'5')]
        inp.sort()
        self.assertCountEqual(cmp(inp, 3, 'C2'), [(70,'4'), (70,'5')])

    def test_C2_kick_3(self):
        inp = [(100,'1'), (90,'2'), (80,'3'), (80,'4'), (70,'5')]
        inp.sort()
        self.assertCountEqual(cmp(inp, 3, 'C2'), [(70,'5')])

    def test_C2_no_kick(self):
        inp = [(100,'1'), (90,'2'), (80,'3'), (80,'4'), (80,'5')]
        inp.sort()
        self.assertCountEqual(cmp(inp, 3, 'C2'), [])

    def test_C2_kick_in(self):
        inp = [(100,'1'), (90,'2'), (80,'3'), (80,'4'), (80,'5'), (80,'6')]
        inp.sort()
        self.assertCountEqual(cmp(inp, 3, 'C2'), [(80,'3'), (80,'4'), (80,'5'), (80,'6')])


if __name__ == "__main__":
    unittest.main()