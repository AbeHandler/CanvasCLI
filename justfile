visible:
  python -m src.cli -v -tt

checkin:
  python -m src.cli -checkin

participation target:
  python -m  src.cli grade -participation -assignment_id {{target}}