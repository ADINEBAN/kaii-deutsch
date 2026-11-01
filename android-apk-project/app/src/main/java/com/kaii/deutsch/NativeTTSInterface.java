package com.kaii.deutsch;

import android.content.Context;
import android.media.AudioAttributes;
import android.media.AudioManager;
import android.media.MediaPlayer;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.webkit.JavascriptInterface;
import android.webkit.WebView;
import android.widget.Toast;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class NativeTTSInterface {

    private final Context context;
    private final WebView webView;
    private final Handler mainHandler;
    private final ExecutorService executor;

    private MediaPlayer mediaPlayer;
    private TextToSpeech textToSpeech;
    private boolean isTtsReady = false;

    public NativeTTSInterface(Context context, WebView webView) {
        this.context = context;
        this.webView = webView;
        this.mainHandler = new Handler(Looper.getMainLooper());
        this.executor = Executors.newSingleThreadExecutor();
        initTTS();
    }

    private void initTTS() {
        textToSpeech = new TextToSpeech(context, status -> {
            if (status == TextToSpeech.SUCCESS) {
                int result = textToSpeech.setLanguage(Locale.GERMAN);
                if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                    result = textToSpeech.setLanguage(Locale.GERMANY);
                }
                isTtsReady = (result != TextToSpeech.LANG_MISSING_DATA && result != TextToSpeech.LANG_NOT_SUPPORTED);
                textToSpeech.setSpeechRate(0.92f);
                textToSpeech.setPitch(1.0f);
            } else {
                isTtsReady = false;
            }
        });

        textToSpeech.setOnUtteranceProgressListener(new UtteranceProgressListener() {
            @Override
            public void onStart(String utteranceId) {
                postJsState(true);
            }

            @Override
            public void onDone(String utteranceId) {
                postJsState(false);
            }

            @Override
            public void onError(String utteranceId) {
                postJsState(false);
            }
        });
    }

    private void postJsState(boolean isSpeaking) {
        mainHandler.post(() -> {
            String js = "if (window.onNativeTtsStateChange) { window.onNativeTtsStateChange(" + isSpeaking + "); }";
            webView.evaluateJavascript(js, null);
        });
    }

    @JavascriptInterface
    public boolean isSupported() {
        return true;
    }

    @JavascriptInterface
    public boolean speak(String text) {
        if (text == null || text.trim().isEmpty()) return false;
        final String cleanText = text.trim();

        // Stop any current sound before starting new
        stop();

        executor.execute(() -> processTtsRequest(cleanText));
        return true;
    }

    private void processTtsRequest(String text) {
        try {
            File cacheDir = new File(context.getCacheDir(), "tts_cache");
            if (!cacheDir.exists()) cacheDir.mkdirs();
            File cachedFile = new File(cacheDir, "de_" + md5(text) + ".mp3");

            // 1. Play from disk cache if exists
            if (cachedFile.exists() && cachedFile.length() > 200) {
                playLocalAudio(cachedFile);
                return;
            }

            // 2. Fetch from Google German Cloud Neural TTS
            List<String> chunks = splitIntoChunks(text, 100);
            ByteArrayOutputStream combined = new ByteArrayOutputStream();
            boolean fetchSuccess = true;

            for (String chunk : chunks) {
                byte[] data = fetchCloudAudioChunk(chunk);
                if (data != null && data.length > 50) {
                    combined.write(data);
                } else {
                    fetchSuccess = false;
                    break;
                }
            }

            if (fetchSuccess && combined.size() > 200) {
                File tempFile = new File(cacheDir, "tmp_" + System.currentTimeMillis() + ".mp3");
                try (FileOutputStream fos = new FileOutputStream(tempFile)) {
                    fos.write(combined.toByteArray());
                }
                if (cachedFile.exists()) cachedFile.delete();
                tempFile.renameTo(cachedFile);
                playLocalAudio(cachedFile);
                return;
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        // 3. Fallback to Android Native TextToSpeech engine
        mainHandler.post(() -> playOfflineTTS(text));
    }

    private byte[] fetchCloudAudioChunk(String chunk) {
        try {
            String encoded = URLEncoder.encode(chunk, "UTF-8");
            String urlStr = "https://translate.google.com/translate_tts?ie=UTF-8&q=" + encoded + "&tl=de-DE&client=tw-ob";
            HttpURLConnection conn = (HttpURLConnection) new URL(urlStr).openConnection();
            conn.setRequestMethod("GET");
            conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36");
            conn.setConnectTimeout(4000);
            conn.setReadTimeout(7000);

            if (conn.getResponseCode() == 200) {
                try (InputStream in = conn.getInputStream(); ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
                    byte[] buf = new byte[4096];
                    int len;
                    while ((len = in.read(buf)) > 0) {
                        baos.write(buf, 0, len);
                    }
                    return baos.toByteArray();
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    private synchronized void playLocalAudio(File file) {
        mainHandler.post(() -> {
            try {
                stopCurrentAudio();
                mediaPlayer = new MediaPlayer();
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    mediaPlayer.setAudioAttributes(new AudioAttributes.Builder()
                            .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                            .setUsage(AudioAttributes.USAGE_MEDIA)
                            .build());
                } else {
                    mediaPlayer.setAudioStreamType(AudioManager.STREAM_MUSIC);
                }
                mediaPlayer.setDataSource(file.getAbsolutePath());
                mediaPlayer.setOnPreparedListener(mp -> {
                    postJsState(true);
                    mp.start();
                });
                mediaPlayer.setOnCompletionListener(mp -> {
                    postJsState(false);
                    stopCurrentAudio();
                });
                mediaPlayer.setOnErrorListener((mp, what, extra) -> {
                    postJsState(false);
                    stopCurrentAudio();
                    return true;
                });
                mediaPlayer.prepareAsync();
            } catch (Exception e) {
                postJsState(false);
            }
        });
    }

    private void playOfflineTTS(String text) {
        if (isTtsReady && textToSpeech != null) {
            postJsState(true);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                textToSpeech.speak(text.trim(), TextToSpeech.QUEUE_FLUSH, null, "utt_" + System.currentTimeMillis());
            } else {
                textToSpeech.speak(text.trim(), TextToSpeech.QUEUE_FLUSH, null);
            }
        } else {
            postJsState(false);
            Toast.makeText(context, "Đang cần mạng tải âm thanh tiếng Đức", Toast.LENGTH_SHORT).show();
        }
    }

    private synchronized void stopCurrentAudio() {
        if (mediaPlayer != null) {
            try {
                if (mediaPlayer.isPlaying()) {
                    mediaPlayer.stop();
                }
                mediaPlayer.reset();
                mediaPlayer.release();
            } catch (Exception ignored) {}
            mediaPlayer = null;
        }
    }

    @JavascriptInterface
    public void stop() {
        mainHandler.post(() -> {
            stopCurrentAudio();
            if (textToSpeech != null) {
                try {
                    textToSpeech.stop();
                } catch (Exception ignored) {}
            }
            postJsState(false);
        });
    }

    private List<String> splitIntoChunks(String text, int maxLen) {
        List<String> chunks = new ArrayList<>();
        if (text == null || text.trim().isEmpty()) return chunks;
        text = text.trim();
        if (text.length() <= maxLen) {
            chunks.add(text);
            return chunks;
        }

        String[] sentences = text.split("(?<=[.!?])\\s+");
        for (String s : sentences) {
            if (s.length() <= maxLen) {
                chunks.add(s);
            } else {
                String[] clauses = s.split("(?<=[,;])\\s+");
                for (String c : clauses) {
                    if (c.length() <= maxLen) {
                        chunks.add(c);
                    } else {
                        String[] words = c.split("\\s+");
                        StringBuilder sb = new StringBuilder();
                        for (String w : words) {
                            if (sb.length() + w.length() + 1 > maxLen) {
                                if (sb.length() > 0) chunks.add(sb.toString().trim());
                                sb = new StringBuilder();
                            }
                            if (sb.length() > 0) sb.append(" ");
                            sb.append(w);
                        }
                        if (sb.length() > 0) chunks.add(sb.toString().trim());
                    }
                }
            }
        }
        return chunks;
    }

    private String md5(String s) {
        try {
            MessageDigest digest = MessageDigest.getInstance("MD5");
            digest.update(s.getBytes("UTF-8"));
            byte[] messageDigest = digest.digest();
            StringBuilder hexString = new StringBuilder();
            for (byte b : messageDigest) {
                String h = Integer.toHexString(0xFF & b);
                while (h.length() < 2) h = "0" + h;
                hexString.append(h);
            }
            return hexString.toString();
        } catch (Exception e) {
            return String.valueOf(s.hashCode());
        }
    }

    public void destroy() {
        stop();
        if (textToSpeech != null) {
            try {
                textToSpeech.stop();
                textToSpeech.shutdown();
            } catch (Exception ignored) {}
            textToSpeech = null;
        }
        if (executor != null && !executor.isShutdown()) {
            executor.shutdownNow();
        }
    }
}
