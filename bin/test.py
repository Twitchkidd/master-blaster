#!/usr/bin/env python

import subprocess


def main():
    result = subprocess.run(["git", "branch"], universal_newlines=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(type(result.stdout))
    print(result.stderr)
    print(result.returncode)


if __name__ == "__main__":
    main()
