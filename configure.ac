AC_INIT([bitsmasher-stargate], [0.2], [smoooth.y62wj@passmail.net])
AM_INIT_AUTOMAKE([-Wall -Werror foreign])

# Check for Python 3
AM_PATH_PYTHON([3.11])

# Verify shared filesystem mount point
AC_CHECK_FILE([/mnt/clusterfs], [], [AC_MSG_WARN([ClusterFS not detected. RCON payloads may fail.])])

AC_CONFIG_FILES([Makefile])
AC_OUTPUT
