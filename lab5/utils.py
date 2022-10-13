def mod(a: int, b: int) -> int:
    return (a % b + b) % b

def get_succ(id, other_ids):
    """
    Find successor of 'id' in ring 'other_ids'.
    """

    gt_id = [other_id for other_id in other_ids if other_id > id]

    if len(gt_id) != 0:
        return min(gt_id)
    else:
        return min(other_ids)

def get_index_of_next_node(id, other_ids):
    """
    Find predecessor of 'id' in ring 'other_ids'.

    :returns: index of predecessor in 'other_ids'.
    """

    lt_id = [other_id for other_id in other_ids if other_id <= id]

    if len(lt_id) != 0:
        return other_ids.index(max(lt_id))
    else:
        return other_ids.index(max(other_ids))

def ring_between(left, num, right):
    """
    Calculate whether 'num' is in between 'left' and 'right' on a number ring.
    """
    if left < right:
        return left < num <= right
    elif left > right:
        return left < num or num <= right
    else:
        raise Exception("undefined")