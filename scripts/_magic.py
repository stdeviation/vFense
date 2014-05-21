import os
import sys

SRC_PATH = (
    os.path.realpath(
        os.path.join(
            os.path.dirname(
                os.path.realpath(__file__)
            ), '..', 'src'
        ),
    )
)
sys.path.insert(0, SRC_PATH)
print sys.path
