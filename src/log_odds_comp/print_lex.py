import pickle

frame_to_lex = pickle.load(open("../frame_analysis/cache/russian_params.pickle", "rb"))

for f in frame_to_lex:
    print (f)
    print (frame_to_lex[f])

