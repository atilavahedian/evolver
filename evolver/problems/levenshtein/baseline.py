def levenshtein(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    left = list(a)
    right = list(b)
    table = []
    for row_index in range(len(left) + 1):
        row = []
        for col_index in range(len(right) + 1):
            if row_index == 0:
                row.append(col_index)
            elif col_index == 0:
                row.append(row_index)
            else:
                row.append(0)
        table.append(row)
    for row_index in range(1, len(left) + 1):
        for col_index in range(1, len(right) + 1):
            delete = table[row_index - 1][col_index] + 1
            insert = table[row_index][col_index - 1] + 1
            replace = table[row_index - 1][col_index - 1] + (
                left[row_index - 1] != right[col_index - 1]
            )
            table[row_index][col_index] = min(delete, insert, replace)
    return table[len(left)][len(right)]
