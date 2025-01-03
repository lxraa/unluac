cdir /S /B *.java > sources.txt
javac -d build  @sources.txt
jar cfm unluac.jar MANIFEST.MF -C build .