import http.server
import socketserver
import json
import random

PORT = 8082

# --- MOCK RL Agent ---
class RLAgent:
    def __init__(self):
        self.epsilon = 0.2
        self.ides = ["cursor", "windsurf", "claude", "vscode_cline"]
        self.q_table = {ide: 0.0 for ide in self.ides}

    def choose_ide(self):
        if random.random() < self.epsilon:
            chosen = random.choice(self.ides)
            explore = True
        else:
            chosen = max(self.q_table, key=self.q_table.get)
            explore = False
        return chosen, explore

    def update_q_value(self, ide, reward, alpha=0.1):
        current_q = self.q_table[ide]
        new_q = current_q + alpha * (reward - current_q)
        self.q_table[ide] = new_q
        return current_q, new_q

rl_agent = RLAgent()
task_counter = 0

class DemoHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

    def do_POST(self):
        global task_counter
        if self.path == '/api/task':
            task_counter += 1
            task_id = f"task-{task_counter:03d}"
            
            # Simulate pipeline
            chosen_ide, explored = rl_agent.choose_ide()
            success = random.choice([True, True, False])
            reward = 1.0 if success else -1.0
            old_q, new_q = rl_agent.update_q_value(chosen_ide, reward)

            response_data = {
                "task_id": task_id,
                "chosen_ide": chosen_ide,
                "explored": explored,
                "success": success,
                "reward": reward,
                "q_table": rl_agent.q_table,
                "old_q": old_q,
                "new_q": new_q
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())

class ReuseTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

with ReuseTCPServer(("127.0.0.1", PORT), DemoHandler) as httpd:
    print(f"Serving demo at http://localhost:{PORT}")
    httpd.serve_forever()
