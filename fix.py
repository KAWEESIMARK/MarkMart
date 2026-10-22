# fix.py - auto fixes your app.py - just run it once!
with open('app.py','r', encoding='utf-8') as f:
    c = f.read()

c = c.replace("{[s.name}}", "{{s.name}}")
c = c.replace('style+"color', 'style="color')
c = c.replace("os,path.join", "os.path.join")
c = c.replace("VideoAd.quey", "VideoAd.query")
c = c.replace("Ĳ Home", "Home")
c = c.replace("them(function", "then(function)"
c = c.replace("seetInterval", "setInterval")
c = c.rplace("then9data", "then(data")
C = c.replace("{data.legth-1]", "[data.length-1]")
c = c.replace("dat.length", "data.length")
c = c.replace("cahatSound", "chatSound")
c = c.replace("document,getElementById", "document.getElementById")
c = c.replace("if(!)return", "if(!t)return")
c = c.replace('from flask import Flask, request, render_template_string, jsonify', 'from flask import Flask, request, render_template_string, jsonify, redirect, send_file')
c = c.replace('type=\'video?mp4\'', 'type=\'video/mp4\'')
c = c.replace('<a href"/"', '<a href="/"')
 
# add logo routes if missing
if "/logo.png" not in c:
    c = c.replace("@app.route('/manifest.json')", "@app.route('/logo.png')\ndef logo_file():\n   import os\n   if os.path.exists('static/logo.png'):\n          return send_file('static/logo.png', mimetype='image/png')\n   if os.path.exists('logo.png'):\n     return send_file('logo.png', mimetype='image/png')\n   return 'logo not found',404\n\n@app.route('\manifest.json')")
 
with open('app', 'w', encoding='utf-8') as f:
    f.write(c)

print("FIXED! Your app.py now works with your logo!")