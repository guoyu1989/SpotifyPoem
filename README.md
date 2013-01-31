# Introduction
This is the project for separating a poem into small phrases and get the similar tracks from spotify to form a playlist

# references
[Sentence Similarity Based on Semantic Nets and Corpus Statistics]
(http://ants.iis.sinica.edu.tw/3BkMJ9lTeWXTSrrvNoKNFDxRm3zFwRR/55/Sentence%20Similarity%20Based%20on%20Semantic%20Nets%20and%20corpus%20statistics.pdf)

[Sentence Similarity Based on Semantic Nets and Corpus Statistics](http://ants.iis.sinica.edu.tw/3BkMJ9lTeWXTSrrvNoKNFDxRm3zFwRR/55/Sentence%20Similarity%20Based%20on%20Semantic%20Nets%20and%20corpus%20statistics.pdf)

# How to use it
python [-B] spotify_poesm_separator.py -m [levenshtein|naive|semantic] -t [number of threads] -n [number of tracks in the response playlist] search_query

### Example

python -B spotify_poem_separator.py -m naive -t 4 -n 15 'if i can't let it go out of my mind'
(This will run the program with 4 threads, naive phrase measurer and there will be at most 15 tracks in the response playlist, the search query is 'if i can't let it go out of my mind')

## Measurers
    semantic[Deprecated, DON'T USE IT NOW] : correspond to NLPPhraseSimMeasurer.py, it will use Part of Speech tag and WordNet's synset to compre two words', even two phrases' semantic similarity. It is much more slower than other twosince it need loading the words' synsets and POS tagging a sentence. Don't use it unless your search query is small enough (less than 6 words)
#### Example

    <red alcoholic drink, a bottle of wine> : 0.2758291
    <red alcoholic drink, fresh orange juice> : 0.108492

    levenshtein : Use the Levenshtein Distance (also referred as Edit Distance) to measure the similarity of two phrases, it only concern about identical words with identical positions
#### Example
    <happy friday, happy friday> : 1
    <happy friday, happy> : 0.5

    naive : Use the identical words to measure similarity of two phrases, but meanwhile take consideration of words' relative order. Good for comparing two phrases with same words but in different positions
#### Example
    <happy friday, friday happy> : 0.5
    <happy friday, happy wednesday> 0.35

## Result
the number of result tracks will be specified with input command line arguments. The response tracks will be sorted in descending order by their similarity

## Parallel
the number of threads can be specified with input command line argument, the recommended thread number is 4, which will speed up by double compared with single thread.

### multiprocessing
This version currently don't support multiprocessing, but I will definitely try multiprocessing after then.
