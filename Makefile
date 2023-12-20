UI_PATH=ui
UI_SOURCES=$(wildcard $(UI_PATH)/*.ui)
UI_FILES=$(patsubst $(UI_PATH)/%.ui, $(UI_PATH)/ui_%.py, $(UI_SOURCES))

LANG_PATH=i18n
LANG_SOURCES=$(wildcard $(LANG_PATH)/*.ts)
LANG_FILES=$(patsubst $(LANG_PATH)/%.ts, $(LANG_PATH)/%.qm, $(LANG_SOURCES))

RES_PATH=.
RES_SOURCES=$(wildcard $(RES_PATH)/*.qrc)
RES_FILES=$(patsubst $(RES_PATH)/%.qrc, $(RES_PATH)/%_rc.py, $(RES_SOURCES))

PRO_PATH=.
PRO_FILES=$(wildcard $(PRO_PATH)/*.pro)

TS_PATH=i18n
TS_FILE_RU=$(TS_PATH)/simplereports_ru.ts
TS_FILE_PT=$(TS_PATH)/simplereports_pt.ts

ALL_FILES= ${RES_FILES} ${UI_FILES} ${LANG_FILES}

all: $(ALL_FILES)

ui: $(UI_FILES)

ts: $(PRO_FILES)
	pylupdate4 -verbose $<

lang: $(LANG_FILES)

compile_ts:
	lrelease $(TS_FILE_RU)
	lrelease $(TS_FILE_PT)

res: $(RES_FILES)

$(UI_FILES): $(UI_PATH)/ui_%.py: $(UI_PATH)/%.ui
	pyuic4 -o $@ $<

$(LANG_FILES): $(LANG_PATH)/%.qm: $(LANG_PATH)/%.ts
	lrelease $<

$(RES_FILES): $(RES_PATH)/%_rc.py: $(RES_PATH)/%.qrc
	pyrcc4 -o $@ $<

clean:
	rm -f $(ALL_FILES)
	find -name "*.pyc" -exec rm -f {} \;
	rm -f *.zip

zip:
	cd .. && rm -f *.zip && zip -r simplereports.zip simplereports -x \*.pyc \*.ts \*.qrc \*.pro \*~ \*.git\* \*Makefile*
	mv ../simplereports.zip .

package: compile_ts zip
	rm $(TS_PATH)/*.qm

upload:
	plugin_uploader.py simplereports.zip
