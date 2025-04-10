###########################################################
# Note: 
# 1) You can modify -arch=sm_60 according to 
#    your GPU architecture.
# 2) For Windows systems, if you get errors like 
#    c1xx : fatal error C1083: Cannot open source file: ...
#    You can consider removing -Xcompiler "/wd 4819"
# 3) Add -DUSE_PLUMED to CFLAGS when use the PLUMED plugin
#    and remove it otherwise.
# 4) Add -DUSE_TABLE to speed up MD simulations with NEP
#    using pre-computed radial functions in the descriptors
###########################################################


###########################################################
# some flags
###########################################################
CC = nvcc
CUDA_ARCH=-arch=sm_86
ifdef OS # For Windows with the cl.exe compiler
CFLAGS = -O3 $(CUDA_ARCH)
else # For linux
CFLAGS = -std=c++17 -O3 $(CUDA_ARCH)
endif
INC = -I./
LDFLAGS = 
LIBS = -lcublas -lcusolver


###########################################################
# source files
###########################################################
# SOURCES_GPUMD =                   \
# 	$(wildcard main_gpumd/*.cu)   \
# 	$(wildcard minimize/*.cu)     \
# 	$(wildcard phonon/*.cu)       \
# 	$(wildcard integrate/*.cu)    \
# 	$(wildcard mc/*.cu)           \
# 	$(wildcard force/*.cu)        \
# 	$(wildcard measure/*.cu)      \
# 	$(wildcard model/*.cu)        \
# 	$(wildcard utilities/*.cu)
# SOURCES_NEP =                     \
# 	$(wildcard main_nep/*.cu)     \
# 	$(wildcard utilities/*.cu)
SOURCES_NEP_ADAM =                     \
	$(wildcard main_nep_adam/*.cu)     \
	$(wildcard utilities/*.cu)


###########################################################
# object files
###########################################################
ifdef OS # For Windows with the cl.exe compiler
OBJ_GPUMD = $(SOURCES_GPUMD:.cu=.obj)
OBJ_NEP = $(SOURCES_NEP:.cu=.obj)
OBJ_NEP_ADAM = $(SOURCES_NEP_ADAM:.cu=.obj)
else
# OBJ_GPUMD = $(SOURCES_GPUMD:.cu=.o)
# OBJ_NEP = $(SOURCES_NEP:.cu=.o)
OBJ_NEP_ADAM = $(SOURCES_NEP_ADAM:.cu=.o)
endif


###########################################################
# headers
###########################################################
HEADERS =                         \
	$(wildcard utilities/*.cuh)   \
	$(wildcard main_nep_adam/*.cuh)


###########################################################
# executables
###########################################################
all: nep_adam
# gpumd: $(OBJ_GPUMD)
# 	$(CC) $(LDFLAGS) $^ -o $@ $(LIBS)
# nep: $(OBJ_NEP)
# 	$(CC) $(LDFLAGS) $^ -o $@ $(LIBS)
nep_adam: $(OBJ_NEP_ADAM)
	$(CC) $(LDFLAGS) $^ -o $@ $(LIBS)


###########################################################
# rules for building object files
###########################################################
ifdef OS # for Windows
utilities/%.obj: utilities/%.cu $(HEADERS)
	$(CC) $(CFLAGS) $(INC) -c $< -o $@
main_nep_adam/%.obj: main_nep_adam/%.cu $(HEADERS)
	$(CC) $(CFLAGS) $(INC) -c $< -o $@
else # for Linux
# integrate/%.o: integrate/%.cu $(HEADERS)
# 	$(CC) $(CFLAGS) $(INC) -c $< -o $@
# mc/%.o: mc/%.cu $(HEADERS)
# 	$(CC) $(CFLAGS) $(INC) -c $< -o $@
# minimize/%.o: minimize/%.cu $(HEADERS)
# 	$(CC) $(CFLAGS) $(INC) -c $< -o $@
# force/%.o: force/%.cu $(HEADERS)
# 	$(CC) $(CFLAGS) $(INC) -c $< -o $@
# measure/%.o: measure/%.cu $(HEADERS)
# 	$(CC) $(CFLAGS) $(INC) -c $< -o $@
# main_gpumd/%.o: main_gpumd/%.cu $(HEADERS)
# 	$(CC) $(CFLAGS) $(INC) -c $< -o $@
utilities/%.o: utilities/%.cu $(HEADERS)
	$(CC) $(CFLAGS) $(INC) -c $< -o $@
# model/%.o: model/%.cu $(HEADERS)
# 	$(CC) $(CFLAGS) $(INC) -c $< -o $@
# phonon/%.o: phonon/%.cu $(HEADERS)
# 	$(CC) $(CFLAGS) $(INC) -c $< -o $@
# main_nep/%.o: main_nep/%.cu $(HEADERS)
# 	$(CC) $(CFLAGS) $(INC) -c $< -o $@
main_nep_adam/%.o: main_nep_adam/%.cu $(HEADERS)
	$(CC) $(CFLAGS) $(INC) -c $< -o $@
endif


###########################################################
# clean up
###########################################################
clean:
ifdef OS
	del /s *.obj *.exp *.lib *.exe
else
	rm -f */*.o nep_adam
endif

