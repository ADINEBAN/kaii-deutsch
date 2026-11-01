FROM thorstenvoice/kokoro-tts:latest

# Hugging Face Spaces runs as user 1000 with exposed port 7860
EXPOSE 7860

# Override default port 8000 to 7860 for Hugging Face Spaces compatibility
ENV PORT=7860

# Kokoro container entrypoint starts on port 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]

