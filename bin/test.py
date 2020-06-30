#!/usr/bin/env python

import subprocess


def main():
    result = subprocess.run(["pwd"], capture_output=True)
    print(result)


if __name__ == "__main__":
    main()
