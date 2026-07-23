import type { CalculationScope } from "./FuturesMacroWorkbench";

type Props = { changeConditions: string[]; scope: CalculationScope };

function CalculationScopeSection({ changeConditions, scope }: Props) {
  return (
    <section className="fm-workbench__decision-basis" aria-labelledby="fm-change-title">
      <div>
        <span>Next check</span>
        <h3 id="fm-change-title">다음 일봉에서 판단이 바뀌는 조건</h3>
        {changeConditions.length > 0 ? (
          <ul>{changeConditions.map((item) => <li key={item}>{item}</li>)}</ul>
        ) : <p>현재 완료 일봉 이후의 정렬 변화가 아직 없습니다.</p>}
      </div>
      <aside>
        <span>계산 범위</span>
        <strong>{scope.collected_count}개 선물 수집 · {scope.direct_family_input_count}개 family 산식 반영 · family {scope.available_family_count}/{scope.required_family_count}</strong>
        <small>달러인덱스는 경제 사이클 공유 · 은은 원본 관찰 전용</small>
      </aside>
    </section>
  );
}

export default CalculationScopeSection;
