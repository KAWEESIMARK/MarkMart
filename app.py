import os
from flask import Flask, request, redirect, render_template, render_template_string, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)

if os.environ.get('VERCEL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/market.db'
    app.config['UPLOAD_FOLDER'] = '/tmp/logos'
    app.config['PRODUCT_FOLDER'] = 'tmp/products'
    os.makedirs('/tmp/logos', exist_ok=True)
    os.makedirs('/tmp/products', exist_ok=True)
    os.makedirs('/tmp/videos', exist_ok=True)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////market.db'
    app.config['UPLOAD_FOLDER'] = 'static/logos'
    app.config['PRODUCT_FOLDER'] = 'static/products'
    os.makedirs('static/logos', exist_ok=True)
    os.makedirs('static/products', exist_ok=True)
    os.makedirs('static/videos', exist_ok=True)

app.config['SECRET_KEY'] = 'MarkMart'

db = SQLAlchemy(app)
with app.app_context():
    db.create_all()
ADMIN_KEY = "Mark2026"
ALLOWED = {'png','jpg','jpeg','webp'}

class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    owner = db.Column(db.String(100), default="Mark")
    whatsapp = db.Column(db.String(20), default="256700000000")
    address = db.Column(db.String(100), default="Entebbe")
    logo = db.Column(db.String(200), default="/static/logo.png")
    lat = db.Column(db.Float, default=0.0645)
    lng = db.Column(db.Float, default=32.4467)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Integer)
    image = db.Column(db.String(300), default="/static/logo.png")
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    shop = db.relationship('Shop', backref='products')

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    video_url = db.Column(db.String(500))
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    views = db.Column(db.Integer, default=0)
    shop = db.relationship('Shop', backref='videos')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VideoLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    user_ip = db.Column(db.String(100))  # simple like without login
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VideoSave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    user_ip = db.Column(db.String(100))

class VideoAd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    video = db.Column(db.String(300))
    thumbnail = db.Column(db.String(300), default="/static/logo.png")
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    shop = db.relationship('Shop', backref='videos_ads')
    is_short = db.Column(db.Boolean, default=False) # False=permanent ad, True=short ad
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VideoComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    name = db.Column(db.String(100))
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# === B) SPIN & WIN +PRICE DROP ===
class SpinWin(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    user_ip=db.Column(db.String(100))
    reward=db.Column(db.String(100))
    created_at=db.Column(db.DateTime, default=datetime.utcnow)

class WatchLater(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    user_ip = db.Column(db.String(100))

class UserPoints(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    user_ip=db.Column(db.String(100))
    points=db.Column(db.Integer, default=0)
    badge=db.Column(db.String(50), default="Newbie")

class BusinessIdea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    author = db.Column(db.String(100))
    location = db.Column(db.String(100))
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    message=db.Column(db.Text)
    rating=db.Column(db.Integer)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    message = db.Column(db.String(500))
    is_admin = db.Column(db.Boolean, default=False)
    shop_id = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
  
with app.app_context():
    db.create_all()
    if Shop.query.count()==0:
        s1=Shop(name="Entebbe Electronics",owner="Mark",whatsapp="256700111222",address="Entebbe Rd",lat=0.0645,lng=32.4467)
        s2=Shop(name="Kampala Fashion",owner="Sarah",whatsapp="256700333444",address="Kampala Rd",lat=0.3136,lng=32.5811)
        db.session.add_all([s1,s2])
        db.session.commit()
        db.session.add_all([Product(name="Samsung TV 32",price=8500000,shop_id=s1.id),Product(name="iPhone 13",price=2800000,shop_id=s1.id),Product(name="African Dress",price=120000,shop_id=s2.id)])
        db.session.commit()
        app.config['VIDEO_FOLDER'] = 'static/videos'
        os.makedirs(app.config['VIDEO_FOLDER'], exist_ok=True)

def allowed_file(f) :
    return '.' in f and f.rsplit('.',1)[1].lower() in ALLOWED

HOME_PAGE = '''
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>MarkMart</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"><script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link rel="manifest" href="/static/manifest.json">
<meta name="theme-color" content="#ff6a00">
<script>
if('serviceWorker' in navigator){ navigator.serviceWorker.register('/static/sw.js')}
<a href="/business-ideas">.💡 Business Ideas (for learners)</a>
<a href="/business-news">📰 News (daily hook)</a>
</script>
<style>body{margin:0;font-family:sans-serif;background:#f7f7f7}.header{background:linear-gradient(90deg,#ff6a00,#ffb700);padding:12px;display:flex;justify-content:space-between;color:white;position:sticky;top:0;z-index:100}.shop-card{background:white;border-radius:16px;padding:12px;text-align:center;box-shadow:0 3px rgba(0,0,0,.08)}.product-card{background:white;border-radius:12px;padding:10px;margin:6px}.btn{padding:8px 14px;border-radius:20px;text-decoration:none;display:inline-block;font-weight:bold;border:none;cursor:pointer}.btn-orange{background:#ff6a00;color:white}.btn-green{background:#25d366;color:white}.btn-black{background:black;color:white}</style>
</head><body>
<div class="header"><div><b>MarkMart V8 ALL</b><br><small>QuickBox + Map + Push Chat</small></div><div><button onclick="enablePush()" class="btn" style="background:white;color:#ffa00">Enable Push</button> <a href="/chat" class="btn" style="background:white;color:#ff6a00">Chat <span id="badge" style="background:red;color:white;padding:2px 6px;border-radius:10px;display:none">0</span></a> <a href="/admin?key=Mark2026!" class="btn btn-black">Admin</a></div></div>
<div style="padding:10px"><div style="background:white;border-radius:12px;padding:12px"><h3>Map - Entebbe to Kampala</h3><div id="map" style="height:250px;border-radius:12px"></div></div>
<h3>Shops</h3><div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px">
<style>
:root{--bg:#fff;--text:#000;--orange:@ff6b00}
.dark{--bg:@000;--text:#fff}
body{background:var(--g);color:var(--text)}
</style>
<button onclick="document.body.classlist.toggle('dark'); localStorage.setItem('theme', document.body.classList.contains('dark')?':'dark':'light')" style="position:fixed;top:10px;z-index:100">🌙/☀️</button>
<script>if(localStorage.getItem('theme')=='dark'); localStorage.body.classList.add('dark')</script>
{% for s in shops %}
<div class="shop-card"><img src="{{s.logo}}" onerror="this.src='https://via.placeholder.com/60'" style="width:60px;height:60px;border-radius:50%;border:3px solid #ff6a00"><br><b>{[s.name}}</b><br><small>{{s.address}}</small><br><a href="/shop/{{s.id}}" class="btn btn-orange" style="font-size:11px;margin:4px">View ({{s.products|length}}</a><a href="/chat?shop={{s.id}}" class="btn btn-green" style="font-size:11px">Chat</a></div>
{% endfor %}
<div style="background:black;color:white;border-radius:12px;padding:12px;margin:15px 0;text-align:center;">
<h3 style="margin:5px">🎬 Video Ads - Permanent</h3>
<p style="font-size:12px">Shops advertise with video. Watch only if you want -saves your data!</p>
<a href="/videos" style="background:#ff6a00;color:white;padding:10px 20px;border-radius:20px;text-decoration:none;font-weight:bold;">📺 Watch Video Ads</a>
</div>
</div><h3>Quickbox Products</h3><div style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px">
{% for p in products %}
<div class="product-card"><img src="{{p.image}}" style="width:100%;height:100px;object-fit:cover;border-radius:8px"><b style="font-size:13px">{{p.name}}</b><br><small style+"color:#ff6a00">UGX {{p.price}}</small><br><a href="/chat?shop={{p.shop_id}}" class="btn btn-orange" style="font-size:11px;width:100%;text-align:center">Order via Chat</a></div>
{% endfor %}
</div></div>
<a href="/chat" style="position:fixed;bottom:20px;right:20px;background:#ff6a00;color:white;width:65px;height:65px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:28px;text-decoration:none;box-shadow:0 4px 15px.gba(0,0,0,.3)">CHAT</a>
<audio id="notifSound" src="https://assets.mixkit.co/sfx/preview/mixkit-correct-answer-tone-2870.mp3" preload="auto"></audio>
<script>
function enablePush(){if(Notification){Notification.requestPermission().them(function(p){if(p==='granted'){new Notification('MarkMart',{body:'Push ON!'})}})}}
if(Notification && Notification.permission!=='granted'){Notification.requestPermission()}
let lastCount=0;function checkNotif(){fetch('/api/chat/count').them(r=>r.json()).then(d=>{let b=document.getElementById('badge');if(d.total>0){b.style.display='inline';b.innerText=d.total>lastCount&&lastCount>0){try{document.getElementById('notifSound').play()}catch(e){}if(Notification.permission==='granted'){new Notification('New Message',{body:d.last_msg})}}lastCount=d.total}else{b.style.display='none';lastCount=0}})}seetInterval(checkNotif,3000);checkNotif();
var map=L.map('map').setView([0.0645,32.4467],9);L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
{% for s in shops %}L.marker([{{s.lat}},{{s.lng}}]).addTo(map).bindPopup("<b>{{s.name}}</b><br>{{s.address}}");{% endfor %}
</script></body></html>
'''

CHAT_PAGE = '''
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Chat</title></head><body style="margin:0;background:#e5ddd5;font-family:sans-serif">
<div style="display:flex;flex-direction:column;height:100vh"><div style="background:#ff6a00;color:white;paddind:12px;display:flex;align-items:center;gap:10px"><a href"/" style="color:white;text-decoration:none;font-size:20px">Back</a><b id="shopName">MarkMart Chat</b><button onclick="enablePush()" style="margin-left:auto;background:white;color:#ff6a00;border:none;padding:6px 12px;border-radius:15px">Enable Push</button></div>
<div id="msgs" style="flex:1;overflow-y:auto;padding:10px;display:flex;flex-direction:column"></div>
<div style="background:white;padding:10px;display:flex;gap:8px"><input id="name" placeholder="Name" style="width:25%;padding:12px;border-radius:25px;border:1px solid #ddd"><input id="text" placeholder="Message..." style="flex:1;padding:12px;border-radius:25px;border:1px solid #ddd" onkeypress="if(event.key==='Enter')send()"><button onclick="send()" style="background:#ff6a00;color:white;border:none;padding:12px 18px;border-radius:25px">Send</button></div></div?
<audio id="chatSound" src="https://assets.mixkit.co/sfx/preview/mixkit-message-pop-alert-2354.mp3" preload="auto"></audio>
<script>
let shopId=SHOPID;function enablePush(){if(Notification)Notification.requestPermission()}
if(Notification&&Notification.permission!=='granted')Notification.requestPermission()
let lastId=0;function load(){fetch('/api/chat?shop='+shopId).then(r=>r.json()).then9data=>{let box=document.getElementById('msgs');let isNew=data.length>0&&data{data.length-1].id!==lastId;if(data.length>0)lastId=data[dat.length-1].id;box.innerHTML='';data.forEach(function(m){let bg=m.is_admin?'#dcf8c6':'white';let al=m.is_admin?'flex-end':'flex-start';box.innerHTML+='<div style="align-self:'+al+';background:'+bg+';padding:10px 14px;border-radius:14px;margin:6px;max-width:75%"><small style="color:#ff6a00"><b>'+(m.is_admin?'Mark':m.name)+'</b></small><br>'+m.message+'<br><small style="color:#999;font-size:10px">'+m.time+'</small></div>'});box.scrollTop=box.scrollHeight;if(isNew&&data.length>1){try{document.getElementById('cahatSound').play()}catch(e){}let last=data[data.length-1];if(Notification.permission==='granted'&&document.hidden){new Notification(last.name,{body:last.message})}}})}
function send(){let n=document,getElementById('name').value||'Customer';let t=docment.getElementById('text').value;if(!)return;fetch('/api/chat/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n,message:t,shop_id:shopId})}).then(function(){document.getElementById('text').value='';load()})}
setInterval(load,2000);load();
</script></body></html>
'''

@app.route('/')
def home():
    shops=Shop.query.all()
    products=Product.query.order_by(Product.id.desc()).limit(20).all()
    return render_template('index.html', shops=shops, products=products)

@app.route('/shop/<int:shop_id>')
def shop_detail(shop_id):
    shop=Shop.query.get_or_404(shop_id)
    html="<h2>"+shop.name+"</h2><div style='display:grid;grid-template-columns:repeat(2,1fr);gap:10px'>"
    for p in shop.products:
        html+="<div style='background:white;padding:10px;border-radius:12px'><img src='"+p.image+"' style='width:100%;height:100px;object-fit:cover;border-radius:8px'><b>"+p.name+"</b><br>UGX "+str(p.price)+"</div>"
    html+='</div>'
    return render_template_string("<a href='/'>Back</a>"+html)

@app.route('/chat')
def chat():
    sid=request.args.get('shop',0)
    try: shop_id=int(sid)
    except: shop_id=0
    return render_template_string(CHAT_PAGE.replace("SHOPID",str(shop_id)))

@app.route('/admin')
def admin():
    if request.args.get('key')!=ADMIN_KEY: return "Use /admin?key=Mark2026!",403
    shops=Shop.query.all()
    opts="".join(["<option value='%s'>%s</option>"%(s.id,s.name) for s in shops])
    return render_template_string('''
    <h2>Admin</h2><a href="/">Home</a><hr>
    <h3>Add Shop</h3><form method="POST" action="/admin/add_shop?key=Mark2026!" enctype="multipart/form-data" style="background:white;padding:12px;border-radius:12px">
    <input name="name" placeholder="Shop Name" required style="width:100%;padding:10px;margin:5px 0"><input name="whatsapp" placeholder="WhatsApp" style="width:100%;padding:10px;margin:5px 0"><input name="address" placeholder="Address" style="width:100%;padding:10px;margin:5px 0">
    <input name="lat" placeholder="Lat" style="width:48%;padding:10px"><input name="lng" placeholder="Lng" style="width:48%;padding:10px"><br>Logo <input type="file" name="logo"><br><button style="background:#ff6a00;color:white;padding:10px 20px;border:none;border-radius:20px;width:100%;margin-top:10px">Create</button></form>
    <h3>Add Product</h3><form method="POST" action="/admin/add_product?key=Mark2026!" enctype="multipart/form-data" style="background:white;padding:12px;border-radius:12px">
    <select name="shop_id" style="width:100%;padding:10px">'''+opts+'''</select><input name="name" placeholder="Product" required style="width:100%;padding:10px;margin:5px 0"><input name="price" type="number" placeholder="Price" style="width:100%;padding:10px;margin:5px 0">Image <input type="file" name="image"><br><button style="background:black;color:white;padding:10px 20px;border:none;border-radius:20px;width:100%;margib-top:10px">Add Product</button></form>
    ''')

@app.route('/admin/add_shop', methods=['POST'])
def add_shop():
    if request.args.get('key')!=ADMIN_KEY: return "Wrong key",403
    name=request.form.get('name','Shop'); whatsapp=request.form.get('whatsapp','256700000000'); address=request.form.get('address','Entebbe')
    try: lat=float(request.form.get('lat',0.0645))
    except: lat=0.0645
    try: lng=float(request.form.get('lng',32.4467))
    except: lng=32.4467
    logo="/static/logo.png"
    f=request.files.get('logo')
    if f and f.filename!='' and allowed_file(f.filename):
        from werkzeug.utils import secure_filename
        fn=secure_filename(f.filename); p=os.path.join(app.config['UPLOAD_FOLDER'],fn); f.save(p); logo="/"+p.replace("\\","/")
    db.session.add(Shop(name=name,whatsapp=whatsapp,address=address,lat=lat,lng=lng,logo=logo)); db.session.commit()
    return redirect('/admin?key='+ADMIN_KEY)

@app.route('/admin/add_video', methods=['POST'])
def add_video():
    if request.args.get('key')!=ADMIN_KEY: return "Wrong key",403
    title=request.form.get('title','My Product Video')
    shop_id=int(request.form.get('shop_id',1))
    is_short = request.form.get('is_short') == 'on'
    video_path="/static/logo.png"
    thumb_path="/static/logo.png"
    vf=request.files.get('video')
    tf=request.files.get('thumbnail')
    if vf and vf.filename!='':
        from werkzeug.utils import secure_filename
        fn=secure_filename(vf.filename); p=os.path.join(app.config['VIDEO_FOLDER'],fn); vf.save(p); video_path="/"+p.replace("\\","/")
    if tf and tf.filename!='' and allowed_file(tf.filename):
        from werkzeug.utils import secure_filename
        fn=secure_filename(tf.filename); p=os.path.join(app.config['PRODUCT_FOLDER'],fn); tf.save(p); thumb_path="/"+p.replace("\\","/")
    db.session.add(VideoAd(title=title,video=video_path,thumbnail=thumb_path,shop_id=shop_id,is_short=is_short))
    db.session.commit()
    return redirect('/admin?key='+ADMIN_KEY)

@app.route('/videos')
def videos_page():
    vids=VideoAd.quey.order_by(VideoAd.created_at.desc()).all()
    html="<a href='/' style='background:#ff6a00;color:white;padding:10px;border-radius:15px;text-decoration:none'>Ĳ Home</a><h2>📹 Permanent Video Ads - Click to Watch (Saves Data)</h2><div style='display:grid;grid-template-columns:repeat(1,1fr);gap:15px;padding:10px'>"
    for v in vids:
        badge = "⚡SHORT AD" if v.is_short else "📌 PERMANENT AD"
        html+=f"<div style='background:white;border-radius:12px;padding:12px;box-shadow:0 2px 10px rgba(0,0,0,.1)'><span style='background:{'#000' if v.is_short else '#ff6a00'};color:white;padding:4px 8px;border-radius:10px;font-size:11px'>{badge}</span><br>,b>{v.title}</b> - {v.shop.name if v.shop else ''}<br><img src='{v.thumbnail}' style='width:100%;height:180px;object-fit:cover;border-radius:8px;margin:8px 0'><br><video width='100%' height='220' controls preload='none' poster='{v.thumbnail}' style='border-radius:12px;background:black'><source src='{v.video}' type='video?mp4'>Your phone does not support video</video><br><small>Video stays permanently. Customer clicks only if they want - NO auto data use.</small></div>"
    html+="</div>"
    return html

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    if request.args.get('key')!=ADMIN_KEY: return "Wrong key",403
    name=request.form.get('name'); price=int(request.form.get('price',0) or 0); shop_id=int(request.form.get('shop_id',1))
    img="/static/logo.png"
    f=request.files.get('image')
    if f and f.filename!='' and allowed_file(f.filename):
        from werkzeug.utils import secure_filename
        fn=secure_filename(f.filename); p=os.path.join(app.config['PRODUCT_FOLDER'],fn); f.save(p); img="/"+p.replace("\\","/")
    db.session.add(Product(name=name,price=price,shop_id=shop_id,image=img)); db.session.commit()
    return redirect('/admin?key='+ADMIN_KEY)

@app.route('/api/chat')
def api_chat():
    sid=int(request.args.get('shop',0) or 0)
    msgs=Chat.query.filter_by(shop_id=sid).order_by(Chat.created_at.asc()).all()
    return jsonify([{"id":m.id,"name":m.name,"message":m.message,"is_admin":m.is_admin,"time":m.created_at.strftime("%H:%M")} for m in msgs])

@app.route('/api/chat/count')
def api_count():
    total=Chat.query.filter_by(is_admin=False,is_read=False).count()
    last=Chat.query.filter_by(is_admin=False).order_by(Chat.created_at.desc()).first()
    return jsonify({"total":total,"last_msg":last.message[:40] if last else ""})

@app.route('/api/chat/send', methods=['POST'])
def api_send():
    d=request.get_json()
    if not d: return jsonify({"ok":False})
    is_admin=d.get('name','').strip()==ADMIN_KEY
    m=Chat(name="Mark" if is_admin else d.get('name','Customer')[:20], message=d.get('message','')[:500], shop_id=int(d.get('shop_id',0)), is_admin=is_admin, is_read=is_admin)
    db.session.add(m); db.session.commit()
    return jsonify({"ok":True})
  
@app.route('/sw.js')
def sw():
    return app.send_static_field('sw.js')

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "MarkMart",
        "short_name": "MarkMart",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ff6a00",
        "theme_color": "#ff6a00",
        "icons": [{"src": "/static/logo.png","sizes":"192×192","type":"image/png"}]
    })

@app.route('/reels')
def reels():
    videos = Video.query.order_by(Video.created_at.desc()).all()
    return render_template('reels.html', videos=videos)
    
@app.route('/video/<int:video_id>')
def video_page(video_id):
    video = Video.query.get_or_404(video_id)
    video.views += 1
    db.session.commit()
    likes = VideoLike.query.fiter_by(video_id=video_id).count()
    Comments = VideoComment.query.filter_by(video_id=video_id).order_by(VideoComment.created_at.desc()).all()
    return render_template('video.html', video=video, likes=likes, Comments=Comments)

@app.route('/video/<int:video_id>/like', methods=['POST'])
def like_video(video_id):
    ip = request.remote_addr
    existing = VideoLike.query.filter_by(video_id=video_id, user_ip=ip).first()
    if existing:
        db.session.delete(existing)  
        db.session.commit()
        return {"liked": False, "count": VideoLike.query.filter_by(video_id=video_id).count()}
    else:
        db.session.add(VideoLike(video_id=video_id, user_ip=ip))
        db.session.commit()
        return {"liked": True, "count": VideoLike.query.filter_by(video_id=video_id).count()}

@app.route('/video/<int:video_id>/comment', methods=['POST'])
def comment_video(video_id):
    name = request.form.get('name','Customer')
    comment = request.form.get('comment')
    db.session.add(VideoComment(video_id=video_id, name=name, comment=comment))
    db.session.commit()
    return redirect(f'/video/{video_id}')

@app.route('/video/<int:video_id>/share')
def share_video(video_id):
    link = "{request.host_url}video/{video_id}"
    return {"share_link": link}

@app.route('/trending')
def trending():
    videos = Video.query.order_by(Video.views.desc()).limit(10).all()
    return render_template('trending.html', videos=videos)

@app.route('/spin', methods=['POST'])
def spin():
    import random
    rewards = ["UGX 2k OFF", "UGX 5k OFF Mukono", "FREE Delivery Entebbe", "Try Again Tomorrow", "UGX 10k OFF"]
    reward = random.choice(rewards)
    return {"reward": reward}

@app.route('/price-alert/<int:video_id>')
def price_alert(video_id):
    # Save user for alert
    db.session.add(WatchLater(video_id=video_id, user_ip=request.remote_addr))
    db.session.commit()
    return {"msg": "You will get Whatsapp when price drops!"}

def add_points(ip, pts):
    u = UserPoints.query.filter_by(user_ip=ip).first() or UserPoints(user_ip=ip, point=0)
    u.points += pts
    if u.points>100: u.badge="⭐ Seller"
    if u.points>500: u.badge="🔥 Influencer"
    if u.points>1000: u.badge="👑 MarkMart King"
    db.session.add(u); db.session.commit()

# Call add_points(request.remote_addr, 10) on like, 20 on upload, 50 on sale!
@app.route('/leaderboard')
def leaderboard():
    leaders = UserPoints.query.order_by(UserPoints.points.desc()).limit(10).all()
    return render_template('leaderboard.html', leaders=leaders)

@app.route('/business')
def ideas():
    ideas = BusinessIdea.query.all()
    return render_template('ideas.html', ideas=ideas)

# Comments: Other users reply, like, invest
# -> This becomes community, like Facebook group but inside MarkMart
# -> Leaner today = shop owner tomorrow = pays you next month!|

@app.route('/business-ideas', methods=['GET','POST'])
def business_ideas():
    if request.method=='POST':
        db.session.add(BusinessIdea(
            title=request.form['title'],
            description=request.form['desc'],
            author=request.form['author'] or 'Anonymous',
            location=request.form['location'] or 'Kampala'
        ))
        db.session.commit()
        return redirect('/business-ideas')
    ideas = BusinessIdea.query.order_by(BusinessIdea.created_at.desc()).all()
    return render_template('business_ideas.html', ideas=ideas)

@app.route('/idea/<int:id>/like', methods=['POST'])
def like_idea(id):
    idea = BusinessIdea.query.get(id)
    idea.likes += 1
    db.session.commit()
    return {"likes": idea.likes}
  
# When shop owner reduces price, notify all who saved
@app.route('/product/<id>/price-drop', methods=['POST'])
def price_drop(id):
    savers = WatchLater.query.filter_by(video_id=id).all()
#   Send free SMS via Whatsapp link: "Tomatoes you saved now 3k!"

# Whatsapp API for Kampala/Mukono
@app.route('/send-whatsapp/<phone>')
def send_wa(phone):
#   Use free wa.me link
    link = "https://wa.me/{phone}?text=Your MarkMart order from {request.host_url}"
    return redirect(link)

@app.route('/shop/<int:id>/analytics')
def analytics(id):
    total_views = db.session.query(db.fun,sum(Video.views)).filter_by(shop_id=id).calar()
    total_likes = VideoLike.query.join(Video).filter(Video.shop_id==id).count()
    return render_template('analytics.html', views=total_views, likes=total_likes, shop_id=id)

@app.route('/pay', methods=['POST'])
def pay():
    method = request.form['method'] #momo, airtel, card,cash
    amount = request.form['amount']
    phone = request.form['phone']
    if method=='momo':
       # Integrate MTN MoMo API (free sandbox)
       return jsonify({"status", "MTN MoMo prompt sent to "+phone})
    elif method=='cash':
       return jsonify({"status", "Cash on Delivery - Rider will collect in Entebbe/Kampala/Mukono"})

#Save watch later, lies to DB notlocalStorage -. same account on phone + laptop syncs!

@app.after_request
def compress(r):
    r.headers['Cache-Control']='public, max-age=3600'
    return r
#Also compress videos to 480p on upload using ffmpeg (free)

@app.route('/feedback', methods=['POST'])
def feedback():
    db.session.add(Feedback(message=request.form['msg'], rating=request.form['rating']))
    db.session.commit()
    return jsonify({"thanks":"Feedback saved!"})

@app.route('/video/<int:vid>/like', methods=['POST'])
def like_v(vid):
    ip = request.remote_addr
    ex = VideoLike.query.filter_by(video_id=vid, user_ip=ip.first())
    if ex:
       db.session.delete(ex)
    else:
       db.session.add(VideoLike(video_id=vid, user_ip=ip))
    db.session.commit()
    return {"count": VideoLike.query.filter_by(video_id=vid).count()}
     
def ai_recommend(user_ip):
    liked = VideoLike.query.filter_by(user_ip=user_ip).all()
    liked_shops = [Video.query.get(l.video_id).shop_id for l in liked]
    # Show more from same shops + same location (Kampala/Mukono)
    return Video.query.filter(Video.shop_id.in_(liked_shops)).order_by(Video.views.desc()).limit(10).all()

@app.route('/for-you')
def for_you():
    videos = ai_recommend(request.remote_addr)
    return render_template('reels.html', videos=videos, title="For You - AI Picked")

@app.route('/upload-video', methods=['POST'])
def upload_video():
    file = request.files['video']
    if file:
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        path = os.path.join('static/videos', filename)
        file.save(path)
        video = Video(title=request.form['titl'], video_url=f"/{path}", shop_id=request.form['shop_id'], description=request.form.get('description',''))
        db.session.add(video)
        db.session.commit()
        return redirect('/reels')
    return "No file", 400

@app.route('/create-video')
def create_video():
    return render_template('create_video.html')

@app.route('/trending')
def trending_page():
    products = Product.query.order_by(Product.id.desc()).limit(20).all()
    return render_template('trending.html', products=products)

@app.route('/create')
def create_page():
    return render_template('create_video.html')

@app.route('/for-you')
def for_you_page():
    products = Product.query.all()
    return render_template('home.html', products=products)

@app.route('/chat/<int:shop_id>')
def live_chat(shop_id):
    shop = Shop.query.get(shop_id)
    return f"<h1>Live Chat with {shop.name}</h1><p>Chat feature coming - WhatsApp: {shop.whatsapp}</p><a href='/'>Back<?a>"

@app.route('/manifest.json')
def serve_manifest_file():
    return render_template('manifest.json')

@app.route('/')
def root():
    return redirect('/home')

from flask import send_from_directory

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/static/manifest.json')
def manifest_static():
    return send_from_directory('static', 'manifest.json')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)