package com.kaii.deutsch;

import android.content.Context;
import android.os.Build;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.webkit.JavascriptInterface;
import android.webkit.WebView;
import java.util.Locale;

public class NativeTTSInterface {

    private final Context context;
    private final WebView webView;
    private TextToSpeech textToSpeech;
    private boolean isReady = false;

    public NativeTTSInterface(Context context, WebView webView) {
        this.context = context;
        this.webView = webView;
        initTTS();
    }

    private void initTTS() {
        textToSpeech = new TextToSpeech(context, status -> {
            if (status == TextToSpeech.SUCCESS) {
                int result = textToSpeech.setLanguage(Locale.GERMAN);
                if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                    // Try German Germany specifically
                    result = textToSpeech.setLanguage(Locale.GERMANY);
                }
                isReady = (result != TextToSpeech.LANG_MISSING_DATA && result != TextToSpeech.LANG_NOT_SUPPORTED);
                textToSpeech.setSpeechRate(0.92f);
                textToSpeech.setPitch(1.0f);
            } else {
                isReady = false;
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
        webView.post(() -> {
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
        if (!isReady || textToSpeech == null) {
            // Re-attempt init if not ready
            if (textToSpeech != null) {
                int res = textToSpeech.setLanguage(Locale.GERMAN);
                if (res != TextToSpeech.LANG_MISSING_DATA && res != TextToSpeech.LANG_NOT_SUPPORTED) {
                    isReady = true;
                }
            }
        }

        if (textToSpeech != null && text != null && !text.trim().isEmpty()) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                textToSpeech.speak(text.trim(), TextToSpeech.QUEUE_FLUSH, null, "utterance_" + System.currentTimeMillis());
            } else {
                textToSpeech.speak(text.trim(), TextToSpeech.QUEUE_FLUSH, null);
            }
            return true;
        }
        return false;
    }

    @JavascriptInterface
    public void stop() {
        if (textToSpeech != null) {
            textToSpeech.stop();
        }
    }

    public void destroy() {
        if (textToSpeech != null) {
            textToSpeech.stop();
            textToSpeech.shutdown();
            textToSpeech = null;
        }
    }
}

