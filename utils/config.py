import os

JOERN_BASE = "/root/Downloads/joern"
JOERN_PARSE_NAME = "joern-parse"
JOERN_PARSE_RUN = os.path.join(JOERN_BASE, JOERN_PARSE_NAME)

RUN_ENV = {
    "PATH": "/usr/lib/jdk11/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local"
            "/games:/snap/bin:/usr/lib/go/bin "
}
