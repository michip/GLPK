if(APPLE)
  set(CMAKE_INSTALL_RPATH
    "@loader_path/../${CMAKE_INSTALL_LIBDIR};@loader_path")
elseif(UNIX)
  set(CMAKE_INSTALL_RPATH "$ORIGIN/../${CMAKE_INSTALL_LIBDIR}:$ORIGIN")
endif()

#add_executable(glpsol glpsol.c)
#target_compile_features(glpsol PRIVATE c_std_11)
#target_link_libraries(glpsol PRIVATE
#  ${PROJECT_NAMESPACE}::GLPK
#  $<$<NOT:$<C_COMPILER_ID:MSVC>>:m>)
#add_executable(${PROJECT_NAMESPACE}::glpsol ALIAS glpsol)

#install(TARGETS glpsol EXPORT ${PROJECT_NAME}Targets)

add_library(primalsimplex primalsimplex.c)
target_compile_features(primalsimplex PRIVATE c_std_11)
target_link_libraries(primalsimplex PRIVATE
        ${PROJECT_NAMESPACE}::GLPK
        $<$<NOT:$<C_COMPILER_ID:MSVC>>:m>)

add_executable(test_primal test_primal.c)
target_compile_features(test_primal PRIVATE c_std_11)
target_link_libraries(test_primal PRIVATE
        ${PROJECT_NAMESPACE}::GLPK
        $<$<NOT:$<C_COMPILER_ID:MSVC>>:m>)
add_executable(${PROJECT_NAMESPACE}::test_primal ALIAS test_primal)


