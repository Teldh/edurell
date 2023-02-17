from itertools import zip_longest, tee
from typing import Generator, Iterable

def _pairwise_linked_reversed(iterable,None_tail):
    curr_index = len(iterable)-1
    while curr_index > 0:
        yield iterable[curr_index], iterable[curr_index-1]
        curr_index -= 1
    if None_tail:
        yield iterable[0], None
    return

def pairwise_linked(iterable, None_tail=True,reversed=False) -> 'Generator[Iterable, Iterable or None]':
    '''
    Iterator over a list of elements
    Params
    ------
    None_tail : if True returns also the (last element, None) tuple
    reversed : if True elemens are returned in reverse order (sN, sN-1)->...->(s1,s0) and optionally also (s0,None)

    Returns
    --------
    An iterator of tuples
    
    '''
    if not reversed:
        a,b = tee(iterable)
        next(b,None)
        return zip_longest(a,b, fillvalue=None) if None_tail else zip(a,b)
    else: return _pairwise_linked_reversed(iterable,None_tail)


def pairwise(iterable,None_tail=True,reversed=False) -> 'Generator[Iterable, Iterable or None]':
    if not reversed:
        iterable = iter(iterable)
        while True:
            try: a = next(iterable)
            except StopIteration: return

            try: yield a,next(iterable)
            except StopIteration: 
                if None_tail: 
                    yield a, None 
                return
    else:
        curr_index = len(iterable)-1
        while curr_index > 1:
            yield iterable[curr_index], iterable[curr_index-1]
            curr_index -= 2
        if None_tail and curr_index == 0:
            yield iterable[0], None
        return