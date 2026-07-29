function TranslateBox({
  inputText,
  setInputText,
  onTranslate,
  loading
}) {
  return (
    <div className="translate-box">

      <div className="input-header">
        <span>✍️ Your Text</span>
        <span>{inputText.length} characters</span>
      </div>

      <textarea
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        placeholder="Type something to translate..."
      />

      <button
        className="translate-btn"
        onClick={onTranslate}
        disabled={loading}
      >
        {loading ? "⏳ Translating..." : "🚀 Translate"}
      </button>

    </div>
  );
}

export default TranslateBox;
