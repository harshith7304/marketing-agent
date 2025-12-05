"""
Marketing AI Agent - ChatGPT-like Interface
Clean, professional chat with follow-up support
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import markdown
import os
import sys

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.graph import MarketingAgent
from knowledge_graph import MarketingKnowledgeGraph
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Marketing AI Agent", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading Marketing AI Agent...")
agent = MarketingAgent()
kg = MarketingKnowledgeGraph()
print("Ready!")

# Store conversation history
conversations = {}

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Marketing AI Agent</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f7f7f8;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        /* Header */
        .header {
            background: #fff;
            border-bottom: 1px solid #e5e5e5;
            padding: 12px 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .header h1 {
            font-size: 1.1rem;
            font-weight: 600;
            color: #202123;
        }
        
        /* Chat Container */
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        
        .chat-wrapper {
            max-width: 768px;
            margin: 0 auto;
        }
        
        /* Welcome Message */
        .welcome {
            text-align: center;
            padding: 60px 20px;
            color: #6e6e80;
        }
        
        .welcome h2 {
            font-size: 1.8rem;
            color: #202123;
            margin-bottom: 10px;
            font-weight: 600;
        }
        
        .welcome p { margin-bottom: 30px; }
        
        .suggestions {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
        }
        
        .suggestion {
            background: #fff;
            border: 1px solid #e5e5e5;
            padding: 12px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            color: #202123;
            transition: all 0.2s;
        }
        
        .suggestion:hover {
            background: #f0f0f0;
            border-color: #ccc;
        }
        
        /* Messages */
        .message {
            padding: 20px 0;
            border-bottom: 1px solid #e5e5e5;
        }
        
        .message:last-child { border-bottom: none; }
        
        .message-user {
            background: #fff;
            margin: 10px 0;
            padding: 15px 20px;
            border-radius: 12px;
            border: 1px solid #e5e5e5;
        }
        
        .message-ai {
            background: #f7f7f8;
            margin: 10px 0;
            padding: 15px 20px;
            border-radius: 12px;
        }
        
        .message-label {
            font-size: 0.75rem;
            font-weight: 600;
            color: #6e6e80;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        
        .message-content {
            color: #202123;
            line-height: 1.7;
        }
        
        .message-content h1, .message-content h2, .message-content h3 {
            color: #202123;
            margin: 16px 0 8px 0;
            font-weight: 600;
        }
        .message-content h1 { font-size: 1.3rem; }
        .message-content h2 { font-size: 1.15rem; }
        .message-content h3 { font-size: 1.05rem; }
        
        .message-content p { margin: 10px 0; }
        
        .message-content ul, .message-content ol {
            margin: 10px 0 10px 24px;
        }
        
        .message-content li { margin: 6px 0; }
        
        .message-content strong {
            font-weight: 600;
            color: #000;
        }
        
        .message-content code {
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.9em;
        }
        
        .message-content blockquote {
            border-left: 3px solid #10a37f;
            padding-left: 15px;
            margin: 10px 0;
            color: #6e6e80;
        }
        
        .message-content hr {
            border: none;
            border-top: 1px solid #e5e5e5;
            margin: 16px 0;
        }
        
        /* Input Area */
        .input-area {
            background: #fff;
            border-top: 1px solid #e5e5e5;
            padding: 20px;
        }
        
        .input-wrapper {
            max-width: 768px;
            margin: 0 auto;
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }
        
        #queryInput {
            flex: 1;
            padding: 14px 16px;
            font-size: 1rem;
            border: 1px solid #d9d9e3;
            border-radius: 12px;
            outline: none;
            resize: none;
            font-family: inherit;
            line-height: 1.5;
            max-height: 200px;
            background: #fff;
        }
        
        #queryInput:focus {
            border-color: #10a37f;
            box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.1);
        }
        
        #submitBtn {
            padding: 14px 24px;
            font-size: 1rem;
            font-weight: 500;
            background: #10a37f;
            color: #fff;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        #submitBtn:hover { background: #0d8a6a; }
        #submitBtn:disabled { background: #ccc; cursor: not-allowed; }
        
        /* Loading */
        .loading {
            display: flex;
            align-items: center;
            gap: 10px;
            color: #6e6e80;
        }
        
        .dot-pulse {
            display: flex;
            gap: 4px;
        }
        
        .dot-pulse span {
            width: 8px;
            height: 8px;
            background: #10a37f;
            border-radius: 50%;
            animation: pulse 1.4s infinite ease-in-out;
        }
        
        .dot-pulse span:nth-child(2) { animation-delay: 0.2s; }
        .dot-pulse span:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes pulse {
            0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
            40% { transform: scale(1); opacity: 1; }
        }
        
        .clear-btn {
            position: fixed;
            top: 12px;
            right: 20px;
            padding: 8px 16px;
            font-size: 0.85rem;
            background: transparent;
            color: #6e6e80;
            border: 1px solid #e5e5e5;
            border-radius: 6px;
            cursor: pointer;
        }
        
        .clear-btn:hover { background: #f0f0f0; }

        /* Feedback Controls */
        .feedback-controls {
            margin-top: 10px; 
            border-top: 1px solid #eee; 
            padding-top: 5px;
            display: flex; 
            align-items: center;
        }
        .feedback-controls button {
            border: none; 
            background: none; 
            cursor: pointer; 
            font-size: 1.1rem;
            margin-right: 8px;
            opacity: 0.6;
            transition: opacity 0.2s;
        }
        .feedback-controls button:hover { opacity: 1; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Marketing AI Agent</h1>
    </div>
    <button class="clear-btn" onclick="clearChat()">Clear Chat</button>
    
    <div class="chat-container" id="chatContainer">
        <div class="chat-wrapper" id="chatWrapper">
            <div class="welcome" id="welcome">
                <h2>How can I help you?</h2>
                <p>Ask me anything about marketing or create ad copy</p>
                <div class="suggestions">
                    <div class="suggestion" onclick="askSuggestion(this)">What are Instagram ad tips?</div>
                    <div class="suggestion" onclick="askSuggestion(this)">Create a summer sale ad</div>
                    <div class="suggestion" onclick="askSuggestion(this)">Write LinkedIn ad copy</div>
                    <div class="suggestion" onclick="askSuggestion(this)">Facebook headline ideas</div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="input-area">
        <div class="input-wrapper">
            <textarea id="queryInput" rows="1" placeholder="Message Marketing AI..." 
                onkeydown="if(event.key==='Enter' && !event.shiftKey){event.preventDefault(); ask()}"
                oninput="autoResize(this)"></textarea>
            <button id="submitBtn" onclick="ask()">Send</button>
        </div>
    </div>
    
    <script>
        let conversationId = 'conv_' + Date.now();
        
        function autoResize(el) {
            el.style.height = 'auto';
            el.style.height = Math.min(el.scrollHeight, 200) + 'px';
        }
        
        function askSuggestion(el) {
            document.getElementById('queryInput').value = el.textContent;
            ask();
        }
        
        function clearChat() {
            document.getElementById('chatWrapper').innerHTML = `
                <div class="welcome" id="welcome">
                    <h2>How can I help you?</h2>
                    <p>Ask me anything about marketing or create ad copy</p>
                    <div class="suggestions">
                        <div class="suggestion" onclick="askSuggestion(this)">What are Instagram ad tips?</div>
                        <div class="suggestion" onclick="askSuggestion(this)">Create a summer sale ad</div>
                        <div class="suggestion" onclick="askSuggestion(this)">Write LinkedIn ad copy</div>
                        <div class="suggestion" onclick="askSuggestion(this)">Facebook headline ideas</div>
                    </div>
                </div>
            `;
            conversationId = 'conv_' + Date.now();
        }

        async function sendFeedback(btn, rating, encQuery, encResponse) {
            // Decode safe URI components
            const query = decodeURIComponent(encQuery);
            const response = decodeURIComponent(encResponse);
            
            // Visual feedback
            const parent = btn.parentElement;
            parent.innerHTML = `<span style="color:#4caf50; font-size:12px">Thanks for feedback!</span>`;
            
            // Extract platform if mentioned in query (simple heuristic)
            let platform = "General";
            let lowerQuery = query.toLowerCase();
            if (lowerQuery.includes("instagram")) platform = "Instagram";
            if (lowerQuery.includes("facebook")) platform = "Facebook";
            if (lowerQuery.includes("linkedin")) platform = "LinkedIn";
            if (lowerQuery.includes("twitter")) platform = "Twitter";
            if (lowerQuery.includes("tiktok")) platform = "TikTok";
            
            try {
                await fetch('/feedback', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        query: query,
                        generated_copy: response,
                        platform: platform,
                        rating: rating,
                        context: {"source": "web_ui"}
                    })
                });
            } catch(e) { console.error(e); }
        }
        
        async function ask() {
            const input = document.getElementById('queryInput');
            const wrapper = document.getElementById('chatWrapper');
            const btn = document.getElementById('submitBtn');
            const query = input.value.trim();
            
            if (!query) return;
            
            // Remove welcome
            const welcome = document.getElementById('welcome');
            if (welcome) welcome.remove();
            
            // Add user message
            wrapper.innerHTML += `
                <div class="message">
                    <div class="message-user">
                        <div class="message-label">You</div>
                        <div class="message-content">${escapeHtml(query)}</div>
                    </div>
                    <div class="message-ai" id="aiResponse">
                        <div class="message-label">Marketing AI</div>
                        <div class="message-content">
                            <div class="loading">
                                <div class="dot-pulse"><span></span><span></span><span></span></div>
                                Thinking...
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            input.value = '';
            input.style.height = 'auto';
            btn.disabled = true;
            
            // Scroll to bottom
            const container = document.getElementById('chatContainer');
            container.scrollTop = container.scrollHeight;
            
            try {
                const res = await fetch('/run-agent?query=' + encodeURIComponent(query) + '&conv_id=' + conversationId);
                const data = await res.json();
                
                // Encode for JS attribute safety
                const encQuery = encodeURIComponent(query);
                const encResponse = encodeURIComponent(data.response);
                
                const aiResponse = document.getElementById('aiResponse');
                if (data.status === 'success') {
                    aiResponse.innerHTML = `
                        <div class="message-label">Marketing AI</div>
                        <div class="message-content">${data.html || escapeHtml(data.response)}</div>
                        <div class='feedback-controls'>
                            <small style='color:#888; margin-right:10px'>Was this helpful?</small>
                            <button onclick='sendFeedback(this, 5, "${encQuery}", "${encResponse}")'>👍</button>
                            <button onclick='sendFeedback(this, 1, "${encQuery}", "${encResponse}")'>👎</button>
                        </div>
                    `;
                } else {
                    aiResponse.innerHTML = `
                        <div class="message-label">Marketing AI</div>
                        <div class="message-content" style="color:#d32f2f">Error: ${data.message}</div>
                    `;
                }
                aiResponse.removeAttribute('id');
            } catch (e) {
                const aiResponse = document.getElementById('aiResponse');
                if (aiResponse) {
                    aiResponse.innerHTML = `
                        <div class="message-label">Marketing AI</div>
                        <div class="message-content" style="color:#d32f2f">Connection error. Try again.</div>
                    `;
                }
            }
            
            btn.disabled = false;
            container.scrollTop = container.scrollHeight;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML.replace(/"/g, '&quot;');
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    print("📢 Request received for Home Page")
    return HTML_PAGE


@app.get("/run-agent")
def run_agent(query: str, conv_id: str = "default"):
    """Main AI agent endpoint with conversation support"""
    try:
        # Get conversation history
        if conv_id not in conversations:
            conversations[conv_id] = []
        
        # Add context from previous messages (last 3)
        history = conversations[conv_id][-3:]
        context = ""
        if history:
            context = "Previous conversation:\n" + "\n".join([f"User: {h['q']}\nAI: {h['a'][:200]}..." for h in history]) + "\n\nCurrent question: "
        
        # Run agent
        result = agent.run(query=context + query if context else query)
        response_text = result.get("response", "")
        
        # Save to history
        conversations[conv_id].append({"q": query, "a": response_text})
        
        # Keep only last 10 messages
        if len(conversations[conv_id]) > 10:
            conversations[conv_id] = conversations[conv_id][-10:]
        
        # Convert to HTML
        html_response = markdown.markdown(response_text, extensions=['extra', 'nl2br'])
        
        return {
            "status": "success",
            "query": query,
            "response": response_text,
            "html": html_response,
            "type": result.get("query_type", "qa")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/run-agent")
def run_agent_post(query: str, conv_id: str = "default"):
    return run_agent(query, conv_id)

class FeedbackRequest(BaseModel):
    query: str
    generated_copy: str
    platform: str
    rating: int
    context: dict = {}

@app.post("/feedback")
def submit_feedback(feedback: FeedbackRequest):
    """Submit feedback for the learning loop"""
    try:
        agent.memory.add_feedback(
            query=feedback.query,
            generated_copy=feedback.generated_copy,
            platform=feedback.platform,
            rating=feedback.rating,
            context=feedback.context
        )
        print(f"✅ Feedback received: {feedback.rating}/5 stars for platform {feedback.platform}")
        return {"status": "success", "rating": feedback.rating}
    except Exception as e:
        print(f"❌ Feedback error: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Use 127.0.0.1 explicitly to avoid IPv6 issues if any
    uvicorn.run(app, host="127.0.0.1", port=8000)