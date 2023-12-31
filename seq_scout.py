import datetime
import random
import copy
import pathlib

import math

from seqscout.utils import read_data, read_data_kosarak, read_data_TT, \
    sequence_mutable_to_immutable, read_data_lateralite_TT,  \
    read_data_sc2, k_length,  \
    compute_first_zero_mask, compute_last_ones_mask, \
    count_target_class_data, extract_items, compute_quality, compute_quality_vertical,  \
    sequence_immutable_to_mutable, encode_items, encode_data, \
    print_results_decode, read_jmlr, print_results, create_result

from seqscout.priorityset import PrioritySet, PrioritySetUCB
import seqscout.conf as conf

VERTICAL_TOOLS = {}
VERTICAL_RPZ = False


def filter_target_class(data, target_class):
    filter_data = []
    for line in data:
        if line[0] == target_class:
            filter_data.append(line)

    return filter_data


def get_itemset_memory(data):
    memory = set()
    for line in data:
        for itemset in line[1:]:
            memory.add(frozenset(itemset))
    return memory


def is_included(pattern, pattern_set):
    if pattern in pattern_set:
        return True
    else:
        for x in pattern_set:
            if pattern.issubset(x):
                return True
        return False


def compute_variations_better_quality(sequence, items, data, itemsets_memory, target_class, target_quality, enable_i=True, quality_measure=conf.QUALITY_MEASURE):
    '''
    Compute variations until quality increases
    :param sequence:
    :param items: the list of all possible items
    :return: the best new element (sequence, quality), or None if we are on a local optimum
    '''
    variations = []

    if VERTICAL_RPZ:
        bitset_slot_size = VERTICAL_TOOLS['bitset_slot_size']
        itemsets_bitsets = VERTICAL_TOOLS['itemsets_bitsets']
        class_data_count = VERTICAL_TOOLS['class_data_count']
        first_zero_mask = VERTICAL_TOOLS['first_zero_mask']
        last_ones_mask = VERTICAL_TOOLS['last_ones_mask']

    for itemset_i, itemset in enumerate(sequence):
        # i_extension
        if enable_i:
            for item_possible in items:
                new_variation_i_extension = copy.deepcopy(sequence)
                new_variation_i_extension[itemset_i].add(item_possible)

                # we check if created pattern is present in data before
                if is_included(new_variation_i_extension, itemsets_memory):
                    if VERTICAL_RPZ:
                        new_variation_i_quality, new_variation_i_bitset = compute_quality_vertical(data,
                                                                                                 new_variation_i_extension,
                                                                                                 target_class,
                                                                                                 bitset_slot_size,
                                                                                                 itemsets_bitsets,
                                                                                                 class_data_count,
                                                                                                 first_zero_mask,
                                                                                                 last_ones_mask,
                                                                                                 quality_measure=quality_measure)
                    else:
                        new_variation_i_quality = compute_quality(data, new_variation_i_extension, target_class)

                    variations.append(
                        (new_variation_i_extension, new_variation_i_quality))

                    if new_variation_i_quality > target_quality:
                        return variations[-1]

        # s_extension
        for item_possible in items:
            new_variation_s_extension = copy.deepcopy(sequence)
            new_variation_s_extension.insert(itemset_i, {item_possible})

            if VERTICAL_RPZ:
                new_variation_s_quality, new_variation_s_bitset = compute_quality_vertical(data,
                                                                                         new_variation_s_extension,
                                                                                         target_class,
                                                                                         bitset_slot_size,
                                                                                         itemsets_bitsets,
                                                                                         class_data_count,
                                                                                         first_zero_mask,
                                                                                         last_ones_mask,
                                                                                         quality_measure=quality_measure)
            else:
                new_variation_s_quality = compute_quality(data,
                                                          new_variation_s_extension,
                                                          target_class)

            variations.append(
                (new_variation_s_extension, new_variation_s_quality))

            if new_variation_s_quality > target_quality:
                return variations[-1]

        for item_i, item in enumerate(itemset):
            new_variation_remove = copy.deepcopy(sequence)

            # we can switch this item, remove it or add it as s or i-extension

            if (k_length(sequence) > 1):
                new_variation_remove[itemset_i].remove(item)

                if len(new_variation_remove[itemset_i]) == 0:
                    new_variation_remove.pop(itemset_i)

                if VERTICAL_RPZ:
                    new_variation_remove_quality, new_variation_remove_bitset = compute_quality_vertical(data,
                                                                                                       new_variation_remove,
                                                                                                       target_class,
                                                                                                       bitset_slot_size,
                                                                                                       itemsets_bitsets,
                                                                                                       class_data_count,
                                                                                                       first_zero_mask,
                                                                                                       last_ones_mask,
                                                                                                       quality_measure=quality_measure)
                else:
                    new_variation_remove_quality = compute_quality(data,
                                                                   new_variation_remove,
                                                                   target_class)

                variations.append(
                    (new_variation_remove, new_variation_remove_quality))
                if new_variation_remove_quality > target_quality:
                    return variations[-1]

    # s_extension for last element
    for item_possible in items:
        new_variation_s_extension = copy.deepcopy(sequence)
        new_variation_s_extension.append({item_possible})

        if VERTICAL_RPZ:
            new_variation_s_quality, new_variation_s_bitset = compute_quality_vertical(data,
                                                                                     new_variation_s_extension,
                                                                                     target_class,
                                                                                     bitset_slot_size,
                                                                                     itemsets_bitsets,
                                                                                     class_data_count,
                                                                                     first_zero_mask,
                                                                                     last_ones_mask,
                                                                                     quality_measure=quality_measure)
        else:
            new_variation_s_quality = compute_quality(data,
                                                      new_variation_s_extension,
                                                      target_class)

        variations.append(
            (new_variation_s_extension, new_variation_s_quality))
        if new_variation_s_quality > target_quality:
            return variations[-1]

    return None


def generalize_sequence(sequence, data, target_class, quality_measure=conf.QUALITY_MEASURE):
    sequence = copy.deepcopy(sequence)
    # we remove z items randomly
    seq_items_nb = len([i for j_set in sequence for i in j_set])
    z = random.randint(0, seq_items_nb - 1)
    for _ in range(z):
        chosen_itemset_i = random.randint(0, len(sequence) - 1)
        chosen_itemset = sequence[chosen_itemset_i]

        chosen_itemset.remove(random.sample(chosen_itemset, 1)[0])

        if len(chosen_itemset) == 0:
            sequence.pop(chosen_itemset_i)

    # now we compute the Wracc
    if VERTICAL_RPZ:
        quality, _ = compute_quality_vertical(data, sequence, target_class,
                                            VERTICAL_TOOLS['bitset_slot_size'],
                                            VERTICAL_TOOLS['itemsets_bitsets'], VERTICAL_TOOLS['class_data_count'],
                                            VERTICAL_TOOLS['first_zero_mask'], VERTICAL_TOOLS['last_ones_mask'], quality_measure=quality_measure)
    else:
        quality = compute_quality(data, sequence, target_class)
    return sequence, quality


def UCB(score, Ni, N):
    # we choose C = 0.5
    return (score + 0.25) * 2 + 0.5 * math.sqrt(2 * math.log(N) / Ni)


def exploit_arm(pattern, quality, items, data, itemsets_memory, target_class, enable_i=True, quality_measure=conf.QUALITY_MEASURE):
    # we optimize until we find local optima
    # print("Optimize")
    while 'climbing hill':
        # we compute all possible variations
        try:

            pattern, quality = compute_variations_better_quality(pattern,
                                                                 items, data,
                                                                 itemsets_memory,
                                                                 target_class,
                                                                 quality,
                                                                 enable_i=enable_i,
                                                                 quality_measure=quality_measure)

        except TypeError:
            # print("Already a local optima")
            break
    return pattern, quality


def play_arm(sequence, data, target_class, quality_measure=conf.QUALITY_MEASURE):
    '''
    Select object, generalise
    :param sequence: immutable sequence to generalise
    :param data:
    :param data_target_class: elements of the data with target class
    :return:
    '''
    sequence = sequence_immutable_to_mutable(sequence)

    pattern, quality = generalize_sequence(sequence,
                                         data,
                                         target_class,
                                         quality_measure=quality_measure)

    return pattern, quality


def seq_scout(data, target_class, time_budget=conf.TIME_BUDGET, top_k=conf.TOP_K, enable_i=True, vertical=True,
              iterations_limit=conf.ITERATIONS_NUMBER, theta=conf.THETA, quality_measure=conf.QUALITY_MEASURE):
    items = extract_items(data)
    begin = datetime.datetime.utcnow()
    time_budget = datetime.timedelta(seconds=time_budget)

    data_target_class = filter_target_class(data, target_class)
    sorted_patterns = PrioritySet(k=top_k, theta=theta)
    UCB_scores = PrioritySetUCB()
    itemsets_memory = get_itemset_memory(data)

    # removing class
    bitset_slot_size = len(max(data, key=lambda x: len(x))) - 1

    global VERTICAL_RPZ
    VERTICAL_RPZ = vertical

    global VERTICAL_TOOLS
    VERTICAL_TOOLS = {
        "bitset_slot_size": bitset_slot_size,
        "first_zero_mask": compute_first_zero_mask(len(data), bitset_slot_size),
        "last_ones_mask": compute_last_ones_mask(len(data), bitset_slot_size),
        "class_data_count": count_target_class_data(data, target_class),
        "itemsets_bitsets": {}
    }

    N = 1

    # init: we add objects with the best ucb so that they are all played one time in the main procedure.
    # By putting a null N, we ensure the mean of the quality will be correct
    for sequence in data_target_class:
        sequence_i = sequence_mutable_to_immutable(sequence[1:])
        UCB_score = UCB(float("inf"), 1, N)
        UCB_scores.add(sequence_i, (UCB_score, 0, 0))

    # play with time budget
    while datetime.datetime.utcnow() - begin < time_budget and N < iterations_limit:
        # we take the best UCB
        _, Ni, mean_quality, sequence = UCB_scores.pop()

        pattern, quality = play_arm(sequence, data, target_class, quality_measure=quality_measure)
        pattern = sequence_mutable_to_immutable(pattern)
        sorted_patterns.add(pattern, quality)

        # we update scores
        updated_quality = (Ni * mean_quality + quality) / (Ni + 1)
        UCB_score = UCB(updated_quality, Ni + 1, N)
        UCB_scores.add(sequence, (UCB_score, Ni + 1, updated_quality))

        N += 1

    print("seqscout optimized iterations: {}".format(N))

    best_patterns = sorted_patterns.get_top_k_non_redundant(data, top_k)

    for pattern in best_patterns:
        pattern_mutable = sequence_immutable_to_mutable(pattern[1])
        optimized_pattern, optimized_quality = exploit_arm(pattern_mutable, pattern[0], items, data, itemsets_memory,
                                                         target_class, enable_i=enable_i, quality_measure=quality_measure)
        optimized_pattern = sequence_mutable_to_immutable(optimized_pattern)
        sorted_patterns.add(optimized_pattern, optimized_quality)



    return sorted_patterns.get_top_k_non_redundant(data, top_k)


def seq_scout_api(dataset=conf.DATA, time_budget=conf.TIME_BUDGET, top_k=conf.TOP_K):
    '''
    Launch seq_scout.
    This function is for the simplicity of the user, so that she does not needs to specify iterations number,
    which is here only for experiments.
    '''

    if dataset == 'splice':
        data = read_data(pathlib.Path(__file__).parent.parent / 'data/splice.data')
        target_class = 'EI'
        enable_i = False
    elif dataset == 'alsbu':
        data = read_data_kosarak(pathlib.Path(__file__).parent.parent / 'data/aslbu.data')
        target_class = '195'
        enable_i = False
    elif dataset == 'alsbu':
        data = read_data_kosarak(pathlib.Path(__file__).parent.parent / 'data/blocks.data')
        target_class = '7'
        enable_i = False
    elif dataset == 'context':
        data = read_data_kosarak(pathlib.Path(__file__).parent.parent / 'data/context.data')
        target_class = '4'
        enable_i = False
    elif dataset == 'sc2':
        data = read_data_sc2(pathlib.Path(__file__).parent.parent / 'data/sequences-TZ-45.txt')[:5000]
        target_class = '1'
        enable_i = True
    elif dataset == 'skating':
        data = read_data_kosarak(pathlib.Path(__file__).parent.parent / 'data/skating.data')
        target_class = '1'
        enable_i = False
    elif dataset == 'jmlr':
        data = read_jmlr('svm', pathlib.Path(__file__).parent.parent / 'data/jmlr/jmlr')
        target_class = '+'
        enable_i = False
    else:
        data = read_data(pathlib.Path(__file__).parent.parent / 'data/promoters.data')
        target_class = '+'
        enable_i = False

    class_present = False
    for sequence in data:
        if target_class == sequence[0]:
            class_present = True
            break

    if not class_present:
        raise ValueError('The target class does not appear in data')

    items = extract_items(data)
    items, items_to_encoding, encoding_to_items = encode_items(items)
    data = encode_data(data, items_to_encoding)

    results = seq_scout(data, target_class, top_k=top_k, vertical=False, time_budget=time_budget, iterations_limit=10000000000000, enable_i=enable_i)

    print_results_decode(results, encoding_to_items)
    return results


def launch():
    #DATA = read_data_sc2('sequences-TZ-45.txt')[:500]
    #DATA = reduce_k_length(10, DATA)
    # DATA = read_data_kosarak('../data/blocks.data')
    # DATA = read_data_kosarak('../data/skating.data')
    # DATA = read_data_kosarak('../data/context.data')
    # DATA = read_data(pathlib.Path(__file__).parent.parent / 'data/promoters.data')
    # DATA = read_jmlr('machin', pathlib.Path(__file__).parent.parent / 'data/jmlr/jmlr')
    DATA = read_data_TT('SeqScoutData.txt',serveur='FLORE')
    #DATA = read_data_lateralite_TT('SeqScoutDataLateralite.txt',serveur='FLORE')

    #ITEMS = extract_items(DATA)
    #ITEMS, items_to_encoding, encoding_to_items = encode_items(ITEMS)
    #DATA = encode_data(DATA, items_to_encoding)

    results = seq_scout(DATA, 'FLORE', time_budget=10000, top_k=5, enable_i=False, vertical=False, iterations_limit=100000)

    #results = seq_scout_api(DATA, '+', 10, 5)
    return results
    #print_results_decode(results, encodi   ng_to_items)


if __name__ == '__main__':
    res=launch()
    #print_results(res)
    create_result(res,'test.csv')
    