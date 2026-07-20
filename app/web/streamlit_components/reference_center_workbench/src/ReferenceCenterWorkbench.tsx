import React, { useEffect, useMemo, useState } from "react";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import type { ReferenceCenterPayload, ReferenceItem, ReferenceScope } from "./contracts";
import { searchReferenceItems } from "./search";
import "./style.css";


const KIND_LABELS: Record<ReferenceItem["kind"], string> = {
  journey: "사용 흐름",
  concept: "상태·용어",
  playbook: "문제 해결",
};

function syncFrameHeightSoon(): void {
  Streamlit.setFrameHeight();
  window.requestAnimationFrame(() => Streamlit.setFrameHeight());
  window.setTimeout(() => Streamlit.setFrameHeight(), 160);
}

function payloadFromProps(args: ComponentProps["args"]): ReferenceCenterPayload | null {
  const value = args?.payload;
  if (!value || typeof value !== "object") {
    return null;
  }
  return value as ReferenceCenterPayload;
}

export function ReferenceCenterWorkbench({ args }: ComponentProps) {
  const payload = payloadFromProps(args);
  const [query, setQuery] = useState("");
  const [scope, setScope] = useState<ReferenceScope>("all");
  const [selectedItemId, setSelectedItemId] = useState<string | null>(payload?.initial_item_id || null);

  const itemById = useMemo(
    () => new Map((payload?.items || []).map((item) => [item.id, item])),
    [payload?.items],
  );
  const results = useMemo(
    () => searchReferenceItems(payload?.items || [], query, scope),
    [payload?.items, query, scope],
  );
  const journeys = useMemo(
    () => (payload?.journeys || []).map((itemId) => itemById.get(itemId)).filter(Boolean) as ReferenceItem[],
    [payload?.journeys, itemById],
  );
  const selectedItem = selectedItemId ? itemById.get(selectedItemId) || null : null;

  useEffect(() => {
    Streamlit.setComponentReady();
    syncFrameHeightSoon();
  }, []);

  useEffect(() => {
    syncFrameHeightSoon();
  }, [payload, query, scope, selectedItemId, results.length]);

  if (!payload) {
    return <div className="reference-center-state">Reference payload를 불러오지 못했습니다.</div>;
  }
  if (!payload.items.length) {
    return <div className="reference-center-state">Reference 콘텐츠를 준비하지 못했습니다.</div>;
  }

  const openItem = (itemId: string) => {
    if (itemById.has(itemId)) {
      setSelectedItemId(itemId);
    }
  };

  const sendNavigation = () => {
    if (!selectedItem?.destination) {
      return;
    }
    Streamlit.setComponentValue({
      event: {
        id: "navigate_to_surface",
        destination: selectedItem.destination,
        item_id: selectedItem.id,
        nonce: `${Date.now()}-${Math.random()}`,
      },
    });
    syncFrameHeightSoon();
  };

  const showJourneys = !query.trim() && (scope === "all" || scope === "journey");

  return (
    <main className="reference-center">
      <header className="reference-center__header">
        <p className="reference-center__eyebrow">REFERENCE CENTER</p>
        <h1>제품 흐름과 용어를 한곳에서 찾으세요</h1>
        <p>현재 화면의 의미, 상태가 미치는 영향, 다음 행동을 검색하거나 사용 흐름에서 시작할 수 있습니다.</p>
      </header>

      <section className="reference-search" aria-label="Reference 찾기">
        <label className="reference-search__field">
          <span className="reference-search__icon" aria-hidden="true">⌕</span>
          <input
            aria-label="Reference 검색"
            autoComplete="off"
            onChange={(event) => setQuery(event.target.value)}
            placeholder="기능, 상태, 문제 상황을 검색하세요"
            type="search"
            value={query}
          />
          {query ? (
            <button type="button" className="reference-search__clear" onClick={() => setQuery("")}>
              검색 지우기
            </button>
          ) : null}
        </label>
        <div className="reference-filters" aria-label="Reference 범위">
          {payload.filters.map((filter) => (
            <button
              aria-pressed={scope === filter.id}
              className={scope === filter.id ? "is-active" : ""}
              key={filter.id}
              onClick={() => setScope(filter.id)}
              type="button"
            >
              {filter.label}
            </button>
          ))}
        </div>
      </section>

      {payload.invalid_initial_item ? (
        <div className="reference-notice" role="status">
          변경되었거나 삭제된 Reference 항목입니다.
        </div>
      ) : null}

      {showJourneys ? (
        <section className="reference-section" aria-labelledby="journey-title">
          <div className="reference-section__heading">
            <div>
              <p>START BY JOURNEY</p>
              <h2 id="journey-title">무엇을 하려는지부터 선택하세요</h2>
            </div>
            <span>{journeys.length}개 흐름</span>
          </div>
          <div className="journey-grid">
            {journeys.map((journey, index) => (
              <button
                aria-label={`사용 흐름: ${journey.title}`}
                className="journey-card"
                key={journey.id}
                onClick={() => openItem(journey.id)}
                type="button"
              >
                <span className="journey-card__number">0{index + 1}</span>
                <strong>{journey.title}</strong>
                <small>{journey.summary}</small>
                <span className="journey-card__surface">{journey.related_surfaces.join(" · ")}</span>
              </button>
            ))}
          </div>
        </section>
      ) : null}

      <section className="reference-section reference-results" aria-labelledby="result-title">
        <div className="reference-section__heading">
          <div>
            <p>{query.trim() ? "SEARCH RESULTS" : "BROWSE ALL"}</p>
            <h2 id="result-title">{query.trim() ? `“${query.trim()}” 검색 결과` : "전체 Reference"}</h2>
          </div>
          <span>{results.length}개 항목</span>
        </div>

        {results.length ? (
          <div className="reference-result-list">
            {results.map((item) => (
              <button
                aria-label={`Reference 열기: ${item.title}`}
                className="reference-result"
                key={item.id}
                onClick={() => openItem(item.id)}
                type="button"
              >
                <span className={`reference-kind reference-kind--${item.kind}`}>{KIND_LABELS[item.kind]}</span>
                <span className="reference-result__body">
                  <strong>{item.title}</strong>
                  <small>{item.summary}</small>
                </span>
                <span className="reference-result__surface">{item.related_surfaces.join(" · ")}</span>
                <span className="reference-result__arrow" aria-hidden="true">→</span>
              </button>
            ))}
          </div>
        ) : (
          <div className="reference-zero-state">
            <strong>{payload.empty_state.title}</strong>
            <p>{payload.empty_state.description}</p>
            <div>
              {payload.empty_state.suggestions.map((suggestion) => (
                <button key={suggestion} onClick={() => setQuery(suggestion)} type="button">
                  {suggestion}
                </button>
              ))}
              <button onClick={() => { setQuery(""); setScope("all"); }} type="button">
                사용 흐름으로 돌아가기
              </button>
            </div>
          </div>
        )}
      </section>

      {selectedItem ? (
        <div className="reference-detail-layer">
          <button
            aria-label="상세 배경 닫기"
            className="reference-detail-backdrop"
            onClick={() => setSelectedItemId(null)}
            type="button"
          />
          <aside
            aria-label={`${selectedItem.title} 상세`}
            aria-modal="true"
            className="reference-detail"
            role="dialog"
          >
            <div className="reference-detail__top">
              <span className={`reference-kind reference-kind--${selectedItem.kind}`}>
                {KIND_LABELS[selectedItem.kind]}
              </span>
              <button aria-label="상세 닫기" onClick={() => setSelectedItemId(null)} type="button">×</button>
            </div>
            <p className="reference-detail__category">{selectedItem.category}</p>
            <h2>{selectedItem.title}</h2>
            <p className="reference-detail__summary">{selectedItem.summary}</p>

            <dl className="reference-detail__facts">
              <div>
                <dt>뜻/목적</dt>
                <dd>{selectedItem.meaning}</dd>
              </div>
              <div>
                <dt>어디서 보이나</dt>
                <dd>{selectedItem.related_surfaces.join(" · ")}</dd>
              </div>
              <div>
                <dt>영향</dt>
                <dd>{selectedItem.impact}</dd>
              </div>
              <div>
                <dt>다음 행동</dt>
                <dd>{selectedItem.next_action}</dd>
              </div>
            </dl>

            {selectedItem.related_item_ids.length ? (
              <section className="reference-related" aria-label="관련 항목">
                <h3>관련 항목</h3>
                <div>
                  {selectedItem.related_item_ids.map((itemId) => {
                    const relatedItem = itemById.get(itemId);
                    return relatedItem ? (
                      <button
                        aria-label={`관련 항목 열기: ${relatedItem.title}`}
                        key={itemId}
                        onClick={() => openItem(itemId)}
                        type="button"
                      >
                        {relatedItem.title}
                      </button>
                    ) : null;
                  })}
                </div>
              </section>
            ) : null}

            {selectedItem.destination ? (
              <button className="reference-detail__destination" onClick={sendNavigation} type="button">
                화면으로 이동 <span aria-hidden="true">→</span>
              </button>
            ) : null}
          </aside>
        </div>
      ) : null}
    </main>
  );
}

export default withStreamlitConnection(ReferenceCenterWorkbench);
