#!/usr/bin/env python3
"""Build the claim-led, print-first LightGuard editorial submission report."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from build_submission_release import DEFINITION, OUT, build_visual_docx

CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
FIG = OUT / "figures"


def write_svg(name: str, body: str, title: str, subtitle: str) -> Path:
    path = FIG / name
    path.write_text(
        f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 720" role="img" aria-label="{title}">
<style>.t{{font-family:NanumBarunGothic,Apple SD Gothic Neo,sans-serif;fill:#102A43}}.b{{font-weight:700}}.n{{fill:#52606D}}.s{{fill:#0F766E}}.a{{fill:#D97706}}.line{{stroke:#D8D4CA;stroke-width:2}}.signal{{stroke:#0F766E;stroke-width:8;fill:none}}</style>
<rect width="1400" height="720" fill="#FFFDF8"/><text class="t b" x="55" y="72" font-size="38">{title}</text><text class="t n" x="55" y="112" font-size="20">{subtitle}</text>{body}
<line class="line" x1="55" y1="675" x2="1345" y2="675"/><text class="t n" x="55" y="704" font-size="15">출처·방법·한계: LightGuard evidence registry · Submission Release v1.0</text></svg>''',
        encoding="utf-8",
    )
    return path


def build_figures() -> list[Path]:
    FIG.mkdir(parents=True, exist_ok=True)
    workload = write_svg(
        "06_workload_comparison.svg",
        '''<text class="t b" x="55" y="192" font-size="23">대구</text><rect class="s" x="220" y="158" width="1060" height="48"/><text x="1240" y="190" text-anchor="end" fill="white" font-family="sans-serif" font-size="23" font-weight="700">101,843건</text>
<text class="t b" x="55" y="292" font-size="23">양주</text><rect fill="#5D9E93" x="220" y="258" width="840" height="48"/><text class="t b" x="1080" y="290" font-size="23">11,892건</text>
<text class="t b" x="55" y="392" font-size="23">부여</text><rect fill="#7FB5AA" x="220" y="358" width="650" height="48"/><text class="t b" x="890" y="390" font-size="23">3,437건</text>
<text class="t b" x="55" y="492" font-size="23">울산 남구</text><rect fill="#B8D5CF" x="220" y="458" width="550" height="48"/><text class="t b" x="790" y="490" font-size="23">1,060건</text>
<text class="t n" x="220" y="550" font-size="18">막대 길이: log10 scale · 숫자: 공개 개별 운영사건 수</text>
<path d="M220 585 H1280" class="line"/><text class="t b a" x="220" y="625" font-size="22">해석</text><text class="t" x="305" y="625" font-size="22">고장 정확도 대체: 제외 / 실제 확인 업무 규모: 해당</text>''',
        "지자체 개별 운영사건 118,232건: 확인 순서 문제의 실제 규모",
        "대구·부여·울산 남구·양주 공개 사건자료 / log scale / 2026 확보본",
    )
    mechanism = write_svg(
        "07_service_mechanism.svg",
        '''<path d="M90 360 H1310" class="signal"/><path d="M1285 338 L1325 360 L1285 382 Z" class="s"/>
<g class="t"><circle cx="145" cy="360" r="58" fill="#102A43"/><text x="145" y="370" text-anchor="middle" fill="white" font-size="25" font-weight="700">자산</text>
<circle cx="420" cy="360" r="58" fill="#0F766E"/><text x="420" y="370" text-anchor="middle" fill="white" font-size="25" font-weight="700">예상</text>
<circle cx="695" cy="360" r="58" fill="#102A43"/><text x="695" y="370" text-anchor="middle" fill="white" font-size="25" font-weight="700">AMI</text>
<circle cx="970" cy="360" r="58" fill="#D97706"/><text x="970" y="370" text-anchor="middle" fill="white" font-size="25" font-weight="700">근거</text>
<circle cx="1245" cy="360" r="58" fill="#0F766E"/><text x="1245" y="370" text-anchor="middle" fill="white" font-size="25" font-weight="700">행동</text>
<text x="145" y="475" text-anchor="middle" font-size="20">정격부하·등수</text><text x="420" y="475" text-anchor="middle" font-size="20">점등창·시민박명</text><text x="695" y="475" text-anchor="middle" font-size="20">실제 전력 흐름</text><text x="970" y="475" text-anchor="middle" font-size="20">차이·지속시간</text><text x="1245" y="475" text-anchor="middle" font-size="20">원격/현장 확인</text></g>
<rect x="390" y="545" width="620" height="70" rx="12" fill="#E7F2EF"/><text class="t b" x="700" y="589" text-anchor="middle" font-size="22">고장 확정: 제외 / 담당자 다음 확인: 지원</text>''',
        "명령 상태 대신 실제 전력 흐름 재확인",
        "분전함 → 자산정보 → 예상 점등시간·부하 → AMI 실측 → 이상근거 → 점검우선순위",
    )
    gates = write_svg(
        "08_validation_gates.svg",
        '''<g class="t"><text x="60" y="205" font-size="22" font-weight="700">통제 시나리오 탐지</text><rect x="380" y="170" width="850" height="48" rx="7" fill="#D8D4CA"/><rect x="380" y="170" width="850" height="48" rx="7" fill="#0F766E"/><text x="1250" y="203" font-size="23" font-weight="700">46 / 46</text>
<text x="60" y="315" font-size="22" font-weight="700">release artifact 해시</text><rect x="380" y="280" width="850" height="48" rx="7" fill="#0F766E"/><text x="1250" y="313" font-size="23" font-weight="700">32 / 32</text>
<text x="60" y="425" font-size="22" font-weight="700">독립 QA</text><rect x="380" y="390" width="850" height="48" rx="7" fill="#0F766E"/><text x="1250" y="423" font-size="23" font-weight="700">PASS</text>
<text x="60" y="535" font-size="22" font-weight="700">금지주장 검사</text><rect x="380" y="500" width="850" height="48" rx="7" fill="#0F766E"/><text x="1250" y="533" font-size="23" font-weight="700">PASS</text></g>
<rect x="55" y="585" width="1290" height="62" rx="10" fill="#FFF1DC"/><text class="t b a" x="80" y="624" font-size="21">주의</text><text class="t" x="155" y="624" font-size="21">46/46: 통제 신호 재현 / 실제 현장 정확도·재현율: 미측정</text>''',
        "제출 무결성 통과 / 현장 정확도 측정 전",
        "분모·검증 대상별 release gate / 항목별 독립 해석",
    )
    linkage = write_svg(
        "09_ulsan_linkage.svg",
        '''<circle cx="360" cy="380" r="180" fill="none" stroke="#D8D4CA" stroke-width="58"/><circle cx="360" cy="380" r="180" fill="none" stroke="#0F766E" stroke-width="58" stroke-dasharray="1073 1131" transform="rotate(-90 360 380)"/><text class="t b" x="360" y="370" text-anchor="middle" font-size="58">95.1%</text><text class="t n" x="360" y="415" text-anchor="middle" font-size="22">안전 연결</text>
<g class="t"><text x="690" y="270" font-size="54" font-weight="700" fill="#0F766E">920</text><text x="850" y="270" font-size="24">안전 연결</text><text x="690" y="385" font-size="54" font-weight="700" fill="#D97706">13</text><text x="850" y="385" font-size="24">모호 · 보류</text><text x="690" y="500" font-size="54" font-weight="700" fill="#7B8794">48</text><text x="850" y="500" font-size="24">미연결 · 과잉 join 금지</text></g>''',
        "울산 위치 연결: 안전 연결 95.1% / 불확실성 보존",
        "위치자산 981개 · 안전 920 · 모호 13 · 미연결 48 · semantic identity 보수적 판정",
    )
    usage = write_svg(
        "10_usage_storyboard.svg",
        '''<g class="t"><rect x="60" y="175" width="290" height="390" rx="18" fill="#F4F1EA"/><text x="85" y="220" font-size="18" fill="#0F766E" font-weight="700">01 · 목록</text><text x="85" y="285" font-size="34" font-weight="700">우선순위 #1</text><text x="85" y="335" font-size="20">오늘 먼저 확인할 자산</text><circle cx="205" cy="455" r="48" fill="#B42318"/><text x="205" y="463" text-anchor="middle" fill="white" font-size="17" font-weight="700">점검</text>
<rect x="390" y="175" width="290" height="390" rx="18" fill="#F4F1EA"/><text x="415" y="220" font-size="18" fill="#0F766E" font-weight="700">02 · 이유</text><text x="415" y="285" font-size="34" font-weight="700">20% 낮음</text><text x="415" y="335" font-size="20">예상 대비 AMI 부하</text><path d="M420 470 L470 430 L520 455 L570 365 L630 405" class="signal"/>
<rect x="720" y="175" width="290" height="390" rx="18" fill="#F4F1EA"/><text x="745" y="220" font-size="18" fill="#0F766E" font-weight="700">03 · 이력</text><text x="745" y="285" font-size="34" font-weight="700">반복 3회</text><text x="745" y="335" font-size="20">과거 사건·backlog</text><line x1="760" y1="430" x2="950" y2="430" class="line"/><circle cx="790" cy="430" r="12" class="a"/><circle cx="855" cy="430" r="12" class="a"/><circle cx="930" cy="430" r="12" class="a"/>
<rect x="1050" y="175" width="290" height="390" rx="18" fill="#102A43"/><text x="1075" y="220" font-size="18" fill="#F7C948" font-weight="700">04 · 행동</text><text x="1075" y="285" font-size="32" fill="white" font-weight="700">원격관찰</text><text x="1075" y="335" font-size="22" fill="white">또는 현장점검</text><path d="M1090 455 H1280" stroke="#F7C948" stroke-width="6"/><path d="M1260 440 L1290 455 L1260 470 Z" fill="#F7C948"/></g>''',
        "담당자 4단계 확인 흐름: 대상·이유·이력·행동",
        "서비스 데모 사용 흐름 · 이상징후 목록 → 이유 → 운영이력 → 원격관찰/현장점검",
    )
    regional = write_svg(
        "11_regional_evidence.svg",
        '''<g class="t"><text x="65" y="185" font-size="19" font-weight="700" fill="#0F766E">OPERATIONS · 5지역</text>
<text x="65" y="235" font-size="27" font-weight="700">대구</text><text x="250" y="235" font-size="20">101,843 사건</text>
<text x="65" y="290" font-size="27" font-weight="700">부여</text><text x="250" y="290" font-size="20">3,437 사건</text>
<text x="65" y="345" font-size="27" font-weight="700">울산 남구</text><text x="250" y="345" font-size="20">1,060 lifecycle</text>
<text x="65" y="400" font-size="27" font-weight="700">양주</text><text x="250" y="400" font-size="20">11,892 민원 · 90일 재접수 7.46%</text>
<text x="65" y="455" font-size="27" font-weight="700">인천 미추홀</text><text x="250" y="455" font-size="20">34개월 · IoT 업무 28.06%</text>
<line x1="690" y1="155" x2="690" y2="555" class="line"/><text x="750" y="185" font-size="19" font-weight="700" fill="#D97706">ASSET / SIGNAL · 3지역</text>
<text x="750" y="255" font-size="27" font-weight="700">수영구</text><text x="980" y="255" font-size="20">204 분전함 기준 객체</text>
<text x="750" y="340" font-size="27" font-weight="700">대전</text><text x="980" y="340" font-size="20">43,082 자산 · 좌표 100%</text>
<text x="750" y="425" font-size="27" font-weight="700">강릉</text><text x="980" y="425" font-size="20">339 분전함 · 용량 99.63%</text>
<rect x="750" y="485" width="550" height="70" rx="10" fill="#FFF1DC"/><text x="780" y="527" font-size="19">동일 전국모델 ✕ · 지역별 field contract ✓</text></g>''',
        "지역 확장 근거: 운영 5지역 · 자산/신호 3지역",
        "같은 정확도 수치가 아닌 evidence role별 적용가능성 검증",
    )
    return [workload, mechanism, gates, linkage, usage, regional]


def page(number: str, eyebrow: str, title: str, content: str, cls: str = "") -> str:
    return f'''<section class="page {cls}"><header><span>{eyebrow}</span><b>{number}</b></header><h2>{title}</h2>{content}<footer>LIGHTGUARD · 김종백 · SUBMISSION RELEASE v1.0</footer></section>'''


def apply_outline_style(markup: str) -> str:
    title_map = {
        "고장을 확정하지 않아도, 확인 순서는 바꿀 수 있습니다": "고장 확정 없이 가능한 확인 순서 개선",
        "101,843건의 기록이 말하는 것은 ‘고장이 많다’가 아니라 ‘확인 업무가 크다’입니다": "고장 건수보다 큰 운영 과제: 확인 업무 <span class=\"nowrap\">101,843건</span>",
        "제어 명령과 독립된 AMI가 ‘실제로 켜졌는가’를 다시 묻습니다": "제어 명령과 독립된 AMI 재확인",
        "자산·시간·부하·AMI·이상근거가 하나의 객체에서 끊김 없이 이어집니다": "단일 데이터 객체: 자산·시간·부하·AMI·이상근거",
        "전력 신호와 운영 이력을 분리해야 지역이 바뀌어도 과장을 피할 수 있습니다": "지역 확장을 위한 SIGNAL·OPERATIONS 분리",
        "제출 무결성은 통과했지만, 실제 현장 정확도는 아직 측정 전입니다": "제출 무결성 통과 / 실제 현장 정확도 측정 전",
        "운영자료는 AMI 성능을 대신하지 않고, 실제 유지관리 맥락을 제공합니다": "운영자료 역할: AMI 성능 대체가 아닌 유지관리 맥락",
        "담당자는 ‘무엇을’보다 먼저 ‘왜’를 확인합니다": "담당자 확인 순서: 대상보다 먼저 근거 확인",
        "원격제어를 교체하지 않고, 센서를 더 달기 전에 검증 공백을 메웁니다": "원격제어·추가 센서 사이 검증 공백 보완",
        "경제효과는 숫자를 먼저 약속하지 않고 pilot 로그로 측정합니다": "경제효과 산정 기준: 사전 약속 대신 pilot 로그",
        "다음 실험은 더 복잡한 모델이 아니라 실제 AMI와 사람의 확인 결과입니다": "다음 검증 과제: 실제 AMI·담당자 확인 결과",
    }
    for source, target in title_map.items():
        markup = markup.replace(source, target)
    replacements = {
        f'<blockquote>{DEFINITION}</blockquote>': '<div class="thesis"><b>서비스 정의</b><ul class="outline"><li>자동 고장 확정: 제외</li><li>기존 AMI 실제 전력 흐름: 독립 확인</li><li>반복 유지관리 이력: 결합</li><li>최종 목적: 원격확인·현장점검 우선순위 지원</li></ul></div>',
        '<p class="note">* 실제 현장 정확도가 아니라 detector contract 검증입니다.</p>': '<ul class="outline-note"><li>46/46: detector contract 검증</li><li>실제 현장 정확도: 미측정</li></ul>',
        '<p class="lead">기존 원격제어는 명령과 통신 상태를 관리합니다. 하지만 명령 이후 실제 전력이 기대대로 흐르는지는 별도 근거가 필요합니다.</p>': '<ul class="outline lead"><li>기존 원격제어: 명령·통신 상태 관리</li><li>검증 공백: 명령 이후 실제 전력 흐름</li><li>필요 근거: 독립 AMI 계측</li></ul>',
        '<p>LightGuard는 민원·일상점검·직원신고를 대체하지 않습니다. AMI를 두 번째 확인자로 사용해 담당자가 먼저 볼 후보를 좁힙니다.</p>': '<ul class="outline"><li>기존 발견경로: 민원·일상점검·직원신고 유지</li><li>AMI 역할: 두 번째 확인자</li><li>운영 결과: 우선 확인 후보 축소</li></ul>',
        '<aside>효과 주장은 민원 감소율이 아니라 <b>대규모 workload에서 확인 대상을 좁히는 운영지원</b>으로 제한합니다.</aside>': '<aside><b>효과 해석</b><ul class="outline"><li>민원 감소율: 주장 제외</li><li>검증 범위: 대규모 workload 내 확인 대상 축소</li></ul></aside>',
        '<p class="lead">SR-A · 독립 QA PASS · 32개 release artifact 해시 일치 · metric/claim/rubric registry · 금지주장 검사</p>': '<ul class="outline lead"><li>Release 등급: SR-A</li><li>독립 QA: PASS</li><li>Artifact 해시: 32/32 일치</li><li>Registry: metric·claim·rubric 완성</li><li>금지주장 검사: PASS</li></ul>',
        '<p class="note">같은 날 사건 순서를 임의로 만들지 않고, 미래 처리일을 사용하는 leakage를 금지합니다.</p>': '<ul class="outline-note"><li>같은 날 사건 순서: 생성 금지</li><li>미래 처리일: 사용 금지</li><li>Feature 기준: 접수 당시 관측 가능 정보</li></ul>',
        '<aside>실제 수영구 AMI 부재는 숨기지 않습니다. 실제 자산에 scenario injection을 적용하되 현장 성능과 분리합니다.</aside>': '<aside><b>AMI 부재 처리</b><ul class="outline"><li>실제 수영구 AMI: 미확보</li><li>대체 검증: 실제 자산 기반 scenario injection</li><li>해석 경계: 현장 성능과 분리</li></ul></aside>',
        '<aside>안전점검·자재자료는 join key가 없으면 비용절감 산정에 사용하지 않습니다.</aside>': '<aside><b>Join 경계</b><ul class="outline"><li>안전점검·자재자료: 운영부담 근거</li><li>확정 join key 부재: 개별 사건 연결 제외</li><li>비용절감 산정: 사용 제외</li></ul></aside>',
        '<div class="product-rule"><b>목록</b>은 후보를 좁히고 · <b>근거</b>는 판단을 설명하고 · <b>이력</b>은 반복성을 보여주고 · <b>행동</b>은 사람에게 남습니다.</div>': '<div class="product-rule"><b>목록</b> · 후보 축소<br><b>근거</b> · 판단 설명<br><b>이력</b> · 반복성 확인<br><b>행동</b> · 담당자 최종 결정</div>',
        '<blockquote>차별점은 제어 대체가 아니라 기존 인프라 사이의 검증 공백을 낮은 추가설비 부담으로 메우는 것입니다.</blockquote>': '<div class="thesis"><b>차별점</b><ul class="outline"><li>원격제어 교체: 제외</li><li>기존 AMI·자산·천문자료: 우선 재사용</li><li>추가 센서: 필요 구간에 단계적 적용</li><li>핵심 가치: 인프라 간 검증 공백 보완</li></ul></div>',
        '<blockquote>전국에 한 모델을 그대로 적용하지 않습니다. SIGNAL과 OPERATIONS layer를 지역별 가용 데이터 수준에 맞게 조합합니다.</blockquote>': '<div class="thesis"><b>확장 원칙</b><ul class="outline"><li>전국 동일 무보정 모델: 주장 제외</li><li>SIGNAL: 공통 전력 신호 계약</li><li>OPERATIONS: 지역 가용자료별 구성</li><li>적용 방식: 지역별 calibration</li></ul></div>',
        '<p>LightGuard v0.22 지역확장 검증 · 수영구 자산·천문·기상 context · 공모전 AMI · 5지역 운영자료 · 대전·강릉 자산자료</p>': '<ul class="outline"><li>LightGuard v0.22 지역확장 검증</li><li>수영구 자산·천문·기상 context</li><li>공모전 AMI</li><li>5지역 운영자료</li><li>대전·강릉 자산자료</li></ul>',
    }
    for source, target in replacements.items():
        markup = markup.replace(source, target)
    return markup


def build_html(figures: list[Path]) -> Path:
    workload, mechanism, gates, linkage, usage, regional = figures
    dashboard_shot = FIG / "app_dashboard.png"
    cabinet_shot = FIG / "app_cabinet.png"
    map_shot = FIG / "app_map.png"
    pages = [
        '''<section class="page cover"><div class="cover-grid"><p class="kicker">2026 AMI 공모 · 공익 서비스</p><h1>Light<br>Guard</h1><p class="cover-deck">실제 전력 흐름으로<br>가로등 점검의 순서를 바꾸다</p><div class="street"><i></i><i></i><i></i><svg viewBox="0 0 900 140"><path d="M0 82 C80 20 130 125 220 60 S380 100 470 45 S650 115 900 40"/></svg></div><p class="author">개인 참가 · 김종백</p></div></section>''',
        page("02", "EXECUTIVE SUMMARY", "고장 확정 없이, 담당자가 먼저 확인할 대상을 좁힙니다", f'''<blockquote>{DEFINITION}</blockquote><div class="rubric"><span>사업 적합성</span><span>개발 용이성</span><span>아이디어 구체성</span><span>유형효과</span><span>범용성</span></div><div class="hero-number"><strong>204</strong><span>수영구 분전함을<br>실행 가능한 데이터 객체로</span></div><div class="metrics-line"><span><b>4,239등</b> 연결 가로등</span><span><b>488.44 kW</b> 추정 정격부하</span><span><b>46/46</b> 통제 신호 탐지*</span></div><p class="note">* detector contract 검증이며 실제 현장 정확도는 미측정 · Live product: good5229.github.io/AMI_2026/</p>'''),
        page("03", "THE PROBLEM", "101,843건의 기록이 말하는 것은 ‘고장이 많다’가 아니라 ‘확인 업무가 크다’입니다", f'''<div class="two-col"><div><p class="lead">기존 원격제어는 명령과 통신 상태를 관리합니다. 하지만 명령 이후 실제 전력이 기대대로 흐르는지는 별도 근거가 필요합니다.</p><p>LightGuard는 민원·일상점검·직원신고를 대체하지 않습니다. AMI를 두 번째 확인자로 사용해 담당자가 먼저 볼 후보를 좁힙니다.</p><aside>효과 주장은 민원 감소율이 아니라 <b>대규모 workload에서 확인 대상을 좁히는 운영지원</b>으로 제한합니다.</aside></div><figure><img src="figures/{workload.name}"></figure></div>'''),
        page("04", "THE MECHANISM", "제어 명령과 독립된 AMI가 ‘실제로 켜졌는가’를 다시 묻습니다", f'''<figure class="wide"><img src="figures/{mechanism.name}"></figure><div class="three"><p><b>DATA QUALITY REVIEW</b><br>결측·계측 품질을 먼저 확인</p><p><b>REMOTE MONITOR</b><br>약한 신호는 원격 관찰</p><p><b>FIELD CANDIDATE</b><br>설명 가능한 지속 신호만 후보화</p></div>'''),
        page("05", "END-TO-END CASE", "정격 3.4 kW 분전함의 20% 부분소등 신호를 끝까지 추적합니다", '''<div class="object-chain"><b>분전함</b><i>→</i><b>자산정보</b><i>→</i><b>예상 점등시간</b><i>→</i><b>예상 정격부하</b><i>→</i><b>AMI 실측</b><i>→</i><b>이상근거</b><i>→</i><b>점검우선순위</b></div><div class="case-flow"><div><b>01 · 예상</b><strong>3.4 kW</strong><span>시민박명·점등창</span></div><div><b>02 · 실측</b><strong>-20%</strong><span>예상 대비 부하</span></div><div><b>03 · 지속</b><strong>90분</strong><span>일출 후 점등 지속 예시</span></div><div><b>04 · 행동</b><strong>확인</strong><span>원격관찰 후 현장후보</span></div></div><aside><b>검증 경계</b><ul class="outline"><li>실제 수영구 자산: 사용</li><li>실제 수영구 AMI: 미확보</li><li>신호: scenario injection</li><li>결론: detector 작동 검증이며 실제 고장 확정 아님</li></ul></aside>'''),
        page("06", "DEPLOYMENT ARCHITECTURE", "기존 시스템을 교체하지 않고 지역별 Adapter로 연결합니다", '''<div class="architecture"><div><b>기존 데이터</b><span>AMI · 자산대장<br>천문·기상 · 운영이력</span></div><i>→</i><div><b>지역 Adapter</b><span>필드·단위·시간대<br>결측·품질 정규화</span></div><i>→</i><div><b>LightGuard</b><span>SIGNAL · OPERATIONS<br>품질 보류·근거 생성</span></div><i>→</i><div><b>담당자 앱</b><span>목록 · 이유 · 이력<br>원격관찰·현장점검</span></div></div><div class="layers compact"><div><em>SIGNAL</em><h3>예상 대비 실제 전력</h3><p>점등창 · 정격부하 · AMI · 지속시간 · 품질</p></div><div><em>OPERATIONS</em><h3>반복과 backlog 맥락</h3><p>30/90/365일 사건 · 열린 건 · start-of-day backlog</p></div></div><p class="note">읽기 중심 연동 · 자동 제어 없음 · 미래 처리 결과 사용 금지 · 지역별 calibration</p>'''),
        page("07", "VALIDATION", "제출 무결성은 통과했지만, 실제 현장 정확도는 아직 측정 전입니다", f'''<figure class="wide"><img src="figures/{gates.name}"></figure><p class="lead">SR-A · 독립 QA PASS · 32개 release artifact 해시 일치 · metric/claim/rubric registry · 금지주장 검사</p>'''),
        page("08", "REGIONAL EVIDENCE", "운영 5지역과 자산·신호 3지역에서 역할별 가치를 확인했습니다", f'''<figure class="wide"><img src="figures/{regional.name}"></figure><aside>양주: 반복·조치 근거 / 미추홀: 월별 IoT workload / 대전: 공간 inventory / 강릉: 분전함·정격용량 계약. 모두 AMI 현장 고장 정확도와 분리합니다.</aside>'''),
        page("09", "IMPLEMENTED PRODUCT", "구현된 앱에서 목록·상세·지도를 하나의 업무 흐름으로 제공합니다", f'''<div class="app-shots"><figure><img src="figures/{dashboard_shot.name}"><figcaption>① 우선순위 목록</figcaption></figure><figure><img src="figures/{cabinet_shot.name}"><figcaption>② 예상·AMI·이상근거</figcaption></figure><figure><img src="figures/{map_shot.name}"><figcaption>③ 분전함 위치·상태</figcaption></figure></div><div class="product-rule"><b>목록</b> · 후보 축소<br><b>근거</b> · 판단 설명<br><b>지도</b> · 분전함 위치 확인<br><b>행동</b> · 담당자 최종 결정</div><p class="note">원형 마커는 개별 가로등이 아니라 분전함 위치이며, 연결 가로등 수는 상세 정보로 분리합니다.</p>'''),
        page("10", "POSITIONING", "원격제어를 교체하지 않고, 센서를 더 달기 전에 검증 공백을 메웁니다", '''<table class="position-table"><thead><tr><th>방식</th><th>실제 전력 확인</th><th>추가 장비</th><th>근거 설명</th><th>우선순위</th></tr></thead><tbody><tr><td>민원 중심</td><td>불가</td><td>없음</td><td>제한적</td><td>사후 대응</td></tr><tr><td>기존 원격제어</td><td>부분적</td><td>기존 설비</td><td>명령·통신 중심</td><td>제한적</td></tr><tr class="focus-row"><td>LightGuard</td><td>AMI 교차 확인</td><td>기존 데이터 재사용</td><td>차이·지속·품질</td><td>핵심 기능</td></tr><tr><td>등기구별 센서</td><td>가능</td><td>추가 설치</td><td>가능</td><td>가능</td></tr></tbody></table><blockquote>제어 대체가 아니라 기존 AMI와 원격제어 사이의 검증 공백을 보완합니다.</blockquote>'''),
        page("11", "EXPECTED VALUE", "유형효과는 공개 산식과 pilot 측정값으로 산정합니다", '''<div class="formula"><b>예상 절감시간</b><span>= 연간 확인 대상 수 × 사전 분류 적용률 × 건당 확인시간 차이</span><b>예상 운영비 절감</b><span>= 예상 절감시간 × 시간당 업무비용</span></div><div class="scenario-grid"><div><b>보수</b><span>낮은 적용률<br>짧은 시간 차이</span></div><div><b>기준</b><span>pilot 중앙값<br>관측 업무량</span></div><div><b>확장</b><span>검증된 적용률<br>다지역 운영</span></div></div><div class="boundary"><div><b>현재 근거</b><p>실제 운영 workload<br>후보 축소 가능성<br>재현 가능한 제품</p></div><div><b>pilot 입력값</b><p>원격 해소율<br>건당 확인시간<br>현장점검 적중률</p></div></div><p class="note">절감액은 관측 결과가 아니라 입력값 공개형 계산 결과이며 pilot 전 확정 주장하지 않습니다.</p>'''),
        page("12", "PILOT & LIMITS", "4–8주 shadow pilot에서 현장 효과와 중단 조건을 함께 측정합니다", '''<table class="pilot-table"><tr><th>대상</th><td>실제 AMI 연결 가능 분전함 표본</td></tr><tr><th>비교</th><td>기존 확인 순서 vs LightGuard 우선순위</td></tr><tr><th>1차 지표</th><td>상위 후보 중 담당자 확인 필요 비율</td></tr><tr><th>2차 지표</th><td>원격 해소율 · 건당 확인시간 · 반복 방문률</td></tr><tr><th>안전장치</th><td>자동 작업지시·자동제어 금지 · 담당자 최종 결정</td></tr><tr><th>중단 조건</th><td>품질 저하 · 오경보 집중 · AMI 결측</td></tr></table><div class="thesis"><b>확장 원칙</b><ul class="outline"><li>전국 동일 무보정 모델: 주장 제외</li><li>SIGNAL: 공통 전력 신호 계약</li><li>OPERATIONS: 지역 가용자료별 구성</li><li>다음 기술 단계: 실제 AMI와 담당자 확인 결과</li></ul></div>'''),
    ]
    pages = [apply_outline_style(item) for item in pages]
    css = '''<style>@font-face{font-family:NB;src:url(file:///Library/Fonts/NanumBarunGothic.ttf)}@font-face{font-family:NS;src:url(file:///Library/Fonts/NanumSquareExtraBold.ttf)}*{box-sizing:border-box}html,body{margin:0;background:#ccc;color:#102A43;font-family:NB,sans-serif;word-break:keep-all;overflow-wrap:normal;line-break:strict;hyphens:none;font-variant-numeric:tabular-nums}.page{position:relative;width:210mm;height:297mm;margin:8mm auto;padding:18mm 18mm 17mm;background:#FFFDF8;overflow:hidden;page-break-after:always}.page header{display:flex;justify-content:space-between;border-bottom:.5mm solid #102A43;padding-bottom:3mm;font-size:9pt;letter-spacing:.12em}.page h2{font-family:NS;font-size:26pt;line-height:1.18;letter-spacing:-.035em;max-width:172mm;margin:11mm 0 8mm;text-wrap:balance;word-break:keep-all}.page h3{font-family:NS;text-wrap:balance}.page p{font-size:10.5pt;line-height:1.68}.page footer{position:absolute;left:18mm;right:18mm;bottom:7mm;border-top:.2mm solid #D8D4CA;padding-top:2mm;font-size:6.5pt;color:#52606D}.cover{padding:0;background:#102A43;color:white}.cover-grid{position:absolute;inset:0;padding:22mm}.kicker{color:#F7C948;letter-spacing:.14em}.cover h1{font-family:NS;font-size:74pt;line-height:.78;letter-spacing:-.07em;margin:32mm 0 14mm}.cover-deck{font-size:22pt!important;line-height:1.35!important;text-wrap:balance}.author{position:absolute;bottom:18mm}.street{position:absolute;right:0;bottom:0;width:115mm;height:170mm;background:#0F766E;clip-path:polygon(35% 0,100% 0,100% 100%,0 100%)}.street i{position:absolute;bottom:25mm;width:2mm;height:65mm;background:#FFFDF8}.street i:after{content:'';position:absolute;top:0;left:-8mm;width:18mm;height:5mm;background:#F7C948}.street i:nth-child(1){left:35mm}.street i:nth-child(2){left:70mm;height:90mm}.street i:nth-child(3){left:100mm;height:115mm}.street svg{position:absolute;bottom:100mm;left:15mm;width:95mm}.street path{fill:none;stroke:#F7C948;stroke-width:6}.page blockquote{font-family:NS;font-size:16pt;line-height:1.55;border-left:3mm solid #0F766E;padding:6mm 8mm;margin:8mm 0;background:#E7F2EF}.hero-number{display:flex;align-items:flex-end;gap:8mm;margin:18mm 0 10mm}.hero-number strong,.asset-hero strong{font-family:NS;font-size:72pt;color:#0F766E;line-height:.8}.hero-number span{font-size:15pt}.metrics-line{display:grid;grid-template-columns:repeat(3,1fr);border-top:.5mm solid #102A43;border-bottom:.5mm solid #102A43}.metrics-line span{padding:6mm 3mm;border-right:.2mm solid #D8D4CA}.metrics-line b{display:block;font-size:18pt}.nowrap,.metrics-line b,.hero-number strong,.asset-hero strong{white-space:nowrap;word-break:keep-all}.note{font-size:8pt!important;color:#52606D}.two-col{display:grid;grid-template-columns:4fr 6fr;gap:10mm}.lead{font-size:13pt!important}.page aside{border-top:1mm solid #D97706;padding-top:4mm;margin-top:8mm;font-size:10pt;line-height:1.6}.page figure{margin:0}.page figure img{width:100%;display:block}.wide img{max-height:155mm;object-fit:contain}.three{display:grid;grid-template-columns:repeat(3,1fr);gap:6mm;margin-top:6mm}.three p{border-top:1mm solid #0F766E;padding-top:3mm}.object-chain{display:flex;align-items:center;flex-wrap:wrap;gap:4mm;padding:8mm;background:#102A43;color:white;font-size:12pt}.object-chain i{color:#F7C948}.asset-hero{display:flex;align-items:center;gap:12mm;margin:20mm 0}.asset-hero div b{font-size:17pt}.layers{display:grid;grid-template-columns:1fr 1fr;gap:8mm;margin-top:15mm}.layers>div{min-height:95mm;padding:10mm;background:#F4F1EA;border-top:3mm solid #0F766E}.layers em,.compare em{color:#0F766E;font-style:normal;font-weight:bold;letter-spacing:.12em}.timeline{display:grid;grid-template-columns:repeat(3,1fr);margin-top:12mm}.timeline span{padding:5mm;border:solid #D8D4CA;border-width:.3mm .3mm .3mm 0}.compare{display:grid;grid-template-columns:repeat(3,1fr);gap:5mm;margin:20mm 0}.compare>div{padding:8mm 6mm;min-height:90mm;border-top:2mm solid #D8D4CA}.compare .focus{background:#102A43;color:white;border-color:#F7C948}.product-rule{font-family:NS;font-size:15pt;line-height:1.7;margin-top:8mm}.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm;margin:16mm 0}.kpis span{padding:8mm 4mm;background:#102A43;color:white;font-weight:bold;text-align:center}.boundary{display:grid;grid-template-columns:1fr 1fr;gap:8mm}.boundary>div{padding:8mm;border:1mm solid #0F766E}.boundary>div:last-child{border-color:#D97706}.roadmap{list-style:none;padding:0;margin:12mm 0}.roadmap li{display:grid;grid-template-columns:45mm 1fr;border-top:.5mm solid #102A43;padding:7mm 0;font-size:14pt}.roadmap b{color:#0F766E}.sources{position:absolute;left:18mm;right:18mm;bottom:25mm;background:#F4F1EA;padding:6mm}@page{size:A4;margin:0}@media print{html,body{background:white}.page{margin:0}}</style>'''
    css = css.replace(
        "</style>",
        ".thesis{font-family:NS;font-size:14pt;line-height:1.5;border-left:3mm solid #0F766E;padding:6mm 8mm;margin:8mm 0;background:#E7F2EF}"
        ".outline{margin:3mm 0;padding-left:6mm;font-family:NB;font-size:10.5pt;line-height:1.65}"
        ".outline li{margin:1.5mm 0}.outline-note{margin:4mm 0;padding:4mm 6mm;background:#F4F1EA;color:#52606D;font-size:8.5pt;line-height:1.55}"
        ".rubric{display:flex;flex-wrap:wrap;gap:2mm}.rubric span{padding:2mm 3mm;background:#F4F1EA;border-radius:10mm;font-size:8pt;font-weight:700}"
        ".case-flow,.architecture{display:flex;align-items:stretch;gap:3mm;margin:13mm 0}.case-flow>div,.architecture>div{flex:1;padding:5mm 4mm;background:#F4F1EA;border-top:2mm solid #0F766E}.case-flow b,.case-flow span,.architecture b,.architecture span{display:block}.case-flow strong{display:block;font-family:NS;font-size:22pt;margin:4mm 0;color:#0F766E}.architecture i{align-self:center;color:#D97706;font-size:18pt}.compact{margin-top:8mm}.compact>div{min-height:48mm;padding:6mm}"
        ".app-shots{display:grid;grid-template-columns:1fr 1fr;gap:3mm}.app-shots figure{background:#F4F1EA;padding:2mm}.app-shots figure:first-child{grid-column:1/-1}.app-shots img{width:100%;height:68mm;object-fit:contain;object-position:center top}.app-shots figure:first-child img{height:55mm}.app-shots figcaption{font-size:8pt;font-weight:700;padding:1mm}.product-rule{font-size:10pt;line-height:1.35;margin-top:3mm}"
        ".position-table,.pilot-table{width:100%;border-collapse:collapse;margin:10mm 0;font-size:9.5pt}.position-table th,.position-table td,.pilot-table th,.pilot-table td{padding:4mm 3mm;border-bottom:.3mm solid #D8D4CA;text-align:left}.position-table thead,.pilot-table th{background:#102A43;color:white}.position-table .focus-row{background:#E7F2EF;font-weight:700}"
        ".formula{display:grid;grid-template-columns:42mm 1fr;margin:10mm 0;border:1mm solid #0F766E}.formula b,.formula span{padding:5mm}.formula b{background:#E7F2EF}.scenario-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm;margin:8mm 0}.scenario-grid>div{padding:6mm;background:#F4F1EA}.scenario-grid b,.scenario-grid span{display:block}.scenario-grid span{font-size:8.5pt;margin-top:2mm}</style>",
    )
    path = OUT / "LightGuard_Competition_Report.html"
    path.write_text(f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>LightGuard</title>{css}</head><body>{"".join(pages)}</body></html>', encoding="utf-8")
    return path


def main() -> None:
    figures = build_figures()
    html = build_html(figures)
    pdf = OUT / "LightGuard_Competition_Report.pdf"
    subprocess.run([str(CHROME), "--headless", "--disable-gpu", "--no-sandbox", "--allow-file-access-from-files", f"--print-to-pdf={pdf}", "--print-to-pdf-no-header", html.as_uri()], check=True)
    docx = build_visual_docx(pdf)
    audit = OUT / "EDITORIAL_REDESIGN.md"
    audit.write_text("# Editorial redesign\n\n- 12-page print-first sequence\n- Claim-led page titles\n- Typewriter/Chalk-derived full-bleed cover and modular print grid\n- Five data/explanatory SVG figures\n- Visible source, denominator, uncertainty, and prohibited-claim notes\n- PDF and visual-preservation DOCX regenerated from the same HTML\n", encoding="utf-8")
    tracked = [html, pdf, docx, audit, *figures]
    (OUT / "SHA256SUMS_EDITORIAL.txt").write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(OUT)}\n" for p in tracked), encoding="utf-8")
    print(f"Built editorial report: {pdf}")


if __name__ == "__main__":
    main()
