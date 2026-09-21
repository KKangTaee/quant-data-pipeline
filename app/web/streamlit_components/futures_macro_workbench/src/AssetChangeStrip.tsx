import React from "react";
import {Price} from "./contracts";
import {change} from "./presentation";
export default function AssetChangeStrip({prices}:{prices:Price[]}) {
 return <section className="prices"><h3>같은 구간의 자산 반응</h3><div className="price-grid">{prices.map(p=><div className="price" key={p.key}><span>{p.label}</span><strong className={p.return_pct!==null&&p.return_pct>=.005?"up":p.return_pct!==null&&p.return_pct<=-.005?"down":"neutral"}>{change(p.return_pct)}</strong><small>{p.return_pct===null?"비교 자료 부족":p.key==="ZN=F"?"금리 아닌 선물 가격":p.key==="dollar"?"통화 5종 역방향 평균":"선물 가격 변화"}</small></div>)}</div></section>;
}
