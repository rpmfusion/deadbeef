%global toolchain clang
%global optflags %optflags -Wno-unused-but-set-variable -Wno-unused-variable
%global build_cxxflags %build_cxxflags -std=c++11

# Git submodules
%global mp4p_commit        156195ccb635f016dc34b89425bfbecf046c90d4
%global mp4p_shortcommit   %(c=%{mp4p_commit}; echo ${c:0:7})

%global ddb_dsp_libretro_commit        b4d3db19566398603069d02eeacb3b06987a1b74
%global ddb_dsp_libretro_shortcommit   %(c=%{mp4p_commit}; echo ${c:0:7})

%global ddb_output_pw_commit        0b099d13ab0e89d9934aabdeb2872f0f66ea6960
%global ddb_output_pw_shortcommit   %(c=%{mp4p_commit}; echo ${c:0:7})

Name:           deadbeef
Version:        1.9.6
Release:        1%{?dist}
Summary:        An audio player for GNU/Linux

License:        GPL-2.0-or later AND LGPL-2.0-or-later and BSD and MIT AND Zlib
URL:            https://deadbeef.sourceforge.io/
Source0:        https://github.com/DeaDBeeF-Player/%{name}/archive/%{version}.tar.gz
Source1:        https://github.com/DeaDBeeF-Player/mp4p/archive/%{mp4p_commit}/mp4p-%{mp4p_shortcommit}.tar.gz
Source2:        https://github.com/DeaDBeeF-Player/ddb_dsp_libretro/archive/%{ddb_dsp_libretro_commit}/ddb_dsp_libretro-%{ddb_dsp_libretro_shortcommit}.tar.gz
Source3:        https://github.com/DeaDBeeF-Player/ddb_output_pw/archive/%{ddb_output_pw_commit}/ddb_output_pw-%{ddb_output_pw_shortcommit}.tar.gz

# Build for armv7hl failed
# https://github.com/DeaDBeeF-Player/deadbeef/issues/2538
ExcludeArch:    armv7hl

BuildRequires:  clang
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  ffmpeg-devel
BuildRequires:  pkgconfig(flac)
BuildRequires:  faad2-devel
BuildRequires:  pkgconfig(libmms)
BuildRequires:  intltool
BuildRequires:  gettext-devel
BuildRequires:  pkgconfig(libcddb)
BuildRequires:  pkgconfig(libcdio)
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(mad)
BuildRequires:  pkgconfig(libmpg123)
BuildRequires:  pkgconfig(samplerate)
BuildRequires:  pkgconfig(sndfile)
BuildRequires:  libtool
BuildRequires:  pkgconfig(vorbis)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(wavpack)
BuildRequires:  yasm-devel
BuildRequires:  bison
BuildRequires:  pkgconfig(imlib2)
BuildRequires:  pkgconfig(libzip)
BuildRequires:  pkgconfig(gtk+-3.0)
BuildRequires:  desktop-file-utils
BuildRequires:  pkgconfig(jansson)
BuildRequires:  pkgconfig(opusfile)
%ifnarch armv7hl
BuildRequires:  libdispatch-devel
%endif

Requires:       hicolor-icon-theme
Requires:       %{name}-plugins%{?_isa} = %{version}-%{release}

Recommends:     deadbeef-mpris2-plugin

%description
DeaDBeeF (as in 0xDEADBEEF) is an audio player for GNU/Linux systems with X11 
(though now it also runs in plain console without X, in FreeBSD, and in
OpenSolaris).


%package devel
Summary:    Static library and header files for the %{name}
Requires:   %{name}%{?_isa} = %{version}-%{release}


%description devel
The %{name}-devel package contains API documentation for
developing %{name}.

%package plugins
Summary:    Plugins for %{name}
Requires:   %{name}%{?_isa} = %{version}-%{release}

%description plugins
This package contains plugins for %{name}


%prep
%autosetup -p1
tar -xvf %{SOURCE1}
mv mp4p-%{mp4p_commit}/* external/mp4p

tar -xvf %{SOURCE2}
mv ddb_dsp_libretro-%{ddb_dsp_libretro_commit}/* external/ddb_dsp_libretro
sed -i 's|#include <stdint.h>||' external/ddb_dsp_libretro/sinc_resampler.h
sed -i "s|#pragma once|#pragma once\n#include <cstdint>|" external/ddb_dsp_libretro/sinc_resampler.h
sed -i "s|size_t|std::size_t|" external/ddb_dsp_libretro/sinc_resampler.h

tar -xvf %{SOURCE3}
mv ddb_output_pw-%{ddb_output_pw_commit}/* external/ddb_output_pw

# Remove exec permission from source files
find . \( -name '*.cpp' -or -name '*.hpp' -or -name '*.h' \) -and -executable -exec chmod -x {} \;

sed -i 's|Toggle Pause|Toggle-Pause|' deadbeef.desktop.in
for data in Play Pause Toggle-Pause Stop Next Prev
do
    sed -i "s|$data Shortcut Group|X-$data Shortcut Group|" deadbeef.desktop.in
done

%build
%if 0%{?fedora} && 0%{?fedora} > 35
export PKG_CONFIG_PATH="%{_libdir}/compat-ffmpeg4/pkgconfig"
%endif
./autogen.sh
%configure \
    --enable-ffmpeg --docdir=%{_defaultdocdir}/%{name}-%{version} \
    --disable-silent-rules \
    --disable-static \
    --disable-gtk2 \
%ifarch armv7hl ppc64le
    --disable-lfm \
    --disable-notify \
%else
    --enable-lfm \
%endif
    --enable-gtk3 \
    --disable-pulse \
    --enable-pipewire
%make_build


%install
%make_install
find %{buildroot} -name "*.la" -exec rm {} \;

install -Dpm0644 %{buildroot}%{_datadir}/icons/hicolor/24x24/apps/%{name}.png \
    %{buildroot}%{_datadir}/pixmaps/%{name}.png

sed -i -e "s!MP3!MP3;!" %{buildroot}%{_datadir}/applications/%{name}.desktop

%find_lang %{name}

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop


%files -f %{name}.lang
%doc README ChangeLog AUTHORS
%license COPYING
%{_defaultdocdir}/%{name}-%{version}
%{_bindir}/%{name}
%dir %{_libdir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/%{name}
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/icons/hicolor/*/apps/*


%files devel
%{_includedir}/%{name}

%files plugins
%{_libdir}/%{name}/convpresets
%{_libdir}/%{name}/*.so
%{_libdir}/%{name}/data68


%changelog
* Mon Nov 13 2023 Vasiliy N. Glazov <vascom2@gmail.com> - 1.9.6-1
- Update to 1.9.6

* Wed Nov 08 2023 Leigh Scott <leigh123linux@gmail.com> - 1.9.5-5
- Rebuild for new faad2 version

* Fri Aug 04 2023 Vasiliy N. Glazov <vascom2@gmail.com> - 1.9.5-4
- Fix Build for F39

* Tue Aug 01 2023 Vasiliy N. Glazov <vascom2@gmail.com> - 1.9.5-3
- Add mpris plugin to recommends

* Wed Mar 01 2023 Leigh Scott <leigh123linux@gmail.com> - 1.9.5-2
- Rebuild for new ffmpeg

* Mon Feb 20 2023 Vasiliy N. Glazov <vascom2@gmail.com> - 1.9.5-1
- Update to 1.9.5
- Switch to Pipewire

* Tue Dec 20 2022 Vasiliy N. Glazov <vascom2@gmail.com> - 1.9.4-1
- Update to 1.9.4

* Tue Nov 15 2022 Vasiliy N. Glazov <vascom2@gmail.com> - 1.9.3-1
- Update to 1.9.3

* Fri Oct 07 2022 Vasiliy N. Glazov <vascom2@gmail.com> - 1.9.2-1
- Update to 1.9.2

* Sun Aug 07 2022 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 1.9.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild and ffmpeg
  5.1

* Tue May 24 2022 Vasiliy N. Glazov <vascom2@gmail.com> - 1.9.1-1
- Update to 1.9.1

* Sat May 14 2022 Vasiliy N. Glazov <vascom2@gmail.com> - 1.9.0-1
- Update to 1.9.0

* Sat Mar 05 2022 Leigh Scott <leigh123linux@gmail.com> - 1.8.8-6
- Use compat-ffmpeg4 for f36+

* Fri Feb 25 2022 Vasiliy N. Glazov <vascom2@gmail.com> - 1.8.8-5
- Enable notifications

* Wed Feb 09 2022 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 1.8.8-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Thu Nov 11 2021 Leigh Scott <leigh123linux@gmail.com> - 1.8.8-3
- Rebuilt for new ffmpeg snapshot

* Thu Sep 23 2021 Vasiliy N. Glazov <vascom2@gmail.com> - 1.8.8-2
- Fix segfault 0 bytes stack allocation

* Thu Aug 05 2021 Vasiliy N. Glazov <vascom2@gmail.com> - 1.8.8-1
- Update to 1.8.8

* Mon Aug 02 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.8.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Tue Feb 23 2021 Vasiliy N. Glazov <vascom2@gmail.com> - 1.8.7-1
- Update to 1.8.7

* Wed Feb 03 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.8.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Thu Dec 31 2020 Leigh Scott <leigh123linux@gmail.com> - 1.8.4-3
- Rebuilt for new ffmpeg snapshot

* Mon Aug 17 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.8.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Sun Jul  5 2020 Vasiliy N. Glazov <vascom2@gmail.com> - 1.8.4-1
- Update to 1.8.4

* Fri Apr 10 2020 Leigh Scott <leigh123linux@gmail.com> - 1.8.3-2
- Rebuild for new libcdio version

* Tue Mar 24 2020 Vasiliy N. Glazov <vascom2@gmail.com> - 1.8.3-1
- Update to 1.8.3

* Tue Feb 04 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.8.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Fri Aug 09 2019 Vasiliy N. Glazov <vascom2@gmail.com> - 1.8.2-1
- Update to 1.8.2

* Wed Aug 07 2019 Leigh Scott <leigh123linux@gmail.com> - 1.8.1-2
- Rebuild for new ffmpeg version

* Fri Jun 28 2019 Vasiliy N. Glazov <vascom2@gmail.com> - 1.8.1-1
- Update to 1.8.1

* Mon Apr 08 2019 Vasiliy N. Glazov <vascom2@gmail.com> - 1.8.0-1
- Update to 1.8.0

* Mon Mar 04 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 0.7.3-0.2.20190209git373f556
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Feb 27 2019 Vasiliy N. Glazov <vascom2@gmail.com> - 0.7.3-0.1.20190209git373f556
- Update to latest git
- Enable LTO

* Thu Dec 27 2018 Vasiliy N. Glazov <vascom2@gmail.com> - 0.7.3-0.1.20181224git73f9722
- Update to latest git

* Tue Aug 14 2018 Vasiliy N. Glazov <vascom2@gmail.com> - 0.7.3-0.1.20180814git6d02b02
- Update to latest git

* Thu Jul 26 2018 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 0.7.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu May 10 2018 Vasiliy N. Glazov <vascom2@gmail.com> - 0.7.2-6
- Correct patches as in upstream

* Fri May 04 2018 Vasiliy N. Glazov <vascom2@gmail.com> - 0.7.2-5
- Rebuild with new ffmpeg

* Tue Feb 07 2017 Vasiliy N. Glazov <vascom2@gmail.com> - 0.7.2-4
- Remove unneeded scriptlet

* Tue Aug 16 2016 Vasiliy N. Glazov <vascom2@gmail.com> - 0.7.2-3
- Clean spec

* Tue Jun 14 2016 Arkady L. Shane <ashejn@russianfedora.pro> - 0.7.2-2.R
- rebuilt against new ffmpeg

* Thu Apr 28 2016 Vasiliy N. Glazov <vascom2@gmail.com> - 0.7.2-1.R
- Update to 0.7.2
- Add patch for desktop-file

* Wed Mar 16 2016 Vasiliy N. Glazov <vascom2@gmail.com> - 0.7.1-1.R
- Update to 0.7.1

* Tue Feb 02 2016 Vasiliy N. Glazov <vascom2@gmail.com> - 0.7.0-2.R
- Add Icon Cache scriptlets
- Add desktop-database scriptlets
- Add libmpg123 support

* Mon Feb 01 2016 Vasiliy N. Glazov <vascom2@gmail.com> - 0.7.0-1.R
- Update to 0.7.0

* Tue Nov 18 2014 Vasiliy N. Glazov <vascom2@gmail.com> - 0.6.2-3.R
- Bump rebuild for new ffmpeg

* Fri Oct 03 2014 Vasiliy N. Glazov <vascom2@gmail.com> - 0.6.2-2.R
- Bump rebuild for new cdio

* Thu Aug 07 2014 Vasiliy N. Glazov <vascom2@gmail.com> - 0.6.2-1.R
- update to 0.6.2

* Mon Feb 03 2014 Vasiliy N. Glazov <vascom2@gmail.com> - 0.6.1-1.R
- update to 0.6.1

* Tue Nov 26 2013 Vasiliy N. Glazov <vascom2@gmail.com> - 0.6.0-2.R
- correct FSF address and other errors and warnings

* Tue Nov 26 2013 Vasiliy N. Glazov <vascom2@gmail.com> - 0.6.0-1.R
- update to 0.6.0

* Wed Apr 03 2013 Vasiliy N. Glazov <vascom2@gmail.com> - 0.5.6-5.R
- bump release for update dependencies

* Tue Nov 06 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 0.5.6-4.R
- added documentation to help menu

* Fri Oct 26 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 0.5.6-3.R
- correct compile for >= F18

* Thu Oct 25 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 0.5.6-2.R
- added plugins artwork, ffmpeg, vfs_zip

* Tue Oct 23 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 0.5.6-1.R
- update to 0.5.6
- switch to GTK3

* Tue Sep 11 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 0.5.5-2.R
- add some BR

* Thu Jun 07 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 0.5.5-1.R
- update to 0.5.5

* Sat May 12 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 0.5.4-1.R
- update to 0.5.4
- enable SID plugin

* Wed Mar 28 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 0.5.2-2.R
- Added APE support

* Mon Mar 26 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 0.5.2-1.R
- update to 0.5.2

* Sun Feb  5 2012 Arkady L. Shane <ashejn@russianfedora.ru> - 0.5.1-4.R
- added conditions to build for EL6

* Tue Nov 22 2011 Vasiliy N. Glazov <vascom2@gmail.com> - 0.5.1-3.R
- Added description in russian language

* Mon Oct 31 2011 Vasiliy N. Glazov <vascom2@gmail.com> - 0.5.1-2.R
- Added patch to compile in F16

* Mon Jun  6 2011 Arkady L. Shane <ashejn@yandex-team.ru> - 0.5.1-1.R
- update to 0.5.1

* Mon May 16 2011 Arkady L. Shane <ashejn@yandex-team.ru> - 0.5.0-1.R
- update to 0.5.0
- added BR: libstdc++-static for fedora >= 14

* Tue Nov 16 2010 Arkady L. Shane <ashejn@yandex-team.ru> - 0.4.4-1
- update to 0.4.4

* Tue Nov  2 2010 Arkady L. Shane <ashejn@yandex-team.ru> - 0.4.3-1
- update to 0.4.3

* Mon Oct 18 2010 Arkady L. Shane <ashejn@yandex-team.ru> - 0.4.2-2
- install deadbeef.png to /usr/share/pixmaps

* Mon Oct 18 2010 Arkady L. Shane <ashejn@yandex-team.ru> - 0.4.2-1
- initial build for Fedora
