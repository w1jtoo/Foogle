from App.FoogleEngine.ReverceIndexBuilder import ReverceIndexBuilder


if __name__ == "__main__":

    import os
    from os.path import isfile, join

    print("Print Path name")
    path = input()
    files = [path + "\\" + f for f in os.listdir(path) if isfile(join(path, f))]
    print(files)
    b = ReverceIndexBuilder(files)
    print("Start base compile.")
    b.compile()
    print("Base already ready. \nPrint EXIT to Exit from the quering.")
    while 1:
        query = input()
        if query == "EXIT":
            break
        print(b.get_static_query(query))
