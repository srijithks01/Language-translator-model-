function LanguageSelector({
  languages,
  sourceLang,
  targetLang,
  setSourceLang,
  setTargetLang,
  onSwap
}) {
  return (
    <div className="language-section">

      <div className="language-box">
        <label>From</label>

        <select
          value={sourceLang}
          onChange={(e) => setSourceLang(e.target.value)}
        >
          {Object.entries(languages).map(([code, name]) => (
            <option key={code} value={code}>
              {name}
            </option>
          ))}
        </select>
      </div>

      <button className="swap-btn" onClick={onSwap}>
        ⇄
      </button>

      <div className="language-box">
        <label>To</label>

        <select
          value={targetLang}
          onChange={(e) => setTargetLang(e.target.value)}
        >
          {Object.entries(languages)
            .filter(([code]) => code !== "auto")
            .map(([code, name]) => (
              <option key={code} value={code}>
                {name}
              </option>
            ))}
        </select>
      </div>

    </div>
  );
}

export default LanguageSelector;