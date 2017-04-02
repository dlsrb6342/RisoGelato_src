from myapp.models import Post, Tag, User, User2Channel
from myapp.views.import_module import TagSplitVerifier
from collections import defaultdict
from itertools import chain, combinations


def subsets(arr):
    """ Returns non empty subsets of arr"""
    return chain(*[combinations(arr, i + 1) for i, a in enumerate(arr)])


def item_with_min_support(item_list, transaction_list, min_support, freq_set):
    item_set = set()
    count_set = defaultdict(int)

    print("transaction list")
    print(transaction_list)
    for item in item_list:
        for transaction in transaction_list:
            if item.issubset(transaction):
                freq_set[item] += 1
                count_set[item] += 1

    for item, count in count_set.items():
        support = float(count) / len(transaction_list)

        if support >= min_support:
            item_set.add(item)

    return item_set

def join(_set, length):
    result = set()

    for item1 in _set:
        for item2 in _set:
            union = item1.union(item2)
            if len(union) == length:
                result.add(union)
    return result

def get_support(freq_set, item, length):
    return float(freq_set[item]) / length


def second(_tuple):
    i, j = _tuple
    return j


def runApriori(mode, min_support, min_confidence):
    '''
    item_set: set of tag/user names
    transaction_list: list of tag list for posts or follower list for channels
    freq_set: dictionary of (key: (set of) tag(user) names, value: support)
    large_set: dictionary of subset of size k whose elements satisfy min_support
    '''
    if mode == "tag":
        item_set, transaction_list = form_tag_data()
    elif mode == "follow":
        item_set, transaction_list = form_follow_data()

    freq_set = defaultdict(int)
    large_set = dict()

    current_set = item_with_min_support(item_set, transaction_list, min_support, freq_set)
    k = 2
    print("current set")
    print(current_set)
    while current_set != set([]) and k <= 4:
        large_set[k - 1] = current_set
        print("I'm in for k = " + str(k))
        current_set = join(current_set, k)
        print(str(k) + " join done!")
        current_set = item_with_min_support(current_set, transaction_list, min_support, freq_set)

        print(str(k) + " done!")
        k += 1
    print("111111--------11111111111-----------11111111111111------------11111111111----")

    items = []
    for key, value in large_set.items():
        items.extend([(tuple(item), get_support(freq_set, item, len(transaction_list)))
                      for item in value])

    print("22222222------------2222222222222222----------------2222222222222-----------")

    rules = []
    for key, value in large_set.items():
        for item in value:
            _subsets = map(frozenset, [x for x in subsets(item)])
            for subset in _subsets:
                diff = item.difference(subset)
                if len(diff) > 0:
                    confidence = get_support(freq_set, item, len(transaction_list)) / get_support(freq_set, subset, len(transaction_list))
                    if confidence >= min_confidence:
                        rules.append(((tuple(subset), tuple(diff)),
                                      confidence))

    rules = sorted(rules, key=second, reverse=True)

    return items, rules


def form_tag_data():
    posts = Post.objects.all()
    tags = Tag.objects.all()

    item_set = set()
    for tag in tags:
        item_set.add(frozenset([tag.name]))

    transaction_list = list()
    for post in posts:
        tag_list, valid = TagSplitVerifier(post.tag_string)
        record = frozenset(tag_list)
        transaction_list.append(record)

    print("data done!")
    return item_set, transaction_list


def form_follow_data():
    users = User.objects.all()

    item_set = set()
    transaction_list = list()
    for user in users:
        item_set.add(frozenset([user.username]))
        followings = User2Channel.objects.filter(user_id=user.id)
        following_list = list()
        for following in followings:
            username = following.channel.admin.username
            if username != user.username:
                following_list.append(username)
        record = frozenset(following_list)
        transaction_list.append(record)

    return item_set, transaction_list


def printresults(items, rules):
    def value(_tuple):
        i, j = _tuple
        return j

    for item, support in sorted(items, key=value):
        print ("item: %s, %.3f" %(str(item), support))
    print ("\n-----------------------RULES:")
    for rule, confidence in sorted(rules, key=value):
        pre, post = rule
        print ("Rule: %s ==> %s, %.3f" %(str(pre), str(post), confidence))


def recommend_tag():
    items, rules = runApriori("tag", min_support=0.01, min_confidence=0.3)
    print("Apriori done!")
    #printresults(items, rules)
    return (items, rules)

def recommend_follow():
    items, rules = runApriori("follow", min_support=0.01, min_confidence=0.1)

    def value(_tuple):
        return _tuple[1]

    items = sorted(items, key=value)
    return (items, rules)
