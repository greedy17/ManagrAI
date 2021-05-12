import operator

# group_1 = [[[True, "OR"], [False, "AND"], [True, "OR"]], "OR"]
# group_2 = [[[True, "AND"], [False, "AND"], [True, "AND"]], "AND"]
# group_3 = [[[True, "AND"], [False, "AND"], [True, "OR"]], "OR"]

group_3 = [[True, "AND"], [False, "AND"], [True, "OR"]]
group_2 = [[True, "AND"], [False, "AND"], [True, "AND"]]
group_1 = [[True, "OR"], [False, "AND"], [True, "AND"]]


def test_fn(group, current_index, current_eval):
    group_length = len(group)
    current_conditional = f"__{group[current_index][1].lower()}__"
    if current_index == 0 and current_index == group_length - 1:
        return group[current_index][0]
    elif current_index == 0:
        # conditional does not matter for first item
        current_eval = group[0][0]
        return test_fn(group, current_index + 1, current_eval)
    else:
        __conditional = getattr(operator, current_conditional)
        current_eval = __conditional(current_eval, group[current_index][0])
        if current_index + 1 < group_length:
            return test_fn(group, current_index + 1, current_eval)
        return current_eval


if __name__ == "__main__":
    print(test_fn(group_3, 0, None))
    print(test_fn(group_2, 0, None))
    print(test_fn(group_1, 0, None))
