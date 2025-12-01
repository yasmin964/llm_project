import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from http.server import BaseHTTPRequestHandler
from bot.telegram_bot import process_webhook_update


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            update = json.loads(post_data)

            response = process_webhook_update(update)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            print(f"Error in webhook: {e}")
            self.send_response(500)
            self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is running on Vercel!")

    def log_message(self, format, *args):
        pass