from collections import deque
from english_words import english_words_set
import heapq
import phonenumbers
import pygtrie as trie


is_dictionary_trie_populated = False
DICTIONARY_TRIE = None


class Node(object):
    def __init__(self, wordified_so_far, index_so_far,
                 number_of_chars_in_word, max_len_substring,
                 max_continous_chars):
        self.wordified_so_far = wordified_so_far
        self.index_so_far = index_so_far
        self.number_of_chars_in_word = number_of_chars_in_word
        self.max_continous_chars = max_continous_chars
        self.max_len_substring = max_len_substring

    # Comparator functions:
    # Compare max length of substrings; max continuous chars; number of chars
    def __le__(self, other):
        return ((self.max_len_substring < other.max_len_substring) or
                ((self.max_len_substring == other.max_len_substring) and
                (self.max_continous_chars < other.max_continous_chars)) or
                ((self.max_len_substring == other.max_len_substring) and
                (self.max_continous_chars == other.max_continous_chars) and
                (self.number_of_chars_in_word < other.number_of_chars_in_word)))  # noqa: E501

    def __eq__(self, other):
        return ((self.max_len_substring == other.max_len_substring) and
                (self.max_continous_chars == other.max_continous_chars) and
                (self.number_of_chars_in_word == other.number_of_chars_in_word))  # noqa: E501

    def __gt__(self, other):
        return ((self.max_len_substring > other.max_len_substring) or
                ((self.max_len_substring == other.max_len_substring) and
                (self.max_continous_chars > other.max_continous_chars)) or
                ((self.max_len_substring == other.max_len_substring) and
                (self.max_continous_chars == other.max_continous_chars) and
                (self.number_of_chars_in_word > other.number_of_chars_in_word)))  # noqa: E501


def replace_string_with_char_at_index(str, index, char):
    # Strings are immutable in python, hence this function
    return str[:index] + char + str[index + 1:]


def populate_dictionary_trie():
    global is_dictionary_trie_populated
    global DICTIONARY_TRIE

    if is_dictionary_trie_populated and DICTIONARY_TRIE is not None:
        # To avoid re-populating the Trie
        return DICTIONARY_TRIE

    DICTIONARY_TRIE = trie.Trie()

    for word in english_words_set:
        if len(word) >= 3 and len(word) <= 10:
            DICTIONARY_TRIE[word.upper()] = True

    is_dictionary_trie_populated = True
    return DICTIONARY_TRIE


def find_char_prefix(word, index):
    """Returns substring of continuous chars in a word until given index

    Args:
        word (str): string of chars
        index (int): index in a word

    Returns:
        char_prefix (boolean): True/False

    """
    char_prefix = ""
    while index >= 0 and word[index].isalpha():
        char_prefix = word[index] + char_prefix
        index -= 1
    return char_prefix


def is_valid_word(char_prefix):
    """Checks if the given string is a valid word or contains valid substrings

    Args:
        word (str): string of chars

    Returns:
        is_valid (boolean): True/False

    """
    valid_word_substrings = find_valid_word_substrings(char_prefix)
    return len(valid_word_substrings) > 0


def find_valid_word_substrings(word):
    """Returns valid words present in a given string

    Args:
        word (str): string of chars

    Returns:
        all_substrings (list): all valid substrings in a word

    """
    global DICTIONARY_TRIE
    populate_dictionary_trie()

    if word in DICTIONARY_TRIE:
        return [word]
    # Some combination of continous words should exist
    for index, _ in enumerate(word):
        if word[:index + 1] in DICTIONARY_TRIE and \
                word[index + 1:] in DICTIONARY_TRIE:
            return [word[:index + 1], word[index + 1:]]

    return []


def is_valid_word_or_prefix(char_prefix):
    """Checks if a given string is a valid word or prefix

    Args:
        word (str): string of chars

    Returns:
        is_valid (boolean): True/False

    """
    global DICTIONARY_TRIE
    populate_dictionary_trie()

    if (char_prefix in DICTIONARY_TRIE or
            DICTIONARY_TRIE.has_subtrie(char_prefix)):
        return True
    # Some combination of continous words should exist
    for index, _ in enumerate(char_prefix):
        if char_prefix[:index + 1] in DICTIONARY_TRIE and \
                DICTIONARY_TRIE.has_subtrie(char_prefix[index + 1:]):
            return True
    return False


def find_all_substrings(word):
    """Returns substrings present in a given string

    Args:
        word (str): string of chars

    Returns:
        all_substrings (list): all substrings in a word

    """

    all_substrings = []
    substring = ""
    len_word = len(word)
    for index, char in enumerate(word):
        if char.isalpha():
            substring += char
            if index == len_word - 1 or not word[index + 1].isdigit():
                all_substrings.append(substring)
        else:
            substring = ""
    return all_substrings


def evaluate_word(word):
    """Check the validity of the word and the substrings

    Args:
        word (str): string of chars

    Returns:
        is_valid (boolean): validity of the word
        max_len_substring (int): maximum length of substring
        max_continous_chars (int): maximum number of continuous chars in a word

    """

    is_valid = True
    max_len_substring = 0
    max_continous_chars = 0

    all_valid_word_substrings = find_all_substrings(word)

    if len(all_valid_word_substrings) == 0:
        is_valid = False
    else:
        for substring in all_valid_word_substrings:
            max_continous_chars = max(len(substring), max_continous_chars)
            valid_word_substrings = find_valid_word_substrings(substring)
            for valid_substring in valid_word_substrings:
                max_len_substring = max(len(valid_substring),
                                        max_len_substring)

    return (is_valid, max_continous_chars, max_len_substring)


def _frame_words_from_number(number: str, max_results: int):
    """Frame words from number

       Uses Breadth First Search(BFS) and Priority Queue

    Args:
        number (str): string of numbers
        max_results (str): maximum number of words

    Returns:
        words_from_numbers_result (list): list of words from numbers

    """

    digit_to_chars = {
        '1': [],
        '2': ['A', 'B', 'C'],
        '3': ['D', 'E', 'F'],
        '4': ['G', 'H', 'I'],
        '5': ['J', 'K', 'L'],
        '6': ['M', 'N', 'O'],
        '7': ['P', 'Q', 'R', 'S'],
        '8': ['T', 'U', 'V'],
        '9': ['W', 'X', 'Y', 'Z'],
        '0': [],
    }
    number_of_digits = len(number)
    queue = deque([])
    queue.append(Node(number, 0, 0, 0, 0))
    priority_queue = []

    while(queue):
        current_node = queue.popleft()
        current_word = current_node.wordified_so_far
        current_index = current_node.index_so_far

        # If the search reached the end, then validate and push to heap
        if current_index == number_of_digits:
            (is_valid, max_continous_chars, max_len_substring) = \
                evaluate_word(current_word)
            if not is_valid:
                continue
            current_node.max_continous_chars = max_continous_chars
            current_node.max_len_substring = max_len_substring
            heapq.heappush(priority_queue, current_node)
            while len(priority_queue) > max_results:
                heapq.heappop(priority_queue)
            continue

        current_digit = number[current_index]
        current_number_of_chars_in_word = current_node.number_of_chars_in_word

        # Find partial words so far
        char_prefix = find_char_prefix(current_word, current_index - 1)
        len_char_prefix = len(char_prefix)

        for char in (digit_to_chars[current_digit] + [current_digit]):

            if ((char.isdigit() and (len_char_prefix == 0 or is_valid_word(char_prefix))) or  # noqa: E501
                    (char.isalpha() and (current_index != number_of_digits - 1 and is_valid_word_or_prefix(char_prefix+char))) or  # noqa: E501
                    (char.isalpha() and (current_index == number_of_digits - 1 and is_valid_word(char_prefix+char)))):  # noqa: E501

                next_word = replace_string_with_char_at_index(
                    current_word, current_index, char)
                next_number_of_chars_in_word = current_number_of_chars_in_word + (1 if char.isalpha() else 0)  # noqa: E501
                (is_valid, max_continous_chars, max_len_substring) = \
                    evaluate_word(next_word)

                queue.append(Node(next_word, current_index + 1,
                             next_number_of_chars_in_word, max_len_substring,
                             max_continous_chars))

    # Picking the first max_results largest from priority queue
    if len(priority_queue) > 0:
        words_from_numbers_result = []

        nlargest_ = heapq.nlargest(max_results, priority_queue)

        for wordified in nlargest_:
            words_from_numbers_result.append(wordified.wordified_so_far)
        print(words_from_numbers_result)
        return words_from_numbers_result[:max_results]
    else:
        return []


def generate(phone_number, max_results=5):
    """generate words from phone number

    Args:
        phone_number (str): string of numbers
        max_results (str): maximum number of words

    Returns:
        vanity_numbers (list): list of vanity numbers

    """

    populate_dictionary_trie()
    parsed_number = phonenumbers.parse(phone_number, None)
    country_code = parsed_number.country_code
    national_number = parsed_number.national_number
    words = _frame_words_from_number(str(national_number), max_results)
    vanity_numbers = [str(country_code) + '-' + word for word in words]
    return vanity_numbers
