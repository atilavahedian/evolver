def has_pair_sum(values, target):
    for left in range(len(values)):
        for right in range(left + 1, len(values)):
            if values[left] + values[right] == target:
                return True
    return False
