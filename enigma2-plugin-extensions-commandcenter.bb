SUMMARY = "CommandCenter by Lululla"
MAINTAINER = "Lululla"
SECTION = "base"
PRIORITY = "required"
LICENSE = "CLOSED"

inherit gitpkgv allarch

SRCREV = "${AUTOREV}"
PV = "1.0+git${SRCPV}"
PKGV = "1.0+git${GITPKGV}"
VER ="1.0"
PR = "r0"

SRC_URI = "git://github.com/OwnerPlugins/CommandCenter.git;protocol=https;branch=main"

S = "${WORKDIR}/git"

do_install() {
    install -d ${D}${libdir}/enigma2/python/Plugins/Extensions/CommandCenter
    cp -r ${S}/usr/lib/enigma2/python/Plugins/Extensions/CommandCenter/* \
          ${D}${libdir}/enigma2/python/Plugins/Extensions/CommandCenter/
    
    # Copia eventuali file etc
    if [ -d ${S}/etc ]; then
        cp -rp ${S}/etc ${D}/
    fi
}

FILES:${PN} = " \
    ${libdir}/enigma2/python/Plugins/Extensions/CommandCenter \
    /etc/commandcenter_commands.json \
    /etc/enigma2/commandcenter_commands.json \
"
