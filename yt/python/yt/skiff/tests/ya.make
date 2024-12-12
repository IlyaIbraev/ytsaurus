PY3TEST()

TEST_SRCS(
    test_skiff.py
)

TAG(
    ya:yt
)

PEERDIR(
    yt/python/yt/wrapper
    yt/yt/python/yt_yson_bindings
)

IF (OPENSOURCE)
    YT_SPEC(yt/yt/tests/integration/spec_opensource.yson)
    REQUIREMENTS(
        ram:20
        cpu:4
    )
    FORK_TESTS()
    SPLIT_FACTOR(1)
ENDIF()

END()
