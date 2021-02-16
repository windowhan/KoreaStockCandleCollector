# KoreaStockCandleCollector
전종목 1분봉 콜렉터 using Creon API 

윈도우 환경에서만 구동됨 (국내 모든 증권사 API가 리눅스에서 실행이 불가능함)<BR>
데이터를 저장할 DB는 처음에 MYSQL를 썼으나 Write속도가 너무 느려서 mongodb로 전환. (실험 결과 약 10배정도 차이가남)<BR>
이것저것 조건을 붙혀서 복잡하게 데이터를 조합해야되면 MYSQL을 썼겠지만 그게 아닌 단순 저장 후 종목별로 iterable하게 꺼내쓰는데 mongodb로 충분하다고 생각이 됬었다.
