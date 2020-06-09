# Foogle

The foogle is search engine with TF-IDF ranking written in [Python](https://www.python.org/).

## Requirements

  Install requirements:

    python -m pip install -r requirements.txt

## Usage

    python foogle.py --help

### Compile date base

  First you need do this:

    python foogle.py compile my_path
  Will create and fill in sqlite date base and needful files.

### Find files

    python foogle.py find "some text"
  Show what files contain phrases similar to _some text_.
  Work with set theory operations: _and_, _or_ and _not_ (or C-like syntax _&_, _|_ and _!_)

    python foogle.py find "!(Bob and Allice & Bacel) or def"
  Show file without 'Bob', 'Allice' and 'Bacel' and files with word 'def'

## Ranking

Use typical [TF-IDF](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) ranking. Where:

TF:

![ref](LATEXfiles/TF.gif)

<!-- $$F(t, p) ={|\{f\in S_\text{files}:g(t)=g(f)\And f = p\}|\over|\{d\in D\}|}.$$ -->
IDF:

![ref](LATEXfiles/IDF.gif)

![ref](LATEXfiles/comments.gif)

<!-- $$F_\text{inversed}(t) =\log_2{|\{f\in S_\text{files}\}|\over|\{d\in D: g(t)= g(d) \}|}. -->
<!-- .$$ -->
<!-- $$\text{Where } g\text{ returns it's file by term.}$$ -->

## Configuration file

```yaml
foogle:
  logging_file_name: mylog.log  
  types:
    - text*
    - application/j
  date_base_name: mydb.db
  extention_types:
    - .h
    - .sh
    - .doc
  general_path:
```

  Support types from mimetypes lib, watch [this](https://docs.python.org/2/library/mimetypes.html).
