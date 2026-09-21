import React, { useEffect, useRef, useState } from "react";
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib";
import { Payload, Period } from "./contracts";
import IntradayChangeSummary from "./IntradayChangeSummary";
import AssetChangeStrip from "./AssetChangeStrip";
import ObservationReading from "./ObservationReading";
import "./style.css";

function FuturesMacroWorkbench({ args, disabled }: ComponentProps) {
  const payload = args.payload as Payload;
  const [period, setPeriod] = useState<Period>("since_close");
  const [pending, setPending] = useState<string | null>(null);
  const pendingRef = useRef<string | null>(null);
  useEffect(() => {
    if (
      pendingRef.current &&
      payload.command?.ack_nonce === pendingRef.current
    ) {
      pendingRef.current = null;
      setPending(null);
    }
  }, [payload.command?.ack_nonce]);
  useEffect(() => {
    const observer = new ResizeObserver(() => Streamlit.setFrameHeight());
    observer.observe(document.body);
    Streamlit.setFrameHeight();
    return () => observer.disconnect();
  }, []);
  const emit = (id: string) => {
    if (pendingRef.current || disabled || payload.command?.pending) return;
    const nonce = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
    pendingRef.current = nonce;
    setPending(nonce);
    Streamlit.setComponentValue({ event: { id, nonce } });
  };
  const w = payload.windows[period];
  const locked = Boolean(pending || disabled || payload.command?.pending);
  return (
    <main className="fm">
      <header className="masthead">
        <div>
          <p className="eyebrow">FUTURES MACRO · 선물 매크로</p>
          <h1>선물로 읽는 시장의 변화</h1>
          <p className="subtitle">
            주가지수의 방향과 금리·달러의 지지 또는 부담을 함께 확인합니다.
          </p>
        </div>
        <button
          className="primary"
          disabled={locked}
          onClick={() => emit("daily_refresh")}
        >
          {pending ? "자료 확인 중…" : "최신 데이터 반영"}
        </button>
      </header>
      <div className="topline">
        <div className="segments" aria-label="비교 구간">
          {(["since_close", "last_hour"] as Period[]).map((p) => (
            <button
              key={p}
              aria-pressed={period === p}
              onClick={() => setPeriod(p)}
            >
              {p === "since_close" ? "미국장 마감 이후" : "최근 1시간"}
            </button>
          ))}
        </div>
        <span className="muted">수동 갱신 · 완료 5분봉 기준</span>
      </div>
      {payload.command?.result?.message && (
        <p role="status" className={`notice ${payload.command.result.status}`}>
          {payload.command.result.message}
        </p>
      )}
      <IntradayChangeSummary window={w} />
      <AssetChangeStrip window={w} />
      <ObservationReading reading={w.reading} />
      <div className="cycle">
        <span>
          <b>경기국면은 월간 배경</b> · {payload.cycle_background.state} ·{" "}
          {payload.cycle_background.as_of_date || "기준일 없음"}
        </span>
        <button disabled={locked} onClick={() => emit("economic_cycle")}>
          경기국면 보기 ↗
        </button>
        <p>
          이 화면은 선택한 시간 구간의 가격 반응을 봅니다. 경제자료로 판단한
          경기국면과 기준이 다릅니다.
        </p>
      </div>
      <details className="source-details">
        <summary>지표 구성과 계산 기준</summary>
        <div className="evidence">
          <p>
            {w.evidence.source} · 미국 정규장 마감 일정{" "}
            {w.evidence.calendar_quality === "CONFIRMED"
              ? "확인됨"
              : "확인 필요"}
          </p>
          <p>핵심 비교 자료 누락: {w.missing_symbols.join(", ") || "없음"}</p>
          {w.evidence.caveats.map((c) => (
            <p key={c}>{c}</p>
          ))}
          <p>
            표시 단위 0.01%에서 상승·하락·보합을 구분합니다. 작은 변화의 부호가
            경제적으로 큰 영향을 뜻하지는 않습니다.
          </p>
          <p>
            국채·달러의 지지·부담은 가격 조합에 대한 해석입니다. 업종과 기업의
            노출에 따라 영향은 다를 수 있습니다.
          </p>
          <p>
            장중 조건의 이후 수익률은 아직 검증하지 않았으며 상승·하락 확률을
            제공하지 않습니다.
          </p>
        </div>
      </details>
      <details className="source-details">
        <summary>추가 관측 근거</summary>
        <ul className="evidence">
          {w.reading.observation_facts.length ? (
            w.reading.observation_facts.map((f) => <li key={f}>{f}</li>)
          ) : (
            <li>비교할 가격이 아직 없습니다.</li>
          )}
        </ul>
      </details>
    </main>
  );
}
export default withStreamlitConnection(FuturesMacroWorkbench);
