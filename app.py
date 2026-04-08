import os
import json
from flask import Flask, request, jsonify, render_template_string
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SlideForge AI</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#0a0a0f;color:#e0e0e0;min-height:100vh}
.container{max-width:900px;margin:0 auto;padding:2rem}
h1{font-size:2rem;font-weight:800;margin-bottom:2rem;background:linear-gradient(135deg,#6366f1,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.form-group{margin-bottom:1.5rem}
label{display:block;margin-bottom:0.5rem;font-weight:600;color:#d1d5db}
input,select,textarea{width:100%;padding:0.8rem 1rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:10px;color:#fff;font-size:1rem;outline:none}
input:focus,select:focus,textarea:focus{border-color:#6366f1}
select option{background:#1a1a2e;color:#fff}
.btn{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;border:none;padding:1rem 2rem;border-radius:10px;font-size:1.1rem;font-weight:700;cursor:pointer;width:100%;transition:opacity .2s}
.btn:hover{opacity:0.9}
.btn:disabled{opacity:0.5;cursor:not-allowed}
.result{margin-top:2rem;display:none}
.slide{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:1.5rem;margin-bottom:1.5rem}
.slide-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem}
.slide-num{background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:0.3rem 0.8rem;border-radius:6px;font-size:0.8rem;font-weight:700}
.slide h3{color:#fff;font-size:1.2rem;margin-bottom:0.8rem}
.slide ul{margin-left:1.2rem;margin-bottom:1rem}
.slide li{margin-bottom:0.3rem;color:#d1d5db}
.notes{background:rgba(99,102,241,0.08);border-left:3px solid #6366f1;padding:0.8rem 1rem;border-radius:0 8px 8px 0;font-size:0.9rem;color:#9ca3af;margin-bottom:0.8rem}
.design{font-size:0.85rem;color:#6366f1;font-style:italic}
.json-toggle{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:#a78bfa;padding:0.5rem 1rem;border-radius:8px;cursor:pointer;font-size:0.9rem;margin-top:1rem}
.json-raw{display:none;margin-top:1rem;background:rgba(0,0,0,0.3);padding:1rem;border-radius:10px;overflow-x:auto;font-family:monospace;font-size:0.85rem;white-space:pre-wrap;max-height:400px;overflow-y:auto}
.loading{display:none;text-align:center;padding:3rem;color:#9ca3af;font-size:1.1rem}
.spinner{display:inline-block;width:24px;height:24px;border:3px solid rgba(99,102,241,0.3);border-top-color:#6366f1;border-radius:50%;animation:spin 0.8s linear infinite;margin-right:0.5rem;vertical-align:middle}
@keyframes spin{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="container">
<h1>SlideForge AI</h1>
<form id="form">
<div class="form-group"><label>Presentation Topic</label><input type="text" id="topic" placeholder="e.g., Q3 Revenue Growth Strategy" required></div>
<div class="form-group"><label>Target Audience</label><input type="text" id="audience" placeholder="e.g., Executive leadership team" required></div>
<div class="form-group"><label>Number of Slides</label><select id="slides">
<option value="5">5 slides</option><option value="8">8 slides</option><option value="10" selected>10 slides</option><option value="15">15 slides</option><option value="20">20 slides</option>
</select></div>
<div class="form-group"><label>Additional Context (optional)</label><textarea id="context" rows="3" placeholder="Any specific points, data, or themes to include..."></textarea></div>
<button type="submit" class="btn" id="submitBtn">Generate Presentation</button>
</form>
<div class="loading" id="loading"><span class="spinner"></span> Generating your presentation...</div>
<div class="result" id="result"></div>
</div>
<script>
document.getElementById('form').addEventListener('submit',async e=>{
e.preventDefault();
const btn=document.getElementById('submitBtn');
const loading=document.getElementById('loading');
const result=document.getElementById('result');
btn.disabled=true;loading.style.display='block';result.style.display='none';
try{
const r=await fetch('/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({topic:document.getElementById('topic').value,audience:document.getElementById('audience').value,slide_count:document.getElementById('slides').value,context:document.getElementById('context').value})});
const data=await r.json();
if(data.error){result.innerHTML='<p style="color:#ef4444">'+data.error+'</p>';result.style.display='block';return}
let html='';
data.slides.forEach((s,i)=>{
html+=`<div class="slide"><div class="slide-header"><span class="slide-num">Slide ${i+1}</span></div><h3>${s.title}</h3><ul>${s.bullet_points.map(b=>'<li>'+b+'</li>').join('')}</ul><div class="notes"><strong>Speaker Notes:</strong> ${s.speaker_notes}</div><div class="design">${s.design_suggestion}</div></div>`;
});
html+=`<button class="json-toggle" onclick="let el=document.getElementById('jsonraw');el.style.display=el.style.display==='none'?'block':'none'">Toggle JSON</button><div class="json-raw" id="jsonraw">${JSON.stringify(data,null,2)}</div>`;
result.innerHTML=html;result.style.display='block';
}catch(err){result.innerHTML='<p style="color:#ef4444">Error: '+err.message+'</p>';result.style.display='block';}
finally{btn.disabled=false;loading.style.display='none';}
});
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    topic = data.get("topic", "")
    audience = data.get("audience", "")
    slide_count = int(data.get("slide_count", 10))
    context = data.get("context", "")

    prompt = f"""Create a professional presentation outline with exactly {slide_count} slides.

Topic: {topic}
Target Audience: {audience}
Additional Context: {context}

Return ONLY valid JSON with this structure:
{{
  "title": "Presentation Title",
  "audience": "{audience}",
  "slides": [
    {{
      "title": "Slide Title",
      "bullet_points": ["Point 1", "Point 2", "Point 3"],
      "speaker_notes": "What to say during this slide...",
      "design_suggestion": "Suggested visual: chart type, image, layout idea"
    }}
  ],
  "design_theme": {{
    "primary_color": "#hex",
    "font_suggestion": "Font name",
    "overall_style": "Style description"
  }}
}}

Make content specific, actionable, and tailored to the audience. Include a title slide and a closing/Q&A slide."""

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        result = json.loads(text)
        return jsonify(result)
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse AI response. Please try again."})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
