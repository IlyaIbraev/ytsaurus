#pragma once

#include <yt/yt/library/query/base/query_common.h>

namespace NYT::NQueryClient {

////////////////////////////////////////////////////////////////////////////////

struct TShufflePart
{
    TDataSource DataSource;
    std::vector<TRange<TRow>> Subranges;
};

////////////////////////////////////////////////////////////////////////////////

THashMap<TString, TShufflePart> Shuffle(
    const TShuffleNavigator& shuffleNavigator,
    TRange<TRow> rows,
    int prefixHint);

////////////////////////////////////////////////////////////////////////////////

} // namespace NYT::NQueryClient