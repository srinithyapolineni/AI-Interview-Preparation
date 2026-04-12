"""
app.py  -  AI Interview Preparation Platform (FULLY UPGRADED + CAMERA FIXED + LOGIN)
Streamlit Frontend with:
  - Login / Signup system
  - FIXED Camera: Uses an external HTML file served via st.components with allow permissions
  - Camera ON/OFF + Start/Stop Recording + Download Video
  - Timer-based mock interview (30s / 60s / 90s)
  - Interview mode tabs (HR / Technical / Mixed)
  - STAR method live coach
  - AI follow-up questions
  - Leaderboard
  - Resume-based interview
  - Voice interview
  - Coding challenge with AI review
  - Performance dashboard

Run: streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
import random
import io
import sys
import os
import base64

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InterviewAI Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE    = "http://127.0.0.1:8000"
GRADE_COLOR = {"A": "#22c55e", "B": "#3b82f6", "C": "#f59e0b", "D": "#ef4444", "F": "#dc2626"}

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #060a10 0%, #0d1520 100%);
    border-right: 1px solid #141e2e;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label { color: #7a8fa6 !important; }
[data-testid="stSidebar"] h2 { color: #ffffff !important; }
[data-testid="stSidebar"] input {
    background: #0d1520 !important; border-color: #1a2535 !important; color: #e2e8f0 !important;
}

.main .block-container { padding-top: 1.5rem; max-width: 1200px; }

.score-card {
    background: linear-gradient(135deg, #0d1520, #111827);
    border: 1px solid #1a2535; border-radius: 16px;
    padding: 22px; text-align: center; color: white; margin-bottom: 14px;
}
.score-number {
    font-size: 52px; font-weight: 700; line-height: 1;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.score-label { font-size: 11px; color: #3d5068; margin-top: 6px; text-transform: uppercase; letter-spacing: 0.08em; }

.question-box {
    background: #0d1520; border-left: 3px solid #3b82f6;
    border-radius: 0 12px 12px 0; padding: 18px 22px;
    color: #e2e8f0; font-size: 16px; line-height: 1.75; margin-bottom: 14px;
}
.followup-box {
    background: #120d20; border-left: 3px solid #a78bfa;
    border-radius: 0 12px 12px 0; padding: 18px 22px;
    color: #e2e8f0; font-size: 15px; line-height: 1.75; margin-bottom: 14px;
}
.hint-box {
    background: #081510; border-left: 3px solid #22c55e;
    border-radius: 0 8px 8px 0; padding: 10px 14px;
    color: #4ade80; font-size: 13px; margin-bottom: 14px;
}
.tag {
    display: inline-block; padding: 3px 11px; border-radius: 99px;
    font-size: 11px; font-weight: 600; margin-right: 6px; margin-bottom: 8px;
    text-transform: uppercase; letter-spacing: 0.05em;
}
.tag-topic  { background: #0d1520; color: #7dd3fc; border: 1px solid #1a3556; }
.tag-easy   { background: #081510; color: #4ade80; border: 1px solid #14532d; }
.tag-medium { background: #150e00; color: #fbbf24; border: 1px solid #78350f; }
.tag-hard   { background: #180808; color: #f87171; border: 1px solid #7f1d1d; }
.tag-ai     { background: #120d20; color: #c4b5fd; border: 1px solid #4c1d95; }
.tag-bank   { background: #0d1520; color: #7dd3fc; border: 1px solid #1a3556; }
.tag-hr     { background: #081510; color: #4ade80; border: 1px solid #14532d; }
.tag-tech   { background: #0a1428; color: #60a5fa; border: 1px solid #1e3a8a; }
.tag-coding { background: #120d20; color: #a78bfa; border: 1px solid #4c1d95; }

.metric-card {
    background: #0d1520; border: 1px solid #1a2535;
    border-radius: 12px; padding: 14px; text-align: center; margin-bottom: 8px;
}
.metric-value { font-size: 26px; font-weight: 700; color: #60a5fa; }
.metric-label { font-size: 11px; color: #3d5068; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.06em; }

.ideal-answer {
    background: #060a10; border: 1px solid #1a3556;
    border-radius: 12px; padding: 16px; color: #93c5fd; font-size: 14px; line-height: 1.8;
}
.resume-box {
    background: #0d1520; border: 2px dashed #1a3556;
    border-radius: 16px; padding: 26px; text-align: center; margin: 14px 0;
}
.code-result {
    background: #060a10; border: 1px solid #1a2535;
    border-radius: 8px; padding: 14px; color: #e6edf3;
    font-family: 'DM Mono', monospace; font-size: 13px; white-space: pre-wrap;
}
.star-box {
    background: #0d1520; border: 1px solid #1a2535;
    border-radius: 12px; padding: 14px 18px; margin-bottom: 12px;
}
.lb-row {
    display: flex; align-items: center; padding: 11px 15px;
    border-radius: 10px; margin-bottom: 6px; background: #0d1520;
    border: 1px solid #1a2535; font-size: 14px; gap: 12px;
}
.lb-you { background: #0a1428 !important; border-color: #3b82f6 !important; }
.stProgress > div > div { background: linear-gradient(90deg, #3b82f6, #8b5cf6); }
.stButton button { border-radius: 10px !important; font-weight: 500 !important; }

/* Camera fix notice */
.cam-notice {
    background: #0a1a0a; border: 1px solid #14532d; border-radius: 10px;
    padding: 10px 14px; color: #4ade80; font-size: 13px; margin-bottom: 8px;
}

/* Login page */
.login-wrap {
    max-width: 460px; margin: 40px auto;
    background: #0d1520; border: 1px solid #1a2535;
    border-radius: 18px; padding: 40px 36px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.4);
}
.login-title { color: #fff; font-size: 28px; font-weight: 700; text-align: center; margin-bottom: 4px; }
.login-sub   { color: #3d5068; font-size: 13px; text-align: center; margin-bottom: 24px; }
</style>
""", unsafe_allow_html=True)

# ── CAMERA FIX: Write standalone HTML file served directly ───────────────────
CAMERA_RECORDER_HTML = """<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Feature-Policy" content="camera *; microphone *">
<meta http-equiv="Permissions-Policy" content="camera=*, microphone=*">
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
body{background:transparent;font-family:'DM Sans',sans-serif;}

@keyframes blink  {0%,100%{opacity:1}50%{opacity:0}}
@keyframes spin   {to{transform:rotate(360deg)}}
@keyframes fadeIn {from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}

.container{background:#0d1520;border:1px solid #1a2535;border-radius:14px;padding:18px;animation:fadeIn 0.3s ease;}
.header{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;}
.header-title{color:#60a5fa;font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:.07em;display:flex;align-items:center;gap:8px;}
.rec-badge{display:none;align-items:center;gap:6px;background:#1a0808;border:1px solid #7f1d1d;border-radius:8px;padding:4px 10px;font-size:12px;font-weight:600;color:#f87171;}
.rec-dot{width:8px;height:8px;border-radius:50%;background:#ef4444;animation:blink 1s infinite;}
.body{display:flex;gap:14px;align-items:flex-start;}
.video-wrap{position:relative;width:220px;height:165px;flex-shrink:0;border-radius:10px;overflow:hidden;background:#060a10;border:1px solid #1a2535;}
#preview{width:100%;height:100%;object-fit:cover;display:block;border-radius:10px;}
.cam-placeholder{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#060a10;color:#1e3a5f;font-size:12px;gap:8px;border-radius:10px;}
.cam-icon{font-size:36px;opacity:.4;}
.spinner{display:none;position:absolute;inset:0;align-items:center;justify-content:center;background:rgba(6,10,16,.7);}
.spin-ring{width:32px;height:32px;border:3px solid #1a2535;border-top-color:#3b82f6;border-radius:50%;animation:spin .8s linear infinite;}
.duration-overlay{display:none;position:absolute;bottom:8px;left:8px;background:rgba(0,0,0,.65);border-radius:6px;padding:3px 8px;font-size:12px;font-weight:600;color:#f87171;letter-spacing:.03em;}
.controls{display:flex;flex-direction:column;gap:8px;flex:1;}
.btn{width:100%;padding:9px 14px;border:none;border-radius:9px;font-size:13px;font-weight:600;cursor:pointer;font-family:'DM Sans',sans-serif;transition:all .15s ease;display:flex;align-items:center;justify-content:center;gap:7px;}
.btn:hover:not(:disabled){filter:brightness(1.12);transform:translateY(-1px);}
.btn:active:not(:disabled){transform:scale(.97);}
.btn:disabled{opacity:.35;cursor:not-allowed;transform:none!important;filter:none!important;}
.btn-cam{background:#1d4ed8;color:#eff6ff;}
.btn-stop-cam{background:#065f46;color:#d1fae5;display:none;}
.btn-record{background:#b91c1c;color:#fee2e2;}
.btn-stop-rec{background:#374151;color:#d1d5db;display:none;}
.btn-download{background:#6d28d9;color:#ede9fe;}
.btn-clear{background:#1a2535;color:#94a3b8;}
.divider{border:none;border-top:1px solid #1a2535;margin:6px 0;}
.recordings-section{margin-top:12px;}
.recordings-title{font-size:12px;font-weight:600;color:#4a6080;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px;}
.recording-item{display:flex;align-items:center;gap:10px;background:#060a10;border:1px solid #1a2535;border-radius:8px;padding:9px 12px;margin-bottom:6px;animation:fadeIn .25s ease;}
.recording-thumb{width:44px;height:33px;object-fit:cover;border-radius:5px;background:#1a2535;flex-shrink:0;}
.recording-info{flex:1;}
.recording-name{font-size:12px;font-weight:600;color:#e2e8f0;}
.recording-dur{font-size:11px;color:#4a6080;margin-top:1px;}
.recording-btn{padding:5px 10px;border:none;border-radius:6px;font-size:11px;font-weight:600;cursor:pointer;font-family:'DM Sans',sans-serif;transition:all .15s;}
.recording-btn:hover{filter:brightness(1.15);}
.dl-btn{background:#4c1d95;color:#ede9fe;}
.del-btn{background:#1a0808;color:#f87171;margin-left:4px;}
.tip{font-size:12px;color:#2a3f55;margin-top:10px;line-height:1.5;}
.err-msg{background:#1a0808;border:1px solid #7f1d1d;border-radius:8px;padding:10px 14px;color:#f87171;font-size:12px;margin-top:8px;display:none;line-height:1.6;}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="header-title">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M15 10l4.55-2.84A1 1 0 0 1 21 8v8a1 1 0 0 1-1.45.89L15 14"/><rect x="1" y="6" width="14" height="12" rx="2"/>
      </svg>
      Video Recorder
    </div>
    <div class="rec-badge" id="recBadge">
      <div class="rec-dot"></div>
      REC <span id="recTime">0:00</span>
    </div>
  </div>

  <div class="body">
    <div class="video-wrap">
      <video id="preview" autoplay muted playsinline></video>
      <div class="cam-placeholder" id="camPh">
        <div class="cam-icon">📷</div>
        <span>Camera off</span>
      </div>
      <div class="spinner" id="spinner"><div class="spin-ring"></div></div>
      <div class="duration-overlay" id="durOverlay">0:00</div>
    </div>

    <div class="controls">
      <button class="btn btn-cam"      id="startCamBtn"  onclick="startCamera()">📷 Start Camera</button>
      <button class="btn btn-stop-cam" id="stopCamBtn"   onclick="stopCamera()">⏏ Stop Camera</button>
      <hr class="divider">
      <button class="btn btn-record"   id="startRecBtn"  onclick="startRecording()" disabled>🔴 Start Recording</button>
      <button class="btn btn-stop-rec" id="stopRecBtn"   onclick="stopRecording()">⏹ Stop Recording</button>
      <hr class="divider">
      <button class="btn btn-download" id="downloadBtn"  onclick="downloadLatest()" disabled>⬇ Download Latest</button>
      <button class="btn btn-clear"                      onclick="clearAll()">🗑 Clear All</button>
    </div>
  </div>

  <div class="err-msg" id="errMsg"></div>
  <div class="recordings-section" id="recordingsSection" style="display:none;">
    <div class="recordings-title">Saved Recordings</div>
    <div id="recordingsList"></div>
  </div>
  <p class="tip">💡 Record your answers for self-review. Works best in Chrome.</p>
</div>

<script>
var stream=null,recorder=null,chunks=[],recording=false,timerInt=null,recSecs=0,recordings=[];

function showErr(msg){
  var e=document.getElementById('errMsg');
  e.style.display='block';
  e.innerHTML='⚠️ '+msg;
}
function hideErr(){document.getElementById('errMsg').style.display='none';}

function startCamera(){
  hideErr();
  var btn=document.getElementById('startCamBtn');
  btn.disabled=true;btn.innerHTML='⏳ Starting…';
  showSpinner(true);

  if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){
    showSpinner(false);
    btn.disabled=false;btn.innerHTML='📷 Start Camera';
    showErr('Camera API not available. Please use Chrome on localhost or enable HTTPS.');
    return;
  }

  navigator.mediaDevices.getUserMedia({video:{width:{ideal:640},height:{ideal:480}},audio:true})
    .then(function(s){
      stream=s;
      var vid=document.getElementById('preview');
      vid.srcObject=stream;
      vid.onloadedmetadata=function(){
        vid.play();
        showSpinner(false);
        document.getElementById('camPh').style.display='none';
        btn.style.display='none';
        document.getElementById('stopCamBtn').style.display='flex';
        document.getElementById('startRecBtn').disabled=false;
      };
    })
    .catch(function(err){
      showSpinner(false);
      btn.disabled=false;btn.innerHTML='📷 Start Camera';
      var msg='';
      if(err.name==='NotAllowedError'||err.name==='PermissionDeniedError'){
        msg='Permission denied. Click the 🔒 icon in the address bar → Allow Camera & Microphone → Refresh.';
      } else if(err.name==='NotFoundError'||err.name==='DevicesNotFoundError'){
        msg='No camera found. Make sure a webcam is connected.';
      } else if(err.name==='NotReadableError'||err.name==='TrackStartError'){
        msg='Camera is in use by another app (Zoom, Teams, etc.). Close it and try again.';
      } else if(err.name==='OverconstrainedError'){
        msg='Camera constraints not met. Trying again with basic settings…';
        navigator.mediaDevices.getUserMedia({video:true,audio:true})
          .then(function(s){stream=s;applyStream(s);}).catch(function(e2){showErr(e2.message);});
        return;
      } else {
        msg=err.name+': '+err.message;
      }
      showErr(msg);
    });
}

function applyStream(s){
  stream=s;
  var vid=document.getElementById('preview');
  vid.srcObject=stream;
  vid.play();
  showSpinner(false);
  document.getElementById('camPh').style.display='none';
  document.getElementById('startCamBtn').style.display='none';
  document.getElementById('stopCamBtn').style.display='flex';
  document.getElementById('startRecBtn').disabled=false;
}

function stopCamera(){
  if(recording)stopRecording();
  setTimeout(function(){
    if(stream){stream.getTracks().forEach(function(t){t.stop();});stream=null;}
    var vid=document.getElementById('preview');
    vid.pause();vid.srcObject=null;
    document.getElementById('camPh').style.display='flex';
    document.getElementById('stopCamBtn').style.display='none';
    var scb=document.getElementById('startCamBtn');
    scb.style.display='flex';scb.disabled=false;scb.innerHTML='📷 Start Camera';
    document.getElementById('startRecBtn').disabled=true;
  },100);
}

function startRecording(){
  if(!stream)return;
  chunks=[];recSecs=0;
  var opts={};
  ['video/webm;codecs=vp9,opus','video/webm;codecs=vp8,opus','video/webm','video/mp4'].forEach(function(t){
    if(!opts.mimeType&&MediaRecorder.isTypeSupported(t))opts={mimeType:t};
  });
  try{
    recorder=new MediaRecorder(stream,opts);
  }catch(e){
    recorder=new MediaRecorder(stream);
  }
  recorder.ondataavailable=function(e){if(e.data&&e.data.size>0)chunks.push(e.data);};
  recorder.onstop=function(){finaliseRecording();};
  recorder.start(100);
  recording=true;
  document.getElementById('startRecBtn').style.display='none';
  document.getElementById('stopRecBtn').style.display='flex';
  document.getElementById('recBadge').style.display='flex';
  document.getElementById('durOverlay').style.display='block';
  timerInt=setInterval(function(){
    recSecs++;
    var t=fmt(recSecs);
    document.getElementById('recTime').textContent=t;
    document.getElementById('durOverlay').textContent=t;
  },1000);
}

function stopRecording(){
  if(!recording)return;
  recording=false;clearInterval(timerInt);
  recorder.stop();
  document.getElementById('stopRecBtn').style.display='none';
  document.getElementById('startRecBtn').style.display='flex';
  document.getElementById('recBadge').style.display='none';
  document.getElementById('durOverlay').style.display='none';
}

function finaliseRecording(){
  var blob=new Blob(chunks,{type:'video/webm'});
  var duration=fmt(recSecs);
  var ts=new Date().toISOString().slice(0,19).replace('T','_').replace(/:/g,'-');
  var name='interview_'+ts+'.webm';
  recordings.unshift({blob:blob,name:name,duration:duration});
  document.getElementById('downloadBtn').disabled=false;
  renderRecordings();
}

function downloadLatest(){if(recordings.length)triggerDL(recordings[0].blob,recordings[0].name);}
function downloadByIndex(i){if(recordings[i])triggerDL(recordings[i].blob,recordings[i].name);}
function triggerDL(blob,name){
  var url=URL.createObjectURL(blob);
  var a=document.createElement('a');a.href=url;a.download=name;
  document.body.appendChild(a);a.click();
  setTimeout(function(){URL.revokeObjectURL(url);a.remove();},1000);
}
function clearAll(){recordings=[];document.getElementById('downloadBtn').disabled=true;renderRecordings();}
function deleteRecording(i){recordings.splice(i,1);if(!recordings.length)document.getElementById('downloadBtn').disabled=true;renderRecordings();}

function renderRecordings(){
  var sec=document.getElementById('recordingsSection');
  var list=document.getElementById('recordingsList');
  list.innerHTML='';
  if(!recordings.length){sec.style.display='none';return;}
  sec.style.display='block';
  recordings.forEach(function(rec,i){
    var url=URL.createObjectURL(rec.blob);
    var item=document.createElement('div');item.className='recording-item';
    item.innerHTML='<video class="recording-thumb" src="'+url+'" preload="metadata" muted></video>'+
      '<div class="recording-info"><div class="recording-name">'+rec.name+'</div>'+
      '<div class="recording-dur">'+rec.duration+' | '+fmtSize(rec.blob.size)+'</div></div>'+
      '<button class="recording-btn dl-btn" onclick="downloadByIndex('+i+')">⬇ Save</button>'+
      '<button class="recording-btn del-btn" onclick="deleteRecording('+i+')">✕</button>';
    list.appendChild(item);
  });
}

function fmt(s){return Math.floor(s/60)+':'+String(s%60).padStart(2,'0');}
function fmtSize(b){return b<1024?b+' B':b<1048576?(b/1024).toFixed(1)+' KB':(b/1048576).toFixed(1)+' MB';}
function showSpinner(show){document.getElementById('spinner').style.display=show?'flex':'none';}

(function patchIframePermissions(){
  try{
    if(window.parent&&window.parent!==window){
      var frames=window.parent.document.querySelectorAll('iframe');
      frames.forEach(function(f){
        try{
          if(f.contentWindow===window){
            f.allow='camera; microphone; display-capture';
          }
        }catch(e){}
      });
    }
  }catch(e){}
})();
</script>
</body>
</html>"""

_CAM_HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "camera_recorder.html")
with open(_CAM_HTML_PATH, "w", encoding="utf-8") as f:
    f.write(CAMERA_RECORDER_HTML)


def render_camera():
    components.html(CAMERA_RECORDER_HTML, height=430, scrolling=False)


# ── Timer Component ───────────────────────────────────────────────────────────
def build_timer_html(duration_secs):
    circ = 2 * 3.14159 * 22
    return f"""
<html><head>
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@500;700&display=swap');
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:transparent;font-family:'DM Sans',sans-serif;}}
</style></head>
<body>
<div style="background:#0d1520;border:1px solid #1a2535;border-radius:12px;
     padding:12px 18px;display:flex;align-items:center;gap:16px;">
  <div style="position:relative;width:52px;height:52px;flex-shrink:0;">
    <svg width="52" height="52" style="transform:rotate(-90deg)">
      <circle cx="26" cy="26" r="22" fill="none" stroke="#1a2535" stroke-width="4"/>
      <circle id="ring" cx="26" cy="26" r="22" fill="none"
              stroke="#3b82f6" stroke-width="4"
              stroke-dasharray="{circ:.1f}" stroke-dashoffset="0"
              stroke-linecap="round" style="transition:stroke-dashoffset .9s linear,stroke .3s;"/>
    </svg>
    <div id="tc" style="position:absolute;inset:0;display:flex;align-items:center;
         justify-content:center;font-size:14px;font-weight:700;color:#60a5fa;">{duration_secs}</div>
  </div>
  <div>
    <div style="font-size:10px;color:#3d5068;text-transform:uppercase;letter-spacing:.07em;margin-bottom:2px;">Time Remaining</div>
    <div id="ttext" style="font-size:22px;font-weight:700;color:#e2e8f0;">
      {duration_secs // 60}:{duration_secs % 60:02d}
    </div>
  </div>
  <div id="expBadge" style="display:none;margin-left:auto;background:#180808;
       border:1px solid #7f1d1d;border-radius:8px;padding:6px 14px;
       color:#f87171;font-size:13px;font-weight:600;">⏰ Time's up!</div>
</div>
<script>
var total={duration_secs},secs={duration_secs};
var circ={circ:.4f};
var iv=setInterval(function(){{
  secs--;
  var m=Math.floor(secs/60),s=secs%60;
  document.getElementById('tc').textContent=secs>0?secs:'0';
  document.getElementById('ttext').textContent=m+':'+(s<10?'0':'')+s;
  document.getElementById('ring').style.strokeDashoffset=circ*(1-secs/total);
  if(secs<=10){{
    document.getElementById('ring').style.stroke='#ef4444';
    document.getElementById('tc').style.color='#ef4444';
    document.getElementById('ttext').style.color='#f87171';
  }}
  if(secs<=0){{clearInterval(iv);document.getElementById('expBadge').style.display='block';}}
}},1000);
</script></body></html>
"""

# ── Helpers ───────────────────────────────────────────────────────────────────
def api_get(path, params=None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to backend. Make sure FastAPI is running: `uvicorn main:app --reload --port 8000`")
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None

def api_post(path, payload):
    try:
        r = requests.post(f"{API_BASE}{path}", json=payload, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to backend.")
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None

def tag(text, cls):
    return f'<span class="tag {cls}">{text}</span>'

def render_evaluation(ev, key_prefix="main"):
    st.markdown("## 📊 Evaluation Results")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f'<div class="score-card"><div class="score-number">{ev["score"]}</div>'
            f'<div class="score-label">Score / 10</div></div>', unsafe_allow_html=True)
    with c2:
        g = ev.get("grade","N/A"); col = GRADE_COLOR.get(g,"gray")
        st.markdown(
            f'<div class="score-card"><div class="score-number" style="color:{col};'
            f'background:none;-webkit-text-fill-color:{col}">{g}</div>'
            f'<div class="score-label">Grade</div></div>', unsafe_allow_html=True)
    nlp = ev.get("nlp_metrics", {})
    with c3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{nlp.get("word_count","—")}</div>'
            f'<div class="metric-label">Words</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{nlp.get("keyword_hits","—")}</div>'
            f'<div class="metric-label">Keywords</div></div>', unsafe_allow_html=True)

    st.progress(ev["score"] / 10, text=f"Overall: {ev['score']}/10")

    cs, ci = st.columns(2)
    with cs:
        st.markdown("### ✅ Strengths")
        for s in ev.get("strengths", []): st.success(s)
    with ci:
        st.markdown("### 🔧 Improvements")
        for i in ev.get("improvements", []): st.warning(i)

    if ev.get("feedback_summary"):
        st.info(f"💬 **Feedback:** {ev['feedback_summary']}")

    if ev.get("ideal_answer") and "OpenAI" not in ev.get("ideal_answer",""):
        with st.expander("📖 See Ideal Answer"):
            st.markdown(f'<div class="ideal-answer">{ev["ideal_answer"]}</div>', unsafe_allow_html=True)

    if ev.get("followup_question"):
        st.markdown("---")
        st.markdown("### 🤖 Interviewer Follow-up Question")
        st.markdown(f'<div class="followup-box">🔍 {ev["followup_question"]}</div>', unsafe_allow_html=True)
        fa = st.text_area("Your follow-up answer:", height=110,
                          placeholder="Answer the follow-up to show depth…",
                          key=f"fu_ans_{key_prefix}")
        if st.button("📤 Submit Follow-up", key=f"fu_sub_{key_prefix}"):
            if fa.strip():
                with st.spinner("Evaluating follow-up…"):
                    ev2 = api_post("/evaluate-answer", {
                        "question": ev["followup_question"],
                        "answer":   fa,
                        "role":     st.session_state.get("last_role","Software Developer"),
                        "username": st.session_state.username
                    })
                    if ev2:
                        ca, cb = st.columns(2)
                        with ca:
                            st.markdown(
                                f'<div class="score-card"><div class="score-number">{ev2["score"]}</div>'
                                f'<div class="score-label">Follow-up Score</div></div>',
                                unsafe_allow_html=True)
                        with cb:
                            if ev2.get("feedback_summary"):
                                st.info(ev2["feedback_summary"])
            else:
                st.warning("Write your follow-up answer first.")

def render_star():
    st.markdown("""
<div class="star-box">
<div style="font-size:12px;font-weight:600;color:#60a5fa;text-transform:uppercase;
     letter-spacing:.07em;margin-bottom:10px;">💡 STAR Method Guide</div>
<div style="display:flex;flex-direction:column;gap:9px;">
  <div style="display:flex;gap:10px;align-items:flex-start;">
    <div style="background:#1a3556;color:#60a5fa;border-radius:6px;padding:3px 8px;font-weight:700;font-size:13px;flex-shrink:0;">S</div>
    <div><span style="color:#e2e8f0;font-weight:600;font-size:14px;">Situation</span>
    <br><span style="color:#3d5068;font-size:13px;">Set the context — when / where did this happen?</span></div>
  </div>
  <div style="display:flex;gap:10px;align-items:flex-start;">
    <div style="background:#1a3556;color:#60a5fa;border-radius:6px;padding:3px 8px;font-weight:700;font-size:13px;flex-shrink:0;">T</div>
    <div><span style="color:#e2e8f0;font-weight:600;font-size:14px;">Task</span>
    <br><span style="color:#3d5068;font-size:13px;">What was your specific role or responsibility?</span></div>
  </div>
  <div style="display:flex;gap:10px;align-items:flex-start;">
    <div style="background:#1a3556;color:#60a5fa;border-radius:6px;padding:3px 8px;font-weight:700;font-size:13px;flex-shrink:0;">A</div>
    <div><span style="color:#e2e8f0;font-weight:600;font-size:14px;">Action</span>
    <br><span style="color:#3d5068;font-size:13px;">What exact steps did YOU take? Be specific.</span></div>
  </div>
  <div style="display:flex;gap:10px;align-items:flex-start;">
    <div style="background:#1a3556;color:#60a5fa;border-radius:6px;padding:3px 8px;font-weight:700;font-size:13px;flex-shrink:0;">R</div>
    <div><span style="color:#e2e8f0;font-weight:600;font-size:14px;">Result</span>
    <br><span style="color:#3d5068;font-size:13px;">What was the outcome? Quantify with numbers where possible.</span></div>
  </div>
</div>
</div>""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
defaults = {
    "current_question": None,
    "evaluation":       None,
    "username":         "guest",
    "logged_in":        False,
    "user_email":       "",
    "interview_count":  0,
    "page":             "🎤 Interview",
    "resume_questions": [],
    "code_result":      None,
    "coding_q":         None,
    "code_evaluation":  None,
    "timer_duration":   60,
    "interview_mode":   "💼 HR",
    "last_role":        "Software Developer",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# LOGIN / SIGNUP GATE — shown before anything else if not logged in
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown("""
    <div class="login-wrap">
        <div class="login-title">🎯 InterviewAI Pro</div>
        <div class="login-sub">Your AI-Powered Interview Coach</div>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Create Account"])

    with tab_login:
        st.markdown("### Welcome back!")
        lu = st.text_input("Username", placeholder="Enter your username", key="login_u")
        lp = st.text_input("Password", type="password", placeholder="Enter your password", key="login_p")
        if st.button("🚀 Login", use_container_width=True, type="primary", key="login_btn"):
            if lu.strip() and lp:
                res = api_post("/login", {"username": lu.strip(), "password": lp})
                if res:
                    st.session_state.logged_in  = True
                    st.session_state.username   = res["username"]
                    st.session_state.user_email = res.get("email", "")
                    st.success(f"✅ Welcome back, {res['username']}!")
                    st.rerun()
            else:
                st.warning("Please enter both username and password.")

    with tab_signup:
        st.markdown("### Create your free account")
        ru  = st.text_input("Username (min 3 chars)",  placeholder="Choose a username",       key="reg_u")
        re_ = st.text_input("Email",                   placeholder="your@email.com",          key="reg_e")
        rp  = st.text_input("Password (min 6 chars)",  type="password",
                             placeholder="Choose a strong password",                           key="reg_p")
        rp2 = st.text_input("Confirm Password",        type="password",
                             placeholder="Repeat your password",                               key="reg_p2")
        if st.button("✨ Create Account", use_container_width=True, type="primary", key="reg_btn"):
            if not (ru.strip() and re_.strip() and rp and rp2):
                st.warning("Please fill in all fields.")
            elif rp != rp2:
                st.error("❌ Passwords do not match.")
            elif len(rp) < 6:
                st.error("❌ Password must be at least 6 characters.")
            else:
                res = api_post("/register", {"username": ru.strip(), "email": re_.strip(), "password": rp})
                if res:
                    st.success("✅ Account created! Please log in.")

    st.stop()  # Stop the rest of the app from rendering until logged in

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<h2 style='color:#fff;font-size:19px;margin-bottom:2px;'>🎯 InterviewAI Pro</h2>"
        "<p style='color:#2a3f55;font-size:12px;margin-bottom:14px;'>Your AI interview coach</p>",
        unsafe_allow_html=True)
    st.markdown("---")

    # Show logged-in user info
    st.markdown(f"👤 **{st.session_state.username}**")
    if st.button("🚪 Logout", use_container_width=True):
        for key in ["logged_in","username","user_email","current_question",
                    "evaluation","interview_count","resume_questions",
                    "code_result","coding_q","code_evaluation"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.markdown("---")

    PAGES = ["🎤 Interview","🎙️ Voice Interview","📄 Resume Interview",
             "🧪 Coding Challenge","📊 Performance","🏆 Leaderboard","ℹ️ About"]
    page = st.radio("Navigate", PAGES,
                    index=PAGES.index(st.session_state.page) if st.session_state.page in PAGES else 0,
                    label_visibility="collapsed")
    st.session_state.page = page
    st.markdown("---")

    roles_data = api_get("/roles")
    roles = roles_data["roles"] if roles_data else ["Software Developer","Frontend Developer","Data Scientist"]
    role  = st.selectbox("🎯 Role", roles)
    st.session_state.last_role = role

    topics_data = api_get("/topics", {"role": role})
    topics      = ["Any Topic"] + (topics_data["topics"] if topics_data else [])
    topic       = st.selectbox("📚 Topic", topics)
    chosen_topic = None if topic == "Any Topic" else topic

    difficulty = st.select_slider("⚡ Difficulty", ["Easy","Medium","Hard"], value="Medium")

    st.markdown("---")
    st.caption(f"Sessions: {st.session_state.interview_count}")


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: INTERVIEW
# ════════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "🎤 Interview":
    diff_class = {"Easy":"tag-easy","Medium":"tag-medium","Hard":"tag-hard"}[difficulty]

    st.markdown(f"# 🎤 Mock Interview — {role}")
    st.markdown(f"Hello **{st.session_state.username}**! Pick a mode and start practising.")
    st.markdown("---")

    mc1, mc2, mc3 = st.columns(3)
    for col, mode, lbl in [(mc1,"💼 HR","HR Interview"),(mc2,"💻 Technical","Technical"),(mc3,"🧠 Mixed","Mixed")]:
        with col:
            is_active = st.session_state.interview_mode == mode
            if st.button(f"{mode} {lbl}", use_container_width=True,
                         type="primary" if is_active else "secondary",
                         key=f"mode_{mode}"):
                if not is_active:
                    st.session_state.interview_mode = mode
                    st.session_state.current_question = None
                    st.session_state.evaluation = None
                    st.rerun()

    mode = st.session_state.interview_mode
    st.markdown(
        tag(mode, "tag-hr" if "HR" in mode else "tag-tech") +
        tag(role, "tag-topic") + tag(difficulty, diff_class),
        unsafe_allow_html=True)

    api_topic = "HR" if "HR" in mode else (None if "Mixed" in mode else chosen_topic)
    st.markdown("---")

    st.markdown("**⏱️ Timer per question**")
    tc1, tc2, tc3, tc4 = st.columns([1,1,1,3])
    with tc1:
        if st.button("30s", use_container_width=True): st.session_state.timer_duration = 30
    with tc2:
        if st.button("60s", use_container_width=True): st.session_state.timer_duration = 60
    with tc3:
        if st.button("90s", use_container_width=True): st.session_state.timer_duration = 90
    with tc4:
        st.caption(f"Set to **{st.session_state.timer_duration}s**")

    gc, rc = st.columns(2)
    with gc:
        if st.button("🎲 Generate Question", use_container_width=True, type="primary"):
            with st.spinner("Generating…"):
                res = api_post("/generate-question",
                               {"role":role,"difficulty":difficulty,"topic":api_topic})
                if res:
                    st.session_state.current_question = res
                    st.session_state.evaluation = None
    with rc:
        if st.button("🔄 Clear & Reset", use_container_width=True):
            st.session_state.current_question = None
            st.session_state.evaluation = None
            st.rerun()

    q = st.session_state.current_question
    if q:
        src_cls = "tag-ai" if q.get("source","ai")=="ai" else "tag-bank"
        src_lbl = "🤖 AI"  if q.get("source","ai")=="ai" else "🏦 Bank"
        st.markdown(tag(q.get("topic",""), "tag-topic") + tag(src_lbl, src_cls),
                    unsafe_allow_html=True)
        st.markdown(f'<div class="question-box">❓ {q["question"]}</div>', unsafe_allow_html=True)
        if q.get("hint"):
            st.markdown(f'<div class="hint-box">💡 <b>Hint:</b> {q["hint"]}</div>', unsafe_allow_html=True)

        components.html(build_timer_html(st.session_state.timer_duration), height=82)

        if "HR" in mode:
            if st.checkbox("Show STAR method guide", key="star_interview"):
                render_star()

        st.markdown("**🎥 Camera & Recording**")
        st.markdown(
            '<div class="cam-notice">💡 <b>Camera tip:</b> If camera doesn\'t start, '
            'click the 🔒 padlock in the address bar → set Camera & Microphone to <b>Allow</b> → '
            'refresh the page. Use <b>Chrome</b> for best compatibility.</div>',
            unsafe_allow_html=True)
        render_camera()

        answer = st.text_area("✍️ Your Answer", height=180,
                              placeholder="Write your answer here…", key="int_answer")
        wc = len(answer.split()) if answer.strip() else 0
        aw, as_ = st.columns([2,1])
        with aw:
            st.progress(min(wc/80, 1.0), text=f"{wc} words  |  Aim for 50–100")
        with as_:
            if st.button("📤 Submit Answer", use_container_width=True, type="primary"):
                if not answer.strip():
                    st.warning("Write an answer first.")
                else:
                    with st.spinner("🧠 Evaluating…"):
                        ev = api_post("/evaluate-answer",
                                      {"question":q["question"],"answer":answer,
                                       "role":role,"username":st.session_state.username})
                        if ev:
                            st.session_state.evaluation = ev
                            st.session_state.interview_count += 1

    ev = st.session_state.evaluation
    if ev:
        st.markdown("---")
        render_evaluation(ev, "interview")
        st.markdown("---")
        if st.button("➡️ Next Question", type="primary"):
            st.session_state.evaluation = None
            st.session_state.current_question = None
            st.rerun()
    elif not q:
        st.markdown("""
        <div style="text-align:center;padding:56px 20px;color:#1a2535;">
            <div style="font-size:60px;margin-bottom:14px;">🎤</div>
            <h2 style="color:#2d3e50;">Ready to practise?</h2>
            <p style="color:#1a2535;">Pick a mode above, then click <strong>Generate Question</strong>.</p>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: VOICE INTERVIEW
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "🎙️ Voice Interview":
    st.markdown("# 🎙️ Voice Interview")
    st.markdown("Speak your answer in the browser — transcribed and evaluated automatically.")
    st.markdown("---")

    gc, rc = st.columns(2)
    with gc:
        if st.button("🎲 Generate Question", use_container_width=True, type="primary"):
            with st.spinner("Generating…"):
                res = api_post("/generate-question",
                               {"role":role,"difficulty":difficulty,"topic":chosen_topic})
                if res:
                    st.session_state.current_question = res
                    st.session_state.evaluation = None
    with rc:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.current_question = None
            st.session_state.evaluation = None
            st.rerun()

    q = st.session_state.current_question
    if q:
        diff_class = {"Easy":"tag-easy","Medium":"tag-medium","Hard":"tag-hard"}[difficulty]
        st.markdown(tag(q.get("topic",""),"tag-topic") + tag(difficulty, diff_class),
                    unsafe_allow_html=True)
        st.markdown(f'<div class="question-box">❓ {q["question"]}</div>', unsafe_allow_html=True)

        components.html(build_timer_html(st.session_state.timer_duration), height=82)

        st.markdown("**🎥 Camera & Recording**")
        st.markdown(
            '<div class="cam-notice">💡 <b>Camera tip:</b> If camera doesn\'t start, '
            'click the 🔒 padlock → Allow Camera & Microphone → Refresh.</div>',
            unsafe_allow_html=True)
        render_camera()

        components.html("""
<html><head>
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'DM Sans',sans-serif;background:transparent;}
.wrap{background:#0d1520;border:2px dashed #1a3556;border-radius:14px;padding:22px;text-align:center;margin:10px 0;}
.icon{font-size:34px;margin-bottom:8px;}
.label{color:#7a8fa6;font-weight:600;font-size:14px;margin-bottom:12px;}
#micBtn{background:#1d4ed8;color:#eff6ff;border:none;border-radius:10px;padding:10px 28px;font-size:14px;font-weight:700;cursor:pointer;font-family:'DM Sans',sans-serif;transition:all .15s;}
#micBtn:hover{filter:brightness(1.1);}
#status{color:#2a3f55;font-size:13px;margin-top:10px;}
#transcript{background:#060a10;border:1px solid #1a2535;border-radius:8px;padding:12px;margin-top:12px;color:#7dd3fc;font-size:14px;min-height:42px;text-align:left;display:none;line-height:1.6;}
.note{color:#1a2535;font-size:12px;margin-top:8px;}
</style></head>
<body>
<div class="wrap">
  <div class="icon">🎤</div>
  <div class="label">Browser Speech Recognition</div>
  <button id="micBtn" onclick="toggle()">🎙️ Start Listening</button>
  <p id="status"></p>
  <div id="transcript"></div>
  <p class="note">Copy the transcript into the answer box below then submit.</p>
</div>
<script>
var r=null,on=false,SR=window.SpeechRecognition||window.webkitSpeechRecognition;
if(!SR){document.getElementById('micBtn').style.display='none';
  document.getElementById('status').textContent='⚠️ Use Chrome for speech support.';}
function toggle(){
  if(on){r.stop();return;}
  r=new SR();r.continuous=true;r.interimResults=true;r.lang='en-US';
  var ft='';
  r.onstart=function(){on=true;document.getElementById('micBtn').textContent='⏹ Stop';
    document.getElementById('micBtn').style.background='#b91c1c';
    document.getElementById('status').textContent='● Listening…';
    document.getElementById('status').style.color='#4ade80';
    document.getElementById('transcript').style.display='block';};
  r.onresult=function(e){var it='';
    for(var i=e.resultIndex;i<e.results.length;i++)
      e.results[i].isFinal?ft+=e.results[i][0].transcript+' ':it+=e.results[i][0].transcript;
    document.getElementById('transcript').textContent=(ft+it)||'Say something…';};
  r.onend=function(){on=false;document.getElementById('micBtn').textContent='🎙️ Start Listening';
    document.getElementById('micBtn').style.background='#1d4ed8';
    document.getElementById('status').textContent=ft?'✅ Done — copy text above into answer box.':'No speech detected.';
    document.getElementById('status').style.color=ft?'#4ade80':'#f87171';};
  r.onerror=function(e){document.getElementById('status').textContent='Error: '+e.error;};
  r.start();}
</script></body></html>""", height=260)

        st.markdown("**✍️ Your Answer** *(type or paste speech transcript above)*")
        answer = st.text_area("Answer", height=150,
                              placeholder="Paste transcript here or type your answer…",
                              key="voice_answer", label_visibility="collapsed")
        wc = len(answer.split()) if answer.strip() else 0
        aw, as_ = st.columns([2,1])
        with aw:
            st.progress(min(wc/80,1.0), text=f"{wc} words  |  Aim for 50–100")
        with as_:
            if st.button("📤 Submit", use_container_width=True, type="primary", key="v_sub"):
                if not answer.strip():
                    st.warning("Write or speak an answer first.")
                else:
                    with st.spinner("🧠 Evaluating…"):
                        ev = api_post("/evaluate-answer",
                                      {"question":q["question"],"answer":answer,
                                       "role":role,"username":st.session_state.username})
                        if ev:
                            st.session_state.evaluation = ev
                            st.session_state.interview_count += 1

    ev = st.session_state.evaluation
    if ev:
        st.markdown("---")
        render_evaluation(ev, "voice")
    elif not q:
        st.markdown("""
        <div style="text-align:center;padding:40px;color:#1a2535;">
            <div style="font-size:60px;">🎙️</div>
            <h3 style="color:#2d3e50;">Click Generate Question to begin!</h3>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: RESUME INTERVIEW
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "📄 Resume Interview":
    st.markdown("# 📄 Resume-Based Interview")
    st.markdown("Upload your resume — AI generates **personalised questions** from your experience.")
    st.markdown("---")

    try:
        import PyPDF2
        PDF_OK = True
    except ImportError:
        PDF_OK = False
        st.warning("⚠️ Install `PyPDF2` for PDF reading: `pip install PyPDF2`")

    st.markdown('<div class="resume-box">', unsafe_allow_html=True)
    st.markdown("### 📎 Upload Resume (PDF) or paste text")
    uploaded = st.file_uploader("Resume PDF", type=["pdf"], label_visibility="collapsed")
    st.markdown("**Or paste resume text:**")
    pasted = st.text_area("Resume text", height=130,
                          placeholder="Paste resume content here…", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    resume_text = ""
    if uploaded and PDF_OK:
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(uploaded)
            for pg in reader.pages:
                resume_text += pg.extract_text() or ""
            if resume_text.strip():
                st.success(f"✅ Resume read! ({len(resume_text.split())} words)")
        except Exception as e:
            st.error(f"PDF error: {e}")
    elif pasted.strip():
        resume_text = pasted

    if resume_text.strip():
        with st.expander("👀 Preview"):
            st.text(resume_text[:800] + "…" if len(resume_text) > 800 else resume_text)

        nc, gc2 = st.columns(2)
        with nc:
            nq = st.slider("Number of questions", 3, 10, 5)
        with gc2:
            st.write("")
            if st.button("🎯 Generate from Resume", type="primary", use_container_width=True):
                with st.spinner("🤖 Analysing resume…"):
                    res = api_post("/resume-questions",
                                   {"resume_text":resume_text,"role":role,
                                    "difficulty":difficulty,"num_questions":nq})
                    if res:
                        st.session_state.resume_questions = res.get("questions",[])
                        st.success(f"✅ {len(st.session_state.resume_questions)} questions generated!")

    if st.session_state.resume_questions:
        st.markdown("---")
        st.markdown(f"## 🎯 {len(st.session_state.resume_questions)} Personalised Questions")
        for i, qd in enumerate(st.session_state.resume_questions, 1):
            with st.expander(f"Q{i}: {qd.get('question','')[:65]}…"):
                st.markdown(f'<div class="question-box">❓ {qd.get("question","")}</div>',
                            unsafe_allow_html=True)
                if qd.get("reason"):
                    st.info(f"🎯 **Why this:** {qd['reason']}")

                components.html(build_timer_html(st.session_state.timer_duration), height=82)

                if "HR" in qd.get("topic",""):
                    if st.checkbox("Show STAR guide", key=f"star_r{i}"):
                        render_star()

                st.markdown("**🎥 Camera & Recording**")
                render_camera()

                ans = st.text_area("Your answer:", height=110, key=f"r_ans_{i}")
                if st.button(f"📤 Submit Q{i}", key=f"r_sub_{i}"):
                    if ans.strip():
                        with st.spinner("Evaluating…"):
                            ev = api_post("/evaluate-answer",
                                         {"question":qd.get("question",""),"answer":ans,
                                          "role":role,"username":st.session_state.username})
                            if ev:
                                st.session_state.interview_count += 1
                                render_evaluation(ev, f"resume_{i}")
                    else:
                        st.warning("Write an answer first!")
    elif not resume_text.strip():
        st.markdown("""
        <div style="text-align:center;padding:40px;color:#1a2535;">
            <div style="font-size:60px;">📄</div>
            <h3 style="color:#2d3e50;">Upload your resume to begin!</h3>
            <p style="color:#1a2535;">The AI reads your skills, projects and experience
               to ask targeted questions.</p>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: CODING CHALLENGE
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "🧪 Coding Challenge":
    st.markdown("# 🧪 Coding Challenge")
    st.markdown("Write real Python code — get AI feedback on correctness, efficiency, and style!")
    st.markdown("---")

    CODING_QS = {
        "Easy": [
            {"title":"Two Sum","description":"Given an array and a target, return indices of two numbers that add up to the target.",
             "example":"Input: nums=[2,7,11,15], target=9\nOutput: [0,1]",
             "starter":"def two_sum(nums, target):\n    # Write your solution here\n    pass\n\nprint(two_sum([2,7,11,15], 9))  # Expected: [0, 1]"},
            {"title":"Reverse String","description":"Reverse a string without using slicing.",
             "example":"Input: 'hello'\nOutput: 'olleh'",
             "starter":"def reverse_string(s):\n    pass\n\nprint(reverse_string('hello'))  # olleh"},
            {"title":"FizzBuzz","description":"1 to n: multiples of 3 → Fizz, 5 → Buzz, both → FizzBuzz.",
             "example":"n=15 → 1,2,Fizz,4,Buzz,…,FizzBuzz",
             "starter":"def fizzbuzz(n):\n    for i in range(1,n+1):\n        pass\n\nfizzbuzz(15)"},
            {"title":"Palindrome Check","description":"Check if a string is a palindrome.",
             "example":"'racecar' → True  |  'hello' → False",
             "starter":"def is_palindrome(s):\n    pass\n\nprint(is_palindrome('racecar'))  # True\nprint(is_palindrome('hello'))    # False"},
        ],
        "Medium": [
            {"title":"Valid Parentheses","description":"Check if brackets are properly opened and closed.",
             "example":"'()[]{}' → True  |  '(]' → False",
             "starter":"def is_valid(s):\n    # Hint: use a stack\n    pass\n\nprint(is_valid('()[]{}'))  # True\nprint(is_valid('(]'))       # False"},
            {"title":"Find Duplicates","description":"Find all duplicate numbers in an array.",
             "example":"[4,3,2,7,8,2,3,1] → [2,3]",
             "starter":"def find_duplicates(nums):\n    pass\n\nprint(find_duplicates([4,3,2,7,8,2,3,1]))"},
            {"title":"Fibonacci","description":"Return the first n Fibonacci numbers efficiently.",
             "example":"n=8 → [0,1,1,2,3,5,8,13]",
             "starter":"def fibonacci(n):\n    pass\n\nprint(fibonacci(8))"},
        ],
        "Hard": [
            {"title":"LRU Cache","description":"Design an LRU Cache with O(1) get and put.",
             "example":"LRUCache(2): put(1,1) put(2,2) get(1)→1 put(3,3) get(2)→-1",
             "starter":"class LRUCache:\n    def __init__(self, capacity):\n        self.capacity = capacity\n\n    def get(self, key):\n        pass\n\n    def put(self, key, value):\n        pass\n\ncache=LRUCache(2)\ncache.put(1,1);cache.put(2,2)\nprint(cache.get(1))   # 1\ncache.put(3,3)\nprint(cache.get(2))   # -1"},
            {"title":"BST Validator","description":"Check if a binary tree is a valid BST.",
             "example":"All left nodes < root < all right nodes",
             "starter":"class TreeNode:\n    def __init__(self,val=0):\n        self.val=val;self.left=None;self.right=None\n\ndef is_valid_bst(root, mn=float('-inf'), mx=float('inf')):\n    pass"},
        ],
    }

    cc1, cc2, cc3 = st.columns([2,1,1])
    with cc1:
        cdiff = st.select_slider("Difficulty",["Easy","Medium","Hard"],value="Easy",key="cdiff")
    with cc2:
        st.write("")
        if st.button("🎲 Random", use_container_width=True):
            st.session_state.coding_q = random.choice(CODING_QS[cdiff])
            st.session_state.code_result = None
            st.session_state.code_evaluation = None
    with cc3:
        st.write("")
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.code_result = None
            st.session_state.code_evaluation = None

    if not st.session_state.coding_q:
        st.session_state.coding_q = CODING_QS["Easy"][0]

    cq = st.session_state.coding_q
    cdiff_cls = {"Easy":"tag-easy","Medium":"tag-medium","Hard":"tag-hard"}[cdiff]
    st.markdown(tag(cdiff, cdiff_cls) + tag("Python","tag-coding"), unsafe_allow_html=True)

    qq, qe = st.columns([3,2])
    with qq:
        st.markdown(f"### 📝 {cq['title']}")
        st.markdown(f'<div class="question-box">{cq["description"]}</div>', unsafe_allow_html=True)
    with qe:
        st.markdown("### 💡 Example")
        st.code(cq["example"], language="text")

    components.html(build_timer_html(st.session_state.timer_duration), height=82)

    st.markdown("**🎥 Camera & Recording**")
    render_camera()

    st.markdown("### 💻 Write Your Python Solution")
    user_code = st.text_area("Code", value=cq["starter"], height=270,
                             key="code_editor", label_visibility="collapsed")

    cr, cs2 = st.columns(2)
    with cr:
        if st.button("▶️ Run & Test", use_container_width=True):
            with st.spinner("Running…"):
                old = sys.stdout; sys.stdout = buf = io.StringIO()
                try:
                    exec(user_code, {"__builtins__": __builtins__})
                    sys.stdout = old
                    out = buf.getvalue()
                    st.session_state.code_result = {"type":"success",
                        "output": out if out.strip() else "✅ Ran successfully (no print output)"}
                except Exception as e:
                    sys.stdout = old
                    st.session_state.code_result = {"type":"error","output":f"❌ {type(e).__name__}: {e}"}
    with cs2:
        if st.button("🤖 AI Review", use_container_width=True, type="primary"):
            if user_code.strip():
                with st.spinner("🤖 AI reviewing your code…"):
                    ev = api_post("/evaluate-answer",{
                        "question": f"Coding problem: {cq['title']}. {cq['description']}",
                        "answer":   f"My Python solution:\n\n{user_code}",
                        "role": role, "username": st.session_state.username})
                    if ev:
                        st.session_state.code_evaluation = ev
                        st.session_state.interview_count += 1

    if st.session_state.code_result:
        r2 = st.session_state.code_result
        st.markdown("### 📤 Output")
        if r2["type"] == "error":
            st.error(r2["output"])
        else:
            st.markdown(f'<div class="code-result">{r2["output"]}</div>', unsafe_allow_html=True)

    if st.session_state.code_evaluation:
        st.markdown("---")
        render_evaluation(st.session_state.code_evaluation, "coding")


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: PERFORMANCE
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "📊 Performance":
    st.markdown("# 📊 Performance Dashboard")
    st.markdown(f"Results for **{st.session_state.username}**")
    st.markdown("---")

    stats = api_get(f"/performance/{st.session_state.username}")
    if stats and stats["total_sessions"] > 0:
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("🎯 Sessions",   stats["total_sessions"])
        with c2: st.metric("📈 Avg Score",  f"{stats['average_score']} / 10")
        with c3: st.metric("🏆 Best Score", f"{stats['best_score']} / 10")
        with c4:
            s = stats["average_score"]
            st.metric("Status", "🌟 Excellent" if s>=8 else ("✅ Good" if s>=6 else "📚 Practise"))

        import pandas as pd
        st.markdown("---")

        if stats.get("history") and len(stats["history"]) > 1:
            st.markdown("### 📈 Score Trend")
            hr = stats["history"][::-1]
            df = pd.DataFrame({"Session":list(range(1,len(hr)+1)),"Score":[h["score"] for h in hr]})
            st.line_chart(df.set_index("Session"), use_container_width=True, height=240)

        if stats.get("role_breakdown"):
            st.markdown("### 🎯 By Role")
            rb = stats["role_breakdown"]
            df2 = pd.DataFrame({"Role":list(rb.keys()),"Avg Score":list(rb.values())})
            st.bar_chart(df2.set_index("Role"), use_container_width=True, height=200)

        scores = [h["score"] for h in stats.get("history",[])]
        if scores:
            st.markdown("### 🏅 Score Breakdown")
            ca,cb,cc,cd = st.columns(4)
            with ca: st.metric("🏆 Excellent (8–10)", sum(1 for s in scores if s>=8))
            with cb: st.metric("✅ Good (6–7)",        sum(1 for s in scores if 6<=s<8))
            with cc: st.metric("⚠️ Average (4–5)",    sum(1 for s in scores if 4<=s<6))
            with cd: st.metric("❌ Needs Work (<4)",   sum(1 for s in scores if s<4))

        st.markdown("### 📋 Recent Sessions")
        for h in stats.get("history",[])[:10]:
            sc = h["score"]
            col = "green" if sc>=7 else ("orange" if sc>=4 else "red")
            st.markdown(f"**{h['timestamp']}** | {h['role']} | :{col}[**{sc}/10**]")

        st.markdown("---")
        if st.button("🗑️ Reset History", type="secondary"):
            requests.delete(f"{API_BASE}/reset/{st.session_state.username}")
            st.success("History cleared!"); st.rerun()
    else:
        st.markdown("""
        <div style="text-align:center;padding:56px;color:#1a2535;">
            <div style="font-size:60px;">📊</div>
            <h3 style="color:#2d3e50;">No sessions yet!</h3>
            <p>Complete some interviews to see your dashboard here.</p>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: LEADERBOARD
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "🏆 Leaderboard":
    st.markdown("# 🏆 Global Leaderboard")
    st.markdown("Top performers — minimum 3 sessions required to appear.")
    st.markdown("---")

    lb = api_get("/leaderboard")
    if lb and lb.get("leaderboard"):
        entries = lb["leaderboard"]
        medals  = ["🥇","🥈","🥉"]
        you = next((e for e in entries if e["username"]==st.session_state.username), None)

        if you:
            rank = entries.index(you)+1
            ca,cb,cc = st.columns(3)
            with ca:
                st.markdown(f'<div class="metric-card"><div class="metric-value">#{rank}</div>'
                            f'<div class="metric-label">Your Rank</div></div>', unsafe_allow_html=True)
            with cb:
                st.markdown(f'<div class="metric-card"><div class="metric-value">{you["avg_score"]:.1f}</div>'
                            f'<div class="metric-label">Your Avg</div></div>', unsafe_allow_html=True)
            with cc:
                st.markdown(f'<div class="metric-card"><div class="metric-value">{you["sessions"]}</div>'
                            f'<div class="metric-label">Sessions</div></div>', unsafe_allow_html=True)
            st.markdown("---")

        st.markdown("### 🏅 Rankings")
        for i, e in enumerate(entries):
            iy  = e["username"] == st.session_state.username
            rk  = medals[i] if i < 3 else f"#{i+1}"
            bw  = int((e["avg_score"]/10)*100)
            bc  = "#22c55e" if e["avg_score"]>=8 else ("#3b82f6" if e["avg_score"]>=6 else "#f59e0b")
            you_lbl = " ← <b>You</b>" if iy else ""
            cls = "lb-row lb-you" if iy else "lb-row"
            st.markdown(f"""
<div class="{cls}">
  <span style="font-size:17px;width:30px;">{rk}</span>
  <span style="flex:1;color:{'#60a5fa' if iy else '#e2e8f0'};font-weight:{'600' if iy else '400'};">
    {e['username']}{you_lbl}
  </span>
  <div style="flex:2;margin:0 12px;">
    <div style="background:#1a2535;border-radius:4px;height:5px;">
      <div style="width:{bw}%;height:100%;background:{bc};border-radius:4px;"></div>
    </div>
  </div>
  <span style="color:#60a5fa;font-weight:700;min-width:60px;text-align:right;">{e['avg_score']:.1f}/10</span>
  <span style="color:#2a3f55;font-size:12px;min-width:80px;text-align:right;">{e['sessions']} sessions</span>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:56px;color:#1a2535;">
            <div style="font-size:60px;">🏆</div>
            <h3 style="color:#2d3e50;">No leaderboard data yet!</h3>
            <p>Complete at least 3 sessions to appear here.</p>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: ABOUT
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "ℹ️ About":
    st.markdown("# 🚀 InterviewAI Pro")
    st.markdown("*Full-stack AI-powered mock interview platform for students and professionals.*")
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
### 🛠️ Tech Stack
| Layer | Technology |
|---|---|
| Frontend | Streamlit (Python) |
| Backend | FastAPI (Python) |
| AI | OpenAI GPT-3.5-turbo |
| NLP | spaCy + NLTK |
| Database | SQLite |
| Voice | Web Speech API |
| Video | Browser MediaRecorder API |
| Resume | PyPDF2 |
""")
    with c2:
        st.markdown("""
### ✨ Features
- 🎥 **Camera + Recording** — Fixed iframe permission patching
- 🎤 **3 Interview Modes** — HR, Technical, Mixed
- ⏱️ **Countdown Timer** — 30 / 60 / 90s animated ring
- 💡 **STAR Method Coach** — live guide for HR answers
- 🤖 **AI Follow-up Questions** — real interviewer simulation
- 🎙️ **Voice Interview** — browser mic → evaluate
- 📄 **Resume Interview** — personalised questions from CV
- 🧪 **Coding Challenge** — write & run Python + AI review
- 📊 **Performance Dashboard** — trends & analytics
- 🏆 **Leaderboard** — compete globally
- 🔐 **Login / Signup** — secure user accounts
""")

    st.markdown("---")
    st.markdown("""
### 📂 Project Structure
```
ai-interview-platform/
├── app.py          # Streamlit frontend (this file)
├── main.py         # FastAPI backend
└── requirements.txt
```
""")
    st.markdown("### ▶️ Run Commands")
    st.code("pip install streamlit fastapi uvicorn requests pandas PyPDF2 openai spacy nltk python-dotenv", language="bash")
    st.code("# Terminal 1 — Backend\nuvicorn main:app --reload --port 8000", language="bash")
    st.code("# Terminal 2 — Frontend\nstreamlit run app.py", language="bash")

    st.markdown("### 🔑 Camera Troubleshooting")
    st.info("""
**If camera doesn't start:**
1. Click the 🔒 padlock icon in Chrome's address bar
2. Set **Camera** → Allow
3. Set **Microphone** → Allow
4. Click **Refresh** (F5)
5. Click **Start Camera** again
""")
    st.markdown("**Built as a final-year project · Python · FastAPI · Streamlit · OpenAI · SQLite**")
