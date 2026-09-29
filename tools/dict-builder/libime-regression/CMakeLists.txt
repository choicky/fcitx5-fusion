cmake_minimum_required(VERSION 3.12)
project(moqi_libime_dictionary_regression LANGUAGES CXX)

find_package(LibIMEPinyin 1.1.16 CONFIG REQUIRED)

add_executable(libime_duplicate_value_regression duplicate_value_regression.cpp)
target_compile_features(libime_duplicate_value_regression PRIVATE cxx_std_20)
target_link_libraries(libime_duplicate_value_regression PRIVATE LibIME::Pinyin)

enable_testing()
add_test(NAME libime_duplicate_value_regression
         COMMAND libime_duplicate_value_regression)
