export type Period = "since_close" | "last_hour";
export type Price = {key:string; label:string; return_pct:number|null; source_symbols:string[]};
export type Reading = {headline:string; observation_facts:string[]; interpretation:string; counter_evidence:string[]; next_checks:string[]};
export type WindowData = {status:string; start_utc:string|null; end_utc:string|null; prices:Price[]; reading:Reading; missing_symbols:string[];
 evidence:{source:string; rule_version:string; calendar_quality:string; caveats:string[]}};
export type Payload = {schema_version:string; windows:Record<Period,WindowData>; cycle_background:{state:string;as_of_date:string|null};
 command:{ack_nonce?:string;pending:boolean;result?:{status?:string;message?:string}}};
