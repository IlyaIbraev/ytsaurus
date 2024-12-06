PY3TEST()

SET(YT_SPLIT_FACTOR 45)

ENV(YT_TEST_FILTER=SMALL)

INCLUDE(../YaMakeDependsBoilerplate.txt)

IF (SANITIZER_TYPE)
    REQUIREMENTS(
        ram:34
        cpu:46
    )
ELSE()
    REQUIREMENTS(
        ram:12
        cpu:16
    )
ENDIF()

IF (OPENSOURCE)
    YT_SPEC(yt/yt/tests/integration/spec_opensource.yson)
    REQUIREMENTS(
        ram:20
        cpu:6
    )
    FORK_TESTS()
    SPLIT_FACTOR(12)
ENDIF()

END()

