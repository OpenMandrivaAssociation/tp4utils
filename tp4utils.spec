%define ver 1.0beta2
%define rel %mkrel 1
%define underversion %(echo %{version}|sed -e 's/\./_/g')

%define have_pre %(echo %ver|awk '{p=0} /[a-z,A-Z][a-z,A-Z]/ {p=1} {print p}')
%if %have_pre
%define pre_ver %(perl -e '$name="%ver"; print ($name =~ /(.*?)[a-z]/);')
%define pre_pre %(echo %ver|sed -e 's/%pre_ver//g')
%define underversion %(echo %{pre_ver}|sed -e 's/\\./_/g')
%endif


Name:		tp4utils
%if %have_pre
Version: %{pre_ver}
Release: 0.%{pre_pre}.%{rel}
%else
Version: %{ver}
Release: %{rel}
%endif
License:	GPL
Group:		System/Servers
Summary:	IBM Thinkpad Trackpoint daemon and utilities
URL:		http://www-hft.ee.tu-berlin.de/~strauman/tp4utils
Source:		%{name}_1_2%{?pre_ver:_%pre_pre}.tar.bz2
Source1:	%{name}.xinitd
Source2:	xtp4.sh
BuildRequires:	libapm-devel libxpm-devel Xaw3d-devel ImageMagick xaw-devel kernel-source-latest

%description
This package provides scroll-wheel emulation for IBM Trackpoints.
See README for more detailed description.

%prep
%setup -q -n %{name}_%{underversion}%{?pre_ver:_%pre_pre}
cp -f xawutils/* .
perl -pi -e 's/-o root -g root//g;s/.*mknod.*$//g;s/.*depmod.*$//g;' Makefile

%build
%make

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall DESTDIR=$RPM_BUILD_ROOT
mkdir -p %{buildroot}%{_bindir}
find %{buildroot}/%{_prefix} -type f -perm -0100 -exec mv -f {} %{buildroot}%{_bindir} \;
rm -Rf %{buildroot}/%{_lib}
mv %{buildroot}/%{_bindir}/xtp4 %{buildroot}/%{_bindir}/xtp4.real
install -m755 %{SOURCE2} %{buildroot}/%{_bindir}/xtp4

#menu entry
mkdir -p %{buildroot}/{%{_iconsdir},%{_miconsdir},%{_liconsdir},%{_menudir}}
convert -resize 16x16 tp4icon.xpm %{buildroot}/%{_miconsdir}/%{name}.png
convert -resize 32x32 tp4icon.xpm %{buildroot}/%{_iconsdir}/%{name}.png
convert -resize 48x48 tp4icon.xpm %{buildroot}/%{_liconsdir}/%{name}.png

cat << EOF > %buildroot%{_datadir}/applications/mandriva-%{name}.desktop
[Desktop Entry]
Type=Application
Exec=xtp4
Icon=%{name}
Categories=Settings;HardwareSettings;
Name=Trackpoint Settings
Comment=Trackpoint settings
EOF

mkdir -p %{buildroot}/%{_sysconfdir}/X11/xinit.d/
install %{SOURCE1} %{buildroot}/%{_sysconfdir}/X11/xinit.d/%{name}

mkdir -p %{buildroot}/%{_mandir}/{man8,man1}
install tp4d.man %{buildroot}/%{_mandir}/man8
install xtp4.man %{buildroot}/%{_mandir}/man1

%post
consoleperms=/etc/security/console.perms
if ! `grep -q "/dev/misc/psaux" $consoleperms` ; then
  echo "adding entry for /dev/misc/psaux to your $consoleperms"
  cat >> $consoleperms << EOF
# allow user access to the psaux device for tp4utils driver
<console>  0600 /dev/misc/psaux   0600 root
EOF
fi

%update_menus

%postun
consoleperms=/etc/security/console.perms
[ $1 -eq 0 ] && perl -pi -e 's/.*psaux.*$//g' $consoleperms

%clean_menus

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc README
%{_bindir}/*
%{_prefix}/X11R6/lib/X11/app-defaults/XTp4
%config(noreplace) %{_sysconfdir}/X11/xinit.d/%{name}
#%{_sysconfdir}/sysconfig/%{name}
%{_datadir}/applications/mandriva-%{name}.desktop
%{_miconsdir}/%{name}.png
%{_iconsdir}/%{name}.png
%{_liconsdir}/%{name}.png
%{_mandir}/*/*

