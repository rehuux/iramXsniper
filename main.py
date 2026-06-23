from flask import Flask, jsonify
import config
import database as db

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    stats = db.get_stats(0)  # total across all users – we can improve
    return jsonify({
        "status": "ok",
        "bot": config.BOT_NAME,
        "pending": stats['pending'],
        "claimed": stats['claimed'],
        "total": stats['total']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.PORT)
