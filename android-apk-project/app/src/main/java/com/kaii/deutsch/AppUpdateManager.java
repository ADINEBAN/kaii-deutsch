package com.kaii.deutsch;

import android.app.DownloadManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.webkit.JavascriptInterface;
import android.webkit.WebView;
import androidx.core.content.FileProvider;
import java.io.File;

public class AppUpdateManager {

    private final Context context;
    private final WebView webView;
    private long downloadId = -1;
    private Handler progressHandler;
    private Runnable progressRunnable;
    private boolean isRegistered = false;

    public AppUpdateManager(Context context, WebView webView) {
        this.context = context;
        this.webView = webView;
        this.progressHandler = new Handler(Looper.getMainLooper());
    }

    @JavascriptInterface
    public void startDownload(String apkUrl) {
        if (apkUrl == null || apkUrl.trim().isEmpty()) return;

        Uri uri = Uri.parse(apkUrl.trim());
        DownloadManager.Request request = new DownloadManager.Request(uri);
        request.setTitle("KAII Deutsch - Cập nhật");
        request.setDescription("Đang tải bản cập nhật mới...");
        request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
        request.setDestinationInExternalFilesDir(context, Environment.DIRECTORY_DOWNLOADS, "kaii_update.apk");

        // Delete existing old update file if present
        File oldApk = new File(context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS), "kaii_update.apk");
        if (oldApk.exists()) {
            oldApk.delete();
        }

        DownloadManager manager = (DownloadManager) context.getSystemService(Context.DOWNLOAD_SERVICE);
        if (manager != null) {
            downloadId = manager.enqueue(request);
            startTrackingProgress(manager);
            registerCompletionReceiver();
        }
    }

    private void startTrackingProgress(DownloadManager manager) {
        stopTrackingProgress();

        progressRunnable = new Runnable() {
            @Override
            public void run() {
                if (downloadId == -1) return;

                DownloadManager.Query query = new DownloadManager.Query();
                query.setFilterById(downloadId);
                Cursor cursor = manager.query(query);

                if (cursor != null && cursor.moveToFirst()) {
                    int bytesDownloadedIdx = cursor.getColumnIndex(DownloadManager.COLUMN_BYTES_DOWNLOADED_SO_FAR);
                    int bytesTotalIdx = cursor.getColumnIndex(DownloadManager.COLUMN_TOTAL_SIZE_BYTES);
                    int statusIdx = cursor.getColumnIndex(DownloadManager.COLUMN_STATUS);

                    long bytesDownloaded = cursor.getLong(bytesDownloadedIdx);
                    long bytesTotal = cursor.getLong(bytesTotalIdx);
                    int status = cursor.getInt(statusIdx);

                    cursor.close();

                    int percent = (bytesTotal > 0) ? (int) ((bytesDownloaded * 100) / bytesTotal) : 0;
                    postProgressToJs(percent, bytesDownloaded, bytesTotal, status);

                    if (status == DownloadManager.STATUS_SUCCESSFUL || status == DownloadManager.STATUS_FAILED) {
                        return; // Done
                    }
                } else if (cursor != null) {
                    cursor.close();
                }

                progressHandler.postDelayed(this, 300);
            }
        };

        progressHandler.post(progressRunnable);
    }

    private void stopTrackingProgress() {
        if (progressRunnable != null) {
            progressHandler.removeCallbacks(progressRunnable);
            progressRunnable = null;
        }
    }

    private void postProgressToJs(int percent, long downloaded, long total, int status) {
        webView.post(() -> {
            String js = String.format(
                "if (window.onAppDownloadProgress) { window.onAppDownloadProgress(%d, %d, %d, %d); }",
                percent, downloaded, total, status
            );
            webView.evaluateJavascript(js, null);
        });
    }

    private void registerCompletionReceiver() {
        if (isRegistered) return;

        BroadcastReceiver onComplete = new BroadcastReceiver() {
            @Override
            public void onReceive(Context c, Intent intent) {
                long id = intent.getLongExtra(DownloadManager.EXTRA_DOWNLOAD_ID, -1);
                if (id == downloadId) {
                    stopTrackingProgress();
                    installApk();
                }
            }
        };

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            context.registerReceiver(onComplete, new IntentFilter(DownloadManager.ACTION_DOWNLOAD_COMPLETE), Context.RECEIVER_EXPORTED);
        } else {
            context.registerReceiver(onComplete, new IntentFilter(DownloadManager.ACTION_DOWNLOAD_COMPLETE));
        }
        isRegistered = true;
    }

    @JavascriptInterface
    public void installApk() {
        File apkFile = new File(context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS), "kaii_update.apk");
        if (!apkFile.exists()) return;

        Intent installIntent = new Intent(Intent.ACTION_VIEW);
        installIntent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            Uri contentUri = FileProvider.getUriForFile(
                context,
                context.getPackageName() + ".fileprovider",
                apkFile
            );
            installIntent.setDataAndType(contentUri, "application/vnd.android.package-archive");
            installIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        } else {
            installIntent.setDataAndType(Uri.fromFile(apkFile), "application/vnd.android.package-archive");
        }

        try {
            context.startActivity(installIntent);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

