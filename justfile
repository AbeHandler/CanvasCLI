visible:
  python -m src.cli -v -tt

checkin:
  python -m src.cli -checkin

participation target:
  python -m  src.cli grade -participation -assignment_id {{target}}

quiz day="":
  python -m src.cli -q {{day}}

autograde canvas_name notebook_name:
  python -m src.cli assignment -cn '{{canvas_name}}' -download -nbn '{{notebook_name}}' -autograde

ta:
  rsync -r /Users/abe/everything/teaching/S2023/3220/3220 /Users/abe/BAIM3220FeedbackReports -v --ignore-existing --include="*/" --include="*.html" --exclude="*" 
  cd /Users/abe/BAIM3220FeedbackReports

perfects group_name notebook_name canvas_name:
  python -m src.cli assignment -nbn "{{notebook_name}}" -sync -g "{{group_name}}" -cn "{{canvas_name}}" -perfects

reports notebook_name canvas_name group_name='Exercises':
  python -m src.cli assignment -reports -nbn "{{notebook_name}}" -g "{{group_name}}" -cn "{{canvas_name}}"