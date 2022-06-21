
# *********** Simple Settings for Changing the App's Behaviour ***************

# The following flag enables the print of the debug messages
# for the main operations
# WARNING: the nodes are going to print A LOT of debug messages due to
# their frequent periodic operations
DEBUG_MODE = False

# The following flag enables the hidden debugging menu
# This menu shows advanced options for understanding how the
# network is working
DEBUG_MENU_ENABLED = True

# The following setting specifies the max number of initialization retries
# for a node. It's here to prevent a loop in case a the most of the TCP
# ports are full
MAX_INITALIZATION_RETRIES = 10

# The following setting specifies the nodes periodic operations timeout
# A higher timeout is suggested if you're going to create a lot of nodes
# for reducing the TCP traffic
PERIODIC_OP_TIMEOUT = 2500