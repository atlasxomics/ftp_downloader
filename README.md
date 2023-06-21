# Downloader for FTP or other
Simple Latch UI for downloading files directly into Latch Console. 

Allows downloads with either [FTP parameters](https://jkorpela.fi/ftpurl.html#:~:text=An%20FTP%20URL%20designates%20a,in%20one%20repository%20of%20RFCs.) or download url.  

Files are saved in the specified output directory in latch:///downloads/outdir. 

FTP will download recursively with url format:

```
ftp://user:password@host:port/
```

Providing full url will download recurively for directories, once for files.

Tested with ftp and https downloads; interally just calling
```
wget -c -r <link> -P <output>
```
so should work with most download urls.
