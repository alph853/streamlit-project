import streamlit as st
import numpy as np


def levenshtein_distance(source: str, target: str):
    M, N = len(source) + 1, len(target) + 1
    D = np.zeros(shape=(M, N), dtype=[('dist', int), ('parent', (int, 2))])

    # init first row and column for 'dist' and 'parent'
    for i in range(M):
        D[i, 0] = i, (i-1, 0)
    for i in range(N):
        D[0, i] = i, (0, i-1)

    for i in range(1, M):
        for j in range(1, N):
            # [0]del, [1]ins, [2]sub
            cost = (1, 1, 0 if (source[i-1] == target[j-1]) else 1)
            parent_index = [(i-1, j), (i, j-1), (i-1, j-1)]

            list_of_changes = [
                (D[pIdx]['dist'] + c, pIdx) for pIdx, c in zip(parent_index, cost)
            ]

            D[i, j] = min(list_of_changes, key=lambda x: x[0])

    edits = []
    i, j = M-1, N-1

    while (i, j) != (0, 0):
        p = D[i, j]['parent'][0], D[i, j]['parent'][1]
        if p == (i-1, j):
            edits.append(f"delete '{source[i-1]}' at index {i-1}")
        elif p == (i, j-1):
            edits.append(f"insert '{target[j-1]}' at index {j-1}")
        elif p == (i-1, j-1) and source[i-1] != target[j-1]:
            edits.append(
                f"substitute '{source[i-1]}' with '{target[j-1]}' at index {i-1}")
        i, j = p

    edits.reverse()
    return D[-1, -1]['dist'], edits


def load_vocab(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    words = sorted(set([line.strip().lower() for line in lines]))
    return words


VOCABS = load_vocab(file_path='./data/vocab.txt')


def add_to_vocab(new_word):
    global VOCABS
    new_word = new_word.lower()
    if new_word != '' and new_word not in VOCABS:
        st.success(f"Word '{new_word}' added to vocab.")
        VOCABS.append(new_word)
        VOCABS = sorted(set(VOCABS))
        with open('./data/vocab.txt', 'a') as f:
            f.write(f"\n{new_word}")
    else:
        st.warning(f"Word '{new_word}' is not valid.")


def main():
    st.title("Word Correction using Levenshtein Distance")
    word = st.text_input('Word:')

    with st.sidebar:
        st.title('Add more vocabs')
        new_word = st.text_input('New word:')
        if st.button("Add word"):
            add_to_vocab(new_word)

    if st.button("Compute"):
        leven_distances = {}
        for vocab in VOCABS:
            leven_distances[vocab] = levenshtein_distance(word, vocab)

        # sorted by distance
        sorted_distances = dict(
            sorted(leven_distances.items(), key=lambda item: item[1][0]))
        correct_word = list(sorted_distances.keys())[0]

        st.markdown(f'Correct word: ```{correct_word}```')
        st.markdown(f"Distance between <span style='color: cyan;'>{
                    word}</span> and available vocabs:", unsafe_allow_html=True)

        for vocab, (distance, edits) in sorted_distances.items():
            col1, col2 = st.columns([1, 3])
            col1.markdown(f"```{vocab}```")
            col1.write('')
            col2.write(f'{distance}')
            edits_str = '\n'.join(edits)

            if not edits_str:
                edits_str = "No edits needed."
            col2.markdown(f"```\n{edits_str}\n```")


if __name__ == "__main__":
    main()
