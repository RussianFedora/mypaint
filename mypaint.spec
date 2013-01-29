%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:           mypaint
Version:        1.1.0
Release:        2%{?dist}
Summary:        A fast and easy graphics application for digital painters

Group:          Applications/Multimedia
# MyPaint is GPLv2+, brush library LGPLv2+
# Ramon and CD_concept brushes are CC-BY
License:        GPLv2+ and LGPLv2+ and CC-BY
URL:            http://mypaint.intilinux.com/
Source0:        http://download.gna.org/mypaint/%{name}-%{version}.tar.bz2
Source1:        http://mypaintatelier.googlecode.com/files/ramon2.zip
# taken from http://mypaintatelier.googlecode.com/files/Concept%20Design.zip
# but koji doesn't like sources with a whitespace, so we rename it
Source2:        Concept_Design.zip
# don't allow a prefix of "/" and assum a prefix of "/usr" instead
# occurs with a usrmoved system
Patch0:         mypaint-1.0.0-usrmove.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python-devel, gtk2-devel, pygtk2-devel
BuildRequires:  numpy, scons, swig, protobuf-devel, lcms2-devel
BuildRequires:  desktop-file-utils, gettext, intltool, json-c-devel
Requires:       gtk2, numpy, pygtk2, python, protobuf-python
Requires:       %{name}-data = %{version}-%{release}

%description
MyPaint is a fast and easy graphics application for digital painters. It lets 
you focus on the art instead of the program. You work on your canvas with 
minimum distractions, bringing up the interface only when you need it.


%package        data
Summary:        Common data files for for %{name}
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description    data
The %{name}-data package contains common data files for %{name}.


%package devel
Summary:        Static library and header files for the %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}


%description devel
The %{name}-devel package contains API documentation for
developing %{name}.


%prep
%setup -q
%patch0 -p1

# Ramon2 brushes
unzip %{SOURCE1} -x order.conf -d brushes
unzip -p %{SOURCE1} order.conf >> brushes/order.conf
mv brushes/readme.txt README.Ramon2

# Concept Design brushes
unzip %{SOURCE2} -x order.conf -d brushes
unzip -p %{SOURCE2} order.conf >> brushes/order.conf
mv brushes/readme.txt README.CD_concept

# the Options class is deprecated; use the Variables class instead
sed -i 's|PathOption|PathVariable|g' SConstruct
sed -i 's|Options|Variables|g' SConstruct
# for 64 bit
sed -i 's|lib/mypaint|%{_lib}/mypaint|g' SConstruct SConscript mypaint.py
sed -i 's|/lib/|/%{_lib}/|g' brushlib/SConscript
sed -i "s|'lib'|'%{_lib}'|g" brushlib/SConscript
# fix menu icon
sed -i 's|mypaint_48|mypaint|g' desktop/%{name}.desktop


%build
export CFLAGS="$RPM_OPT_FLAGS"
export CXXFLAGS="$RPM_OPT_FLAGS"
scons prefix=%{_prefix} %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
scons prefix=$RPM_BUILD_ROOT%{_prefix} install

desktop-file-install --vendor="fedora" \
  --delete-original \
  --remove-key="Encoding" \
  --dir=${RPM_BUILD_ROOT}%{_datadir}/applications \
   $RPM_BUILD_ROOT%{_datadir}/applications/%{name}.desktop

find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'

%find_lang %{name}
%find_lang libmypaint

sed s,"%{buildroot}",,g -i %{buildroot}%{_libdir}/pkgconfig/libmypaint.pc


%clean
rm -rf $RPM_BUILD_ROOT


%post
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
update-desktop-database &> /dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi
update-desktop-database &> /dev/null || :


%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%files -f %{name}.lang
%defattr(-,root,root,-)
%doc changelog COPYING LICENSE README README.CD_concept README.Ramon2 doc/
%{_bindir}/%{name}
%dir %{_libdir}/mypaint/
%{_libdir}/mypaint/_mypaintlib.so
%dir %{_datadir}/%{name}/
%{_datadir}/%{name}/brushlib
%{_datadir}/%{name}/gui
%{_datadir}/%{name}/lib


%files data
%defattr(-,root,root,-)
%{_datadir}/%{name}/backgrounds
%{_datadir}/%{name}/brushes
%{_datadir}/%{name}/pixmaps
%{_datadir}/%{name}/palettes/
%{_datadir}/applications/fedora-%{name}.desktop
%{_datadir}/icons/hicolor/*/*/*


%files devel -f libmypaint.lang
%defattr(-,root,root,-)
%{_libdir}/pkgconfig/libmypaint.pc
%{_libdir}/*.a
%{_includedir}/*


%changelog
* Tue Jan 29 2013 Arkady L. Shane <ashejn@russianfedora.ru> - 1.1.0-2.R
- make data package

* Wed Jan 23 2013 Arkady L. Shane <ashejn@russianfedora.ru> - 1.1.0-1.R
- update to 1.1.0

* Fri Jan 04 2013 Christoph Wickert <cwickert@fedoraproject.org> - 1.0.0-5
- Rebuild against numpy 1.7 (fixes 4837925)

* Wed Sep 26 2012 Thomas Spura <tomspur@fedoraproject.org> - 1.0.0-4
- patch: assume a prefix of /usr instead of / in a usrmoved system (fixes #797263)

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jan 10 2012 Christoph Wickert <cwickert@fedoraproject.org> - 1.0.0-2
- %%{_bindir}/mypaint is arch specific and belongs into base package (#773079)

* Tue Jan 10 2012 Christoph Wickert <cwickert@fedoraproject.org> - 1.0.0-1
- Update to 1.0.0
- Add brush sets Ramon2 and Concept Design

* Tue Dec 06 2011 Adam Jackson <ajax@redhat.com> - 0.9.1-2
- Rebuild for new libpng

* Sat Mar 05 2011 Christoph Wickert <cwickert@fedoraproject.org> - 0.9.1-1
- Update to 0.9.1

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Aug 11 2010 David Malcolm <dmalcolm@redhat.com> - 0.8.2-4
- recompiling .py files against Python 2.7 (rhbz#623339)

* Wed Jul 11 2010 Christoph Wickert <cwickert@fedoraproject.org> - 0.8.2-3
- Rebuild for Python 2.7 (#623339)
 
* Fri Apr 16 2010 Christoph Wickert <cwickert@fedoraproject.org> - 0.8-2-2
- Rebuild (fixes 583156)

* Mon Mar 01 2010 Christoph Wickert <cwickert@fedoraproject.org> - 0.8.2-1
- Update to 0.8.2

* Sun Feb 21 2010 Christoph Wickert <cwickert@fedoraproject.org> - 0.8.1-1
- Update to 0.8.1

* Fri Jan 29 2010 Christoph Wickert <cwickert@fedoraproject.org> - 0.8.0-1
- Update to 0.8.0

* Sat Nov 28 2009 Christoph Wickert <cwickert@fedoraproject.org> - 0.7.1-2
- Require numpy

* Wed Nov 25 2009 Christoph Wickert <cwickert@fedoraproject.org> - 0.7.1-1
- Update to 0.7.1
- Move private python modules to a private location
- Add scriptlets for gtk-update-icon-cache and update-desktop-database
- Fix License and Source0 tags

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.5.1-3
- Rebuild for Python 2.6

* Mon Nov 3 2008 Marc Wiriadisastra <marc@mwiriadi.id.au> - 0.5.1-2
- Add new website and download link
- Fix mydrawwidget location for F-10

* Sun Jul 27 2008 Marc Wiriadisastra <marc@mwiriadi.id.au> - 0.5.1-1
- New version

* Wed Feb 13 2008 Marc Wiriadisastra <marc@mwiriadi.id.au> - 0.5.0-7
- Rebuild for gcc4.3

* Mon Jan 21 2008 Marc Wiriadisastra <marc@mwiriadi.id.au> - 0.5.0-6
- Added python sitearch instead of site lib
- Removed sitelib declaration

* Sat Jan 19 2008 Marc Wiriadisastra <marc@mwiriadi.id.au> - 0.5.0-5
- Moved static object around thanks parag

* Mon Jan 14 2008 Marc Wiriadisastra <marc@mwiriadi.id.au> - 0.5.0-4
- Fixed spec sheet

* Mon Jan 14 2008 Marc Wiriadisastra <marc@mwiriadi.id.au> - 0.5.0-3
- Add devel package
- Remove static libraries

* Mon Jan 14 2008 Marc Wiriadisastra <marc@mwiriadi.id.au> - 0.5.0-2
- Changed premissions on generate.py
- Removed static package

* Sun Jan 13 2008 Marc Wiriadisastra <marc@mwiriadi.id.au> - 0.5.0-1
- initial spec file with static libraries in static file
