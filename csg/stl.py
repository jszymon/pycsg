
# remove for Python >= 3.7
class _contextlib_nullcontext(object):
    """Context manager that does no additional processing.
    Used as a stand-in for a normal context manager, when a particular
    block of code is only sometimes used with a normal context manager:
    cm = optional_cm if condition else nullcontext()
    with cm:
        # Perform operation, using optional_cm if condition is True
    """

    def __init__(self, enter_result=None):
        self.enter_result = enter_result

    def __enter__(self):
        return self.enter_result

    def __exit__(self, *excinfo):
        pass

def _numbered_line_reader(f):
    for li, l in enumerate(f):
        yield li+1, l.strip()

def _match_line(f, match):
    for li, l in f:
        if li != "": break
    else:
        raise RuntimeError("Unexpected end of file, expected " + str(match))
    if l != match:
        raise RuntimeError("Expected " + str(match) + " on line " + str(li))
def _parse_vector(f, match, raise_on_nonmatch=True):
    for li, l in f:
        if li != "": break
    else:
        if raise_on_nonmatch:
            raise RuntimeError("Unexpected end of file, expected " + str(match))
        return None, li, l
    if not l.startswith(match):
        if raise_on_nonmatch:
            raise RuntimeError("Expected '" + str(match) + "' on line " + str(li))
        return None, li, l
    toks = l[len(match):].strip().split()
    if len(toks) != 3:
        raise RuntimeError("A vector must have exactly 3 coordinates"
                               " (line " + str(li) + ")")
    vec = [float(x) for x in toks]
    return vec, li, l

def read_ascii_stl(fname):
    if hasattr(fname, 'read'):
        f_ctx = _contextlib_nullcontext(filename)
    else:
        f_ctx = open(fname, 'r')
    with f_ctx as fl:
        f = _numbered_line_reader(fl)
        li, header = next(f)
        if header[0:6].lower() != "solid ":
            raise RuntimeError("Wrong ASCII STL header")
        name = header[6:].strip()
        print("read stl", name)
        while True:
            normal, li, l = _parse_vector(f, "facet normal",
                                              raise_on_nonmatch=False)
            if normal is None and l.startswith("endsolid"):
                if name != l[9:]:
                    print("Warning: different names in 'solid'"
                                           " and 'endsolid'")
                break
            _match_line(f, "outer loop")
            v1, li, l = _parse_vector(f, "vertex")
            v2, li, l = _parse_vector(f, "vertex")
            v3, li, l = _parse_vector(f, "vertex")
            _match_line(f, "endloop")
            _match_line(f, "endfacet")
            print("facet")
            print("  normal", normal)
            print("  v1", v1)
            print("  v2", v2)
            print("  v3", v3)
        else:
            raise RuntimeError("Missing 'endsolid'")
        for li, l in f:
            if l != "":
                raise RuntimeError("Content after 'endsolid'")

