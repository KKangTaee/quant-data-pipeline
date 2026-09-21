import React from "react";
import {Reading} from "./contracts";
export default function ObservationReading({reading:r}:{reading:Reading}) {
 return <section className="reading"><div className="reading-grid"><div><h3>관측 사실</h3><ul>{r.observation_facts.length?r.observation_facts.map(f=><li key={f}>{f}</li>):<li>비교할 가격이 아직 없습니다.</li>}</ul></div><div><h3>가능한 의미</h3><p>{r.interpretation}</p>{r.counter_evidence.map(f=><p className="counter" key={f}>{f}</p>)}</div></div>
 <div className="next"><h3>다음 확인 조건</h3><div className="checks">{r.next_checks.map((f,i)=><p key={f}><b>0{i+1}</b>{f}</p>)}</div></div></section>;
}
