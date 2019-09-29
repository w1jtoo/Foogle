import re

CLEANING_PATTERN = re.compile(r'[\W_]+')


class ReverceIndexBuilder(object):
    def __init__(self, _files):
        self.files = _files

    @property
    def index(self):
        if self._index:
            return self._index
        else:
            raise Exception("Compile first")

    def compile(self):
        self._index = self.full_index_build(
            self.make_indixes(
                self.builder_init()))

    def builder_init(self):
        file_terms = {}
        for fname in self.files:
            with open(fname, 'r') as f:
                file_terms[fname] = f.read().lower()
            file_terms[fname] = CLEANING_PATTERN.sub(' ', file_terms[fname])
            re.sub(r'[\W_]+', '', file_terms[fname])
            file_terms[fname] = file_terms[fname].split()
        return file_terms

    def single_index_build(self, terms):
        file_indexes = {}
        for index, word in enumerate(terms):
            if word in file_indexes.keys():
                file_indexes[word].append(index)
            else:
                file_indexes[word] = [index]
        return file_indexes

    def make_indixes(self, terms):
        total = {}
        for filename in terms.keys():
            total[filename] = self.single_index_build(terms[filename])
        return total

    def full_index_build(self, total):
        total_index = {}
        for filename in total.keys():
            for word in total[filename].keys():
                if word in total_index.keys():
                    if filename in total_index[word].keys():
                        total_index[word][filename].extend(
                            total[filename][word][:])
                    else:
                        total_index[word][filename] = total[filename][word]
                else:
                    total_index[word] = {filename: total[filename][word]}
        return total_index
