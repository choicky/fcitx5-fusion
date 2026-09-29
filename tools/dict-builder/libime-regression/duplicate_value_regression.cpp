/*
 * Runtime regression for the converter's official-negative-value policy.
 * This intentionally uses PinyinIME/PinyinContext, so lattice construction
 * and candidate deduplication run through the production decoder path.
 */
#include <cassert>
#include <cmath>
#include <iostream>
#include <memory>
#include <sstream>

#include "libime/core/userlanguagemodel.h"
#include "libime/pinyin/pinyincontext.h"
#include "libime/pinyin/pinyindictionary.h"
#include "libime/pinyin/pinyinime.h"

namespace {

float templateScore(float officialValue, float extraValue, bool includeExtra) {
    auto dict = std::make_unique<libime::PinyinDictionary>();
    auto model = std::make_unique<libime::UserLanguageModel>();
    libime::PinyinIME ime(std::move(dict), std::move(model));
    ime.setNBest(8);
    ime.setScoreFilter();

    std::stringstream official;
    official << "模板 mu'ban " << officialValue << '\n';
    ime.dict()->load(libime::PinyinDictionary::SystemDict, official,
                     libime::PinyinDictFormat::Text);

    if (includeExtra) {
        ime.dict()->addEmptyDict();
        std::stringstream extra;
        extra << "模板 mu'ban " << extraValue << '\n';
        // SystemDict is 0, UserDict is 1; the separately enabled extra path
        // is the next dictionary, index 2.
        ime.dict()->load(2, extra, libime::PinyinDictFormat::Text);
    }

    libime::PinyinContext context(&ime);
    context.type("muban");
    for (const auto &candidate : context.candidates()) {
        if (candidate.toString() == "模板" &&
            context.candidateFullPinyin(candidate) == "mu'ban") {
            return candidate.score();
        }
    }
    assert(false && "模板/mu'ban was not produced by the decoder");
    return 0.0F;
}

} // namespace

int main() {
    const float negativeOnly = templateScore(-1.248F, 0.0F, false);
    const float negativeWithZero = templateScore(-1.248F, 0.0F, true);
    // The zero-valued duplicate must be the surviving higher-scoring path.
    assert(negativeWithZero > negativeOnly);

    const float positiveOnly = templateScore(1.248F, 0.0F, false);
    const float positiveWithZero = templateScore(1.248F, 0.0F, true);
    // A positive official path must remain preferable to the third-party 0.
    assert(std::fabs(positiveWithZero - positiveOnly) < 1e-5F);

    std::cout << "negative candidate-only-score=" << negativeOnly
              << " candidate-with-zero-score=" << negativeWithZero
              << "\npositive candidate-only-score=" << positiveOnly
              << " candidate-with-zero-score=" << positiveWithZero << '\n';
    return 0;
}
