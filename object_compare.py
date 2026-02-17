def compare_objects(before_labels, after_labels):

    before_set = set(before_labels)
    after_set = set(after_labels)

    removed = list(before_set - after_set)
    added = list(after_set - before_set)

    return added, removed
