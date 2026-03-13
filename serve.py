"""Open the quiz app in your browser. Run: python serve.py"""
import http.server, webbrowser, threading, os

PORT = 8080
os.chdir(os.path.dirname(os.path.abspath(__file__)))
threading.Timer(0.5, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
print(f"Serving at http://localhost:{PORT}  (Ctrl+C to stop)")
http.server.HTTPServer(("", PORT), http.server.SimpleHTTPRequestHandler).serve_forever()
