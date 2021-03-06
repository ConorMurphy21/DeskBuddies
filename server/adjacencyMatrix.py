import csv


class AdjacencyMatrix:
    FALSE_STRS = ['false', '', 'no', '0']

    def __init__(self, directory):
        self.directory = directory
        self.matrix = {}
        self.open_file()

    def write_to_csv(self, directory):
        with open(directory, "w+", encoding="utf-8-sig", newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', skipinitialspace=True)
            row1 = list(self.matrix.keys())
            row1.insert(0, '')
            writer.writerow(row1)

            for uid1 in self.matrix.keys():
                row = [uid1]
                for uid2 in self.matrix.keys():
                    row.append(self.matrix[uid1][uid2])

                writer.writerow(row)

    def open_file(self):
        with open(self.directory, "r", encoding="utf-8-sig") as csvfile:
            reader = csv.reader(csvfile, delimiter=',', skipinitialspace=True)
            row1 = next(reader)
            row1.remove('')
            for row in reader:
                i = 1
                self.matrix[row[0]] = {}
                for uids in row1:
                    self.matrix[row[0]][uids] = self._boolify(row[i])
                    i += 1
        if not self._is_valid(row1):
            raise ValueError

    def is_adjacent(self, a, b) -> bool:
        if a == b:
            return False
        return self.matrix[a][b] or self.matrix[b][a]

    def includes(self, uid) -> bool:
        row1 = list(self.matrix.keys())
        return uid in row1

    def _is_valid(self, row1) -> bool:
        if len(self.matrix) != len(row1):
            return False

        for uid in self.matrix:
            occur = row1.count(uid)
            if occur != 1:
                return False

        return True

    def _boolify(self, file_arg) -> bool:
        return file_arg.lower() not in self.FALSE_STRS

