import React,{useEffect,useRef,useState} from "react";
import {ComponentProps,Streamlit,withStreamlitConnection} from "streamlit-component-lib";
import {Payload,Period} from "./contracts";
import IntradayChangeSummary from "./IntradayChangeSummary";
import AssetChangeStrip from "./AssetChangeStrip";
import ObservationReading from "./ObservationReading";
import "./style.css";

function FuturesMacroWorkbench({args,disabled}:ComponentProps) {
 const payload=args.payload as Payload;
 const [period,setPeriod]=useState<Period>("since_close");
 const [pending,setPending]=useState<string|null>(null);
 const pendingRef=useRef<string|null>(null);
 useEffect(()=>{if (pendingRef.current && payload.command?.ack_nonce===pendingRef.current) {pendingRef.current=null;setPending(null);}},[payload.command?.ack_nonce]);
 useEffect(()=>{const observer=new ResizeObserver(()=>Streamlit.setFrameHeight());observer.observe(document.body);Streamlit.setFrameHeight();return ()=>observer.disconnect();},[]);
 const emit=(id:string)=>{if(pendingRef.current||disabled||payload.command?.pending)return;const nonce=`${Date.now()}-${Math.random().toString(36).slice(2)}`;pendingRef.current=nonce;setPending(nonce);Streamlit.setComponentValue({event:{id,nonce}});};
 const w=payload.windows[period];const locked=Boolean(pending||disabled||payload.command?.pending);
 return <main className="fm"><header><div><p className="eyebrow">선물 매크로 · 장중 변화</p><h1>지금, 무엇이 달라졌나</h1><p className="muted">가격 변화와 동반 반응으로 주식시장에 대한 부담·지지를 읽습니다.</p></div><div className="actions"><button className="primary" disabled={locked} onClick={()=>emit("daily_refresh")}>{pending?"자료 확인 중…":"최신 데이터 반영"}</button><button disabled={locked} onClick={()=>emit("reload")}>저장 자료 다시 읽기</button></div></header>
 <div className="topline"><div className="segments" aria-label="비교 구간">{(["since_close","last_hour"] as Period[]).map(p=><button key={p} aria-pressed={period===p} onClick={()=>setPeriod(p)}>{p==="since_close"?"미국장 마감 이후":"최근 1시간"}</button>)}</div><span className="muted">수동 갱신 · 완료된 가격 관측</span></div>
 {payload.command?.result?.message&&<p role="status" className={`notice ${payload.command.result.status}`}>{payload.command.result.message}</p>}
 <IntradayChangeSummary window={w}/><div className="cycle">경기 배경: <b>{payload.cycle_background.state}</b> · {payload.cycle_background.as_of_date||"기준일 없음"}<button disabled={locked} onClick={()=>emit("economic_cycle")}>경기국면 보기 ↗</button><span>발표된 경제자료의 월간 배경</span></div>
 <AssetChangeStrip prices={w.prices}/><ObservationReading reading={w.reading}/>
 <details><summary>계산 기준과 자료 공백</summary><div className="evidence"><p>{w.evidence.source} · 공식 마감 일정 {w.evidence.calendar_quality==="CONFIRMED"?"확인됨":"확인 필요"}</p><p>핵심 누락: {w.missing_symbols.join(", ")||"없음"}</p>{w.evidence.caveats.map(c=><p key={c}>{c}</p>)}</div></details>
 <details><summary>과거 사례 검증</summary><p className="evidence">장중 조건 검증 전입니다. 현재 구간의 이후 상승·하락 확률은 제공하지 않습니다. 충분한 장중 이력과 별도 검증이 필요합니다.</p></details>
 </main>;
}
export default withStreamlitConnection(FuturesMacroWorkbench);
