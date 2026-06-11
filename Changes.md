## `connectwo_core.launch`

**BaudRate 수정(`230400`):** 라즈베리 파이와 STM32 간의 데이터 전송 대역폭을 일치시킴

**`sleep_time 0.005` 추가:** 루프 사이에 미세한 딜레이를 주어 CPU 점유율 과부하를 막고 통신 흐름을 안정화

## `connectwo_rplidar.launch` (라이다 센서 설정)

**`frame_id`: `map` -> `base_scan` 변경:** 라이다의 물리적 장착 위치 기준 좌표계인 base_scan으로 프레임 ID를 바로잡아, 로봇 중심 기준으로 라이다 데이터가 올바르게 투영되도록 수정

## `connectwo_gmapping.launch`
```
<rosparam command="load" file="$(find turtlebot3_slam)/config/gmapping_params.yaml" />
```
기본 설정 파일이 코드 하단에서 값을 덮어씌우고 있기에 상단으로 위치 변경

## connectwo_slam.launch

**Rviz 가동 스크립트 주석 처리:** 로봇 PC(라즈베리 파이)의 연산 부담과 그래픽 리소스 낭비를 줄이기 위해, Rviz는 원격 개발 PC에서만 켜기 위해 변경

## `connectwo_remote.launch` && `connectwo.urdf`

**터틀봇 의존성 줄임:** 기존 description.launch.xml을 주석 처리하고, `connectwo.urdf` 모델을 추가해 사용하도록 변경

## odom_to_tf.py

**컴퓨팅 아키텍처 최적화:** STM32 보드의 메모리 부족 현상을 해결하기 위해, 상대적으로 여유로운 상위 PC(라즈베리 파이)에서 오도메트리 기반 TF(좌표 변환)를 브로드캐스팅하도록 이관 및 구현
