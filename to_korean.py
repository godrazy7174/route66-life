"""영어판 워크샵 스크립트를 한국어 클라이언트용으로 변환한다.

한국어 오버워치 클라이언트는 액션/값 이름은 영어를 그대로 쓰지만
(225개 액션 중 222개, 267개 값 중 266개가 영어와 동일),
아래 항목들만 번역된 이름을 요구한다:
  - settings 블록의 키와 값 전부
  - 블록 키워드 conditions/actions (단수형 condition/action)
  - 영웅·맵·게임모드 이름
  - 상수 White(흰색), Gray(회색)
주의: event 블록의 팀 토큰(Team 1; / Team 2;)은 상수라서 **영어 그대로**다.
한국어 1팀/2팀은 settings 블록의 '최대 N팀 플레이어 수'에만 쓰인다.
(실기 확인: event 블록에 2팀을 쓰면 "팀이 있어야 합니다" 오류)
근거: OverPy 요소 정의의 ko-KR 필드 (ref/*.ts)
"""
import io, re, sys

SETTINGS_KO = '''settings
{
	main
	{
		모드 이름: "66번 국도 — 서부 인생게임"
		설명: "서부 66번 국도에서 살아남아라. 캐서디와 애쉬, 좌클릭만으로."
	}

	lobby
	{
		최대 1팀 플레이어 수: 8
		최대 2팀 플레이어 수: 4
		최대 관전자 수: 12
		대기실로 돌아가기: 안 함
	}

	modes
	{
		연습 전투
		{
			영웅 변경 허용: 활성화

			enabled maps
			{
				66번 국도 972777519512068153
			}
		}

		일반
		{
			게임 모드 시작: 즉시
			생명력 팩 생성: 비활성화
			실시간 처치 정보: 비활성화
			영웅 제한: 비활성화
			적 생명력 막대: 비활성화
		}
	}

	heroes
	{
		일반
		{
			생명력 지속 재생: 비활성화

			enabled heroes
			{
				애쉬
				캐서디
			}
		}
	}
}

'''

BODY_REPLACEMENTS = [
    ('Color(White)', 'Color(흰색)'),
    ('Color(Gray)', 'Color(회색)'),
    ('Hero(Cassidy)', 'Hero(캐서디)'),
    ('Hero(Ashe)', 'Hero(애쉬)'),
    ('Hero(Reaper)', 'Hero(리퍼)'),
    ('Hero(Jetpack Cat)', 'Hero(제트팩 캣)'),
    ('Hero(Tracer)', 'Hero(트레이서)'),
    ('Hero(Shion)', 'Hero(시온)'),
    ('Hero(Freja)', 'Hero(프레야)'),
    ('Hero(Wrecking Ball)', 'Hero(레킹볼)'),
]


def convert(src):
    # 1) settings 블록 교체
    out = SETTINGS_KO + src[src.index('variables\n{'):]

    # 2) 블록 키워드 (탭 하나 들여쓴 단독 줄만)
    out = re.sub(r'(?m)^\tconditions$', '\tcondition', out)
    out = re.sub(r'(?m)^\tactions$', '\taction', out)

    # 3) 번역되는 상수/영웅
    for a, b in BODY_REPLACEMENTS:
        out = out.replace(a, b)
    return out


def main():
    src_path, dst_path = sys.argv[1], sys.argv[2]
    src = io.open(src_path, encoding='utf-8').read()
    out = convert(src)
    io.open(dst_path, 'w', encoding='utf-8', newline='\n').write(out)

    print('생성: ' + dst_path)
    print('  condition 블록 : %d' % len(re.findall(r'(?m)^\tcondition$', out)))
    print('  action 블록    : %d' % len(re.findall(r'(?m)^\taction$', out)))
    print('  event 팀 토큰  : 영어 유지 (Team 1 %d / Team 2 %d)' % (
        len(re.findall(r'(?m)^\t\tTeam 1;$', out)), len(re.findall(r'(?m)^\t\tTeam 2;$', out))))
    print('  흰색 %d / 회색 %d / 캐서디 %d / 애쉬 %d' % (
        out.count('Color(흰색)'), out.count('Color(회색)'),
        out.count('Hero(캐서디)'), out.count('Hero(애쉬)')))
    leftovers = []
    for bad in ('Color(White)', 'Color(Gray)', 'Hero(Ashe)', 'Hero(Cassidy)'):
        if bad in out:
            leftovers.append(bad)
    # 사전에 없는 영웅이 영문으로 남으면 한국어 클라이언트가 임포트를 거부한다
    for m in re.finditer(r'Hero\(([A-Za-z][A-Za-z ]*)\)', out):
        name = m.group(1)
        if name.split()[-1] in ('Player', 'Attacker', 'Victim', 'Target'):
            continue
        leftovers.append('미번역 영웅 Hero(%s)' % name)
    if re.search(r'(?m)^\tconditions$', out) or re.search(r'(?m)^\tactions$', out):
        leftovers.append('영문 conditions/actions 블록')
    # KO settings는 하드코딩이라 EN 로비 변경이 자동 반영되지 않는다 — 숫자를 대조한다
    for en_key, ko_key in (('Max Team 1 Players', '최대 1팀 플레이어 수'),
                           ('Max Team 2 Players', '최대 2팀 플레이어 수')):
        m_en = re.search(en_key + r': (\d+)', src)
        m_ko = re.search(ko_key + r': (\d+)', out)
        if m_en and m_ko and m_en.group(1) != m_ko.group(1):
            leftovers.append('로비 불일치 %s EN=%s KO=%s' % (en_key, m_en.group(1), m_ko.group(1)))
    print('  남은 영문 항목 : ' + (', '.join(leftovers) if leftovers else '없음'))


main()
