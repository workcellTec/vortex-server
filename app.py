from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "VortexDownloader Server rodando!"})

@app.route('/api/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()

        if not url:
            return jsonify({"error": "URL não informada"}), 400

        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Pega a melhor URL direta
            video_url = None
            if 'url' in info:
                video_url = info['url']
            elif 'formats' in info:
                # Pega o melhor formato mp4
                formats = [f for f in info['formats']
                           if f.get('ext') == 'mp4' and f.get('url')]
                if formats:
                    video_url = formats[-1]['url']
                elif info['formats']:
                    video_url = info['formats'][-1]['url']

            if not video_url:
                return jsonify({"error": "Não foi possível extrair o vídeo"}), 400

            title = info.get('title', 'video')
            # Remove caracteres inválidos do nome do arquivo
            filename = "".join(c for c in title if c.isalnum() or c in ' -_') + '.mp4'

            return jsonify({
                "url": video_url,
                "filename": filename,
                "platform": info.get('extractor', 'unknown')
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
