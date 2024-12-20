#include "program.h"

#include "bootstrap.h"
#include "config.h"

#include <yt/yt/library/server_program/server_program.h>

#include <yt/yt/ytlib/program/native_singletons.h>

namespace NYT::NReplicatedTableTracker {

////////////////////////////////////////////////////////////////////////////////

class TReplicatedTableTrackerProgram
    : public TServerProgram<TReplicatedTableTrackerServerConfig>
{
public:
    TReplicatedTableTrackerProgram()
    {
        SetMainThreadName("RttMain");
    }

    void DoStart() final
    {
        auto config = GetConfig();

        ConfigureNativeSingletons(config);

        auto configNode = GetConfigNode();

        auto* bootstrap = CreateBootstrap(std::move(config), std::move(configNode)).release();
        bootstrap->Run();
    }
};

////////////////////////////////////////////////////////////////////////////////

void RunReplicatedTableTrackerProgram(int argc, const char** argv)
{
    TReplicatedTableTrackerProgram().Run(argc, argv);
}

////////////////////////////////////////////////////////////////////////////////

} // namespace NYT::NReplicatedTableTracker
