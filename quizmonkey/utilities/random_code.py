import random


class random_code:
    def __init__(self):
        self.code_set = set()
        self.start = 100000
        self.end = 999999
        self.size = self.end - self.start + 1

    def get_pin_code(self):
        while 1:
            r = random.randint(self.start, self.end)
            if r not in self.code_set:
                self.code_set.add(r)
                return r
            if len(self.code_set) >= self.size:
                self.start = self.end + 1
                self.end = self.start * 10 - 1
                self.size = self.end - self.start + 1


# Test function
# finished test on 100,000 size
if __name__ == "__main__":
    my_set = set()
    size = 0
    rc = random_code()
    while size < 1000000:
        r = rc.get_pin_code()
        if r not in my_set:
            my_set.add(r)
            size += 1
            # print(r)
        else:
            print('duplicate')
            print(r)
