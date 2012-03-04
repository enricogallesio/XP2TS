all: xp2ts_plugin

clean: clean_xp2ts_plugin

##############################
#######  TARGET: XP2TS_plugin
##############################
TOP_xp2ts_plugin=./
WD_xp2ts_plugin=$(shell cd ${TOP_xp2ts_plugin};echo `pwd`)
cpp_SRC_xp2ts_plugin+=${WD_xp2ts_plugin}/xp2ts_plugin.cpp

OBJS_xp2ts_plugin+=$(cpp_SRC_xp2ts_plugin:.cpp=.cpp.o)

CFLAGS_xp2ts_plugin+= -iquote./\
 -iquoteSDK/CHeaders/XPLM\
 -iquoteSDK/CHeaders/Widgets\
 -iquote- -iquote/usr/include/\
  -DIBM=0 -DAPL=0 -DLIN=1

DBG=-g

CFLAGS_xp2ts_plugin+=-O0 -x c++ -ansi

clean_xp2ts_plugin:
	rm -f ${OBJS_xp2ts_plugin}
	rm -f xp2ts_plugin.cpp.d
	rm -f xp2ts_plugin.d

xp2ts_plugin:
	$(MAKE) -f xp2ts_plugin.mk xp2ts_plugin.xpl TARGET=xp2ts_plugin.xpl\
 CC="g++"  LD="g++"  AR="ar -crs"  SIZE="size" LIBS+="-lGL -lGLU"

xp2ts_plugin.xpl: ${OBJS_xp2ts_plugin}
	${CC} -shared ${LDFLAGS} -o xp2ts_plugin.xpl ${OBJS_xp2ts_plugin} ${LIBS}


ifeq (${TARGET}, xp2ts_plugin.xpl)

%.cpp.o: %.cpp
	gcc -c -fPIC ${CFLAGS_xp2ts_plugin} $< -o $@ -MMD
include $(cpp_SRC_xp2ts_plugin:.cpp=.d)

%.d: %.cpp
	set -e; $(CC) -M $(CFLAGS_xp2ts_plugin) $< \
 | sed 's!\($(*F)\)\.o[ :]*!$(*D)/\1.o $@ : !g' > $@; \
 [ -s $@ ] || rm -f $@

endif
# end Makefile
