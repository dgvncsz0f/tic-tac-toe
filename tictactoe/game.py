
class TicTacToe (object):

    def __init__ (self, state=None):
        if state is None:
            state = [None for _ in range(9)]
        if len(state) != 9:
            raise ValueError("state size must be exactly 9!")
        for v in state:
            self.check_value_(v)
        self.state = state

    def dump (self):
        return(self.state)

    def play (self, row, col, value):
        self.check_value_(value)
        self.check_bounds_(row, col)
        if value not in self.next_turn():
            raise ValueError("bad move")
        ix = self.state[row * 3 + col]
        if ix is not None:
            raise ValueError("bad move")
        self.state[row * 3 + col] = value

    def get (self, row, col):
        return self.state[row * 3 + col]

    def winner (self):
        return self.check_rows_n_cols_() or self.check_diagonals_()

    def next_turn (self):
        stat = {'x': 0, 'o': 0, None: 0}
        for v in self.state:
            stat[v] = stat[v] + 1
        xcount = stat['x']
        ocount = stat['o']
        if xcount == (ocount - 1):
            return set(['x'])
        elif ocount == (xcount - 1):
            return set(['o'])
        elif xcount == ocount:
            return set(['o', 'x', None])
        else:
            raise ValueError("invalid state")

    def next_turn1 (self):
        turn = self.next_turn()
        user = turn.pop()
        if user is None:
            user = turn.pop()
        return user

    def check_rows_n_cols_ (self):
        for i in range(3):
            j = i * 3
            data = set(self.state[j : j + 3])
            if self.has_winner_(data):
                return data.pop()

            data = set([self.state[i], self.state[3 + i], self.state[6 + i]])
            if self.has_winner_(data):
                return data.pop()

    def check_diagonals_ (self):
        data = set([self.state[0], self.state[4], self.state[8]])
        if self.has_winner_(data):
            return data.pop()

        data = set([self.state[2], self.state[4], self.state[6]])
        if self.has_winner_(data):
            return data.pop()

    def check_bounds_ (self, r, c):
        if (r < 0 or r > 2):
            raise IndexError("invalid row index: %d" % (r,))
        if (c < 0 or c > 2):
            raise IndexError("invalid col index: %s" % (c,))

    def check_value_ (self, v):
        valid = set(['x', 'o', None])
        if v not in valid:
            raise ValueError("invalid value [%s] [valid is: %s]" % (v, repr(valid)))

    def has_winner_ (self, s):
        return len(s) == 1 and s != set([None])

if __name__ == "__main__":
    t = TicTacToe()
    assert t.winner() is None
    assert t.next_turn() == set(['x', 'o', None])

    for i in range(3):
        l = [None for _ in range(0, i * 3)]
        m = ['x' for _ in range(i * 3, i * 3 + 3)]
        r = [None for _ in range(i * 3 + 3, 9)]
        t = TicTacToe(l + m + r)
        assert t.winner() == 'x'

        t = TicTacToe(['x' if (j % 3 == i) else None for j in range(9)])
        assert t.winner() == 'x'

    t = TicTacToe(['x', None, None, None, 'x', None, None, None, 'x'])
    assert t.winner() == 'x'

    t = TicTacToe([None, None, 'x', None, 'x', None, 'x', None, None])
    assert t.winner() == 'x'
