# Notes

- Browser reproduction before implementation showed the preflight iframe loads `src="/assets/index-DEqo_suL.js"` and Chrome rejects it because the server returns HTML with MIME type `text/html`.
- Other working Streamlit React components use Vite `base: "./"` and built `./assets/...` paths.
- Strategy detail form ownership currently lives in `app/web/backtest_single_forms/`; React detail panel should remain read-only until Streamlit form state migration is intentionally designed.

