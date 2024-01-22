# spec

Name:		demo-slides
Version:	1
Release:	1%{?dist}
Summary:	Provides %{name}

License: 	Apache-2.0

%description
%{summary}

%build
cat > reveal.json <<EOF
{
  width: "100%",
  height: "100%",
  minScale: 0.2,
  maxScale: 2.0,
  margin: 0,
  navigationMode: "linear"
}
EOF
cat > slides.md <<EOF
### Find us at

- https://osbuild.org/
- https://matrix.to/#/#image-builder:fedoraproject.org
- https://github.com/osbuild/
EOF

%install
mkdir -p %{buildroot}/root/
install -m 0644 -vp slides.md %{buildroot}/root/
install -m 0644 -vp reveal.json %{buildroot}/root/

%clean
%files
/root/slides.md
/root/reveal.json

%changelog
* Mon Jan 22 2024 Sanne Raymaekers <sanne.raymaekers@gmail.com>
- slides
