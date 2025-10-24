import streamlit as st
import os
import base64
import json

def load_images_as_dataurls(folder):
    dataurls = []
    if not os.path.exists(folder):
        return dataurls
    for fn in sorted(os.listdir(folder)):
        if fn.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            path = os.path.join(folder, fn)
            with open(path, "rb") as f:
                b = f.read()
                mime = "image/png"
                if fn.lower().endswith(".jpg") or fn.lower().endswith(".jpeg"):
                    mime = "image/jpeg"
                elif fn.lower().endswith(".gif"):
                    mime = "image/gif"
                elif fn.lower().endswith(".webp"):
                    mime = "image/webp"
                data = base64.b64encode(b).decode("utf-8")
                dataurls.append(f"data:{mime};base64,{data}")
    return dataurls


def main():
    st.set_page_config(page_title="Archery Management System", layout="wide")

    
    # ============ MAIN CONTENT ============
    # Hiển thị logo ở chính giữa đầu trang
    col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 2, 2, 2, 1, 1])
    with col4:
        st.image("images/logo.png", width=150)
    st.title("🏹 Archery Management System")
    st.markdown("""
    <div style="text-align: justify; font-size: 18px;">
    Welcome to the <b>Archery Management System</b>, a comprehensive online platform designed to bring together archery enthusiasts, athletes, and clubs in one digital space. Our mission is to simplify the way tournaments, scores, and community connections are managed, providing a modern solution for both organizers and participants. Whether you are a beginner or a professional archer, our system ensures a seamless experience from registration to performance tracking.
    <br><br>
    Our services cover every essential aspect of archery management. Users can <b>register for national or local tournaments</b>, explore and <b>join official archery clubs</b>, and even <b>build friendships</b> with other members through a social feature similar to Facebook’s friend connection. Participants can <b>track and update their shooting scores</b>, view historical performance, and compare results by <b>category, competition, or ranking</b>. For clubs and event organizers, the system offers tools to manage members, schedule events, and publish results quickly and transparently.
    <br><br>
    Beyond functionality, the Archery Management System aims to foster a vibrant and supportive archery community. We believe technology can strengthen the connection between archers, clubs, and associations — helping them share knowledge, celebrate achievements, and grow the sport together. With an intuitive interface and constantly evolving features, our platform is built to make archery more accessible, organized, and enjoyable for everyone.
    </div>
    """, unsafe_allow_html=True)

    
    if not st.session_state.get("logged_in", False):
        st.info("🔒 Please log in or sign up to view posters and documentation.")
        return

    st.success(f"Welcome back, {st.session_state.get('fullname', 'User')}!")
    st.divider()

    # -----------------------
    # Slideshow Poster
    # -----------------------
    st.subheader("📸 Upcoming Archery Posters & Events")

    poster_folder = os.path.join(os.path.dirname(__file__), "posters")
    pos = load_images_as_dataurls(poster_folder)

    if pos:
        interval_ms = 7000
        images_json = json.dumps(pos)
        html = f"""
        <style>
        .carousel-wrapper {{
            width: 100%;
            display:flex;
            justify-content:center;
            align-items:center;
            margin-bottom: 10px;
        }}
        .carousel-main {{
            max-height: 650px;
            width: auto;
            transition: opacity 0.6s ease, transform 0.6s ease;
            border-radius: 8px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.15);
            display:block;
            margin: 0 auto;
        }}
        .thumbs {{
            margin-top:8px;
            display:flex;
            gap:8px;
            justify-content:center;
            align-items:center;
            flex-wrap:wrap;
        }}
        .thumbs img {{
            width:80px;
            height:60px;
            object-fit:cover;
            opacity:0.4;
            border-radius:6px;
            transition: opacity 0.25s ease, transform 0.25s ease;
            cursor:pointer;
        }}
        .thumbs img.active {{
            opacity:1;
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        </style>

        <div id="carousel" class="carousel-wrapper">
            <img id="carousel-main" class="carousel-main" src="{pos[0]}">
        </div>
        <div id="thumbs" class="thumbs"></div>

        <script>
        const images = {images_json};
        let idx = 0;
        const main = document.getElementById("carousel-main");
        const thumbs = document.getElementById("thumbs");

        images.forEach((src, i) => {{
            const t = document.createElement("img");
            t.src = src;
            t.dataset.index = i;
            if(i===0) t.classList.add("active");
            t.onclick = () => {{
                idx = i;
                update();
                resetInterval();
            }};
            thumbs.appendChild(t);
        }});

        function update() {{
            main.style.opacity = 0;
            setTimeout(() => {{
                main.src = images[idx];
                main.style.opacity = 1;
                document.querySelectorAll("#thumbs img").forEach(img => img.classList.remove("active"));
                const activeThumb = document.querySelector(`#thumbs img[data-index='{'}${idx}{'}']`);
                if(activeThumb) activeThumb.classList.add("active");
            }}, 300);
        }}

        let interval = setInterval(() => {{
            idx = (idx + 1) % images.length;
            update();
        }}, {interval_ms});

        function resetInterval() {{
            clearInterval(interval);
            interval = setInterval(() => {{
                idx = (idx + 1) % images.length;
                update();
            }}, {interval_ms});
        }}
        </script>
        """

        st.components.v1.html(html, height=760, scrolling=False)
    else:
        st.warning("⚠️ No images found in the 'posters' folder.")

    st.divider()

    # -----------------------
    # PDF Viewer + Download
    # -----------------------
    st.subheader("📘 Further Information and Documentation")

    pdf_folder = os.path.join(os.path.dirname(__file__), "pdfs")
    if not os.path.exists(pdf_folder):
        st.warning("⚠️ 'pdfs' folder not found.")
    else:
        pdf_files = [f for f in sorted(os.listdir(pdf_folder)) if f.lower().endswith(".pdf")]
        if not pdf_files:
            st.warning("⚠️ No PDF files found in the 'pdfs' folder.")
        else:
            for pdf in pdf_files:
                pdf_path = os.path.join(pdf_folder, pdf)
                with st.expander(f"📄 {pdf}"):
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                        b64 = base64.b64encode(pdf_bytes).decode("utf-8")

                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name=pdf,
                        mime="application/pdf"
                    )

                    st.markdown(
                        f"""
                        <iframe src="data:application/pdf;base64,{b64}" width="100%" height="800" style="border:none;"></iframe>
                        """,
                        unsafe_allow_html=True
                    )


if __name__ == "__main__":
    main()
