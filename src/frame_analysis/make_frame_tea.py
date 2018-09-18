import pickle
import random
import sys

def main():
    frame_to_lex = pickle.load(open("./cache/russian_params.pickle", "rb"))
    frame_to_lex['Policy Prescription and Evaluation'].remove('и')

    frame_to_set_words = {}
    frame_to_draw_words = {}
    for f in frame_to_lex:
        if f == "Other":
            continue

        # randomly sample 100 words from frame.
        # 75 This gets turned into 10 sets of 5
        # the rest get used for other frames
        frame_words = random.sample(frame_to_lex[f], 105)
        frame_to_set_words[f] = frame_words[:75]

        frame_to_draw_words[f] = frame_words[75:]


    # randomly sample
    samples = []
    answers = []
    for f in frame_to_lex:
        if f == "Other":
            continue

        sets = frame_to_set_words[f]

        random.shuffle(sets)
        my_lex = frame_to_lex[f]

        # identify which frames we can draw from, we can't draw from ones that have
        # overlapping words
        frames_to_draw_intruder = []
        for f_sample in frame_to_lex:
            if f_sample == "Other":
                continue
            other_lex = frame_to_lex[f_sample]

            skip = False
            for word in other_lex:
                if word in my_lex:
                    skip = True
                    break
            if not skip:
                frames_to_draw_intruder += frame_to_draw_words[f_sample]

        random.shuffle(frames_to_draw_intruder)
        intruders = random.sample(frames_to_draw_intruder, 15)

        # Is it bad if we repeat intruder words?
        # I think so
        for word in intruders:
            for f2 in frame_to_draw_words:
                if word in frame_to_draw_words[f2]:
                    frame_to_draw_words[f2].remove(word)

        j = 0
        for i in range(0,75,5):
            final_set = sets[i:i+5] + [intruders[j]]
            random.shuffle(final_set)
            samples.append((f, final_set))
            answers.append(intruders[j])
            j += 1


    ordering = random.sample(range(0, len(samples)), len(samples))
    for o in ordering:
        print(samples[o][0], end=";")
        for word in samples[o][1]:
            print(word, end=";")
        print(answers[o])


if __name__ == "__main__":
    main()
