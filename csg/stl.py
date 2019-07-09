
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
        yield li, l.strip()

def _match_line(f, match):
    for li, l in f:
        if li != "": break
    else:
        raise RuntimeError("Unexpected end of file, expected " + str(match))
    if l != match:
        raise RuntimeError("Expected " + str(match) + " on line " + str(li))

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
            li, l = next(f)
            if l == "":
                continue
            if l.startswith("endsolid"):
                if name != l[9:]:
                    print("Warning: different names in 'solid'"
                                           " and 'endsolid'")
                break
            if not l.startswith("facet normal "):
                raise RuntimeError("Facet should start with 'facet normal'")
            toks = l.split()
            if len(toks) != 5:
                raise RuntimeError("Wrong facet normal format")
            normal = [float(ni) for ni in toks[2:]]
            print("normal", normal)
            _match_line(f, "outer loop")
        else:
            raise RuntimeError("Missing 'endsolid'")
        for li, l in f:
            if l != "":
                raise RuntimeError("Content after 'endsolid'")

