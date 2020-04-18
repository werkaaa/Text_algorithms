import time
import re
import string

pattern_length = 10**5

#naive approach
def naive(text, pattern):
    ans = []
    m = len(pattern)
    n = len(text)
    for i in range(n-m+1):
        if text[i:i+m] == pattern:
            ans.append(i)
    return ans

#automata approach
def repair_alphabet(alphabet, letter):
    if letter in alphabet:
        return letter

    return "any"

def transition_table(pattern):
    alphabet = set(pattern)
    #print(alphabet)
    result = []
    for q in range(0, len(pattern) + 1):
        result.append({})
        for a in alphabet:
            k = min(len(pattern) + 1, q + 2)
            while True:
                k = k - 1
                if re.search(f"{pattern[:k]}$", pattern[:q] + a):
                    break
            result[q][a] = k
        result[q]["any"] = 0
    return result

def cheating_delta(q, letter):
    if letter=='a' and q < pattern_length:
        return q+1
    if letter=='a' and q == pattern_length:
        return q
    return 0

def automata(text, pattern, delta, cheat = False):
    #print(delta)
    alphabet = set(pattern)
    ans = []
    q = 0
    m = len(pattern)
    n = len(text)
    for s in range(n):
        #print(repair_alphabet(alphabet, text[s]))
        if cheat:
            q = cheating_delta(q, repair_alphabet(alphabet, text[s]))
        else:
            q = delta[q][repair_alphabet(alphabet, text[s])]
        #print(q)
        l = pattern_length if cheat else len(delta) - 1
        if q == l:
            ans.append(s-m+1)
    return ans

#KMP approach
#lps[i] = the longest proper prefix of pattern[0..i] which is also a suffix of pattern[0..i]
#it's only about the pattern
def prefix_function(pattern):
    lps = [0]
    k = 0
    for q in range(1, len(pattern)):
        while k > 0 and pattern[k] != pattern[q]:
            k = lps[k-1]
        if pattern[k] == pattern[q]:
            k = k + 1
        lps.append(k)
    return lps

def kmp(text, pattern, lps):

    ans = []
    q = 0
    for i in range(len(text)):
        while q > 0 and pattern[q] != text[i]:
            q = lps[q-1]
        if pattern[q] == text[i]:
            q = q + 1
        if q == len(pattern):
            ans.append(i+1-q)
            q = lps[q-1]
    return ans

#test
def test_run_time(text, pattern, print_outputs, cheat=False):
    times = []
    outputs = []
    start_time = time.time()
    outputs.append(naive(text, pattern))
    end_time = time.time()
    times.append(end_time-start_time)
    print(f'Naive algorithm: {end_time-start_time}')

    if cheat:
        delta = []
    else:
        delta = transition_table(pattern)
    start_time = time.time()
    outputs.append(automata(text, pattern, delta, cheat=cheat))
    end_time = time.time()
    times.append(end_time-start_time)
    print(f'Automata algorithm: {end_time-start_time}')

    lps = prefix_function(pattern)
    start_time = time.time()
    outputs.append(kmp(text, pattern, lps))
    #kmp(text, pattern, lps)
    end_time = time.time()
    times.append(end_time-start_time)
    print(f'KMP algorithm: {end_time-start_time}')

    if print_outputs:
        print(f'{len(outputs[0])} {outputs[0][:10]}')
        print(f'{len(outputs[1])} {outputs[1][:10]}')
        print(f'{len(outputs[2])} {outputs[2][:10]}')
    return times

def test_generate_run_time(text, pattern, print_outputs):
    times = []
    outputs = []
    start_time = time.time()
    outputs.append(naive(text, pattern))
    end_time = time.time()
    times.append(end_time-start_time)
    print(f'Naive algorithm: {end_time-start_time}')

    start_time = time.time()
    delta = transition_table(pattern)
    outputs.append(automata(text, pattern, delta))
    end_time = time.time()
    times.append(end_time-start_time)
    print(f'Automata algorithm (with transition table generation): {end_time-start_time}')

    start_time = time.time()
    lps = prefix_function(pattern)
    outputs.append(kmp(text, pattern, lps))
    end_time = time.time()
    times.append(end_time-start_time)
    print(f'KMP algorithm (with prefix function generation): {end_time-start_time}')

    if print_outputs:
        print(f'{len(outputs[0])} {outputs[0][:10]}')
        print(f'{len(outputs[1])} {outputs[1][:10]}')
        print(f'{len(outputs[2])} {outputs[2][:10]}')
    return times

def test_generate_time(pattern):
    times = []

    start_time = time.time()
    delta = transition_table(pattern)
    end_time = time.time()
    times.append(end_time-start_time)
    print(f'Automata transition table generation: {end_time-start_time}')

    start_time = time.time()
    lps = prefix_function(pattern)
    end_time = time.time()
    times.append(end_time-start_time)
    print(f'KMP prefix function generation: {end_time-start_time}')

    return times

#1997_714
def find_art():
    with open('1997_714.txt') as data:
        text = data.read()
        test_generate_run_time(text, 'art', True)

#Wikipedia
def scan_wiki():
    with open('wiki.txt') as data:
        # Tried one line at a time approach but it lasted too long anyway
        # for line in data:
        #     time_line = test_run_time(line, 'Kruszwil', False)
        #     for i in range(3):
        #         time[i] += time_line[i]
        #     #output.append(output_line)
        text = data.read(10**8)
        test_generate_run_time(text.lower(), "kruszwil", True)



#KMP and automata 2xfaster
def example1():
    #pattern_length = 10**5
    pattern = "".join(["a" for i in range(pattern_length)])
    text = "".join(["a" for i in range(10**6)])
    test_run_time(text, pattern, True, cheat=True)

#KMP gen 2x faster than automata gen
def example2():
    pattern = "".join(string.ascii_lowercase for i in range(10))
    test_generate_time(pattern)


if __name__=='__main__':
    scan_wiki()
    find_art()
    example1()
    example2()



