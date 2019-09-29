import os
import re
import math

CLEANING_PATTERN = re.compile(r'[\W_]+')


class ReverceIndexBuilder(object):
    def __init__(self, _files):
        self.files = _files
        self.tf = {}
        self.df = {}
        self.idf = {}
        self.magnitudes = {}
        self.vectors = {}

    def idf_func(self, N, N_t):
        return math.log(N/N_t) if N_t != 0 else 0

    @property
    def size(self):
        return len(self.files)

    @property
    def index(self):
        if self._index:
            return self._index
        else:
            raise Exception("Compile first")

    def compile(self):
        self._index = self._full_index_build(
            self._make_indixes(
                self._builder_init()))

        self._inialize_stats()

    def _builder_init(self):
        # there is some optimization
        # so we can do it in 2o(nl) instead of 3o(nl)
        file_terms = {}
        for fname in self.files:
            with open(fname, 'r') as f:
                file_terms[fname] = f.read().lower()
            file_terms[fname] = CLEANING_PATTERN.sub(' ', file_terms[fname])
            re.sub(r'[\W_]+', '', file_terms[fname])
            file_terms[fname] = file_terms[fname].split()
        return file_terms

    def _single_index_build(self, terms):
        file_indexes = {}
        for index, word in enumerate(terms):
            if word in file_indexes.keys():
                file_indexes[word].append(index)
            else:
                file_indexes[word] = [index]
        return file_indexes

    def _make_indixes(self, terms):
        total = {}
        for filename in terms.keys():
            total[filename] = self._single_index_build(terms[filename])
        return total

    def _full_index_build(self, total):
        finall_index = {}
        for fname in total.keys():
            self.tf[fname] = {}
            for word in total[fname].keys():
                self.tf[fname][word] = len(total[fname][word])

                self.df[word] = self.df[word] + \
                    1 if word in self.df.keys() else 1

                if word in finall_index.keys():
                    if fname in finall_index[word].keys():
                        finall_index[word][fname].append(
                            total[fname][word][:])
                    else:
                        finall_index[word][fname] = total[fname][word]
                else:
                    finall_index[word] = {
                        fname: total[fname][word]}

                # MAKE VECTORS
                self.vectors[fname] = [len(total[fname][word])
                                       for word in total[fname].keys()]
                # MAKE MAGNITUDE
                self.magnitudes[fname] = pow(
                    sum(map(lambda x: x**2, self.vectors[fname])), .5)

        return finall_index

    def _inialize_stats(self):
        for fname in self.files:
            for term in self.index:
                self.tf[fname][term] = self._term_frequency(term, fname)
                if term in self.df.keys():
                    self.idf[term] = self.idf_func(
                        self.size, self.df[term])
                else:
                    self.idf[term] = 0
        return self.df, self.tf, self.idf


    def _term_frequency(self, term, fname):
        if term in self.tf[fname].keys():
            return self.tf[fname][term] / self.magnitudes[fname]
        else:
            return 0

    def get_static_query(self, string):
        pattern = re.compile(r'[\W_]+')
        string = pattern.sub(' ', string)
        lists, result = [], []
        for word in string.split():
            # make query for a single word
            if word in self.index.keys():
                # add rank
                lists.append(
                    [*self.index[word].keys()])
            else:
                lists.append([])

        # CAN BE FASTER
        setted = set(lists[0]).intersection(*lists)

        for filename in setted:
            temp_list = []
            for word in string.split():
                temp_list.append(self.index[word][filename][:])
            for i in range(len(temp_list)):
                for ind in range(len(temp_list[i])):
                    temp_list[i][ind] -= i
            if set(temp_list[0]).intersection(*temp_list):
                result.append(filename)
        return self._get_rank(result, string)

    def _term_total_freq(self, terms, query):
        temp = [0]*len(terms)
        for i, term in enumerate(terms):
            count = 0
            for word in query.split():
                if word == term:
                    count += 1
            temp[i] = count
        return temp

    def _make_vectors_for_query(self, fnames):
        vecs = {}
        for f in fnames:
            vdoc = [0]*len(self.index.keys())
            for ind, term in enumerate(self.index.keys()):
                vdoc[ind] = self.tf[f][term] * self.idf[term]
            vecs[f] = vdoc
        return vecs

    def _query_vecor(self, query):
        pattern = re.compile(r'[\W_]+')
        query = pattern.sub(' ', query)
        queryls = query.split()
        vquery = [0]*len(queryls)
        index = 0
        for _, word in enumerate(queryls):
            vquery[index] = self.queryFreq(word, query)
            index += 1
        queryidf = [self.idf[word] for word in self.index.keys()]
        magnitude = pow(sum(map(lambda x: x**2, vquery)), .5)
        freq = self._term_total_freq(self.index.keys(), query)
        tf = [x/magnitude for x in freq]
        final = [tf[i]*queryidf[i]
                 for i in range(len(self.index.keys()))]
        return final

    def queryFreq(self, term, query):
        count = 0
        for word in query.split():
            if word == term:
                count += 1
        return count


    def _product(self, doc1, doc2):
        if len(doc1) != len(doc2):
            return 0
        return sum([x*y for x, y in zip(doc1, doc2)])

    def _get_rank(self, result_files, query) -> list:
        vectors = self._make_vectors_for_query(result_files)
        # print(vectors)
        queryVec = self._query_vecor(query)
        # print(queryVec)
        results = [[self._product(vectors[result], queryVec), result]
                   for result in result_files]
        # print(results)
        results.sort(key=lambda x: x[0])
        # print(results)
        results = [x[1] for x in results]
        return results
