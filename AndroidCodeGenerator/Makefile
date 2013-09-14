DOCTEST2 = python -m doctest
DOCTEST3 = python3 -m doctest

SRC = $(wildcard *.py)

doctests: doctest2 doctest3

doctest3: $(SRC)
	$(DOCTEST3) $^

doctest2: $(SRC)
	$(DOCTEST2) $^
