function OutputBox({
  outputText,
  onCopy,
  copied
}) {
  return (
    <div className="output-box">

      <div className="output-header">
        <span>🤖 Translation</span>

        <button
          className="copy-btn"
          onClick={onCopy}
          disabled={!outputText}
        >
          {copied ? "✅ Copied" : "📋 Copy"}
        </button>
      </div>

      <div className="output-content">
        {outputText || "Your translated text will appear here..."}
      </div>

    </div>
  );
}

export default OutputBox;

