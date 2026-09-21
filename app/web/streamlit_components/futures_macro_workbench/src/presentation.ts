export function kst(value:string|null) {
 if (!value) return "확인 불가";
 return new Intl.DateTimeFormat("ko-KR",{timeZone:"Asia/Seoul",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false}).format(new Date(value));
}
export const statusLabels:Record<string,string>={AVAILABLE:"관측 가능",PARTIAL:"일부 자료 부족",STALE:"관측 지연",MARKET_CLOSED:"정규 거래 중단 · 마지막 관측",UNAVAILABLE:"비교 자료 부족"};
export function change(value:number|null) {return value===null?"—":`${value>0?"+":""}${Math.abs(value)<.005?"0.00":value.toFixed(2)}%`;}
