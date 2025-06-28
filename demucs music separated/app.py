import os
import subprocess
import yt_dlp
import streamlit as st

st.set_page_config(page_title="Demucs Audio Separation", page_icon="🎵", layout="centered")
st.title(" Demucs 分離音源")
st.write("輸入 YouTube 音樂連結，將自動下載並使用 Demucs 分離聲部。")

youtube_url = st.text_input("YouTube 連結", placeholder="https://www.youtube.com/watch?v=example")

if st.button("start separate") and youtube_url:
    with st.spinner("Downloading and processing audio..."):
        os.makedirs("downloads", exist_ok=True)

        # yt-dlp 設定
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            title = info.get("title", "output")
            audio_path = f"downloads/{title}.wav"

    st.success("Audio downloaded successfully!")

    with st.spinner(" 正在進行 Demucs 音源分離..."):
        try:
            subprocess.run(["demucs", audio_path], check=True)
        except FileNotFoundError:
            st.error
            st.stop()
        except subprocess.CalledProcessError as e:
            st.error(f" Demucs 分離失敗：{e}")
            st.stop()

    st.success("Audio downloaded successfully!")

    # 音檔輸出路徑
    sep_dir = f"separated/htdemucs/{os.path.splitext(os.path.basename(audio_path))[0]}"

    st.markdown("### 🎵 分離後音軌預覽與下載：")
    for part in ["vocals", "drums", "bass", "other"]:
        part_path = os.path.join(sep_dir, f"{part}.wav")
        if os.path.exists(part_path):
            st.audio(part_path, format="audio/wav")
            with open(part_path, "rb") as f:
                st.download_button(f"下載 {part}.wav", f, file_name=f"{part}.wav")
        else:
            st.warning(f"找不到 {part}.wav")
