// Utility for recording audio and returning a Blob
export async function recordAudio() {
  if (!navigator.mediaDevices) throw new Error("Audio recording not supported");
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mediaRecorder = new MediaRecorder(stream);
  let chunks = [];

  return new Promise((resolve, reject) => {
    mediaRecorder.ondataavailable = e => chunks.push(e.data);
    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, { type: 'audio/webm' });
      resolve(blob);
    };
    mediaRecorder.onerror = reject;
    mediaRecorder.start();
    setTimeout(() => {
      mediaRecorder.stop();
      stream.getTracks().forEach(track => track.stop());
    }, 5000); // 5 seconds max
  });
}

// Utility to play audio from a Blob or URL
export function playAudio(blobOrUrl, audioElement) {
  if (blobOrUrl instanceof Blob) {
    audioElement.src = URL.createObjectURL(blobOrUrl);
  } else {
    audioElement.src = blobOrUrl;
  }
  audioElement.style.display = 'block';
  audioElement.play();
}
