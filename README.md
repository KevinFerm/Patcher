# Patcher
This is a file patcher, it downloads the latest version of files from a server.

Needs a webserver with the latest version of the files you want to patch. It also needs the updated version.json that you get from running this script.
Also needs to be able to serve files from the relative path sent through a get request to the url in the self.downloadurl variable.

Example web server usage: (nodejs)
```js
router.get('/download', function(req,res){
    var file = req.query.path.split("./")[1];
    var file = replaceAll(file,"/", "\\");
    var cwd = process.cwd();
    res.download(cwd + "\\Game\\WindowsNoEditor\\"+file);
});
```
